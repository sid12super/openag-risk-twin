from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class Interval80(BaseModel):
    low: float
    high: float


class Regime(BaseModel):
    label: str
    vol_pct: float


class HistoryPoint(BaseModel):
    date: str
    close: float


class ForecastResponse(BaseModel):
    as_of: str
    horizon_days: int
    last_price: float
    point: float
    interval_80: Interval80
    regime: Regime
    history: list[HistoryPoint]


class ScenarioResponse(BaseModel):
    as_of: str
    regime: str
    narrative: str
    source: str


class Evaluation(BaseModel):
    oos_period: str
    rmse: float
    skill_vs_rw: float
    per_year_rmse: dict[str, float]


class ModelCardResponse(BaseModel):
    model: str
    horizon_days: int
    target: str
    features: list[str]
    evaluation: Evaluation
    data_sources: list[str]
    framing: str
