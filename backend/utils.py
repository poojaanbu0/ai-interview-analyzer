from datetime import datetime, timezone
from typing import Optional


def candidate_code(user_id: int) -> str:
    """Display ID for HR, e.g. user_id 1 -> aalamIN_01. Calculated, never stored,
    and never sent to candidates."""
    return f"aalamIN_{user_id:02d}"


def utcnow() -> datetime:
    """Current UTC time as a naive datetime, the way the DATETIME columns store it."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(value: datetime) -> datetime:
    """Aware datetimes are converted to UTC; naive ones are taken to be UTC already."""
    if value.tzinfo is not None:
        return value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


def utc_iso(value: Optional[datetime]) -> Optional[str]:
    """'2026-11-13T05:00:00Z', so browsers know it is UTC and show it in local time."""
    if value is None:
        return None
    return value.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")