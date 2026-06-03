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

## Infrastructure

- **Database migration**: Replace DuckDB with PostgreSQL for append-only audit trail
- **Data lake**: S3 for raw downloads and model artifacts
- **Orchestration**: Prefect or Airflow for pipeline DAGs
- **Feature store**: Tecton or Feast for versioned features
