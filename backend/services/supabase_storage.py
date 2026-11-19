
"""Supabase Storage helpers for resume uploads.

Uses direct HTTP requests to avoid SDK key-format issues
with newer Supabase secret keys (sb_secret_...).
"""

import os
import uuid

import httpx
from dotenv import load_dotenv

load_dotenv()


def _get_config() -> tuple[str, str]:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"
        )
    return url, key


def upload_resume(file_bytes: bytes, filename: str, candidate_id: int, room_id: int) -> str:
    """Upload a resume to the 'resumes' bucket and return the storage path."""
    url, key = _get_config()
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    storage_path = f"{room_id}/{candidate_id}/{unique_name}"

    # Detect content type
    lower = filename.lower()
    if lower.endswith(".pdf"):
        content_type = "application/pdf"
    elif lower.endswith(".docx"):
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    else:
        content_type = "application/octet-stream"

    upload_url = f"{url}/storage/v1/object/resumes/{storage_path}"

    resp = httpx.post(
        upload_url,
        content=file_bytes,
        headers={
            "Authorization": f"Bearer {key}",
            "apikey": key,
            "Content-Type": content_type,
        },
        timeout=30,
    )

    if resp.status_code not in (200, 201):
        raise RuntimeError(
            f"Supabase Storage upload failed ({resp.status_code}): {resp.text}"
        )

    return storage_path
