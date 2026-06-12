import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.schemas import (
    ForecastResponse,
    HealthResponse,
    ModelCardResponse,
    ScenarioResponse,
)
from backend.stubs import (
    get_forecast,
    get_model_card,
    get_scenario,
)

app = FastAPI(title="OpenAg Risk Twin", version="0.1.0")

ALLOWED_ORIGIN_REGEX = os.getenv(
    "ALLOWED_ORIGIN_REGEX",
    r"https://.*\.vercel\.app|http://localhost:3000",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/status", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/forecast", response_model=ForecastResponse)
def forecast() -> ForecastResponse:
    return get_forecast()


@app.get("/scenario", response_model=ScenarioResponse)
def scenario() -> ScenarioResponse:
    return get_scenario()


@app.get("/model-card", response_model=ModelCardResponse)
def model_card() -> ModelCardResponse:
    return get_model_card()
