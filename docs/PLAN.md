# OpenAg Risk Twin — 5-Week Plan to MSV

> Companion to SCOPE.md. This document preserves all technical decisions and conversation context so any new chat in the Claude Project can pick up where the last one left off.

## Current state (as of June 2026)

- **Graduation**: complete (MS Applied Data Science, Syracuse iSchool, May 2026)
- **ProAg engagement**: complete
- **Active commitments**: HyperQuark Research Fellow + active job search (primary focus)
- **Handshake AI**: resuming after EAD authorization
- **Week 1 (Research)**: ✅ complete — RESEARCH_NOTES.md shipped and corrected
- **Now in**: Week 2 (Foundation) — Python 3.13 + uv set up, repo initialized, docs locked; data pipeline next

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

### Week 2 — Foundation 🚧 IN PROGRESS

**Window**: ~June 1–7, 2026  
**Time**: 8–10 hours

**Goal**: Repo skeleton, data pipeline, GitHub Actions skeleton.

**Progress**: ✅ Python 3.13 via uv, repo initialized, `docs/` + `CLAUDE.md`/`AGENTS.md` locked, file structure created. ⬜ Data pipeline (healthcheck → 5 sources → DuckDB) and the two GitHub Actions workflows still to do — these are what actually close out Week 2.

▶ NEXT: wire cftc/drought/macro_fred (same fetch/validate + cache-first pattern, FRED key already in .env); then build_duckdb to unify all five — remember the version-suffix fallback and 404-tolerance for missing months.
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

**Deliverable**: Clean repo with 5 data sources unified in a single DuckDB file. Actions skeleton visible on the repo's Actions tab.

**Open as new chat**. Topic: "OpenAg Week 2 foundation — repo + data pipeline."

---

### Week 3 — Regime Analysis

**Window**: ~June 8–14, 2026  
**Time**: 10–12 hours

**Goal**: Empirical regime detection. The notebook that justifies every subsequent modeling decision.

**Tasks**:

- Changepoint detection with `ruptures` library on log returns and rolling volatility
- Statistical break tests: Chow test for known break points, supremum Wald for unknown windows
- Regime characterization features computed: vol percentile, term-structure shape, COT positioning extremity, drought stress index, USD index regime
- Visualize regime structure across 10y of history
- Writeup section: where breaks are, what they correspond to (where attributable), magnitude
- README section #1 drafted

**Deliverable**: `notebooks/01_regime_analysis.ipynb` + README section with figures and findings.

**Open as new chat**. Topic: "OpenAg Week 3 regime analysis — changepoint detection on corn."

---

### Week 4 — Baselines + Dashboard Shell

**Window**: ~June 15–21, 2026  
**Time**: 10–12 hours

**Goal**: Baseline forecasters + frontend scaffold deployed.

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
