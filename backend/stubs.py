import json
from datetime import date as Date
from pathlib import Path

from backend.schemas import ForecastResponse, ModelCardResponse, ScenarioResponse


def get_forecast_data_path() -> Path:
    """Locate forecast.json in the backend/data directory."""
    root = next(
        p for p in [Path.cwd(), *Path.cwd().parents] if (p / "pyproject.toml").exists()
    )
    return root / "backend" / "data" / "forecast.json"


def get_model_card_data_path() -> Path:
    """Locate model_card.json in the backend/data directory."""
    root = next(
        p for p in [Path.cwd(), *Path.cwd().parents] if (p / "pyproject.toml").exists()
    )
    return root / "backend" / "data" / "model_card.json"


def get_forecast() -> ForecastResponse:
    """Load the committed forecast.json and validate against the frozen contract."""
    forecast_path = get_forecast_data_path()

    if not forecast_path.exists():
        raise FileNotFoundError(
            f"forecast.json not found at {forecast_path}. "
            "Run pipeline/generate_forecast.py to create it."
        )

    data = json.loads(forecast_path.read_text())
    return ForecastResponse(**data)


def get_scenario() -> ScenarioResponse:
    # TODO(Week 5): replace with Kimi K2.6 LLM call
    return ScenarioResponse(
        as_of=Date(2026, 4, 23),
        regime="low_23_26",
        narrative=(
            "Corn sits in a low-volatility, reverted regime: prices have settled "
            "to a higher post-2021 floor near 420 cents, speculative positioning is "
            "roughly flat, and ending stocks are ample. Absent a weather or policy "
            "shock, the 30-day outlook is range-bound with modest downside skew."
        ),
        source="stub",
    )


def get_model_card() -> ModelCardResponse:
    """Load the committed model_card.json and validate against the frozen contract."""
    model_card_path = get_model_card_data_path()

    if not model_card_path.exists():
        raise FileNotFoundError(
            f"model_card.json not found at {model_card_path}. "
            "Run pipeline/generate_forecast.py to create it."
        )

    data = json.loads(model_card_path.read_text())
    return ModelCardResponse(**data)
