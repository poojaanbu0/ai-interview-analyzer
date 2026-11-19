import enum
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

if TYPE_CHECKING:
    from .user import User
    from .interview import Interview


class RoomStatus(str, enum.Enum):
    open = "open"
    closed = "closed"


class InterviewRoom(Base):
    """A job-posting room created by HR. Multiple candidates can be assigned."""

    __tablename__ = "interview_rooms"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    hr_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    job_title: Mapped[str] = mapped_column(String(200))
    job_description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(150))
    employment_type: Mapped[Optional[str]] = mapped_column(String(50))
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20), default=RoomStatus.open.value, server_default=RoomStatus.open.value
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    hr: Mapped["User"] = relationship(back_populates="rooms", foreign_keys=[hr_id])
    interviews: Mapped[list["Interview"]] = relationship(
        back_populates="room", cascade="all, delete-orphan"
    )
