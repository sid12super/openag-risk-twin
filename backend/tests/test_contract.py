"""Contract lock for the OpenAg API.

Runs in ci.yml alongside the existing pytest suite. Two jobs:

1. Validate the stub payloads against the frozen schema AND assert the
   cross-field sanity invariants that Pydantic type-checking can't see
   (price-range sanity, exact per_year_rmse key set, history shape). These are
   the checks that catch the return-vs-price transform bug WHEN the live model
   is wired next session — type equality alone would let it through green.

2. Snapshot the OpenAPI schema. The committed snapshot is the literal freeze;
   any unintended change to a field name, type, or enum fails CI. Regenerate
   intentionally by deleting the snapshot and re-running.

NOTE: adjust the import paths if your layout differs:
  - backend.stubs   (get_forecast / get_scenario / get_model_card)
  - backend.main:app  (FastAPI app, for the OpenAPI snapshot)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.stubs import get_forecast, get_model_card, get_scenario

SNAPSHOT = Path(__file__).parent / "contract_openapi_snapshot.json"

EXPECTED_YEAR_KEYS = {"2020", "2021", "2022", "2023", "2024", "2025", "2026"}
EXPECTED_FEATURE_COUNT = 8  # ret_1/5/10/21/63, vol_21, sin_doy, cos_doy

# A 30-day corn move outside +/-40% is a unit/transform bug, not a market move.
PRICE_BAND = 0.40
# Sanity that point/interval are in cents (hundreds), not return units (~0.0x).
CENTS_MIN, CENTS_MAX = 100.0, 2000.0


def test_forecast_stub_is_self_consistent():
    """Constructing the model already enforces ordering + cone coherence.

    If this raises a ValidationError, the stub violates the frozen contract
    (the current stub does: last_price 421 != history tail ~418). Fix the stub
    to be self-consistent before wiring live data.
    """
    f = get_forecast()  # raises if the model_validators fail

    # Price-range sanity: interval and point sit in a plausible band of last_price.
    lo, hi = f.last_price * (1 - PRICE_BAND), f.last_price * (1 + PRICE_BAND)
    assert lo <= f.interval_80.low <= f.point <= f.interval_80.high <= hi, (
        "interval/point outside +/-40% of last_price -- likely a return-vs-price "
        "transform bug rather than a real market move"
    )
    # Unit sanity: these are cents, not log returns.
    for v in (f.last_price, f.point, f.interval_80.low, f.interval_80.high):
        assert CENTS_MIN < v < CENTS_MAX, (
            f"{v} not in cents range -- return units leaked?"
        )

    assert f.horizon_days == 30


def test_history_shape():
    f = get_forecast()
    assert len(f.history) >= 30, "history window too short for the chart"
    # Strict ascending + no dupes is enforced in the validator; re-assert tail.
    assert f.history[-1].date == f.as_of
    assert abs(f.history[-1].close - f.last_price) <= 0.05


def test_scenario_stub():
    s = get_scenario()
    assert s.source == "stub", "Week-4 stub must report source=stub"
    assert s.narrative.strip(), "scenario narrative must be non-empty"


def test_regime_label_is_canonical():
    """Verify forecast regime label is one of the seven canonical labels."""
    CANONICAL = {
        "calm_16_21",
        "breakout_21",
        "burst_spr21",
        "high_21_22",
        "cooling_22_23",
        "burst_spr23",
        "low_23_26",
    }
    f = get_forecast()
    assert f.regime.label in CANONICAL, (
        f"regime.label '{f.regime.label}' not in {CANONICAL}"
    )
    s = get_scenario()
    assert s.regime in CANONICAL, (
        f"scenario.regime '{s.regime}' not in {CANONICAL}"
    )


def test_scenario_source_is_canonical():
    """Verify scenario source is one of the canonical sources."""
    CANONICAL = {"stub", "kimi-k2.6"}
    s = get_scenario()
    assert s.source in CANONICAL, (
        f"scenario.source '{s.source}' not in {CANONICAL}"
    )


def test_vol_pct_percentile_range():
    """Verify vol_pct is a percentile rank (0-100), not a decimal (0-1)."""
    f = get_forecast()
    assert 0 <= f.regime.vol_pct <= 100, (
        f"vol_pct {f.regime.vol_pct} not in [0, 100] -- must be percentile rank"
    )


def test_model_card_year_keys_locked():
    card = get_model_card()
    keys = set(card.evaluation.per_year_rmse.keys())
    assert keys == EXPECTED_YEAR_KEYS, (
        f"per_year_rmse keys drifted: {keys ^ EXPECTED_YEAR_KEYS}"
    )
    assert len(card.features) == EXPECTED_FEATURE_COUNT


def test_openapi_snapshot():
    """Freeze the wire contract. Delete the snapshot to regenerate intentionally."""
    try:
        from backend.main import app
    except ImportError:
        pytest.skip("backend.main:app not importable -- fix the path to enable")

    current = json.dumps(app.openapi(), sort_keys=True, indent=2)
    if not SNAPSHOT.exists():
        SNAPSHOT.write_text(current)
        pytest.skip("wrote initial OpenAPI snapshot -- commit it and re-run")

    assert current == SNAPSHOT.read_text(), (
        "OpenAPI schema changed. If intentional, delete "
        f"{SNAPSHOT.name} and re-run to regenerate, then commit."
    )
