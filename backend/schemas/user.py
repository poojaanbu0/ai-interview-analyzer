import re
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from backend.models.user import UserRole


class UserCreate(BaseModel):
    """Candidate self-registration. Role is set by the server."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str
    password: str = Field(min_length=8, max_length=72)

    @field_validator("phone")
    @classmethod
    def normalize_phone(cls, v: str) -> str:
        """Accepts Indian mobile numbers and stores 10 digits."""

        digits = re.sub(r"[\s\-()]", "", v)

        if digits.startswith("+91"):
            digits = digits[3:]
        elif digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]
        elif digits.startswith("0") and len(digits) == 11:
            digits = digits[1:]

        if not re.fullmatch(r"[6-9]\d{9}", digits):
            raise ValueError("Enter a valid 10-digit mobile number")

        return digits

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password is too long (max 72 bytes)")
        return v


class UserOut(BaseModel):
    """Safe user data. Never exposes password_hash."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int = Field(validation_alias="id")
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
