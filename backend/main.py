from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.routers.interview import router

from .database import Base, engine, create_database
from . import models  # noqa: F401  (registers all models)
from .routers import auth, hr_jobs, candidate_jobs, candidate_applications, hr_resumes

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()                    # creates the MySQL database if missing
    Base.metadata.create_all(bind=engine)  # creates the six tables if missing
    yield


app = FastAPI(title="Kyra Nova API", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # lets the resume download keep its file name
)

app.include_router(router)
app.include_router(auth.router)
app.include_router(hr_jobs.router)
app.include_router(candidate_jobs.router)
app.include_router(candidate_applications.router)
app.include_router(hr_resumes.router)



@app.get("/")
def root():
    return {"message": "Kyra Nova backend running"}






