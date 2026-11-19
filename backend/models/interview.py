import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .user import User
    from .conversation import Conversation
    from .interview_report import InterviewReport
    from .interview_room import InterviewRoom


class InterviewStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    closed = "closed"
    in_progress = "in_progress"
    completed = "completed"
    abandoned = "abandoned"


class Interview(Base):
    """A candidate-specific interview created by HR."""
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hr_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    job_title: Mapped[str] = mapped_column(String(200))
    job_description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(150))
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    room_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("interview_rooms.id", ondelete="CASCADE"), index=True
    )
    candidate_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    candidate_summary: Mapped[Optional[str]] = mapped_column(Text)
    resume_url: Mapped[Optional[str]] = mapped_column(Text)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(
        String(20), default=InterviewStatus.open.value, server_default=InterviewStatus.open.value
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    room: Mapped[Optional["InterviewRoom"]] = relationship(
        back_populates="interviews", foreign_keys=[room_id]
    )
    hr: Mapped["User"] = relationship(back_populates="interviews", foreign_keys=[hr_id])
    candidate: Mapped[Optional["User"]] = relationship(
        back_populates="candidate_interviews", foreign_keys=[candidate_id]
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="interview",
        cascade="all, delete-orphan",
        order_by="Conversation.sequence_number",
    )
    report: Mapped[Optional["InterviewReport"]] = relationship(
        back_populates="interview", uselist=False, cascade="all, delete-orphan"
    )