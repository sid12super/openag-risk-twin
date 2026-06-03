# CLAUDE.md — OpenAg Risk Twin

Project context for agentic coding sessions. **Read this first.** Full detail lives in `docs/`.

## What this is

A public, NDA-safe commodity risk modeling system — a spiritual successor to proprietary ag-fintech work, built entirely on free public data. It pitches itself as **risk-management infrastructure under regime uncertainty**, NOT a price predictor. The honest position: forecasting commodity prices is hard; the system's value is in *quantifying what it doesn't know*.

Detail: `docs/SCOPE.md` (the contract), `docs/PLAN.md` (schedule + locked decisions), `docs/RESEARCH_NOTES.md` (domain background), `docs/v2-ideas.md` (parking lot).

## Locked technical decisions — do not relitigate

- **Env**: Python 3.13, managed with **uv** (`pyproject.toml` + `uv.lock`). Never pip/conda.
- **Commodity**: corn front-month (`ZC=F`) only for v1. Single 30-day horizon.
- **Model**: single XGBoost with regime-aware features for MSV. Stacked ensemble is v2.
- **Evaluation**: walk-forward (rolling-origin) ONLY. Never k-fold on time series.
- **Output**: probabilistic — quantile + conformal intervals. Never bare point forecasts.
- **Regime features**: continuous indicators, never discrete classification labels.
- **Storage**: DuckDB, file-based. Raw downloads cached in `data/raw/` (precious); the DuckDB file is regenerable from raw via build script.
- **Data**: free public sources only — yfinance (CME proxy), USDA WASDE, CFTC COT, NOAA Drought Monitor, FRED.
- **Deploy (Week 4+)**: FastAPI on Render, Next.js on Vercel.
- **AI layer (Week 5)**: single Kimi K2.6 prompt for scenario narration. NOT for accuracy lift.

## Scope rules — enforce these

- Anything not in `docs/SCOPE.md` goes to `docs/v2-ideas.md`. Never build v2 features into v1.
- No new dependencies after Week 3 unless they solve a problem already encountered.
- README and code/comment framing stays "risk infrastructure," never "prediction accuracy."
- Deliberate learning-surface tools (allowed new deps): NannyML, Evidently, ruptures, mapie, Kimi K2.6. Everything else uses already-known tools.

## Code conventions

- One module per data source under `pipeline/sources/`, each exposing `fetch() -> DataFrame` and `validate()`.
- Secrets via `.env` (gitignored); `.env.example` committed, names the keys with no values.
- Raw downloads timestamped into `data/raw/`; `data/` is gitignored on main.
- Tests with `pytest`, lint with `ruff`. CI runs both on push/PR.

## Repo structure (target)

```
openag-risk-twin/
├── README.md  CLAUDE.md  AGENTS.md      # root
├── pyproject.toml  uv.lock  .gitignore
├── .env.example                          # committed; .env is gitignored
├── docs/         # SCOPE, PLAN, RESEARCH_NOTES, v2-ideas, MD files
├── pipeline/
│   ├── sources/  # prices_yf, wasde, cftc, drought, macro_fred
│   ├── healthcheck.py
│   └── build_duckdb.py
├── data/         # raw/ (cached, gitignored) + openag.duckdb (regenerable)
├── notebooks/
├── backend/      # FastAPI — empty scaffold until Week 4
├── frontend/     # Next.js — empty scaffold until Week 4
└── .github/workflows/   # ci.yml + refresh.yml
```

## Current phase

**Week 2 — Foundation.** Repo + structure + data pipeline + GitHub Actions skeleton. See `docs/PLAN.md` Week 2 for the task list and definition of done.
