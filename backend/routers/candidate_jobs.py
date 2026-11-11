"""Candidate-only routes for browsing jobs that HR has created."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_candidate
from ..models.application import Application
from ..models.interview import Interview, InterviewStatus
from ..models.user import User
from ..schemas.interview import JobPublic

router = APIRouter(prefix="/jobs", tags=["Candidate: jobs"])


def _applied_ids(db: Session, candidate: User) -> set[int]:
    return set(
        db.scalars(
            select(Application.interview_id).where(Application.candidate_id == candidate.user_id)
        )
    )


@router.get("", response_model=list[JobPublic])
def browse_jobs(
    q: Optional[str] = Query(None, max_length=100, description="Search in job title"),
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    stmt = (
        select(Interview)
        .where(Interview.status == InterviewStatus.open)
        .order_by(Interview.created_at.desc(), Interview.interview_id.desc())
    )
    if q:
        stmt = stmt.where(Interview.job_title.ilike(f"%{q.strip()}%"))

    applied = _applied_ids(db, candidate)
    result = []
    for job in db.scalars(stmt):
        item = JobPublic.model_validate(job)
        item.has_applied = job.interview_id in applied
        result.append(item)
    return result


@router.get("/{interview_id}", response_model=JobPublic)
def get_job(
    interview_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    job = db.scalar(
        select(Interview).where(
            Interview.interview_id == interview_id,
            Interview.status == InterviewStatus.open,
        )
    )
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")

    item = JobPublic.model_validate(job)
    item.has_applied = interview_id in _applied_ids(db, candidate)
    return item