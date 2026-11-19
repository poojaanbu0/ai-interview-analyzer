
"""Builds the HR report after a candidate finishes the interview."""

import logging

from sqlalchemy import select

from backend.database import SessionLocal
from backend.models.conversation import Conversation
from backend.models.interview_report import InterviewReport
from backend.services.interview_summary import generate_interview_summary

logger = logging.getLogger(__name__)


def generate_report(interview_id: int) -> None:
    """Generate and save one report for an interview."""

    db = SessionLocal()

    try:
        # Check whether a report already exists.
        already = db.scalar(
            select(InterviewReport.id).where(
                InterviewReport.interview_id == interview_id
            )
        )

        if already is not None:
            return

        # Fetch all answers belonging to this interview.
        rows = db.scalars(
            select(Conversation)
            .where(Conversation.interview_id == interview_id)
            .order_by(Conversation.sequence_number)
        ).all()

        if not rows:
            return

        # Prepare the history for the AI summary service.
        history = []

        for row in rows:
            metrics = row.speech_metrics or {}

            history.append(
                {
                    "question": row.question,
                    "transcript": row.transcript or "",
                    "speech_rate": float(
                        metrics.get("speech_rate") or 0.0
                    ),
                    "filler_words": int(
                        metrics.get("filler_words") or 0
                    ),
                    "answer_analysis": row.answer_analysis or {},
                }
            )

        summary = generate_interview_summary(history)
        summary_dict = summary.model_dump()

        # Calculate overall interview metrics.
        rates = [
            item["speech_rate"]
            for item in history
            if item["speech_rate"] > 0
        ]

        report_data = {
            "summary": summary_dict,
            "metrics": {
                "questions_answered": len(history),
                "average_speech_rate": (
                    round(sum(rates) / len(rates), 1)
                    if rates else 0.0
                ),
                "total_filler_words": sum(
                    item["filler_words"] for item in history
                ),
                "technical_strength": summary_dict.get("technical_strength", 50),
                "communication": summary_dict.get("communication", 50),
                "confidence": summary_dict.get("confidence", 50),
                "problem_solving": summary_dict.get("problem_solving", 50),
                "relevance": summary_dict.get("relevance", 50),
                "clarity": summary_dict.get("clarity", 50),
            },
        }

        # Save the report directly against the interview.
        db.add(
            InterviewReport(
                interview_id=interview_id,
                report_data=report_data,
            )
        )

        db.commit()

    except Exception:
        db.rollback()
        logger.exception(
            "Could not generate the interview report for interview %s",
            interview_id,
        )

    finally:
        db.close()
