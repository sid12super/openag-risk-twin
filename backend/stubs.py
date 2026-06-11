import random
from datetime import datetime, timedelta

from backend.schemas import (
    Evaluation,
    ForecastResponse,
    HistoryPoint,
    Interval80,
    ModelCardResponse,
    Regime,
    ScenarioResponse,
)


def get_forecast() -> ForecastResponse:
    # TODO(Week 5): replace with live DuckDB read
    as_of = "2026-04-23"
    random.seed(42)  # deterministic history

    history = []
    base_date = datetime(2026, 2, 23)
    current_price = 418.0

    for i in range(60):
        date_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        history.append(HistoryPoint(date=date_str, close=current_price))
        current_price += random.uniform(-1.0, 1.0)

    return ForecastResponse(
        as_of=as_of,
        horizon_days=30,
        last_price=421.0,
        point=423.0,
        interval_80=Interval80(low=388.0, high=460.0),
        regime=Regime(label="reverted", vol_pct=21.0),
        history=history,
    )


def get_scenario() -> ScenarioResponse:
    # TODO(Week 5): replace with Kimi K2.6 LLM call
    return ScenarioResponse(
        as_of="2026-04-23",
        regime="reverted",
        narrative="Corn sits in a low-volatility, reverted regime: prices have settled to a higher post-2021 floor near 420 cents, speculative positioning is roughly flat, and ending stocks are ample. Absent a weather or policy shock, the 30-day outlook is range-bound with modest downside skew.",
        source="stub",
    )


def get_model_card() -> ModelCardResponse:
    # TODO(Week 5): replace with live metadata from model + evaluation cache
    return ModelCardResponse(
        model="XGBoost (single; regime-aware in v1.0)",
        horizon_days=30,
        target="30-day log return",
        features=[
            "ret_1",
            "ret_5",
            "ret_10",
            "ret_21",
            "ret_63",
            "vol_21",
            "sin_doy",
            "cos_doy",
        ],
        evaluation=Evaluation(
            oos_period="2020-2026",
            rmse=0.098,
            skill_vs_rw=-0.03,
            per_year_rmse={
                "2020": 0.1332,
                "2021": 0.1072,
                "2022": 0.1171,
                "2023": 0.0786,
                "2024": 0.0589,
                "2025": 0.0826,
                "2026": 0.0614,
            },
        ),
        data_sources=[
            "yfinance ZC=F",
            "USDA WASDE",
            "CFTC COT",
            "NOAA Drought Monitor",
            "FRED",
        ],
        framing="Risk-management infrastructure under regime uncertainty. Not a point-accuracy price predictor.",
    )
