# OpenAg Risk Twin — 5-Week Plan to MSV

> Companion to SCOPE.md. This document preserves all technical decisions and conversation context so any new chat in the Claude Project can pick up where the last one left off.

## Current state (as of June 11, 2026)

- **Graduation**: complete (MS Applied Data Science, Syracuse iSchool, May 2026)
- **ProAg engagement**: complete
- **Active commitments**: HyperQuark Research Fellow + active job search (primary focus)
- **Handshake AI**: resuming after EAD authorization
- **Week 2** [done] — five-source warehouse + CI/CD, both workflows green.
- **Week 3** [done] — seven validated regimes (detection + Chow/variance validation + multi-source characterization), regime figure, README section #1 drafted.
- **Week 4** [done] — baselines notebook + live stubbed dashboard + live API. Live URLs:
  - API: https://openag-risk-twin.onrender.com (`/docs`)
  - Dashboard: https://openag-risk-twin.vercel.app

## Sprint structure

Each phase opens a new chat in the Claude Project. SCOPE.md and PLAN.md travel with the project so context is preserved without re-explaining the foundation every time.

---

### Week 1 — Market & Domain Research [COMPLETE]

**Goal**: Understand commodity futures and corn markets well enough to make sensible technical decisions in Week 2. No code commits required this week.

**Deliverable**: `RESEARCH_NOTES.md` — key terms, primary sources, synthesis in own words. [done]

---

### Week 2 — Foundation [COMPLETE]

**Goal**: Repo skeleton, data pipeline, GitHub Actions skeleton.

**Shipped**: Python 3.13 via uv; repo initialized; `docs/` + `CLAUDE.md`/`AGENTS.md` locked; monorepo structure created. Five-source pipeline (yfinance `ZC=F`, USDA WASDE via `curl_cffi` browser impersonation, CFTC COT via `cot_reports`, NOAA Drought Monitor, FRED via `fredapi`) unified into `data/openag.duckdb` through `build_duckdb.py`, with a `fetch()/validate()` interface and cache-first behavior. Both GitHub Actions workflows green: `ci.yml` (ruff + pytest) and `refresh.yml` (scheduled healthcheck + `workflow_dispatch`).

**Deliverable**: Clean repo with 5 data sources unified in a single DuckDB file. [done]

---

### Week 3 — Regime Analysis [COMPLETE]

**Goal**: Empirical regime detection. The notebook that justifies every subsequent modeling decision.

**Shipped (June 10, 2026)**:

- `notebooks/01_regime_analysis.ipynb` — DuckDB load -> log returns + 21-day annualized rolling vol -> **dual PELT** (variance via `model="normal"` on returns; trend via `l2` on log price) with a **penalty sweep** so the breakpoint count is stability-based, not hand-picked.
- **Validation**: Chow test on level breaks, F-test on return variance for volatility breaks. Two trend walls — 2021-01-05 (+221c, p~1e-210) and 2023-07-31 (-201c, p~1e-236) — plus five validated volatility breaks. The Feb-2022 candidate was correctly **rejected** (vol 36%->35%, p=0.85): the Russia-Ukraine invasion was a price/direction move inside an already-high-vol regime, not a new volatility regime.
- **Characterization**: as-of join (`merge_asof`, backward, no lookahead) of all five sources onto the trading-day calendar; per-regime profile across realized vol, speculative positioning (spec net % OI), drought stress, USD/macro, and WASDE ending stocks. **Seven regimes.**
- `notebooks/figures/01_regime_structure.png` — annotated regime-structure figure.
- README section #1 drafted: "Regime structure under uncertainty."

**Key findings**:

- **Volatility alone cannot define a regime.** The spring-2021 and spring-2023 bursts are vol-twins (44% vs 43%) but opposite states: specs +26% vs +1% of OI, stocks 36 vs 57 MMT, price rising vs falling. This is the empirical argument for multi-factor regime features.
- **Reversion found a higher floor**: post-2023 calm ~440c vs the 2016-2020 baseline ~366c — not a return to the old level.
- **COVID was not a regime change for corn**: the early-2020 dip is absorbed inside the calm baseline with no break.
- **Drought level != volatility**: the highest drought reading (2022-23 cooling) coincided with the lowest vol -> featurize drought as change/percentile, not raw level.
- **Coverage asymmetry documented honestly**: CFTC + WASDE begin 2021; calm-era fundamentals are uncovered, not zero.

**Deviations from plan**:

- **Term-structure shape** deferred to v2 — front-month-only data has no curve slope. Parked in `v2-ideas.md`.
- **Supremum-Wald not implemented** — Chow + variance F-test + the stability sweep are sufficient for v1.

