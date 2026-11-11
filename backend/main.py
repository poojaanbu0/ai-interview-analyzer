from contextlib import asynccontextmanager
from fastapi import FastAPI
from backend.routers.interview import router

from database import Base, engine, create_database
import models  # noqa: F401  (registers all models)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database()                    # creates the MySQL database if missing
    Base.metadata.create_all(bind=engine)  # creates the six tables if missing
    yield


app = FastAPI(title="Kyra Nova API", lifespan=lifespan)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Kyra Nova backend running"}






