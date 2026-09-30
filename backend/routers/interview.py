from fastapi import APIRouter, UploadFile, File

from backend.services.transcription import transcribe_audio
from backend.services.fluency import (
    calculate_speech_rate,
    count_filler_words
)


router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)


@router.post("/audio")
async def receive_audio(
    audio: UploadFile = File(...)
):

    audio_bytes = await audio.read()

    transcript, duration = transcribe_audio(audio_bytes)

    speech_rate = calculate_speech_rate(
        transcript,
        duration
    )

    filler_words = count_filler_words(
        transcript
    )

    return {
        "transcript": transcript,
        "duration": round(duration, 2),
        "speech_rate": speech_rate,
        "filler_words": filler_words
    }