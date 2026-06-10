# OpenAg Risk Twin — 5-Week Plan to MSV

> Companion to SCOPE.md. This document preserves all technical decisions and conversation context so any new chat in the Claude Project can pick up where the last one left off.

## Current state (as of June 10, 2026)

- **Graduation**: complete (MS Applied Data Science, Syracuse iSchool, May 2026)
- **ProAg engagement**: complete
- **Active commitments**: HyperQuark Research Fellow + active job search (primary focus)
- **Handshake AI**: resuming after EAD authorization
- **Week 2** ✅ — five-source warehouse + CI/CD, both workflows green.
- **Week 3** ✅ — seven validated regimes (detection + Chow/variance validation + multi-source characterization), regime figure, README section #1 drafted.

## Sprint structure

Each phase opens a new chat in the Claude Project. SCOPE.md and PLAN.md travel with the project so context is preserved without re-explaining the foundation every time.

---

### Week 1 — Market & Domain Research ✅ COMPLETE

**Window**: now through ~June 1, 2026  
**Time**: 4–6 hours total  
**Mode**: Research-oriented, low practical commitment

**Goal**: Understand commodity futures and corn markets well enough to make sensible technical decisions in Week 2. No code commits required this week.

**Topics to internalize**:

- Commodity futures basics: contract specifications, roll mechanics, basis vs spread, term structure (contango / backwardation)
- Corn market structure: USDA reporting cycle, planting / pollination / harvest calendar, key supply-demand drivers, ethanol mandate impact
- WASDE report anatomy: what's in each section, which numbers move markets, the history of major WASDE surprises
- Basis risk: cash vs futures, why basis exists, how producers and elevators traditionally hedge
- Regime concept: what defines a regime in commodity markets, how quants distinguish trend / mean-reverting / high-vol regimes
- 2020–2025 commodity regime history: COVID shock and recovery, Russia-Ukraine and the Black Sea grain corridor, El Niño / La Niña multi-year cycles, US-China trade dynamics, tariff regime effects

**Deliverable**: `RESEARCH_NOTES.md` — key terms, useful primary sources (USDA report URLs, CFTC explainers), and 10–15 paragraphs in own words. Optional: 2–3 short Python explorations of yfinance corn data to get a feel for the `ZC=F` series.

**Open this phase as a new chat** with the project files attached. Topic: "OpenAg Week 1 research — commodity futures & corn fundamentals."

---

### Week 2 — Foundation ✅ COMPLETE

**Window**: ~June 1–7, 2026  
**Time**: 8–10 hours

**Goal**: Repo skeleton, data pipeline, GitHub Actions skeleton.

**Shipped**: Python 3.13 via uv; repo initialized; `docs/` + `CLAUDE.md`/`AGENTS.md` locked; monorepo structure created. Five-source pipeline (yfinance `ZC=F`, USDA WASDE via `curl_cffi` browser impersonation, CFTC COT via `cot_reports`, NOAA Drought Monitor, FRED via `fredapi`) unified into `data/openag.duckdb` through `build_duckdb.py`, with a `fetch()/validate()` interface and cache-first behavior. Both GitHub Actions workflows green: `ci.yml` (ruff + pytest) and `refresh.yml` (scheduled healthcheck + `workflow_dispatch`).

**Tasks**:

- Initialize `openag-risk-twin` repo with SCOPE.md, PLAN.md, RESEARCH_NOTES.md, README.md skeleton
- Set up monorepo structure: `backend/` (FastAPI), `frontend/` (Next.js), `pipeline/` (data ingestion), `notebooks/` (analysis), `data/` (DuckDB)
- Pull 10 years of CME corn front-month settlements via `yfinance` into DuckDB
- Wire USDA WASDE: manual historical download + parser script
- Wire CFTC Commitments of Traders: CSV download + parser
- Wire NOAA US Drought Monitor: historical archive + ingestion script
- Wire FRED macro series via `fredapi` (USD index, 10Y Treasury, energy proxies)
- GitHub Actions workflow #1: skeleton with one trivial test passing
- GitHub Actions workflow #2: scheduled data refresh (cron, does nothing yet but exists)

**Deliverable**: Clean repo with 5 data sources unified in a single DuckDB file. Actions skeleton visible on the repo's Actions tab. ✅

---

### Week 3 — Regime Analysis ✅ COMPLETE

**Window**: ~June 8–14, 2026  
**Time**: ~10–12 hours

**Goal**: Empirical regime detection. The notebook that justifies every subsequent modeling decision.

**Shipped (June 10, 2026)**:

