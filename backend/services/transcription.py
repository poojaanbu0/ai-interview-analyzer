
import os
import io
import wave

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env")

client = Groq(api_key=GROQ_API_KEY)


def transcribe_audio(audio_bytes: bytes):

    # Calculate audio duration from the WAV file
    with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
        frames = wav_file.getnframes()
        sample_rate = wav_file.getframerate()

        duration = frames / float(sample_rate)

    # Send audio to Groq
    transcription = client.audio.transcriptions.create(
        file=("answer.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="json",
        language="en",
        temperature=0.0
    )

    transcript = transcription.text.strip()

    return transcript, duration
