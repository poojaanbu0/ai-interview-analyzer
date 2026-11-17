"""Create an HR account. Run from the project root (venv active):

    python -m backend.create_hr
"""
import re
from getpass import getpass

from sqlalchemy import select

from backend import models  # noqa: F401  (registers every table)
from backend.database import SessionLocal
from backend.models.user import User, UserRole
from backend.security import hash_password


def main() -> None:
    name = input("Full name: ").strip()
    email = input("Email: ").strip().lower()
    phone = input("Phone (optional): ").strip() or None
    password = getpass("Password (8 to 72 characters): ")
    confirm = getpass("Confirm password: ")

    if not name or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise SystemExit("Please enter a name and a valid email.")
    if not 8 <= len(password.encode("utf-8")) <= 72:
        raise SystemExit("The password must be 8 to 72 characters.")
    if password != confirm:
        raise SystemExit("The passwords do not match.")

    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == email)):
            raise SystemExit("That email is already registered.")
        db.add(
            User(
                name=name,
                email=email,
                phone=phone,
                password_hash=hash_password(password),
                role=UserRole.hr,
            )
        )
        db.commit()
    print(f"HR account created for {email}")


if __name__ == "__main__":
    main()