- `notebooks/01_regime_analysis.ipynb` — DuckDB load → log returns + 21-day annualized rolling vol → **dual PELT** (variance via `model="normal"` on returns; trend via `l2` on log price) with a **penalty sweep** so the breakpoint count is stability-based, not hand-picked.
- **Validation**: Chow test on level breaks, F-test on return variance for volatility breaks. Two trend walls — 2021-01-05 (+221¢, p≈1e-210) and 2023-07-31 (−201¢, p≈1e-236) — plus five validated volatility breaks. The Feb-2022 candidate was correctly **rejected** (vol 36%→35%, p=0.85): the Russia-Ukraine invasion was a price/direction move inside an already-high-vol regime, not a new volatility regime.
- **Characterization**: as-of join (`merge_asof`, backward, no lookahead) of all five sources onto the trading-day calendar; per-regime profile across realized vol, speculative positioning (spec net % OI), drought stress, USD/macro, and WASDE ending stocks. **Seven regimes.**
- `notebooks/figures/01_regime_structure.png` — annotated regime-structure figure.
- README section #1 drafted: "Regime structure under uncertainty."

**Key findings**:

- **Volatility alone cannot define a regime.** The spring-2021 and spring-2023 bursts are vol-twins (44% vs 43%) but opposite states: specs +26% vs +1% of OI, stocks 36 vs 57 MMT, price rising vs falling. This is the empirical argument for multi-factor regime features.
- **Reversion found a higher floor**: post-2023 calm ~440¢ vs the 2016–2020 baseline ~366¢ — not a return to the old level.
- **COVID was not a regime change for corn**: the early-2020 dip is absorbed inside the calm baseline with no break.
- **Drought level ≠ volatility**: the highest drought reading (2022–23 cooling) coincided with the lowest vol → featurize drought as change/percentile, not raw level.
- **Coverage asymmetry documented honestly**: CFTC + WASDE begin 2021; calm-era fundamentals are uncovered, not zero.

**Deviations from plan**:

- **Term-structure shape** (planned characterization feature) **deferred to v2** — front-month-only data has no curve slope; needs ≥2 curve points. Parked in `v2-ideas.md`.
- **Supremum-Wald not implemented** — Chow + variance F-test + the stability sweep are sufficient for v1; sup-Wald stays available if a formal "break-somewhere" test is ever needed.

**Deliverable**: `notebooks/01_regime_analysis.ipynb` + README section with figure and findings. ✅

---

### Week 4 — Baselines + Dashboard Shell

**Window**: ~June 15–21, 2026  
**Time**: 10–12 hours

**Goal**: Baseline forecasters + frontend scaffold deployed.

 ▶ NEXT: Week 4 baselines + dashboard scaffold. First task: build the modeling frame from the Week-3 panel (target = 30-day-ahead `ZC=F`; features = the regime/characterization columns already joined). Then naïve baselines (random walk, seasonal naïve, AR(1)) + a vanilla XGBoost forecaster under walk-forward (rolling-origin) evaluation with a per-year breakdown. In parallel: Next.js shell to Vercel (stub data) and FastAPI `/forecast` stub on Render. Deliverable: `notebooks/02_baselines.ipynb` + live stubbed dashboard + live API URL.

**Tasks**:

- Naïve forecast baselines: random walk, seasonal naïve, AR(1)
- Vanilla XGBoost forecaster (no regime features yet) with walk-forward evaluation
- Per-year performance breakdown documented in the notebook and README
- Next.js dashboard shell deployed to Vercel — structure only, stub data
- FastAPI scaffolded with one `/forecast` endpoint returning stub data
- Render deployment of FastAPI working

**Deliverable**: `notebooks/02_baselines.ipynb` + live (stubbed) dashboard URL + live API URL.

**Open as new chat**. Topic: "OpenAg Week 4 baselines + dashboard scaffold."

---

### Week 5 — Lift + Ship MSV

**Window**: ~June 22–28, 2026  
**Time**: 12–14 hours

**Goal**: Show regime features lift over baseline, wire everything live, ship.

**Tasks**:

- Add regime features to XGBoost; document lift vs Week 4 baseline
- Quantile regression for probabilistic output (10/50/90 quantiles)
- Conformal prediction wrapper via `mapie` for calibrated intervals
- Wire FastAPI to serve live forecasts from DuckDB
- Next.js dashboard reads live API and renders forecast + 80% interval + regime indicator
- Kimi K2.6 scenario narration on button click — single prompt integration
- Blog post draft on the journey
- Tag `v1.0.0`

**Deliverable**: Live MSV. Public URL. Resume-ready. Discussable in interviews.

**Open as new chat**. Topic: "OpenAg Week 5 ship — regime lift + live integration."

---

## Key technical decisions captured from conversation

These are decisions Sid and Claude already made in the originating conversation. They're locked unless explicitly revisited.

### Architecture decisions

- **Stacked ensemble** (XGBoost + LightGBM + CatBoost → logistic regression meta) is the v2 architecture. v1 ships with single XGBoost to reduce shipping risk. The ensemble code can be scaffolded but is not on the critical path for MSV.
- **Champion-challenger** pattern is the v2 deployment story. v1 ships with one model in production.
- **NannyML + Evidently** are the monitoring stack:
  - NannyML estimates performance without labels — DLE (Direct Loss Estimation) applies to this regression problem
  - Evidently tracks data and prediction drift
