from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from backend.utils import utc_iso


class RoomCreate(BaseModel):
    job_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=150)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)


class RoomOut(BaseModel):
    id: int
    job_title: str
    job_description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    status: str
    created_at: datetime
    candidate_count: int = 0
    completed_count: int = 0


class RoomCandidateOut(BaseModel):
    interview_id: int
    candidate_id: int
    candidate_name: str
    candidate_email: str
    candidate_summary: Optional[str] = None
    resume_url: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    status: str
    overall_score: Optional[float] = None

    @field_serializer("scheduled_at")
    def serialize_scheduled_at(self, value):
        return utc_iso(value)


class AssignCandidateOut(BaseModel):
    interview_id: int
    candidate_summary: str
    resume_url: Optional[str] = None
