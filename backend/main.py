from fastapi import FastAPI
from pydantic import BaseModel
from orchestrator import run_pipeline

app = FastAPI(title="Tourism Multi-Agent Recommendation API")


class TripRequest(BaseModel):
    destination: str
    state: str
    origin_place: str
    preferences: dict
    total_budget: float
    num_days: int
    home_language: str
    destination_language: str


@app.post("/recommend")
def recommend(request: TripRequest):
    return run_pipeline(request.dict())


@app.get("/")
def health_check():
    return {"status": "running"}