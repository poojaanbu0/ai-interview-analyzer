from fastapi import FastAPI
from backend.routers.interview import router

app = FastAPI(title="Kyra Nova API")

app.include_router(router)


@app.get("/")
def root():
    return {"message": "Kyra Nova backend running"}