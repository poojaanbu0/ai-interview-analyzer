"""Candidate-only routes: apply with a resume, list my applications,
attend the interview (one attempt only) and finish it."""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..dependencies import require_candidate
from ..models.application import Application, ApplicationStatus
from ..models.interview import Interview, InterviewStatus
from ..models.interview_session import InterviewSession, SessionStatus
from ..models.user import User
from ..schemas.application import ApplicationOut, SessionOut
from ..storage import delete_resume, save_resume

router = APIRouter(prefix="/applications", tags=["Candidate: applications"])


def _to_out(application: Application, job_title: str,
            session: Optional[InterviewSession]) -> ApplicationOut:
    return ApplicationOut(
        application_id=application.application_id,
        interview_id=application.interview_id,
        job_title=job_title,
        status=application.status,
        applied_at=application.applied_at,
        session_id=session.session_id if session else None,
        session_status=session.status if session else None,
        # one attempt only: can attend until the session is completed/abandoned
        can_attend=session is None or session.status in (SessionStatus.scheduled, SessionStatus.in_progress),
    )


def get_own_application(db: Session, application_id: int, candidate: User) -> Application:
    """404 for missing OR someone else's application."""
    application = db.scalar(
        select(Application).where(
            Application.application_id == application_id,
            Application.candidate_id == candidate.user_id,
        )
    )
    if application is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")
    return application


def _get_session(db: Session, application_id: int) -> Optional[InterviewSession]:
    return db.scalar(
        select(InterviewSession).where(InterviewSession.application_id == application_id)
    )


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply_to_job(
    interview_id: int = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    # only open jobs accept applications
    job = db.scalar(
        select(Interview).where(
            Interview.interview_id == interview_id,
            Interview.status == InterviewStatus.open,
        )
    )
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")

    # no duplicate applications (checked before saving the file, so no orphan files)
    already = db.scalar(
        select(Application.application_id).where(
            Application.interview_id == interview_id,
            Application.candidate_id == candidate.user_id,
        )
    )
    if already:
        raise HTTPException(status.HTTP_409_CONFLICT, "You have already applied to this job")

    key = save_resume(resume)  # validates type, content and size

    application = Application(
        interview_id=interview_id,
        candidate_id=candidate.user_id,
        resume_path=key,
        status=ApplicationStatus.applied,
    )
    db.add(application)
    try:
        db.commit()
    except IntegrityError:  # two identical requests at once; the DB constraint wins
        db.rollback()
        delete_resume(key)
        raise HTTPException(status.HTTP_409_CONFLICT, "You have already applied to this job")
    db.refresh(application)
    return _to_out(application, job.job_title, None)


@router.get("/mine", response_model=list[ApplicationOut])
def my_applications(
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    applications = db.scalars(
        select(Application)
        .where(Application.candidate_id == candidate.user_id)
        .options(selectinload(Application.interview), selectinload(Application.sessions))
        .order_by(Application.applied_at.desc())
    ).all()

    return [
        _to_out(
            app,
            app.interview.job_title,
            max(app.sessions, key=lambda s: s.session_id, default=None),
        )
        for app in applications
    ]


@router.post("/{application_id}/attend", response_model=SessionOut)
def attend_interview(
    application_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """Creates the interview session, or returns the unfinished one
    (so a page refresh doesn't create duplicates)."""
    application = get_own_application(db, application_id, candidate)
    session = _get_session(db, application.application_id)

    if session is None:
        session = InterviewSession(
            application_id=application.application_id,
            status=SessionStatus.in_progress,
            started_at=datetime.now(),
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
        session.started_at = datetime.now()
        db.commit()
        db.refresh(session)
    return session


@router.post("/{application_id}/finish", response_model=SessionOut)
def finish_interview(
    application_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """Marks the session completed. The frontend then shows the thank-you page."""
    application = get_own_application(db, application_id, candidate)
    session = _get_session(db, application.application_id)

    if session is None or session.status in (SessionStatus.scheduled, SessionStatus.abandoned):
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview has not been started")

    if session.status == SessionStatus.in_progress:
        session.status = SessionStatus.completed
        session.completed_at = datetime.now()
    # already completed -> nothing to change, so a repeated call is harmless

    application.status = ApplicationStatus.interviewed
    db.commit()
    db.refresh(session)
    return session