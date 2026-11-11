"""HR downloads an applicant's resume, only for jobs that HR created."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_hr
from ..models.application import Application
from ..models.interview import Interview
from ..models.user import User
from ..storage import MEDIA_TYPES, resume_file_path

router = APIRouter(prefix="/hr/applications", tags=["HR: resumes"])


@router.get("/{application_id}/resume")
def download_resume(
    application_id: int,
    db: Session = Depends(get_db),
    hr: User = Depends(require_hr),
):
    application = db.scalar(
        select(Application)
        .join(Interview, Interview.interview_id == Application.interview_id)
        .where(
            Application.application_id == application_id,
            Interview.hr_id == hr.user_id,  # ownership check
        )
    )
    if application is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Application not found")

    path = resume_file_path(application.resume_path)
    return FileResponse(
        path,
        media_type=MEDIA_TYPES.get(path.suffix.lower(), "application/octet-stream"),
        filename=f"resume_{application_id}{path.suffix}",
    )