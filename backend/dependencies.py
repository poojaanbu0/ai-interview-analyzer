from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User, UserRole
from backend.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise credentials_error

    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise credentials_error
    return user




def require_role(*allowed: UserRole):
    """Allow access only to users with an explicitly permitted role."""

    allowed_values = {role.value for role in allowed}

    def checker(user: User = Depends(get_current_user)) -> User:
        user_role = getattr(user.role, "value", user.role)

        if user_role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied. Required role: {sorted(allowed_values)}. "
                    f"Current role: {user_role}"
                ),
            )

        return user

    return checker


require_hr = require_role(UserRole.hr)
require_candidate = require_role(UserRole.candidate)
