import json
from datetime import date as Date
from pathlib import Path
import os
import httpx

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


MOONSHOT_URL = "https://api.moonshot.ai/v1/chat/completions"

_SYSTEM = (
    "You are a grain-market analyst writing a short scenario note for a corn "
    "producer or grain elevator. Use plain commercial language — cash and futures, "
    "price risk, hedging and marketing decisions. Never mention models, statistics, "
    "percentiles, intervals, or confidence levels. Write exactly one paragraph "
    "(3-5 sentences), concrete about what the next 30 days means for a marketing "
    "or hedging decision."
    "Refer to nearby corn futures generally; do not name a specific contract month. Reason only from the price, regime, and range provided — do not invent specific support or resistance levels, price targets, or order instructions"
)

_REGIME_PLAIN = {
    "calm_16_21": "a long, calm, range-bound stretch",
    "breakout_21": "an upside breakout",
    "burst_spr21": "a sharp volatility burst",
    "high_21_22": "a sustained high-price, high-volatility regime",
    "cooling_22_23": "a cooling-off from the highs",
    "burst_spr23": "a sharp volatility burst",
    "low_23_26": "a lower-priced, range-bound regime after the 2021-23 highs",
}

_scenario_cache: dict[str, ScenarioResponse] = {}


def _build_prompt(f) -> str:
    last, low, high = f.last_price, f.interval_80.low, f.interval_80.high
    down, up = (low / last - 1) * 100, (high / last - 1) * 100
    skew = "to the downside" if abs(down) > up else "to the upside" if up > abs(down) else "roughly balanced"
    regime_txt = _REGIME_PLAIN.get(f.regime.label, "the current regime")
    return (
        f"Corn (CME ZC=F) is trading near {last:.0f} cents and the market is in {regime_txt}. "
        f"Over the next 30 days the plausible price range is about {low:.0f} to {high:.0f} cents, "
        f"with the balance of risk leaning {skew}. Write the scenario note."
    )


def _fallback(f) -> ScenarioResponse:
    note = (
        f"Corn is near {f.last_price:.0f} cents in {_REGIME_PLAIN.get(f.regime.label, 'the current regime')}. "
        f"The 30-day range looks like roughly {f.interval_80.low:.0f} to {f.interval_80.high:.0f} cents — "
        f"plan marketing and hedging coverage around that span."
    )
    return ScenarioResponse(as_of=f.as_of, regime=f.regime.label, narrative=note, source="stub")


def get_scenario() -> ScenarioResponse:
    f = get_forecast()  # live context, so the note matches the chart
    cache_key = str(f.as_of)
    if cache_key in _scenario_cache:
        return _scenario_cache[cache_key]

    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        return _fallback(f)  # no key (e.g. CI) -> deterministic note, no network

    try:
        resp = httpx.post(
            MOONSHOT_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "kimi-k2.6",
                "messages": [
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": _build_prompt(f)},
                ],
                "temperature": 0.6, "top_p": 0.95, "max_tokens": 400,
                "thinking": {"type": "disabled"},
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        narrative = resp.json()["choices"][0]["message"]["content"].strip()
        result = ScenarioResponse(as_of=f.as_of, regime=f.regime.label, narrative=narrative, source="kimi-k2.6")
        _scenario_cache[cache_key] = result  # cache only successful calls
        return result
    except Exception:
        return _fallback(f)  # transient Kimi failure -> stub, not a 500


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
