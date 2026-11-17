"""Feeds the candidate dropdown on the Create Interview page. HR only."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.dependencies import require_hr
from backend.models.user import User, UserRole
from backend.schemas.interview import CandidateInfo

router = APIRouter(prefix="/hr/candidates", tags=["HR: candidates"])


@router.get("", response_model=list[CandidateInfo])
def list_candidates(
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    candidates = db.scalars(
        select(User)
        .where(User.role == UserRole.candidate)
        .order_by(User.name, User.id)
    ).all()

    return [CandidateInfo.from_user(candidate) for candidate in candidates]