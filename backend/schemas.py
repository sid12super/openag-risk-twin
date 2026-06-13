"""OpenAg Risk Twin — API response contract (FROZEN at Week 5).

This module is the single source of truth for the API contract. The frontend
`type.ts` mirrors these shapes; the live pipeline (Week 5) must conform to them
exactly. Changes here are contract changes — they break the dashboard if the
mirror and the OpenAPI snapshot are not updated in lockstep.

Diff this against your current backend/schemas.py. If your current file is plain
BaseModels with no constraints (likely), this is the upgrade. If you already have
validators, keep them and merge.
"""

from __future__ import annotations

from datetime import date as Date
from typing import Literal

from pydantic import BaseModel, Field, model_validator

# --- Canonical enums -------------------------------------------------------

# The seven canonical regimes from notebooks/01_regime_analysis (the detector's
# own labels). The stub's "reverted" is a human placeholder for "low_23_26" --
# the API emits the machine label; the frontend maps label -> display name.
RegimeLabel = Literal[
    "calm_16_21",
    "breakout_21",
    "burst_spr21",
    "high_21_22",
    "cooling_22_23",
    "burst_spr23",
    "low_23_26",
]

ScenarioSource = Literal["stub", "kimi-k2.6"]


# --- Leaf models -----------------------------------------------------------

class HealthResponse(BaseModel):
    status: str


class Interval80(BaseModel):
    """80% prediction interval, in PRICE (cents).

    Live: low = last_price * exp(q10_return); high = last_price * exp(q90_return).
    Never the raw return quantiles.
    """

    low: float = Field(description="80% interval lower bound, price in cents")
    high: float = Field(description="80% interval upper bound, price in cents")

    @model_validator(mode="after")
    def _ordered(self) -> "Interval80":
        if not self.low < self.high:
            raise ValueError(
                f"interval not ordered: low={self.low} >= high={self.high}"
            )
        return self


class Regime(BaseModel):
    label: RegimeLabel
    vol_pct: float = Field(
        ge=0, le=100, description="realized-vol percentile rank, 0-100 (NOT 0-1)"
    )


class HistoryPoint(BaseModel):
    date: Date = Field(
        description="trading day, ISO YYYY-MM-DD; ascending in history[]"
    )
    close: float = Field(description="settlement close, price in cents")


class Evaluation(BaseModel):
    oos_period: str
    rmse: float
    skill_vs_rw: float = Field(description="1 - RMSE/RMSE_rw; negative = worse than RW")
    per_year_rmse: dict[str, float] = Field(
        description="keys are 4-digit year strings 2020..2026"
    )


# --- Endpoint response models ---------------------------------------------

class ForecastResponse(BaseModel):
    as_of: Date = Field(description="forecast anchor date; == history[-1].date")
    horizon_days: int = Field(description="forecast horizon; v1 is 30 only")
    last_price: float = Field(
        description="close on as_of, price in cents; == history[-1].close"
    )
    point: float = Field(description="point (median) forecast, price in cents")
    interval_80: Interval80
    regime: Regime
    history: list[HistoryPoint] = Field(min_length=1)

    @model_validator(mode="after")
    def _coherent(self) -> "ForecastResponse":
        # The cone apex sits at (as_of, last_price); the price line ends at
        # (as_of, history[-1].close). They must coincide or the cone floats
        # off the price line. This is the invariant the current stub violates.
        last = self.history[-1]
        if last.date != self.as_of:
            raise ValueError(f"history tail date {last.date} != as_of {self.as_of}")
        if abs(last.close - self.last_price) > 0.05:
            raise ValueError(
                f"history tail close {last.close} != last_price {self.last_price}"
            )
        # Median must sit inside the 80% band.
        if not self.interval_80.low <= self.point <= self.interval_80.high:
            raise ValueError(
                f"point {self.point} outside interval "
                f"[{self.interval_80.low}, {self.interval_80.high}]"
            )
        # History must be strictly ascending in date.
        dates = [h.date for h in self.history]
        if dates != sorted(dates) or len(set(dates)) != len(dates):
            raise ValueError(
                "history dates not strictly ascending / contain duplicates"
            )
        return self


class ScenarioResponse(BaseModel):
    as_of: Date
    regime: RegimeLabel
    narrative: str
    source: ScenarioSource


class ModelCardResponse(BaseModel):
    model: str
    horizon_days: int
    target: str
    features: list[str] = Field(min_length=1)
    evaluation: Evaluation
    data_sources: list[str] = Field(min_length=1)
    framing: str
