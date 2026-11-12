"""Runs one answer through your existing audio pipeline.
Same steps as /interview/audio: Whisper + Librosa in parallel, fluency metrics,
then the Nemotron answer analysis."""
import json
from concurrent.futures import ThreadPoolExecutor

from .audio_features import extract_audio_features
from .fluency import calculate_speech_rate, count_filler_words
from .interview_analyzer import analyze_interview
from .transcription import transcribe_audio

MIN_WORDS = 2  # fewer words than this = we did not really hear an answer


class NoSpeechError(Exception):
    """The recording had no usable speech."""


def _json_default(value):
    if hasattr(value, "tolist"):  # numpy arrays and numpy numbers
        return value.tolist()
    return str(value)


def json_safe(data):
    """Make sure the result can be stored in a MySQL JSON column."""
    return json.loads(json.dumps(data, default=_json_default))


def process_answer(audio_bytes: bytes, question: str) -> dict:
    with ThreadPoolExecutor(max_workers=2) as pool:
        transcription = pool.submit(transcribe_audio, audio_bytes)
        features = pool.submit(extract_audio_features, audio_bytes)
        transcript, duration = transcription.result()
        audio_features = features.result()

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
                "audio_features": audio_features,
            },
            "answer_analysis": analysis.model_dump(),
        }
    )