
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, field_serializer

from ..utils import utc_iso


class MyInterviewOut(BaseModel):
    """One assigned interview, as the candidate sees it."""

    interview_id: int
    job_title: str
    job_description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    scheduled_at: Optional[datetime] = None

    state: Literal[
        "upcoming",
        "ready",
        "in_progress",
        "completed",
    ]

    can_attend: bool
    seconds_until_start: int = 0

    @field_serializer("scheduled_at")
    def serialize_scheduled_at(
        self, value: Optional[datetime]
    ) -> Optional[str]:
        return utc_iso(value)


class AttendInterviewOut(BaseModel):
    """Response after the candidate starts an interview."""

    interview_id: int
    status: Literal["in_progress"]
