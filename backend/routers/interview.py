# from fastapi import APIRouter, UploadFile, File
# import time
# from backend.services.transcription import transcribe_audio
# from backend.services.audio_features import extract_audio_features

# from backend.services.fluency import (
#     calculate_speech_rate,
#     count_filler_words
# )


# router = APIRouter(
#     prefix="/interview",
#     tags=["Interview"]
# )


# @router.post("/audio")
# async def receive_audio(
#     audio: UploadFile = File(...)):

#     total_start = time.perf_counter()

#     audio_bytes = await audio.read()

#     start = time.perf_counter()

#     transcript, duration = transcribe_audio(audio_bytes)

#     whisper_time = time.perf_counter() - start

#     # -----------------------
#     # FLUENCY
#     # -----------------------
#     start = time.perf_counter()
    
#     speech_rate = calculate_speech_rate(
#         transcript,
#         duration
#     )

#     filler_words = count_filler_words(
#         transcript
#     )

#     fluency_time = time.perf_counter() - start

#     # -----------------------
#     # LIBROSA
#     # -----------------------
#     start = time.perf_counter()

#     audio_features = extract_audio_features(
#         audio_bytes
#     )

#     librosa_time = time.perf_counter() - start

#     total_time = time.perf_counter() - total_start

#     print("\n----- PROCESSING TIME -----")
#     print(f"Whisper: {whisper_time:.2f}s")
#     print(f"Fluency: {fluency_time:.4f}s")
#     print(f"Librosa: {librosa_time:.2f}s")
#     print(f"TOTAL: {total_time:.2f}s")
#     print("---------------------------\n")

#     return {
#     "transcript": transcript,
#     "duration": round(duration, 2),
#     "speech_rate": speech_rate,
#     "filler_words": filler_words,
#     "audio_features": audio_features,

#     "processing_time": {
#         "whisper": round(whisper_time, 2),
#         "fluency": round(fluency_time, 4),
#         "librosa": round(librosa_time, 2),
#         "total": round(total_time, 2)
#     }
# }

from fastapi import APIRouter, UploadFile, File, Form
import asyncio
import time
from pathlib import Path

from backend.services.transcription import transcribe_audio
from backend.services.audio_features import extract_audio_features
from backend.services.fluency import (
    calculate_speech_rate,
    count_filler_words
)
from backend.services.interview_analyzer import analyze_interview

router = APIRouter(
    prefix="/interview",
    tags=["Interview"]
)

@router.post("/audio")
async def receive_audio(
    question: str = Form(...),
    audio: UploadFile = File(...)
):
    total_start = time.perf_counter()

    # Read uploaded audio
    audio_bytes = await audio.read()

    # audio_extension = Path(audio.filename).suffix

    # if not audio_extension:
    #     audio_extension = ".wav"


    # -----------------------------------
    # WHISPER + LIBROSA IN PARALLEL
    # -----------------------------------

    parallel_start = time.perf_counter()

    transcription_result, audio_features = await asyncio.gather(

        asyncio.to_thread(
        transcribe_audio,
        audio_bytes
        ),

        asyncio.to_thread(
        extract_audio_features,
        audio_bytes
        )
    )

    parallel_time = time.perf_counter() - parallel_start


    # -----------------------------------
    # TRANSCRIPTION RESULT
    # -----------------------------------

    transcript, duration = transcription_result


    # -----------------------------------
    # SPEECH METRICS
    # -----------------------------------

    fluency_start = time.perf_counter()

    speech_rate = calculate_speech_rate(
        transcript,
        duration
    )

    filler_words = count_filler_words(
        transcript
    )

    fluency_time = time.perf_counter() - fluency_start


    # -----------------------------------
    # NEMOTRON ANSWER ANALYSIS
    # -----------------------------------

    nemotron_start = time.perf_counter()

    answer_analysis = await asyncio.to_thread(
        analyze_interview,
        question,
        transcript,
        speech_rate,
        filler_words
    )

    nemotron_time = time.perf_counter() - nemotron_start


    # -----------------------------------
    # TOTAL PROCESSING TIME
    # -----------------------------------

    total_time = time.perf_counter() - total_start

    print("\n----- PROCESSING TIME -----")
    print(f"Whisper + Librosa: {parallel_time:.2f}s")
    print(f"Fluency: {fluency_time:.4f}s")
    print(f"Nemotron: {nemotron_time:.2f}s")
    print(f"TOTAL: {total_time:.2f}s")
    print("---------------------------\n")


    # -----------------------------------
    # RESPONSE
    # -----------------------------------

    return {
        "question": question,

        "transcript": transcript,

        "duration": round(duration, 2),

        "speech_rate": speech_rate,

        "filler_words": filler_words,

        "audio_features": audio_features,

        "answer_analysis": answer_analysis.model_dump()
    }