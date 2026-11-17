from datetime import datetime
from sqlalchemy import JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .interview import Interview


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    interview_id: Mapped[int] = mapped_column(
        ForeignKey("interviews.id", ondelete="CASCADE"), unique=True
    )
    report_data: Mapped[dict] = mapped_column(JSON)
    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    interview: Mapped["Interview"] = relationship(back_populates="report")