- **Kimi K2.6** integration for MSV is a single prompt that generates a paragraph of scenario context. The agent swarm pattern (300 sub-agents, bull/bear analyst decomposition) is v2.

### Modeling principles

- Walk-forward (rolling-origin) evaluation only. No standard k-fold on time-series data.
- Per-year metric breakdown in evaluation reporting — surface the years where the model underperforms instead of burying them in an aggregate.
- Probabilistic outputs (quantile regression + conformal wrapper) rather than point forecasts.
- Time-weighted sampling as a hyperparameter knob (exponential decay).
- Regime indicators as continuous features, not as discrete classification labels.
- Calibration tracking: log every prediction with its interval; record empirical coverage over rolling windows.

### Data decisions

- Corn front-month (`ZC=F`) for v1. Soybean (`ZS=F`) is the natural v2 expansion.
- 10 years of daily history.
- Free public sources only: USDA WASDE, USDA NASS Quickstats, yfinance for CME prices, CFTC Commitments of Traders, NOAA US Drought Monitor, FRED.
- DuckDB for storage (file-based, fast, version-friendly).
- **Term-structure shape feature deferred to v2** — front-month-only data has no curve slope (needs ≥2 curve points). See `v2-ideas.md`.
- **WASDE units note**: the ingested US corn ending-stocks series is in **million metric tons** (world-table US line), not million bushels. Irrelevant for modeling (it gets percentiled), but documented so the unit isn't misread.

### Framing decisions

- README pitch is **"risk management infrastructure under regime uncertainty"**, never "predicts corn within X%."
- The honest position: **an LLM layer does not improve forecast accuracy.** It improves interpretability and decision-readiness. Don't claim otherwise.
- Selling points: calibrated uncertainty, regime awareness, scenario reasoning, production monitoring, automated retraining.
- Acknowledge upfront in the writeup that forecasting commodity prices is hard; the value of the system is in *quantifying what it doesn't know*.

### Tooling decisions

- **Python 3.13**, managed with **uv** (`pyproject.toml` + `uv.lock` for reproducible builds). No pip/conda. (uv was already in use from ProAg, so not new tooling.)
- **Python version rationale**: 3.13 is the sweet spot — newer than the 3.11 stable floor, fully supported across the data/ML ecosystem, but not the bleeding 3.14 edge (niche monitoring libs lag on new releases, and interpreter-speed gains are marginal for a compiled-extension workload).
- **Repo layout**: monorepo. Planning docs live in `docs/`; `README.md`, `CLAUDE.md`, and `AGENTS.md` stay at root so agentic coding tools (Claude Code, Codex) pick them up automatically.
- **Backups**: raw downloads cached and timestamped in `data/raw/` (the precious artifact); the DuckDB file is regenerable from raw and gitignored on main. GitHub is the offsite backup once pushed.
- **`ruptures`** is the sanctioned new dependency for Week 3 (changepoint detection); `scipy` rides in with it (used for Chow / variance F-tests — no separate dependency). Structural-break tests are hand-rolled, not a new library.
- **Agentic split**: plan-mode-with-Sonnet + execution-with-Haiku is the proven pattern. Upgrading the planner to Claude Fable 5 for open-ended work (best fit: Week 5 live wiring) is parked in `v2-ideas.md`, not used for pre-specced notebooks.

## Risks to monitor

Listed in roughly the order of likelihood for Sid specifically:

1. **Scope creep** — high probability given project history. Mitigation: every new idea goes to `v2-ideas.md`, never into v1.
2. **Job search competition** — this project must accelerate, not compete with, job search. Mitigation: weekly time audit; if OpenAg hours exceeded job-search hours, correct the next week.
3. **Burnout** — multiple concurrent commitments. Mitigation: protect hobbies (Rocket League, F1 weekends, cooking, gym). If skipping these, OpenAg is over-committed.
4. **Domain perfectionism** — temptation to learn everything about commodity markets before building. Mitigation: Week 1 is the research week; after that, learn what the data forces you to learn.
5. **Tool sprawl** — new libraries are a learning cost. Mitigation: use already-known tools for everything except the deliberate learning surface (NannyML, Evidently, `ruptures`, Kimi K2.6, conformal via `mapie`).
6. **Hackathon followup contention** — Cerebral Valley engagement could pull hours. Mitigation: if hackathon followup demands time, OpenAg pauses for a week — that's a good problem to have.

## How to resume across chats

Each new chat in the Claude Project should open with:

> "Picking up OpenAg Risk Twin at Week N. SCOPE.md and PLAN.md are in the project files. Today's focus: [specific topic]."

This keeps the architectural context loaded without re-explaining it. Update this PLAN.md at the end of each phase with what actually shipped vs what was planned, so the historical record stays accurate.