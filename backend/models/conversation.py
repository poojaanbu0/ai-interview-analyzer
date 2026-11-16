from typing import Optional
from sqlalchemy import Text, Integer, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .interview import Interview


class Conversation(Base):
    """One question/answer turn in an interview."""
    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("interview_id", "sequence_number", name="uq_conv_interview_seq"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id", ondelete="CASCADE"), index=True)
    sequence_number: Mapped[int] = mapped_column(Integer)
    question: Mapped[str] = mapped_column(Text)
    transcript: Mapped[Optional[str]] = mapped_column(Text)
    speech_metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    answer_analysis: Mapped[Optional[dict]] = mapped_column(JSON)

    interview: Mapped["Interview"] = relationship(back_populates="conversations")