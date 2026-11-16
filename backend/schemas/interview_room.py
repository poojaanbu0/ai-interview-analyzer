
from typing import Optional

from pydantic import BaseModel


class InterviewResponseOut(BaseModel):
    question_number: int
    question: str
    answer: str


class InterviewStateOut(BaseModel):
    interview_id: int
    total_questions: int
    answered: int
    current_question: Optional[str] = None
    finished: bool
    responses: list[InterviewResponseOut] = []


class AnswerResultOut(BaseModel):
    """Candidate receives only progress and the next question."""

    answered: int
    total_questions: int
    finished: bool
    next_question: Optional[str] = None
