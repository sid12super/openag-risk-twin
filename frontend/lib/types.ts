export interface HealthResponse {
  status: string;
}

export interface Interval80 {
  low: number;
  high: number;
}

export interface Regime {
  label: string;
  vol_pct: number;
}

export interface HistoryPoint {
  date: string;
  close: number;
}

export interface ForecastResponse {
  as_of: string;
  horizon_days: number;
  last_price: number;
  point: number;
  interval_80: Interval80;
  regime: Regime;
  history: HistoryPoint[];
}

export interface Evaluation {
  oos_period: string;
  rmse: number;
  skill_vs_rw: number;
  per_year_rmse: Record<string, number>;
}

export interface ModelCardResponse {
  model: string;
  horizon_days: number;
  target: string;
  features: string[];
  evaluation: Evaluation;
  data_sources: string[];
  framing: string;
}

export interface ScenarioResponse {
  as_of: string;
  regime: string;
  narrative: string;
  source: string;
}