**Deliverable**: `notebooks/01_regime_analysis.ipynb` + README section with figure and findings. [done]

---

### Week 4 — Baselines + Dashboard Shell [COMPLETE]

**Window**: ~June 15-21, 2026
**Time**: ~12-14 hours (incl. environment/deploy debugging)

**Goal**: Baseline forecasters + frontend scaffold deployed.

**Shipped (June 11, 2026)**:

- `notebooks/02_baselines.ipynb` — modeling frame built from the Week-3 panel. **Target = 30-day forward log return** (not price level — trees can't extrapolate above the training range, so a level target would flatline through breakouts). Vanilla model uses **price + calendar features only** (`ret_1/5/10/21/63`, `vol_21`, `sin_doy`, `cos_doy`); regime/exogenous columns are deliberately benched for the Week-5 lift test. Walk-forward (rolling-origin, expanding window, step=21, 30-day embargo so train/test targets never overlap).
- **Results (76 folds, OOS 2020-2026, skill = 1 - RMSE/RMSE_rw)**: random walk RMSE **0.0952** (the floor); seasonal naive 0.1199 (-26%); AR(1) 0.0989 (-4%); **vanilla XGBoost 0.0980 (-3%)**. None beats the random walk overall — the honest "price-only signal doesn't beat the wall" result. But XGBoost's skill is **regime-dependent** per-year: it beats RW in the trending years (2021/2023/2024) and loses in shock/calm years (2020/2022/2025/26). That asymmetry is the empirical hook for Week-5 regime features.
- `notebooks/figures/02_xgb_vs_rw_by_year.png` + README section #2 drafted.
- **FastAPI stub backend live on Render**: https://openag-risk-twin.onrender.com — endpoints `/status`, `/forecast`, `/scenario`, `/model-card`, `/docs`. Contracts + stub data only; **zero live LLM/data calls** (those are Week 5; `/scenario` returns `"source":"stub"`). `render.yaml` IaC (uv build, `healthCheckPath: /status`), CORS via env-var `ALLOWED_ORIGIN_REGEX` (allows `*.vercel.app`). httpx added as a dev dep for the FastAPI TestClient.
- **Next.js dashboard shell live on Vercel**: https://openag-risk-twin.vercel.app — three views (forecast, scenario explorer, model card) + a polling health-status badge, reading the live API on stub data via `NEXT_PUBLIC_API_URL`. Design: instrument aesthetic — uncertainty-band **cone** as the signature visual, IBM Plex Mono (tabular) for all figures via `next/font`, olive accent with amber reserved for uncertainty. Client-side fetch with loading/error/cold-start states; responsive header.

**Deviations from plan**:

- **`/health` renamed to `/status`** — ad-blockers (uBlock/Brave) block `/health`-pattern paths, which made the status badge show a false "offline." `/status` dodges the blocklists.
- **Fonts via `next/font/google`** rather than a remote CSS `@import` (the import was a build-time network dependency).
- **Custom domain deferred to v2** (default Vercel/Render URLs for v1, per SCOPE).
- A few cosmetic polish items (broader mobile pass beyond the header, pasting the three README sections into `README.md`) are tracked in `WEEK4_CLEANUP.md`; none block the deliverable.

**Environment lessons (logged so they don't recur)**: OneDrive-synced repo corrupts build artifacts (`.venv`, `.next`) and a zombie dev server on port 3000 masked all edits — `netstat -ano | findstr :3000`, kill the PID, then look at code. And **CI green != deployed**: Render needed an explicit "deploy latest commit" of the green commit.

**Deliverable**: `notebooks/02_baselines.ipynb` + live (stubbed) dashboard URL + live API URL. [done]

---

### Week 5 — Lift + Ship MSV

**Window**: ~June 22-28, 2026
**Time**: 12-14 hours

**Goal**: Show regime features lift over baseline, wire everything live, ship.

> NEXT: Week 5 ship — regime lift + live integration. **First task: contract-lock.** Before wiring any live data, freeze and verify the API response contract the frontend already hardcodes — `interval_80.low/high`, `regime.label`, `regime.vol_pct`, `history[].date`, `history[].close`, `last_price`, `point`, `as_of`, `horizon_days`, `per_year_rmse` keys, `features[]`, `framing` — so the stub->live swap doesn't silently break the dashboard. Confirm the live pipeline's output shapes match these exactly (Pydantic response models are the single source of truth; the frontend `types.ts` must mirror them). Only then start swapping stubs for live data.

**Tasks**:

- **Contract-lock first** (above) — make the live endpoints conform to the frozen stub shapes.
- Add regime features to XGBoost; document **lift vs the 0.0980 vanilla baseline** (the regime-dependent per-year skill from Week 4 is the hypothesis to confirm).
- Quantile regression for probabilistic output (10/50/90 quantiles).
- Conformal prediction wrapper via `mapie` for calibrated intervals.
- Wire FastAPI to serve live forecasts from DuckDB (replace the stubs behind the now-locked contract).
- Next.js dashboard reads live API and renders forecast + 80% interval + regime indicator (the cone is already built — it just needs real data).
- Kimi K2.6 scenario narration on button click — single prompt integration (`/scenario` flips `"source"` from `"stub"` to `"kimi-k2.6"`).
- Blog post draft on the journey.
- Tag `v1.0.0`.

**Open as new chat**. Topic: "OpenAg Week 5 ship — regime lift + live integration."

**Candidate workflow**: the open-ended live-wiring is the best fit for the parked plan-mode-with-Fable-5 + execution-with-Haiku experiment (see `v2-ideas.md`), if you want to try it here.

---

## Key technical decisions captured from conversation

These are decisions Sid and Claude already made. They're locked unless explicitly revisited.

### Architecture decisions

- **Stacked ensemble** (XGBoost + LightGBM + CatBoost -> logistic regression meta) is the v2 architecture. v1 ships with single XGBoost to reduce shipping risk.
- **Champion-challenger** pattern is the v2 deployment story. v1 ships with one model in production.
- **NannyML + Evidently** are the monitoring stack: NannyML estimates performance without labels (DLE for this regression problem); Evidently tracks data and prediction drift.
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
- **Term-structure shape feature deferred to v2** — front-month-only data has no curve slope (needs >=2 curve points). See `v2-ideas.md`.
- **WASDE units note**: the ingested US corn ending-stocks series is in **million metric tons** (world-table US line), not million bushels. Irrelevant for modeling (it gets percentiled), but documented so the unit isn't misread.

### Framing decisions

- README pitch is **"risk management infrastructure under regime uncertainty"**, never "predicts corn within X%."
- The honest position: **an LLM layer does not improve forecast accuracy.** It improves interpretability and decision-readiness. Don't claim otherwise.
- Selling points: calibrated uncertainty, regime awareness, scenario reasoning, production monitoring, automated retraining.
- Acknowledge upfront that forecasting commodity prices is hard; the value of the system is in *quantifying what it doesn't know*.

### Tooling decisions

- **Python 3.13**, managed with **uv** (`pyproject.toml` + `uv.lock`). No pip/conda.
- **Repo layout**: monorepo. Planning docs live in `docs/`; `README.md`, `CLAUDE.md`, and `AGENTS.md` stay at root for agentic tools.
- **Frontend stack** (Week 4): Next.js (App Router) + TypeScript + Tailwind + recharts; `next/font` for type. Deployed on Vercel (Root Directory = `frontend`). Backend FastAPI on Render (`render.yaml` IaC, uv build). `NEXT_PUBLIC_API_URL` is the frontend->backend seam; CORS via `ALLOWED_ORIGIN_REGEX`.
- **Backups**: raw downloads cached/timestamped in `data/raw/`; the DuckDB file is regenerable and gitignored on main. GitHub is the offsite backup.
- **`ruptures`** is the sanctioned new dependency for Week 3; `scipy` rides in with it. Structural-break tests are hand-rolled.
- **Agentic split**: plan-mode-with-Sonnet + execution-with-Haiku is the proven pattern. Upgrading the planner to Claude Fable 5 for open-ended work (best fit: Week 5 live wiring) is parked in `v2-ideas.md`.
- **Environment**: keep the working repo out of OneDrive-synced folders — sync corrupts `.venv`/`.next`/`node_modules`. Git is the sync.

## Risks to monitor

1. **Scope creep** — high probability. Mitigation: every new idea goes to `v2-ideas.md`, never into v1.
2. **Job search competition** — this project must accelerate, not compete with, job search. Mitigation: weekly time audit.
3. **Burnout** — multiple concurrent commitments. Mitigation: protect hobbies (Rocket League, F1 weekends, cooking, gym).
4. **Domain perfectionism** — Mitigation: Week 1 was the research week; after that, learn what the data forces.
5. **Tool sprawl** — Mitigation: use known tools except the deliberate learning surface (NannyML, Evidently, `ruptures`, Kimi K2.6, conformal via `mapie`).
6. **Hackathon followup contention** — if Cerebral Valley followup demands time, OpenAg pauses for a week.

## How to resume across chats

Each new chat in the Claude Project should open with:

> "Picking up OpenAg Risk Twin at Week N. SCOPE.md and PLAN.md are in the project files. Today's focus: [specific topic]."

Update this PLAN.md at the end of each phase with what actually shipped vs what was planned, so the historical record stays accurate.