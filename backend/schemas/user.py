from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from ..models.user import UserRole

class UserCreate(BaseModel):
    """Request body for /auth/register."""
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    role: UserRole

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        return v.strip().lower() if isinstance(v, str) else v

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, v: str) -> str:
        # bcrypt only handles 72 bytes (non-English characters take more than 1 byte)
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password is too long (max 72 bytes)")
        return v


class UserOut(BaseModel):
    """Safe user data to return. Never includes password_hash."""
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    name: str
    email: EmailStr
    role: UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut