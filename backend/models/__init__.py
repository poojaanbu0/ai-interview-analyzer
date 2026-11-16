# Importing every model here registers them with Base.metadata
# and lets string-based relationships (e.g. "Interview") resolve.
from .user import User, UserRole
from .interview import Interview, InterviewStatus
from .conversation import Conversation
from .interview_report import InterviewReport

__all__ = [
    "User", "UserRole",
    "Interview", "InterviewStatus",
    "Conversation",
    "InterviewReport",
]