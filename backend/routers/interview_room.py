"""The candidate's interview room. The server decides every question and counts the
answers, so the browser cannot skip ahead or change a question."""
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import require_candidate
from ..models.application import ApplicationStatus
from ..models.conversation import Conversation
from ..models.interview_session import SessionStatus
from ..models.user import User
from ..schemas.interview_room import AnswerResultOut, InterviewStateOut
from ..services.interview_pipeline import NoSpeechError, process_answer
from ..services.report_service import generate_report
from ..utils import utcnow
from .candidate_applications import _get_session, get_own_application

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/applications/{application_id}/interview",
    tags=["Candidate: interview room"],
)

MAX_QUESTIONS = 5
FIRST_QUESTION = "Tell me about yourself."
FALLBACK_FOLLOW_UP = "Is there anything else about your experience that you would like to add?"
MAX_AUDIO_BYTES = 25 * 1024 * 1024


def _conversations(db: Session, session_id: int) -> list[Conversation]:
    return list(
        db.scalars(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(Conversation.sequence_number)
        )
    )


def _follow_up(analysis: dict) -> str:
    question = (analysis or {}).get("follow_up_question")
    return question.strip() if isinstance(question, str) and question.strip() else FALLBACK_FOLLOW_UP


def _current_question(conversations: list[Conversation]) -> str:
    if not conversations:
        return FIRST_QUESTION
    return _follow_up(conversations[-1].answer_analysis)


@router.get("/state", response_model=InterviewStateOut)
def interview_state(
    application_id: int,
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    """Where the interview stands. After a page refresh the candidate continues from here."""
    application = get_own_application(db, application_id, candidate)
    session = _get_session(db, application.application_id)
    if session is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Interview has not been started")

    conversations = _conversations(db, session.session_id)
    finished = session.status == SessionStatus.completed
    return InterviewStateOut(
        session_id=session.session_id,
        status=session.status,
        total_questions=MAX_QUESTIONS,
        answered=len(conversations),
        current_question=None if finished else _current_question(conversations),
        finished=finished,
    )


@router.post("/answer", response_model=AnswerResultOut)
def submit_answer(
    application_id: int,
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    candidate: User = Depends(require_candidate),
):
    application = get_own_application(db, application_id, candidate)
    session = _get_session(db, application.application_id)
    if session is None or session.status != SessionStatus.in_progress:
        raise HTTPException(status.HTTP_409_CONFLICT, "This interview is not in progress")

    conversations = _conversations(db, session.session_id)
    answered = len(conversations)
    if answered >= MAX_QUESTIONS:
        raise HTTPException(status.HTTP_409_CONFLICT, "All questions have already been answered")
    question = _current_question(conversations)  # chosen by the server, never by the browser

    audio_bytes = audio.file.read(MAX_AUDIO_BYTES + 1)
    if not audio_bytes:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No audio was received")
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "Recording is too long")

    try:
        result = process_answer(audio_bytes, question)
    except NoSpeechError:
        # does not use up a question and nothing is saved
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "We could not hear your answer. Please check your microphone and record again.",
        )
    except Exception:
        logger.exception("Processing the answer failed (application %s)", application_id)
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "We could not process your recording. Please try again.",
        )

    db.add(
        Conversation(
            session_id=session.session_id,
            sequence_number=answered + 1,
            question=question,
            transcript=result["transcript"],
            speech_metrics=result["speech_metrics"],
            answer_analysis=result["answer_analysis"],
        )
    )

    finished = answered + 1 >= MAX_QUESTIONS
    if finished:  # rule: candidate finishes -> session completed
        session.status = SessionStatus.completed
        session.completed_at = utcnow()
        application.status = ApplicationStatus.interviewed

    try:
        db.commit()
    except IntegrityError:  # the same answer was submitted twice at once
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "This answer was already submitted")

    if finished:
        background_tasks.add_task(generate_report, session.session_id)

    return AnswerResultOut(
        answered=answered + 1,
        total_questions=MAX_QUESTIONS,
        finished=finished,
        next_question=None if finished else _follow_up(result["answer_analysis"]),
    )