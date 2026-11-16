
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401 - register SQLAlchemy models
from .routers import (
    auth,
    hr_interviews,
    hr_candidates,
    candidate_applications,
    interview_room,
)
from .routers.interview import router as interview_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Existing Supabase tables are managed separately.
    yield


app = FastAPI(
    title="Kyra Nova API",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
      "*"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


# Register each router exactly once.

# Register candidate static routes before HR dynamic routes.

# Register candidate static routes before HR dynamic routes.

# Register candidate static routes before HR dynamic routes.
app.include_router(interview_router)
app.include_router(auth.router)
app.include_router(candidate_applications.router)
app.include_router(interview_room.router)
app.include_router(hr_candidates.router)
app.include_router(hr_interviews.router)





@app.get("/")
def root():
    return {"message": "Kyra Nova backend running"}
