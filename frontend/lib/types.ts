// Canonical regime labels (machine labels from the detector)
export type RegimeLabel =
  | "calm_16_21"
  | "breakout_21"
  | "burst_spr21"
  | "high_21_22"
  | "cooling_22_23"
  | "burst_spr23"
  | "low_23_26";

// Scenario source
export type ScenarioSource = "stub" | "kimi-k2.6";

// Regime display names (machine label → human-readable name)
export const REGIME_DISPLAY_NAMES: Record<RegimeLabel, string> = {
  calm_16_21: "Calm (2016–21)",
  breakout_21: "Breakout (2021)",
  burst_spr21: "Spring Burst (2021)",
  high_21_22: "Sustained High (2021–22)",
  cooling_22_23: "Cooling (2022–23)",
  burst_spr23: "Spring Burst (2023)",
  low_23_26: "Reverted (2023–26)",
};

export interface HealthResponse {
  status: string;
}

export interface Interval80 {
  low: number;
  high: number;
}

export interface Regime {
  label: RegimeLabel;
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
  regime: RegimeLabel;
  narrative: string;
  source: ScenarioSource;
}
