"""HR-only routes. Every query is scoped to the logged-in HR (hr_id check),
so one HR can never see or change another HR's jobs or applicants."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..dependencies import require_hr
from ..models.application import Application
from ..models.interview import Interview, InterviewStatus
from ..models.interview_session import InterviewSession
from ..models.user import User
from ..schemas.application import ApplicantOut
from ..schemas.interview import InterviewCreate, InterviewOut, InterviewUpdate

router = APIRouter(prefix="/interviews", tags=["HR: interviews"])


def get_owned_interview(db: Session, interview_id: int, hr: User) -> Interview:
    """404 (not 403) when the job doesn't exist OR belongs to another HR,
    so nobody can probe for other HRs' job ids."""
    interview = db.scalar(
        select(Interview).where(
            Interview.interview_id == interview_id,
            Interview.hr_id == hr.user_id,
        )
    )
    if interview is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")
    return interview


def to_out(db: Session, interview: Interview) -> InterviewOut:
    count = db.scalar(
        select(func.count(Application.application_id)).where(
            Application.interview_id == interview.interview_id
        )
    )
    out = InterviewOut.model_validate(interview)
    out.applicant_count = count or 0
    return out


@router.post("", response_model=InterviewOut, status_code=status.HTTP_201_CREATED)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    # Rule: HR creates job -> job becomes available to candidates (status = open)
    interview = Interview(hr_id=hr.user_id, status=InterviewStatus.open, **data.model_dump())
    db.add(interview)
    db.commit()
    db.refresh(interview)
    return to_out(db, interview)


@router.get("", response_model=list[InterviewOut])
def list_my_interviews(
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    rows = db.execute(
        select(Interview, func.count(Application.application_id))
        .outerjoin(Application, Application.interview_id == Interview.interview_id)
        .where(Interview.hr_id == hr.user_id)
        .group_by(Interview.interview_id)
        .order_by(Interview.created_at.desc(), Interview.interview_id.desc())
    ).all()

    result = []
    for interview, count in rows:
        out = InterviewOut.model_validate(interview)
        out.applicant_count = count
        result.append(out)
    return result


@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    return to_out(db, get_owned_interview(db, interview_id, hr))


@router.patch("/{interview_id}", response_model=InterviewOut)
def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    interview = get_owned_interview(db, interview_id, hr)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(interview, field, value)
    db.commit()
    db.refresh(interview)
    return to_out(db, interview)


@router.get("/{interview_id}/applicants", response_model=list[ApplicantOut])
def list_applicants(
    interview_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    interview = get_owned_interview(db, interview_id, hr)

    applications = db.scalars(
        select(Application)
        .where(Application.interview_id == interview.interview_id)
        .options(
            selectinload(Application.candidate),
            selectinload(Application.sessions).selectinload(InterviewSession.report),
        )
        .order_by(Application.applied_at.desc())
    ).all()

    result = []
    for app in applications:
        session = max(app.sessions, key=lambda s: s.session_id, default=None)
        result.append(
            ApplicantOut(
                application_id=app.application_id,
                candidate_id=app.candidate_id,
                candidate_name=app.candidate.name,
                candidate_email=app.candidate.email,
                status=app.status,
                applied_at=app.applied_at,
                session_status=session.status if session else None,
                has_report=bool(session and session.report),
            )
        )
    return result