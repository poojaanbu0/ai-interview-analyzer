from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from ..models.application import ApplicationStatus
from ..models.interview_session import SessionStatus


class ApplicantOut(BaseModel):
    """One row in HR's applicant list. Server file paths are never exposed."""
    application_id: int
    candidate_id: int
    candidate_name: str
    candidate_email: EmailStr
    status: ApplicationStatus
    applied_at: datetime
    session_status: Optional[SessionStatus] = None  # None = has not attended yet
    has_report: bool = False


class ApplicationOut(BaseModel):
    """One row in the candidate's 'my applications' list."""
    application_id: int
    interview_id: int
    job_title: str
    status: ApplicationStatus
    applied_at: datetime
    session_id: Optional[int] = None
    session_status: Optional[SessionStatus] = None
    can_attend: bool = True  # drives the Attend Interview button


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    application_id: int
    status: SessionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None