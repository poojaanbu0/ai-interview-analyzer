"""HR-only routes for managing interview rooms."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from backend.database import get_db
from backend.dependencies import require_hr
from backend.models.interview import Interview, InterviewStatus
from backend.models.interview_room import InterviewRoom
from backend.models.user import User, UserRole
from backend.schemas.room import AssignCandidateOut, RoomCandidateOut, RoomCreate, RoomOut
from backend.utils import to_utc_naive

router = APIRouter(
    prefix="/rooms",
    tags=["HR: rooms"],
)


def _get_owned_room(db: Session, room_id: int, hr: User) -> InterviewRoom:
    room = db.scalar(
        select(InterviewRoom).where(
            InterviewRoom.id == room_id,
            InterviewRoom.hr_id == hr.id,
        )
    )
    if room is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Room not found")
    return room


@router.post("", response_model=RoomOut, status_code=status.HTTP_201_CREATED)
def create_room(
    data: RoomCreate,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Create a new interview room."""
    room = InterviewRoom(
        hr_id=hr.id,
        **data.model_dump(),
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return RoomOut(
        id=room.id,
        job_title=room.job_title,
        job_description=room.job_description,
        requirements=room.requirements,
        location=room.location,
        employment_type=room.employment_type,
        experience_level=room.experience_level,
        status=room.status,
        created_at=room.created_at,
        candidate_count=0,
        completed_count=0,
    )


@router.get("", response_model=list[RoomOut])
def list_rooms(
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """List all rooms for the logged-in HR with candidate counts."""
    rooms = db.scalars(
        select(InterviewRoom)
        .where(InterviewRoom.hr_id == hr.id)
        .options(selectinload(InterviewRoom.interviews))
        .order_by(InterviewRoom.created_at.desc())
    ).all()

    results = []
    for room in rooms:
        candidate_count = len(room.interviews)
        completed_count = sum(
            1 for i in room.interviews if i.status == InterviewStatus.completed.value
        )
        results.append(
            RoomOut(
                id=room.id,
                job_title=room.job_title,
                job_description=room.job_description,
                requirements=room.requirements,
                location=room.location,
                employment_type=room.employment_type,
                experience_level=room.experience_level,
                status=room.status,
                created_at=room.created_at,
                candidate_count=candidate_count,
                completed_count=completed_count,
            )
        )
    return results


def _compute_overall_score(interview: Interview) -> Optional[float]:
    """Average of the 6 metrics from report_data, if available."""
    if interview.report is None:
        return None
    report_data = interview.report.report_data
    if not isinstance(report_data, dict):
        return None
    metrics = report_data.get("metrics") or report_data.get("scores")
    if not isinstance(metrics, dict):
        return None
    values = [v for v in metrics.values() if isinstance(v, (int, float))]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


@router.get("/{room_id}", response_model=dict)
def get_room_detail(
    room_id: int,
    status_filter: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Return room info and its candidates."""
    room = _get_owned_room(db, room_id, hr)

    query = (
        select(Interview)
        .where(Interview.room_id == room.id)
        .options(
            selectinload(Interview.candidate),
            selectinload(Interview.report),
        )
    )

    if status_filter:
        query = query.where(Interview.status == status_filter)

    interviews = db.scalars(query).all()

    candidates = []
    for iv in interviews:
        if iv.candidate is None:
            continue

        if search and search.lower() not in iv.candidate.name.lower():
            continue

        overall_score = _compute_overall_score(iv)

        candidates.append(
            RoomCandidateOut(
                interview_id=iv.id,
                candidate_id=iv.candidate.id,
                candidate_name=iv.candidate.name,
                candidate_email=iv.candidate.email,
                candidate_summary=iv.candidate_summary,
                resume_url=iv.resume_url,
                scheduled_at=iv.scheduled_at,
                status=iv.status,
                overall_score=overall_score,
            )
        )

    # Sort
    if sort_by == "score":
        candidates.sort(key=lambda c: c.overall_score or 0, reverse=True)
    elif sort_by == "name":
        candidates.sort(key=lambda c: c.candidate_name.lower())
    else:  # default: date
        candidates.sort(
            key=lambda c: c.scheduled_at or datetime.min, reverse=True
        )

    room_out = RoomOut(
        id=room.id,
        job_title=room.job_title,
        job_description=room.job_description,
        requirements=room.requirements,
        location=room.location,
        employment_type=room.employment_type,
        experience_level=room.experience_level,
        status=room.status,
        created_at=room.created_at,
        candidate_count=len(candidates),
        completed_count=sum(1 for c in candidates if c.status == InterviewStatus.completed.value),
    )

    return {"room": room_out, "candidates": candidates}


@router.post(
    "/{room_id}/candidates",
    response_model=AssignCandidateOut,
    status_code=status.HTTP_201_CREATED,
)
async def assign_candidate(
    room_id: int,
    candidate_id: int = Form(...),
    scheduled_at: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    """Assign a candidate to a room with a resume upload."""
    room = _get_owned_room(db, room_id, hr)

    # Validate candidate
    candidate = db.scalar(
        select(User).where(User.id == candidate_id, User.role == UserRole.candidate)
    )
    if candidate is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Candidate not found")

    # Check not already assigned
    existing = db.scalar(
        select(Interview).where(
            Interview.room_id == room.id,
            Interview.candidate_id == candidate_id,
        )
    )
    if existing is not None:
        raise HTTPException(
            status.HTTP_409_CONFLICT, "Candidate is already assigned to this room"
        )

    # Validate file type
    filename = resume.filename or ""
    if not filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Resume must be a PDF or DOCX file"
        )

    # Upload resume
    from backend.services.supabase_storage import upload_resume

    file_bytes = await resume.read()
    resume_url = upload_resume(file_bytes, filename, candidate_id, candidate.name, room_id)

    # Extract text and generate summary
    from backend.services.resume_processor import extract_text, generate_candidate_summary

    text = extract_text(file_bytes, filename)
    candidate_summary = generate_candidate_summary(text, room.job_description)

    # Parse scheduled_at
    parsed_scheduled = to_utc_naive(datetime.fromisoformat(scheduled_at))

    # Create interview
    interview = Interview(
        room_id=room.id,
        hr_id=hr.id,
        candidate_id=candidate.id,
        resume_url=resume_url,
        candidate_summary=candidate_summary,
        scheduled_at=parsed_scheduled,
        job_title=room.job_title,
        job_description=room.job_description,
        requirements=room.requirements,
        location=room.location,
        employment_type=room.employment_type,
        experience_level=room.experience_level,
        status=InterviewStatus.open,
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)

    return AssignCandidateOut(
        interview_id=interview.id,
        candidate_summary=candidate_summary,
        resume_url=resume_url,
    )
