from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..models.interview import InterviewStatus


class InterviewCreate(BaseModel):
    """HR creates a job/interview. Status is always set to 'open' by the server."""
    model_config = ConfigDict(str_strip_whitespace=True)

    job_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=150)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)


class InterviewUpdate(BaseModel):
    """Partial update: send only the fields you want to change."""
    model_config = ConfigDict(str_strip_whitespace=True)

    job_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    job_description: Optional[str] = Field(default=None, min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=150)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)
    status: Optional[InterviewStatus] = None

    @model_validator(mode="after")
    def required_fields_cannot_be_null(self):
        for field in ("job_title", "job_description", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class InterviewOut(BaseModel):
    """What HR sees about their own jobs."""
    model_config = ConfigDict(from_attributes=True)

    interview_id: int
    job_title: str
    job_description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    status: InterviewStatus
    created_at: datetime
    applicant_count: int = 0


class JobPublic(BaseModel):
    """What candidates see. No hr_id and no status (only open jobs are shown)."""
    model_config = ConfigDict(from_attributes=True)

    interview_id: int
    job_title: str
    job_description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    created_at: datetime
    has_applied: bool = False