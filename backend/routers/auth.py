from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models.user import User, UserRole
from ..schemas.user import Token, UserCreate, UserOut
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Candidates only. HR accounts are created with `python -m backend.create_hr`."""
    email = data.email.lower()

    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")

    user = User(
        name=data.name.strip(),
        email=email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=UserRole.candidate,  # fixed by the server, the client cannot choose it
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # two requests registered the same email at once
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2 form field is called "username"; we put the email in it
    user = db.scalar(select(User).where(User.email == form.username.lower()))

    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.user_id, user.role.value)
    return Token(access_token=token, user=user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user