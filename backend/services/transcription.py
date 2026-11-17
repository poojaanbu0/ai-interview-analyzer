
import os
import io
import wave

from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def _get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment variables")
    return Groq(api_key=api_key)



def transcribe_audio(audio_bytes: bytes):

    # Calculate audio duration from the WAV file
    with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
        frames = wav_file.getnframes()
        sample_rate = wav_file.getframerate()

        duration = frames / float(sample_rate)

    # Send audio to Groq
    client = _get_client()
    transcription = client.audio.transcriptions.create(
        file=("answer.wav", audio_bytes),
        model="whisper-large-v3-turbo",
        response_format="json",
        language="en",
        temperature=0.0
    )

    transcript = transcription.text.strip()

    return transcript, duration
