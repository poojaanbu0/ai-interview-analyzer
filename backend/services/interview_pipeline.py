"""Runs one answer through your existing audio pipeline:
Whisper transcription, fluency metrics, then the Nemotron answer analysis."""
import json

from backend.services.fluency import calculate_speech_rate, count_filler_words
from backend.services.interview_analyzer import analyze_interview
from backend.services.transcription import transcribe_audio

MIN_WORDS = 2  # fewer words than this = we did not really hear an answer


class NoSpeechError(Exception):
    """The recording had no usable speech."""


def _json_default(value):
    if hasattr(value, "tolist"):  # numpy arrays and numpy numbers
        return value.tolist()
    return str(value)


def json_safe(data):
    """Make sure the result can be stored in a database JSON column."""
    return json.loads(json.dumps(data, default=_json_default))


def process_answer(audio_bytes: bytes, question: str) -> dict:
    transcript, duration = transcribe_audio(audio_bytes)

    transcript = (transcript or "").strip()
    if len(transcript.split()) < MIN_WORDS:
        raise NoSpeechError()  # skip the LLM call for an empty recording

    speech_rate = calculate_speech_rate(transcript, duration)
    filler_words = count_filler_words(transcript)
    analysis = analyze_interview(question, transcript, speech_rate, filler_words)

    return json_safe(
        {
            "transcript": transcript,
            "speech_metrics": {
                "duration": round(duration, 2),
                "speech_rate": speech_rate,
                "filler_words": filler_words,
            },
            "answer_analysis": analysis.model_dump(),
        }
    )