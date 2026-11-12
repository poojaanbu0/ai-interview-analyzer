"""Builds the HR report after a candidate finishes. Runs in the background,
so the candidate sees the thank-you page without waiting for the summary."""
import logging

from sqlalchemy import select

from ..database import SessionLocal
from ..models.conversation import Conversation
from ..models.interview_report import InterviewReport
from .interview_summary import generate_interview_summary

logger = logging.getLogger(__name__)


def generate_report(session_id: int) -> None:
    db = SessionLocal()  # background tasks need their own database session
    try:
        already = db.scalar(
            select(InterviewReport.report_id).where(InterviewReport.session_id == session_id)
        )
        if already:
            return

        rows = db.scalars(
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(Conversation.sequence_number)
        ).all()
        if not rows:
            return

        # same shape as InterviewRound in routers/interview.py
        history = []
        for row in rows:
            metrics = row.speech_metrics or {}
            history.append(
                {
                    "question": row.question,
                    "transcript": row.transcript or "",
                    "speech_rate": float(metrics.get("speech_rate") or 0.0),
                    "filler_words": int(metrics.get("filler_words") or 0),
                    "answer_analysis": row.answer_analysis or {},
                }
            )

        summary = generate_interview_summary(history)

        rates = [h["speech_rate"] for h in history if h["speech_rate"] > 0]
        report_data = {
            "summary": summary.model_dump(),
            "metrics": {
                "questions_answered": len(history),
                "average_speech_rate": round(sum(rates) / len(rates), 1) if rates else 0.0,
                "total_filler_words": sum(h["filler_words"] for h in history),
            },
        }
        db.add(InterviewReport(session_id=session_id, report_data=report_data))
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Could not generate the interview report for session %s", session_id)
    finally:
        db.close()