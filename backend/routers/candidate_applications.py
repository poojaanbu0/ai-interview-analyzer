"""Candidate-only routes: list the interviews HR assigned to me, and attend them.
There is no browsing and no applying: a candidate only ever sees their own assignments."""
import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..dependencies import require_candidate
from ..models.application import Application
from ..models.interview import Interview, InterviewStatus
from ..models.interview_session import InterviewSession, SessionStatus
from ..models.user import User
from ..schemas.application import MyInterviewOut, SessionOut
from ..utils import utcnow

router = APIRouter(prefix="/applications", tags=["Candidate: my interviews"])


def get_own_application(db: Session, application_id: int, candidate: User) -> Application:
    """404 for missing OR someone else's assignment."""
    application = db.scalar(
        select(Application).where(
            Application.application_id == application_id,
            Application.candidate_id == candidate.user_id,
        )
    )
    if application is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Interview not found")
    return application


def _get_session(db: Session, application_id: int) -> Optional[InterviewSession]:
    return db.scalar(
        select(InterviewSession).where(InterviewSession.application_id == application_id)
    )


def _state(application: Application, session: Optional[InterviewSession], now: datetime):
    """-> (state, can_attend, seconds_until_start), using the SERVER clock."""
    if session is not None:
        if session.status in (SessionStatus.completed, SessionStatus.abandoned):
            return "completed", False, 0  # one attempt only
        return "in_progress", True, 0
    if application.scheduled_at is not None and application.scheduled_at > now:
        seconds = math.ceil((application.scheduled_at - now).total_seconds())
        return "upcoming", False, seconds
    return "ready", True, 0  # no schedule (older rows) counts as ready


@router.get("/mine", response_model=list[MyInterviewOut])
def my_interviews(
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    now = utcnow()
    applications = db.scalars(
        select(Application)
        .join(Interview, Interview.interview_id == Application.interview_id)
        .where(
            Application.candidate_id == candidate.user_id,
            Interview.status == InterviewStatus.open,  # cancelled interviews disappear
        )
        .options(selectinload(Application.interview), selectinload(Application.sessions))
    ).all()

    items = []
    for app in applications:
        session = max(app.sessions, key=lambda s: s.session_id, default=None)
        state, can_attend, seconds = _state(app, session, now)
        job = app.interview
        items.append(
            (
                app,
                MyInterviewOut(
                    application_id=app.application_id,
                    job_title=job.job_title,
                    job_description=job.job_description,
                    requirements=job.requirements,
                    location=job.location,
                    employment_type=job.employment_type,
                    experience_level=job.experience_level,
                    scheduled_at=app.scheduled_at,
                    state=state,
                    can_attend=can_attend,
                    seconds_until_start=seconds,
                ),
            )
        )

    # upcoming work first (soonest at the top), finished interviews last
    active = sorted(
        (i for i in items if i[1].state != "completed"),
        key=lambda i: i[0].scheduled_at or datetime.min,
    )
    done = sorted(
        (i for i in items if i[1].state == "completed"),
        key=lambda i: i[0].scheduled_at or datetime.min,
        reverse=True,
    )
    return [out for _, out in active + done]


@router.post("/{application_id}/attend", response_model=SessionOut)
def attend_interview(
    application_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """Starts the interview, or returns the unfinished one (so a refresh doesn't duplicate it).
    Refused before the scheduled time, no matter what the browser says."""
    application = get_own_application(db, application_id, candidate)
    session = _get_session(db, application.application_id)

    if session is None:
        if application.interview.status != InterviewStatus.open:
            raise HTTPException(status.HTTP_409_CONFLICT, "This interview has been cancelled")
        if application.scheduled_at is not None and application.scheduled_at > utcnow():
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "This interview has not started yet. Please come back at the scheduled time.",
            )

        session = InterviewSession(
            application_id=application.application_id,
            status=SessionStatus.in_progress,
            started_at=utcnow(),
        )
        db.add(session)
        try:
            db.commit()
            db.refresh(session)
            return session
        except IntegrityError:  # a parallel request created it first
            db.rollback()
            session = _get_session(db, application.application_id)
            if session is None:
                raise

    # one attempt only
    if session.status in (SessionStatus.completed, SessionStatus.abandoned):
        raise HTTPException(status.HTTP_409_CONFLICT, "You have already attended this interview")

    if session.status == SessionStatus.scheduled:
        session.status = SessionStatus.in_progress
        session.started_at = utcnow()
        db.commit()
        db.refresh(session)
    return session