# Importing every model here registers them with Base.metadata
# and lets string-based relationships (e.g. "Interview") resolve.
from backend.models.user import User, UserRole
from backend.models.interview import Interview, InterviewStatus
from backend.models.conversation import Conversation
from backend.models.interview_report import InterviewReport
from backend.models.interview_room import InterviewRoom, RoomStatus

__all__ = [
    "User", "UserRole",
    "Interview", "InterviewStatus",
    "Conversation",
    "InterviewReport",
    "InterviewRoom", "RoomStatus",
]