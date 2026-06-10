# OpenAg Risk Twin — v2 Ideas Parking Lot

Features and architectural changes scoped for v2 and beyond. v1 is locked to the spec in `SCOPE.md`.

## Modeling & Forecasting

- **Stacked ensemble**: XGBoost + LightGBM + CatBoost → logistic regression meta-learner
- **Multi-commodity**: soybeans (ZS=F), wheat (ZWH=F), oats (ZO=F)
- **Longer horizons**: 60-day and 90-day quantile forecasts
- **Regime classification**: discrete regime labels (trend, mean-reverting, high-vol) as a secondary head
- **Agent swarm**: 300 sub-agents for bull/bear scenario decomposition

## Deployment & Monitoring

- **Champion-challenger pattern**: A/B testing against production baseline
- **NannyML monitoring**: DLE (Direct Loss Estimation) for performance without labels
- **Evidently tracking**: Data and prediction drift detection
- **Auto-retraining**: Trigger retraining on performance degradation

## Data

- **NASS QuickStats**: Planting and harvesting progress
- **Satellite imagery**: NDVI, insolation, precipitation proxies
- **Ethanol crack spreads**: Energy market coupling
- **Basis curves**: Historical cash-to-futures relationships
- **Term-structure shape (contango/backwardation)**: deferred from v1 — needs ≥2
  points on the corn futures curve, but v1 ingests only front-month `ZC=F`. Add a
  deferred contract (a later delivery month) to compute curve slope, then restore
  term-structure shape as a regime characterization + model feature. Data-scope
  change, not a Week 3 task.

## Infrastructure

- **Database migration**: Replace DuckDB with PostgreSQL for append-only audit trail
- **Data lake**: S3 for raw downloads and model artifacts
- **Orchestration**: Prefect or Airflow for pipeline DAGs
- **Feature store**: Tecton or Feast for versioned features
- **Fable 5 plan mode → Haiku execution**: upgrade the agentic split's *planner*
  from Sonnet to Claude Fable 5 (plan mode), keeping Haiku at execution. The
  Sonnet-plan / Haiku-execute pattern is already proven in practice; this swaps
  in a stronger planner for open-ended, unspecced work. Best fit: Week 5 live
  wiring (FastAPI + DuckDB + dashboard), where the plan space is large. Not for
  pre-specced notebooks — constrain any plan to one section at a time to avoid
  scaffolding whole phases past scope.
