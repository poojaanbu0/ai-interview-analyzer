import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, DeclarativeBase


BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIR.parent / ".env")
load_dotenv(BACKEND_DIR / ".env", override=True)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL is required. Set it to your Supabase PostgreSQL connection string."
    )

url = make_url(database_url)
if url.drivername in {"postgres", "postgresql"}:
    url = url.set(drivername="postgresql+psycopg")
elif url.drivername != "postgresql+psycopg":
    raise ValueError("DATABASE_URL must use the PostgreSQL psycopg driver.")

query = dict(url.query)
query.setdefault("sslmode", "require")
DATABASE_URL = url.set(query=query)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"prepare_threshold": None},
    echo=False,
)


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


# FastAPI dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




