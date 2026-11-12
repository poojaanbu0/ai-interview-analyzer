"""HR-only routes: create an interview for one candidate, then list, view, edit or cancel it.
Every query is scoped to the logged-in HR (hr_id), so one HR never sees another HR's work."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..dependencies import require_hr
from ..models.application import Application, ApplicationStatus
from ..models.interview import Interview, InterviewStatus
from ..models.interview_session import InterviewSession
from ..models.user import User, UserRole
from ..schemas.interview import (
    AssignmentOut,
    CandidateInfo,
    InterviewCreate,
    InterviewOut,
    InterviewUpdate,
)

router = APIRouter(prefix="/interviews", tags=["HR: interviews"])

JOB_FIELDS = {"job_title", "job_description", "requirements", "location", "employment_type", "experience_level"}


def _load_options():
    return (
        selectinload(Interview.applications).selectinload(Application.candidate),
        selectinload(Interview.applications)
        .selectinload(Application.sessions)
        .selectinload(InterviewSession.report),
    )


def get_owned_interview(db: Session, interview_id: int, hr: User) -> Interview:
    """404 (not 403) when the interview is missing OR belongs to another HR."""
    interview = db.scalar(
        select(Interview)
        .where(Interview.interview_id == interview_id, Interview.hr_id == hr.user_id)
        .options(*_load_options())
        .execution_options(populate_existing=True)
    )
    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")
    return interview


def build_out(interview: Interview) -> InterviewOut:
    application = min(interview.applications, key=lambda a: a.application_id, default=None)
    assignment = None
    if application is not None:
        session = max(application.sessions, key=lambda s: s.session_id, default=None)
        assignment = AssignmentOut(
            application_id=application.application_id,
            candidate=CandidateInfo.from_user(application.candidate),
            scheduled_at=application.scheduled_at,
            candidate_summary=application.candidate_summary,
            application_status=application.status,
            session_status=session.status if session else None,
            has_report=bool(session and session.report),
        )
    return InterviewOut(
        interview_id=interview.interview_id,
        job_title=interview.job_title,
        job_description=interview.job_description,
        requirements=interview.requirements,
        location=interview.location,
        employment_type=interview.employment_type,
        experience_level=interview.experience_level,
        status=interview.status,
        created_at=interview.created_at,
        assignment=assignment,
    )


@router.post("", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    candidate = db.scalar(
        select(User).where(User.user_id == data.candidate_id, User.role == UserRole.candidate)
    )
    if candidate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    interview = Interview(
        hr_id=hr.user_id,
        status=InterviewStatus.open,
        **data.model_dump(include=JOB_FIELDS),
    )
    # the application row is the assignment: this candidate, this time, this summary
    interview.applications.append(
        Application(
            candidate_id=candidate.user_id,
            candidate_summary=data.candidate_summary,
            scheduled_at=data.scheduled_at,
            status=ApplicationStatus.applied,
        )
    )
    db.add(interview)
    db.commit()
    return build_out(get_owned_interview(db, interview.interview_id, hr))


@router.get("", response_model=list[InterviewOut])
def list_my_interviews(
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    interviews = db.scalars(
        select(Interview)
        .where(Interview.hr_id == hr.user_id)
        .options(*_load_options())
        .order_by(Interview.created_at.desc(), Interview.interview_id.desc())
    ).all()
    return [build_out(i) for i in interviews]


@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    return build_out(get_owned_interview(db, interview_id, hr))


@router.patch("/{interview_id}", response_model=InterviewOut)
def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Edit or cancel (status=closed). Only possible until the candidate has started."""
    interview = get_owned_interview(db, interview_id, hr)
    application = min(interview.applications, key=lambda a: a.application_id, default=None)

    if application is not None and application.sessions:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "The candidate has already started this interview, so it can no longer be changed",
        )

    changes = data.model_dump(exclude_unset=True)
    for field in ("candidate_summary", "scheduled_at"):  # these belong to the assignment
        if field in changes:
            value = changes.pop(field)
            if application is not None:
                setattr(application, field, value)
    for field, value in changes.items():
        setattr(interview, field, value)

    db.commit()
    return build_out(get_owned_interview(db, interview_id, hr))