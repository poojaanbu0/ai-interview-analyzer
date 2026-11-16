
"""Candidate-only routes for assigned interviews."""

import math
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_candidate
from ..models.interview import Interview, InterviewStatus
from ..models.user import User
from ..schemas.application import MyInterviewOut, AttendInterviewOut
from ..utils import utcnow

router = APIRouter(
    prefix="/interviews",
    tags=["Candidate: my interviews"],
)


def get_own_interview(
    db: Session,
    interview_id: int,
    candidate: User,
) -> Interview:
    """Return only an interview assigned to this candidate."""

    interview = db.scalar(
        select(Interview).where(
            Interview.id == interview_id,
            Interview.candidate_id == candidate.id,
        )
    )

    if interview is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Interview not found",
        )

    return interview


def _state(interview: Interview, now: datetime):
    """Calculate candidate-visible state using the server clock."""

    if interview.status == InterviewStatus.completed:
        return "completed", False, 0

    if interview.status == InterviewStatus.abandoned:
        return "completed", False, 0

    if interview.status == InterviewStatus.in_progress:
        return "in_progress", True, 0

    if interview.status == InterviewStatus.open:
        if (
            interview.scheduled_at is not None
            and interview.scheduled_at > now
        ):
            seconds = math.ceil(
                (interview.scheduled_at - now).total_seconds()
            )
            return "upcoming", False, seconds

        return "ready", True, 0

    # Draft and closed interviews are not available to candidates.
    return "completed", False, 0


@router.get("/mine", response_model=list[MyInterviewOut])
def my_interviews(
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """List interviews assigned to the logged-in candidate."""

    now = utcnow()

    interviews = db.scalars(
        select(Interview).where(
            Interview.candidate_id == candidate.id,
            Interview.status.in_(
                [
                    InterviewStatus.open,
                    InterviewStatus.in_progress,
                    InterviewStatus.completed,
                    InterviewStatus.abandoned,
                ]
            ),
        )
    ).all()

    items = []

    for interview in interviews:
        state, can_attend, seconds = _state(interview, now)

        # Hide cancelled/closed interviews from the candidate.
        if interview.status == InterviewStatus.closed:
            continue

        items.append(
            (
                interview,
                MyInterviewOut(
                    interview_id=interview.id,
                    job_title=interview.job_title,
                    job_description=interview.job_description,
                    requirements=interview.requirements,
                    location=interview.location,
                    employment_type=interview.employment_type,
                    experience_level=interview.experience_level,
                    scheduled_at=interview.scheduled_at,
                    state=state,
                    can_attend=can_attend,
                    seconds_until_start=seconds,
                ),
            )
        )

    # Upcoming and ready interviews first.
    active = sorted(
        (item for item in items if item[1].state != "completed"),
        key=lambda item: (
            item[0].scheduled_at or datetime.min
        ),
    )

    # Completed interviews last.
    done = sorted(
        (item for item in items if item[1].state == "completed"),
        key=lambda item: (
            item[0].scheduled_at or datetime.min
        ),
        reverse=True,
    )

    return [output for _, output in active + done]


@router.post(
    "/{interview_id}/attend",
    response_model=AttendInterviewOut,
)
def attend_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """Start an assigned interview or resume an existing one."""

    # Lock the interview row to avoid simultaneous start requests.
    interview = db.scalar(
        select(Interview)
        .where(
            Interview.id == interview_id,
            Interview.candidate_id == candidate.id,
        )
        .with_for_update()
    )

    if interview is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Interview not found",
        )

    if interview.status == InterviewStatus.in_progress:
        return AttendInterviewOut(
            interview_id=interview.id,
            status="in_progress",
        )

    if interview.status == InterviewStatus.completed:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "You have already completed this interview",
        )

    if interview.status != InterviewStatus.open:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This interview is not available",
        )

    if (
        interview.scheduled_at is not None
        and interview.scheduled_at > utcnow()
    ):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "This interview has not started yet. "
            "Please come back at the scheduled time.",
        )

    interview.status = InterviewStatus.in_progress

    db.commit()
    db.refresh(interview)

    return AttendInterviewOut(
        interview_id=interview.id,
        status="in_progress",
    )
