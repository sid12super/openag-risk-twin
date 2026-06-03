# OpenAg Risk Twin — Scope Contract (v1 / MSV)

## Project vision

A public, fully-open commodity risk modeling system that demonstrates the same architecture pattern used in proprietary ag-fintech work (ProAg-equivalent), built entirely on free public data sources. The system frames itself as **risk-management infrastructure under regime uncertainty** rather than as a price forecaster — a deliberate framing that survives recruiter scrutiny and matches how mature quant teams actually think about commodity markets.

## In scope for v1 (MSV)

- **Commodity**: Corn front-month futures (`ZC=F`)
- **Forecast horizon**: 30 days out, single horizon only
- **Output**: Probabilistic forecast with a calibrated 80% prediction interval
- **Modeling**: Single XGBoost forecaster with regime-aware features and walk-forward evaluation. The stacked ensemble is documented as v2 work, not built for MSV.
- **Monitoring**: NannyML for performance estimation under delayed labels (DLE for regression); Evidently for input distribution drift
- **AI scenario layer**: Kimi K2.6 narration on button click — one prompt, one paragraph of context-aware commentary. Bull/bear/neutral decomposition is v2.
- **Frontend**: Next.js dashboard with three views — forecast, scenario explorer, model card
- **Backend**: FastAPI on Render (hobby tier)
- **CI/CD**: GitHub Actions for tests, scheduled data refresh, and model retraining
- **Data sources**: USDA WASDE, USDA NASS, yfinance (CME front-month proxy), CFTC Commitments of Traders, NOAA US Drought Monitor, FRED macro series
- **Storage**: DuckDB file checked into repo's data branch (under size limits)
- **Environment**: Python 3.13, managed with uv (`pyproject.toml` + `uv.lock`). Planning docs in `docs/`; `CLAUDE.md` and `AGENTS.md` at root for agentic coding context.

## Explicitly deferred to v2+

- Additional commodities (wheat, soybean, cattle, crude)
- Multi-horizon forecasts (only 30-day for v1)
- Stacked ensemble (XGB + LightGBM + CatBoost → logistic meta)
- Champion-challenger automation with promotion gates
- Cross-commodity correlation modeling
- Portfolio risk / hedging effectiveness module
- Custom domain, production-grade auth, paid data feeds
- Real-time intraday data
- Kimi K2.6 agent swarm (300 sub-agents) — v1 uses a single prompt

## Success criteria for MSV

- Public GitHub repo with documented codebase and clear README
- Live dashboard deployed to Vercel
- FastAPI backend live on Render
- At least one GitHub Actions workflow passing
- Probabilistic forecast displaying a calibrated 80% interval
- Walk-forward evaluation results in the README with per-year breakdown
- Regime analysis writeup showing detected break points and their impact
- Kimi K2.6 scenario narration working on a button click
- Blog post draft summarizing the project narrative

## Scope discipline rules

1. Every "what if I also..." idea goes into `v2-ideas.md`, never into v1.
2. No new tools introduced after Week 3 unless they solve a problem already encountered.
3. The risk-management framing in the README never gets weakened toward "prediction accuracy."
4. Job search and HyperQuark are higher priority than any commit on this repo. If a given week shows more OpenAg hours than job-search hours, the next week corrects.

## Time and money budget

- **Realistic time to MSV**: 7–10 hrs/week over 5 weeks ≈ 40–50 hours total
- **Realistic monthly cost**: $0 during build, $15–25/month at steady state (Render hobby tier + Kimi K2.6 API usage)

## Authorship and provenance

Built by Siddhant Kasture (Sid). Companion to industry work on agricultural risk modeling. Designed to demonstrate a production-grade architecture pattern using only public data.
