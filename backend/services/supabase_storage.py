
"""Supabase Storage helpers for resume uploads.

Uses direct HTTP requests to avoid SDK key-format issues
with newer Supabase secret keys (sb_secret_...).
"""

import os
import re

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


def _sanitize(name: str) -> str:
    """Make a name safe for use in a file path."""
    return re.sub(r"[^a-zA-Z0-9_-]", "_", name.strip()).lower()


def upload_resume(
    file_bytes: bytes,
    filename: str,
    candidate_id: int,
    candidate_name: str,
    room_id: int,
) -> str:
    """Upload a resume to the 'resumes' bucket.

    Path: resume/{room_id}/{candidate_id}/candidate_{name}.ext
    """
    url, key = _get_config()

    # Get file extension
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "pdf"
    safe_name = _sanitize(candidate_name)
    storage_path = f"resume/{room_id}/{candidate_id}/candidate_{safe_name}.{ext}"

    # Detect content type
    if ext == "pdf":
        content_type = "application/pdf"
    elif ext == "docx":
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
