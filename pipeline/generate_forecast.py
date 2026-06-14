#!/usr/bin/env python3
"""Generate live forecast.json and model_card.json for the API.

Runs in refresh.yml (cron + manual trigger). Loads the DuckDB panel, applies
the serialized quantile models + CQR calibration, and writes contract-shaped JSON.

The JSON is validated against Pydantic models before writing.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import duckdb
import joblib

from backend.schemas import ForecastResponse, HistoryPoint, ModelCardResponse


def locate_root() -> Path:
    """Find project root (where pyproject.toml exists)."""
    return next(
        p for p in [Path.cwd(), *Path.cwd().parents] if (p / "pyproject.toml").exists()
    )


def load_panel(root: Path) -> pd.DataFrame:
    """Load the DuckDB panel with all features and regime labels."""
    con = duckdb.connect(str(root / "data" / "openag.duckdb"), read_only=True)
    panel = con.sql('SELECT * FROM panel ORDER BY "Date"').df()
    con.close()

    panel["Date"] = pd.to_datetime(panel["Date"]).astype("datetime64[ns]")
    panel = panel.set_index("Date")
    return panel


def engineer_features(panel: pd.DataFrame) -> pd.DataFrame:
    """Add vanilla features to the panel (same as notebooks)."""
    H = 30
    df = panel.copy()

    # Target (30-day forward log return)
    df["y"] = np.log(df["Close"].shift(-H)) - np.log(df["Close"])

    # Vanilla features
    for lag in [1, 5, 10, 21, 63]:
        df[f"ret_{lag}"] = np.log(df["Close"]) - np.log(df["Close"].shift(lag))

    df["vol_21"] = df["rolling_vol"]

    doy = df.index.dayofyear
    df["sin_doy"] = np.sin(2 * np.pi * doy / 365.25)
    df["cos_doy"] = np.cos(2 * np.pi * doy / 365.25)

    return df


def load_or_create_models(root: Path):
    """Load serialized models from Task 3, or return a fallback."""
    models_dir = root / "backend" / "models"

    if (models_dir / "quantile_models.joblib").exists():
        quantile_models = joblib.load(models_dir / "quantile_models.joblib")
        cqr_calibration = joblib.load(models_dir / "conformal_calibration.joblib")
        return quantile_models, cqr_calibration

    print(
        "⚠️  Models not found in backend/models/. Using fallback (stub mode).\n"
        "   To enable live predictions, run the conformal notebook first."
    )
    return None, None


def enforce_quantile_monotonicity(q_low, q_mid, q_high):
    """Ensure q_low <= q_mid <= q_high via sorting per row."""
    quantiles = np.column_stack([q_low, q_mid, q_high])
    sorted_q = np.sort(quantiles, axis=1)
    return sorted_q[:, 0], sorted_q[:, 1], sorted_q[:, 2]


def generate_forecast_json(
    root: Path, quantile_models=None, cqr_calibration=None
) -> dict:
    """Generate the forecast JSON payload."""
    FEATURES_VANILLA = [
        "ret_1",
        "ret_5",
        "ret_10",
        "ret_21",
        "ret_63",
        "vol_21",
        "sin_doy",
        "cos_doy",
    ]

    panel = load_panel(root)
    df = engineer_features(panel)

    # Get the latest row with valid vanilla features
    latest_idx = len(df) - 1
    latest_row = df.iloc[latest_idx]

    as_of = latest_row.name.date()
    last_price = latest_row["Close"]

    # Build history (last ~60 rows, ascending by date)
    history_window = min(60, len(df))
    history_rows = df.iloc[-history_window:]
    history = [
        HistoryPoint(date=idx.date(), close=float(row["Close"]))
        for idx, row in history_rows.iterrows()
    ]

    # Get regime label from the latest row
    regime_label = str(latest_row["regime"])

    # Compute vol_pct as percentile rank of vol_21
    # Causal: rank against historical data up to (not including) as_of
    vol_history = df.iloc[:-1]["vol_21"].dropna()
    latest_vol = latest_row["vol_21"]
    if len(vol_history) > 0 and not np.isnan(latest_vol):
        vol_pct = float(
            (vol_history <= latest_vol).sum() / len(vol_history) * 100
        )
    else:
        vol_pct = 50.0

    vol_pct = np.clip(vol_pct, 0, 100)

    # Predict quantiles or use fallback
    if quantile_models is not None and cqr_calibration is not None:
        X_latest = latest_row[FEATURES_VANILLA].values.reshape(1, -1)

        q10_ret = float(quantile_models[0.1].predict(X_latest)[0])
        q50_ret = float(quantile_models[0.5].predict(X_latest)[0])
        q90_ret = float(quantile_models[0.9].predict(X_latest)[0])

        q10_ret, q50_ret, q90_ret = enforce_quantile_monotonicity(
            np.array([q10_ret]), np.array([q50_ret]), np.array([q90_ret])
        )
        q10_ret, q50_ret, q90_ret = float(q10_ret[0]), float(q50_ret[0]), float(q90_ret[0])

        # Apply CQR corrections
        correction_q10 = cqr_calibration.get(
            "correction_q10", 0.0
        )
        correction_q90 = cqr_calibration.get(
            "correction_q90", 0.0
        )

        # Recenter and correct
        low_ret = (q10_ret - q50_ret) + correction_q10
        high_ret = (q90_ret - q50_ret) + correction_q90

        # Transform to price
        low_price = last_price * np.exp(low_ret)
        point_price = last_price  # exp(0) = 1
        high_price = last_price * np.exp(high_ret)
    else:
        # Fallback: use random walk with fixed cone
        low_ret = -0.15
        high_ret = 0.15

        low_price = last_price * np.exp(low_ret)
        point_price = last_price
        high_price = last_price * np.exp(high_ret)

    # Assemble ForecastResponse
    forecast_dict = {
        "as_of": as_of,
        "horizon_days": 30,
        "last_price": float(last_price),
        "point": float(point_price),
        "interval_80": {
            "low": float(low_price),
            "high": float(high_price),
        },
        "regime": {
            "label": regime_label,
            "vol_pct": vol_pct,
        },
        "history": [
            {"date": h.date, "close": h.close} for h in history
        ],
    }

    # Validate by constructing the Pydantic model
    ForecastResponse(**forecast_dict)

    return forecast_dict


def generate_model_card_json() -> dict:
    """Generate the model card JSON payload from fixed metadata."""
    model_card_dict = {
        "model": "Random-walk point + XGBoost quantile interval (CQR-calibrated)",
        "horizon_days": 30,
        "target": "30-day log return",
        "features": [
            "ret_1",
            "ret_5",
            "ret_10",
            "ret_21",
            "ret_63",
            "vol_21",
            "sin_doy",
            "cos_doy",
        ],
        "evaluation": {
            "oos_period": "2020-2026",
            "rmse": 0.0980,
            "skill_vs_rw": -0.0303,
            "per_year_rmse": {
                "2020": 0.1332,
                "2021": 0.1072,
                "2022": 0.1171,
                "2023": 0.0786,
                "2024": 0.0589,
                "2025": 0.0826,
                "2026": 0.0614,
            },
        },
        "data_sources": [
            "yfinance ZC=F",
            "USDA WASDE",
            "CFTC COT",
            "NOAA Drought Monitor",
            "FRED",
        ],
        "framing": (
            "Risk-management infrastructure under regime uncertainty, not a point-accuracy "
            "predictor. The point forecast is the random walk — XGBoost showed no point-skill "
            "over it (-0.03 vs RW) — while XGBoost quantile regression with conformal (CQR) "
            "calibration produces the 80% interval."
        ),
    }

    # Validate by constructing the Pydantic model
    ModelCardResponse(**model_card_dict)

    return model_card_dict


def main():
    """Generate forecast.json and model_card.json."""
    root = locate_root()
    print(f"Root: {root}")

    # Create backend/data directory
    data_dir = root / "backend" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Load models if available
    quantile_models, cqr_calibration = load_or_create_models(root)

    # Generate forecasts
    print("\nGenerating forecast.json...")
    forecast_dict = generate_forecast_json(root, quantile_models, cqr_calibration)
    forecast_path = data_dir / "forecast.json"
    forecast_path.write_text(json.dumps(forecast_dict, indent=2, default=str))
    print(f"✓ {forecast_path}")

    print("\nGenerating model_card.json...")
    model_card_dict = generate_model_card_json()
    model_card_path = data_dir / "model_card.json"
    model_card_path.write_text(json.dumps(model_card_dict, indent=2, default=str))
    print(f"✓ {model_card_path}")

    print("\n✓ Both JSON files generated and validated against Pydantic contracts.")


if __name__ == "__main__":
    main()
