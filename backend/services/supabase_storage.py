
"""Supabase Storage helpers for resume uploads."""

import os
import uuid

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

_client: Client | None = None


def _get_supabase_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"
            )
        _client = create_client(url, key)
    return _client


def upload_resume(file_bytes: bytes, filename: str, candidate_id: int, room_id: int) -> str:
    """Upload a resume to the 'resumes' bucket and return the storage path."""
    client = _get_supabase_client()
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    storage_path = f"{room_id}/{candidate_id}/{unique_name}"

    client.storage.from_("resumes").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": "application/octet-stream"},
    )

    return storage_path
