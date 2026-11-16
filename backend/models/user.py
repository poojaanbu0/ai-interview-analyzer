import enum
from datetime import datetime
from sqlalchemy import String, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from .interview import Interview


class UserRole(str, enum.Enum):
    hr = "hr"
    candidate = "candidate"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(15))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    interviews: Mapped[list["Interview"]] = relationship(
        back_populates="hr", foreign_keys="Interview.hr_id"
    )
    candidate_interviews: Mapped[list["Interview"]] = relationship(
        back_populates="candidate", foreign_keys="Interview.candidate_id"
    )