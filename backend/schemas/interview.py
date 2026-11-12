from datetime import datetime, timedelta
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator, model_validator

from ..models.application import ApplicationStatus
from ..models.interview import InterviewStatus
from ..models.interview_session import SessionStatus
from ..models.user import User
from ..utils import candidate_code, to_utc_naive, utc_iso, utcnow


def _not_in_the_past(value: datetime) -> datetime:
    value = to_utc_naive(value)
    if value < utcnow() - timedelta(minutes=5):  # small allowance for "start now"
        raise ValueError("Scheduled time cannot be in the past")
    return value


class InterviewCreate(BaseModel):
    """HR creates an interview and assigns it to one candidate."""
    model_config = ConfigDict(str_strip_whitespace=True)

    job_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=150)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)

    candidate_id: int
    candidate_summary: str = Field(min_length=1)  # HR-only; the AI uses it to tailor questions
    scheduled_at: datetime  # send with a timezone, e.g. 2026-11-13T05:00:00Z

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_not_in_past(cls, v: datetime) -> datetime:
        return _not_in_the_past(v)


class InterviewUpdate(BaseModel):
    """Partial update: send only the fields you want to change."""
    model_config = ConfigDict(str_strip_whitespace=True)

    job_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    job_description: Optional[str] = Field(default=None, min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=150)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)
    candidate_summary: Optional[str] = Field(default=None, min_length=1)
    scheduled_at: Optional[datetime] = None
    status: Optional[InterviewStatus] = None  # open <-> closed (cancel / reopen)

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_not_in_past(cls, v: Optional[datetime]) -> Optional[datetime]:
        return None if v is None else _not_in_the_past(v)

    @model_validator(mode="after")
    def required_fields_cannot_be_null(self):
        for field in ("job_title", "job_description", "candidate_summary", "scheduled_at", "status"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class CandidateInfo(BaseModel):
    """Candidate details for HR, including the aalamIN_ ID."""
    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    candidate_code: str

    @classmethod
    def from_user(cls, user: User) -> "CandidateInfo":
        return cls(
            user_id=user.user_id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            candidate_code=candidate_code(user.user_id),
        )


class AssignmentOut(BaseModel):
    application_id: int
    candidate: CandidateInfo
    scheduled_at: Optional[datetime] = None
    candidate_summary: Optional[str] = None
    application_status: ApplicationStatus
    session_status: Optional[SessionStatus] = None  # None = candidate has not started
    has_report: bool = False

    @field_serializer("scheduled_at")
    def serialize_scheduled_at(self, value: Optional[datetime]) -> Optional[str]:
        return utc_iso(value)


class InterviewOut(BaseModel):
    """What HR sees about an interview they created."""
    interview_id: int
    job_title: str
    job_description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    status: InterviewStatus  # closed = cancelled
    created_at: datetime
    assignment: Optional[AssignmentOut] = None