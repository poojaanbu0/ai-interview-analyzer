from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database import Base, engine
from . import models  # noqa: F401  (registers all models)
from .routers.interview import router as interview_router
from .routers import auth, hr_interviews, hr_candidates, candidate_applications, interview_room

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Kyra Nova API", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # lets the resume download keep its file name
)

app.include_router(interview_router)
app.include_router(auth.router)
app.include_router(candidate_applications.router)
app.include_router(auth.router)
app.include_router(hr_interviews.router)
app.include_router(hr_candidates.router)
app.include_router(candidate_applications.router)
app.include_router(interview_room.router)



@app.get("/")
def root():
    return {"message": "Kyra Nova backend running"}






