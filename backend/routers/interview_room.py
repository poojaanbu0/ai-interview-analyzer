
"""Candidate interview room.

The server controls the questions and answer count.
The browser cannot skip questions or submit its own question.
"""

import logging

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_candidate
from ..models.conversation import Conversation
from ..models.interview import Interview, InterviewStatus
from ..models.user import User
from ..schemas.interview_room import (
    AnswerResultOut,
    InterviewResponseOut,
    InterviewStateOut,
)
from ..services.interview_pipeline import NoSpeechError, process_answer
from ..services.report_service import generate_report
from .candidate_applications import get_own_interview

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/interviews/{interview_id}",
    tags=["Candidate: interview room"],
)

MAX_QUESTIONS = 5
FIRST_QUESTION = "Tell me about yourself."
FALLBACK_FOLLOW_UP = (
    "Is there anything else about your experience "
    "that you would like to add?"
)
MAX_AUDIO_BYTES = 25 * 1024 * 1024


def _conversations(
    db: Session,
    interview_id: int,
) -> list[Conversation]:

    return list(
        db.scalars(
            select(Conversation)
            .where(Conversation.interview_id == interview_id)
            .order_by(Conversation.sequence_number)
        )
    )


def _follow_up(analysis: dict) -> str:

    question = (analysis or {}).get("follow_up_question")

    if isinstance(question, str) and question.strip():
        return question.strip()

    return FALLBACK_FOLLOW_UP


def _current_question(
    conversations: list[Conversation],
) -> str:

    if not conversations:
        return FIRST_QUESTION

    return _follow_up(conversations[-1].answer_analysis)



@router.get("/state", response_model=InterviewStateOut)
def interview_state(
    interview_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """Return interview progress and previous answers."""

    interview = get_own_interview(
        db, interview_id, candidate
    )

    if interview.status not in (
        InterviewStatus.in_progress,
        InterviewStatus.completed,
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Interview has not been started",
        )

    conversations = _conversations(db, interview_id)

    finished = (
        interview.status == InterviewStatus.completed
    )

    responses = [
        InterviewResponseOut(
            question_number=conversation.sequence_number,
            question=conversation.question,
            answer=conversation.transcript or "",
        )
        for conversation in reversed(conversations)
    ]

    return InterviewStateOut(
        interview_id=interview.id,
        total_questions=MAX_QUESTIONS,
        answered=len(conversations),
        current_question=(
            None if finished
            else _current_question(conversations)
        ),
        finished=finished,
        responses=responses,
    )


@router.post("/answer", response_model=AnswerResultOut)
def submit_answer(
    interview_id: int,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """Process and save one candidate answer."""

    # Lock the interview row to prevent simultaneous submissions
    # from creating duplicate question numbers.
    interview = db.scalar(
        select(Interview)
        .where(
            Interview.id == interview_id,
            Interview.candidate_id == candidate.id,
        )
        .with_for_update()
    )

    if interview is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "Interview not found",
        )

    if interview.status != InterviewStatus.in_progress:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This interview is not in progress",
        )

    conversations = _conversations(db, interview_id)
    answered = len(conversations)

    if answered >= MAX_QUESTIONS:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "All questions have already been answered",
        )

    # The server decides the question.
    question = _current_question(conversations)

    audio_bytes = audio.file.read(MAX_AUDIO_BYTES + 1)

    if not audio_bytes:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "No audio was received",
        )

    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            "Recording is too long",
        )

    try:
        result = process_answer(audio_bytes, question)

    except NoSpeechError:
        db.rollback()

        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "We could not hear your answer. "
            "Please check your microphone and record again.",
        )

    except Exception:
        db.rollback()

        logger.exception(
            "Processing answer failed for interview %s",
            interview_id,
        )

        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "We could not process your recording. Please try again.",
        )

    # Save the answer directly against the interview.
    db.add(
        Conversation(
            interview_id=interview.id,
            sequence_number=answered + 1,
            question=question,
            transcript=result["transcript"],
            speech_metrics=result["speech_metrics"],
            answer_analysis=result["answer_analysis"],
        )
    )

    finished = answered + 1 >= MAX_QUESTIONS

    if finished:
        interview.status = InterviewStatus.completed

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "This answer was already submitted",
        )

    if finished:
        background_tasks.add_task(
            generate_report,
            interview.id,
        )

    return AnswerResultOut(
        answered=answered + 1,
        total_questions=MAX_QUESTIONS,
        finished=finished,
        next_question=(
            None if finished
            else _follow_up(result["answer_analysis"])
        ),
    )
