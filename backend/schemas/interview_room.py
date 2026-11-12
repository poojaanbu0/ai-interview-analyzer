from typing import Optional

from pydantic import BaseModel

from ..models.interview_session import SessionStatus


class InterviewStateOut(BaseModel):
    session_id: int
    status: SessionStatus
    total_questions: int
    answered: int
    current_question: Optional[str] = None  # None once the interview is finished
    finished: bool


class AnswerResultOut(BaseModel):
    """All the candidate gets back. Transcript, metrics and analysis stay HR-only."""
    answered: int
    total_questions: int
    finished: bool
    next_question: Optional[str] = None