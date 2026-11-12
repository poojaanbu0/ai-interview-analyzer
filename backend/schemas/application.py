from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, field_serializer

from ..models.interview_session import SessionStatus
from ..utils import utc_iso


class MyInterviewOut(BaseModel):
    """One assigned interview, as the candidate sees it.
    No candidate summary, no HR details and no candidate ID."""
    application_id: int
    job_title: str
    job_description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    state: Literal["upcoming", "ready", "in_progress", "completed"]
    can_attend: bool
    seconds_until_start: int = 0  # decided by the server clock

    @field_serializer("scheduled_at")
    def serialize_scheduled_at(self, value: Optional[datetime]) -> Optional[str]:
        return utc_iso(value)


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: int
    application_id: int
    status: SessionStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None