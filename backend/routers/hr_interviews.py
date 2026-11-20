
"""HR-only routes for creating, viewing, updating and cancelling interviews."""

from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from backend.database import get_db
from backend.dependencies import require_hr
from backend.models.interview import Interview, InterviewStatus
from backend.models.interview_room import InterviewRoom
from backend.models.user import User, UserRole
from backend.models.conversation import Conversation
from backend.schemas.interview import (
    CandidateInfo,
    InterviewCreate,
    InterviewOut,
    InterviewUpdate,
)

router = APIRouter(
    prefix="/interviews",
    tags=["HR: interviews"],
)

JOB_FIELDS = {
    "job_title",
    "job_description",
    "requirements",
    "location",
    "employment_type",
    "experience_level",
}


def get_owned_interview(
    db: Session,
    interview_id: int,
    hr: User,
) -> Interview:
    """Return an interview only if it belongs to the logged-in HR."""

    interview = db.scalar(
        select(Interview)
        .where(
            Interview.id == interview_id,
            Interview.hr_id == hr.id,
        )
        .options(
            selectinload(Interview.candidate),
            selectinload(Interview.report),
        )
    )

    if interview is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Interview not found",
        )

    return interview


def build_out(interview: Interview) -> InterviewOut:
    """Build the HR response for an interview."""

    candidate_info = None

    if interview.candidate is not None:
        candidate_info = CandidateInfo.from_user(
            interview.candidate
        )

    return InterviewOut(
        interview_id=interview.id,
        job_title=interview.job_title,
        job_description=interview.job_description,
        requirements=interview.requirements,
        location=interview.location,
        employment_type=interview.employment_type,
        experience_level=interview.experience_level,
        candidate=candidate_info,
        candidate_summary=interview.candidate_summary,
        scheduled_at=interview.scheduled_at,
        status=interview.status,
        created_at=interview.created_at,
        has_report=interview.report is not None,
    )


@router.post(
    "",
    response_model=InterviewOut,
    status_code=status.HTTP_201_CREATED,
)
def create_interview(
    data: InterviewCreate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Create a one-candidate room and assign an interview to the candidate."""

    candidate = db.scalar(
        select(User).where(
            User.id == data.candidate_id,
            User.role == UserRole.candidate,
        )
    )

    if candidate is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Candidate not found",
        )

    job_data = data.model_dump(include=JOB_FIELDS)
    room = InterviewRoom(
        hr_id=hr.id,
        **job_data,
    )
    db.add(room)
    db.flush()

    interview = Interview(
        room_id=room.id,
        hr_id=hr.id,
        candidate_id=candidate.id,
        candidate_summary=data.candidate_summary,
        scheduled_at=data.scheduled_at,
        status=InterviewStatus.open,
        **job_data,
    )

    db.add(interview)
    db.commit()
    db.refresh(interview)

    return build_out(
        get_owned_interview(db, interview.id, hr)
    )


@router.get(
    "",
    response_model=list[InterviewOut],
)
def list_my_interviews(
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """List interviews created by the logged-in HR."""

    interviews = db.scalars(
        select(Interview)
        .where(Interview.hr_id == hr.id)
        .options(
            selectinload(Interview.candidate),
            selectinload(Interview.report),
        )
        .order_by(
            Interview.created_at.desc(),
            Interview.id.desc(),
        )
    ).all()

    return [
        build_out(interview)
        for interview in interviews
    ]


@router.get(
    "/{interview_id}",
    response_model=InterviewOut,
)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Get one interview created by this HR."""

    interview = get_owned_interview(
        db,
        interview_id,
        hr,
    )

    return build_out(interview)



@router.get("/{interview_id}/report")
def get_interview_report(
    interview_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Return the generated report and candidate answers for this HR's interview."""

    interview = get_owned_interview(
        db,
        interview_id,
        hr,
    )

    if interview.status != InterviewStatus.completed:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "The interview has not been completed yet.",
        )

    if interview.report is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "The interview report has not been generated yet.",
        )

    conversations = db.scalars(
        select(Conversation)
        .where(Conversation.interview_id == interview.id)
        .order_by(Conversation.sequence_number.desc())
    ).all()

    responses = [
    {
        "question_number": conversation.sequence_number,
        "question": conversation.question,
        "answer": conversation.transcript or "",
        "speech_metrics": conversation.speech_metrics or {},
    }
    for conversation in conversations
]

    return {
        "interview_id": interview.id,
        "report_data": interview.report.report_data,
        "generated_at": interview.report.generated_at,
        "responses": responses,
    }


@router.get("/{interview_id}/report/pdf")
def download_report_pdf(
    interview_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Download the interview report as a PDF."""

    interview = get_owned_interview(db, interview_id, hr)

    if interview.status != InterviewStatus.completed:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "The interview has not been completed yet.",
        )

    if interview.report is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "The interview report has not been generated yet.",
        )

    conversations = db.scalars(
        select(Conversation)
        .where(Conversation.interview_id == interview.id)
        .order_by(Conversation.sequence_number)
    ).all()

    from backend.services.pdf_report import generate_pdf_report

    pdf_conversations = [
        {
            "question": conversation.question,
            "answer": conversation.transcript or "",
        }
        for conversation in conversations
    ]
    pdf_bytes = generate_pdf_report(
        candidate_name=interview.candidate.name if interview.candidate else "Candidate",
        job_title=interview.job_title,
        report_data=interview.report.report_data,
        conversations=pdf_conversations,
    )

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="report_{interview_id}.pdf"'
        },
    )


@router.patch(
    "/{interview_id}",
    response_model=InterviewOut,
)
def update_interview(
    interview_id: int,
    data: InterviewUpdate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Edit or cancel an interview before the candidate starts."""

    interview = get_owned_interview(
        db,
        interview_id,
        hr,
    )

    # Once the candidate starts, HR cannot edit or cancel it.
    if interview.status in (
        InterviewStatus.in_progress,
        InterviewStatus.completed,
        InterviewStatus.abandoned,
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "The candidate has already started or finished "
            "this interview, so it can no longer be changed.",
        )

    changes = data.model_dump(exclude_unset=True)

    # HR may open or close an interview, but cannot manually
    # mark it as in_progress or completed.
    if "status" in changes:
        new_status = changes["status"]

        if new_status not in (
            InterviewStatus.open,
            InterviewStatus.closed,
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "HR can only open or close an interview.",
            )

    for field, value in changes.items():
        setattr(interview, field, value)

    db.commit()

    return build_out(
        get_owned_interview(db, interview_id, hr)
    )
