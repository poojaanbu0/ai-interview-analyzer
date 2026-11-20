import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://test:test@localhost/test",
)

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend import models
from backend.database import Base
from backend.models.interview import Interview
from backend.models.interview_room import InterviewRoom
from backend.models.user import User, UserRole
from backend.routers.hr_interviews import create_interview
from backend.routers.hr_rooms import list_rooms
from backend.schemas.interview import InterviewCreate


def test_create_interview_also_creates_one_candidate_room():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)

    try:
        with Session(engine) as db:
            hr = User(
                name="HR",
                email="hr@example.com",
                password_hash="hash",
                role=UserRole.hr,
            )
            candidate = User(
                name="Candidate",
                email="candidate@example.com",
                password_hash="hash",
                role=UserRole.candidate,
            )
            db.add_all([hr, candidate])
            db.commit()

            data = InterviewCreate(
                job_title="Python developer",
                job_description="Build Python services.",
                candidate_id=candidate.id,
                candidate_summary="Python experience",
                scheduled_at=datetime.now(timezone.utc) + timedelta(days=1),
            )

            create_interview(data, db, hr)

            legacy_interview = Interview(
                hr_id=hr.id,
                candidate_id=candidate.id,
                job_title="Older direct interview",
                job_description="An existing direct interview.",
            )
            db.add(legacy_interview)
            db.commit()

            listed_rooms = list_rooms(db, hr)
            interviews = db.scalars(select(Interview)).all()
            rooms = db.scalars(select(InterviewRoom)).all()

            assert len(listed_rooms) == 2
            assert len(rooms) == 2
            assert all(interview.room_id is not None for interview in interviews)
            assert {room.job_title for room in listed_rooms} == {
                "Python developer",
                "Older direct interview",
            }
            assert all(room.candidate_count == 1 for room in listed_rooms)
            assert len(list_rooms(db, hr)) == 2
            assert len(db.scalars(select(InterviewRoom)).all()) == 2
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()
