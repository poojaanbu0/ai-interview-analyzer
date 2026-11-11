"""Resume file storage. Files live on disk; the database stores only the
generated file name (the 'storage key'), never the candidate's original name."""
import os
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status

BASE_DIR = Path(__file__).resolve().parent.parent  # project root
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads")) / "resumes"
MAX_RESUME_BYTES = int(os.getenv("MAX_RESUME_MB", 5)) * 1024 * 1024

# allowed extension -> file signature(s) that the content must start with
ALLOWED_TYPES = {
    ".pdf": [b"%PDF"],
    ".docx": [b"PK\x03\x04"],
    ".doc": [b"\xd0\xcf\x11\xe0"],
}
MEDIA_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".doc": "application/msword",
}


def save_resume(upload: UploadFile) -> str:
    """Validate and save the file. Returns the storage key to put in the DB."""
    ext = Path(upload.filename or "").suffix.lower()
    if ext not in ALLOWED_TYPES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Resume must be a PDF, DOC or DOCX file")

    # don't trust the extension alone: check the file's first bytes too
    header = upload.file.read(8)
    upload.file.seek(0)
    if not any(header.startswith(sig) for sig in ALLOWED_TYPES[ext]):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File content does not match its extension")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    key = f"{uuid.uuid4().hex}{ext}"
    destination = UPLOAD_DIR / key

    size = 0
    try:
        with open(destination, "wb") as out:
            while chunk := upload.file.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_RESUME_BYTES:
                    raise HTTPException(
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        f"Resume is too large (max {MAX_RESUME_BYTES // (1024 * 1024)} MB)",
                    )
                out.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return key


def delete_resume(key: str) -> None:
    (UPLOAD_DIR / key).unlink(missing_ok=True)


def resume_file_path(key: str) -> Path:
    """Resolve a storage key to a file, refusing anything outside UPLOAD_DIR."""
    path = (UPLOAD_DIR / key).resolve()
    if UPLOAD_DIR.resolve() not in path.parents or not path.is_file():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume file not found")
    return path