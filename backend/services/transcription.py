from pathlib import Path
from faster_whisper import WhisperModel
import tempfile
import os

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "models" / "faster_whisper_base"

print("Model path:", MODEL_PATH)
print("Model exists:", MODEL_PATH.exists())

model = WhisperModel(
    str(MODEL_PATH),
    device="cpu",
    compute_type="int8"
)


def transcribe_audio(
    audio_bytes: bytes
):
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_file:

        temp_file.write(audio_bytes)
        temp_path = temp_file.name

    try:
        segments, info = model.transcribe(
            temp_path,
            beam_size=5
        )

        transcript = " ".join(
            segment.text.strip()
            for segment in segments
        )

        return transcript, info.duration

    finally:
        os.remove(temp_path)  