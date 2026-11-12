"""Feeds the candidate dropdown on the Create Interview page. HR only."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_hr
from ..models.user import User, UserRole
from ..schemas.interview import CandidateInfo

router = APIRouter(prefix="/hr/candidates", tags=["HR: candidates"])


@router.get("", response_model=list[CandidateInfo])
def list_candidates(
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    candidates = db.scalars(
        select(User).where(User.role == UserRole.candidate).order_by(User.name, User.user_id)
    ).all()
    return [CandidateInfo.from_user(c) for c in candidates]