
from datetime import datetime, timedelta
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

from ..models.interview import InterviewStatus
from ..models.user import User
from ..utils import candidate_code, to_utc_naive, utc_iso, utcnow


def _not_in_the_past(value: datetime) -> datetime:
    value = to_utc_naive(value)

    if value < utcnow() - timedelta(minutes=5):
        raise ValueError("Scheduled time cannot be in the past")

    return value


class InterviewCreate(BaseModel):
    """HR creates an interview and assigns it directly to a candidate."""

    model_config = ConfigDict(str_strip_whitespace=True)

    job_title: str = Field(min_length=1, max_length=200)
    job_description: str = Field(min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=150)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)

    candidate_id: int
    candidate_summary: str = Field(min_length=1)
    scheduled_at: datetime

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_not_in_past(cls, value: datetime) -> datetime:
        return _not_in_the_past(value)


class InterviewUpdate(BaseModel):
    """Partial update of an interview."""

    model_config = ConfigDict(str_strip_whitespace=True)

    job_title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    job_description: Optional[str] = Field(default=None, min_length=1)
    requirements: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=150)
    employment_type: Optional[str] = Field(default=None, max_length=50)
    experience_level: Optional[str] = Field(default=None, max_length=50)

    candidate_summary: Optional[str] = Field(default=None, min_length=1)
    scheduled_at: Optional[datetime] = None
    status: Optional[InterviewStatus] = None

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_not_in_past(
        cls, value: Optional[datetime]
    ) -> Optional[datetime]:
        return None if value is None else _not_in_the_past(value)

    @model_validator(mode="after")
    def required_fields_cannot_be_null(self):
        for field in (
            "job_title",
            "job_description",
            "candidate_summary",
            "scheduled_at",
            "status",
        ):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")

        return self


class CandidateInfo(BaseModel):
    """Candidate information displayed to HR."""

    user_id: int
    name: str
    email: str
    phone: Optional[str] = None
    candidate_code: str

    @classmethod
    def from_user(cls, user: User) -> "CandidateInfo":
        return cls(
            user_id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            candidate_code=candidate_code(user.id),
        )


class InterviewOut(BaseModel):
    """Interview details returned to HR."""

    interview_id: int
    job_title: str
    job_description: str
    requirements: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None

    candidate: Optional[CandidateInfo] = None
    candidate_summary: Optional[str] = None
    scheduled_at: Optional[datetime] = None

    status: InterviewStatus
    created_at: datetime
    has_report: bool = False

    @field_serializer("scheduled_at")
    def serialize_scheduled_at(
        self, value: Optional[datetime]
    ) -> Optional[str]:
        return utc_iso(value)
