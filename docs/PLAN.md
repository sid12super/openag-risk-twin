# OpenAg Risk Twin — 5-Week Plan to MSV

> Companion to SCOPE.md. This document preserves all technical decisions and conversation context so any new chat in the Claude Project can pick up where the last one left off.

## Current state (as of June 15, 2026) — **v1.0.0 SHIPPED**

- **Graduation**: complete (MS Applied Data Science, Syracuse iSchool, May 2026)
- **ProAg engagement**: complete
- **Active commitments**: HyperQuark Research Fellow + active job search (primary focus)
- **Week 1** [done] — domain research, `RESEARCH_NOTES.md`.
- **Week 2** [done] — five-source warehouse + CI/CD, both workflows green.
- **Week 3** [done] — seven validated regimes (detection + Chow/variance validation + multi-source characterization), regime figure, README section #1.
- **Week 4** [done] — baselines notebook + live stubbed dashboard + live API.
- **Week 5** [done] — contract-lock, regime lift test (no-lift result), conformal calibration, live wiring via precompute-at-refresh, daily auto-refresh, Kimi K2.6 scenario layer. **MSV live and tagged `v1.0.0`.**
- **Live URLs**:
  - API: https://openag-risk-twin.onrender.com (`/docs`)
  - Dashboard: https://openag-risk-twin.vercel.app
- **Remaining**: blog post draft (in progress, Sid-authored). Everything else in SCOPE's success criteria is live.

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

> **Note (Week 5):** the panel-construction logic in this notebook (the `merge_asof` joins + the pinned regime breaks) was later extracted into `pipeline/build_panel.py` — the canonical panel builder. If the breaks or features change, edit the script and mirror here.

---

### Week 4 — Baselines + Dashboard Shell [COMPLETE]

**Shipped (June 11, 2026)**:

- `notebooks/02_baselines.ipynb` — modeling frame built from the Week-3 panel. **Target = 30-day forward log return** (not price level — trees can't extrapolate above the training range, so a level target would flatline through breakouts). Vanilla model uses **price + calendar features only** (`ret_1/5/10/21/63`, `vol_21`, `sin_doy`, `cos_doy`); regime/exogenous columns deliberately benched for the Week-5 lift test. Walk-forward (rolling-origin, expanding window, step=21, 30-day embargo).
- **Results (76 folds, OOS 2020-2026, skill = 1 - RMSE/RMSE_rw)**: random walk RMSE **0.0952** (the floor); seasonal naive 0.1199 (-26%); AR(1) 0.0989 (-4%); **vanilla XGBoost 0.0980 (-3%)**. None beats the random walk overall. XGBoost's skill is **regime-dependent** per-year: beats RW in trending years (2021/2023/2024), loses in shock/calm years. That asymmetry was the hypothesis for the Week-5 lift test.
- `notebooks/figures/02_xgb_vs_rw_by_year.png` + README section #2.
- **FastAPI stub backend on Render**; **Next.js dashboard shell on Vercel** (three views + status badge, stub data). Instrument aesthetic — uncertainty-band **cone** as the signature visual.

**Deviations from plan**: `/health` renamed to `/status` (ad-blockers); fonts via `next/font/google`; custom domain deferred to v2.

**Environment lessons**: OneDrive-synced repo corrupts build artifacts; **CI green != deployed** (Render needs the green commit promoted).

**Deliverable**: `notebooks/02_baselines.ipynb` + live (stubbed) dashboard + live API. [done]

---

### Week 5 — Lift + Ship MSV [COMPLETE]

**Window**: ~June 12-15, 2026 (compressed)
**Goal**: Show regime features lift over baseline, wire everything live, ship.

**Shipped (June 15, 2026)** — task by task:

**1. Contract-lock** [done]. Froze the API response contract before any live wiring. `backend/schemas.py` upgraded to constrained models: `RegimeLabel` (Literal of seven canonical labels), `ScenarioSource` (`stub`|`kimi-k2.6`), `vol_pct` bounded 0-100, `as_of`/`history[].date` as dates, and a `model_validator` on `ForecastResponse` enforcing cone-coherence (`history[-1] == (as_of, last_price)`, `low <= point <= high`, ascending unique dates). Frontend `frontend/lib/types.ts` mirrors the enums. `backend/tests/test_contract.py` + a committed OpenAPI snapshot guard it.

**2. Regime-feature lift test** [done] — `notebooks/03_regime_lift.ipynb`, pre-registered A/B. **Result: NO LIFT.** Vanilla (8 price/calendar features) RMSE **0.0980** / skill **−0.030** (reproduced the Week-4 baseline — integrity gate passed); Variant A (+4 exogenous) 0.1031 / −0.083; Variant B (+2 more) 0.1082 / −0.137. Regime/exogenous features *hurt*, with damage concentrated in 2023 (consistent with the coverage asymmetry — COT/WASDE begin 2021). **The Week-4 lift hypothesis was rejected; vanilla stands, and the point forecast is the random walk.** PELT regime *labels* were excluded as features (they leak future boundary information). Deeper variants parked in `v2-ideas.md`.

**3. Conformal calibration** [done] — `notebooks/04_conformal.ipynb`. XGBoost quantile regression (10/50/90) + **Conformalized Quantile Regression (CQR)**, **hand-rolled, not `mapie`**. Point **anchored at the random walk** (`point == last_price`) per the no-skill finding; the band is the model's quantile spread recentered on the RW point with a single conformal correction `Q` applied symmetrically, on a trailing ~252-row calibration window. **Marginal CQR shipped over conditional**: the vol-tercile conditional variant *relocated* coverage rather than fixing it (it broke the spring-2021 high-vol bucket because there's no pre-2021 high-vol history to calibrate against), so it's unvalidatable on this window → v2. Marginal coverage ~80.8% overall; per-regime uneven and documented honestly (2020 COVID ~68%, unfixable with trailing data). Production model (3 quantile models + the corrections) serialized to `backend/models/`.

**4. Live wiring** [done] — **precompute-at-refresh architecture** (a deliberate refinement of the planned "serve from DuckDB," chosen for Render's free-tier ephemeral disk + cold starts). `pipeline/generate_forecast.py` runs the model on the latest panel row, writes contract-shaped `backend/data/forecast.json` + `model_card.json` (validated against the Pydantic models before writing), which are committed. The API stays **thin** — loads the JSON, validates against the frozen contract, serves `/forecast`, `/model-card`, `/status`. No XGBoost at request time. `pipeline/build_panel.py` (new) extracts the panel construction from notebook 01 into a script (as-of joins + features + **pinned regime breaks**, no PELT re-run) so the warehouse → panel → forecast chain is reproducible in CI.

**5. Daily auto-refresh** [done] — `refresh.yml` repurposed from the healthcheck no-op to a daily cron (weekdays 12:00 UTC) + `workflow_dispatch`: `build_duckdb` → `build_panel` → `generate_forecast` → commit the JSON → Render auto-redeploys. `FRED_API_KEY` as a repo secret; WASDE source files committed (they were gitignored, which broke the runner's `download=False` read). The forecast now advances daily; `as_of` is current.

**6. Kimi scenario (the AI layer)** [done] — `/scenario` flips `source` from `stub` to `kimi-k2.6`. **Model choice: Kimi K2.6, not K2.7** — K2.7 shipped (June 12) as "K2.7 **Code**," a coding SKU with *forced thinking* and no instant mode, the wrong tool for a latency/cost-sensitive prose narration; K2.6 is the general model and supports instant mode (`"thinking": {"type": "disabled"}`). Called via **`httpx`** (no `openai` SDK — already a dep, no tool sprawl). The handler reads the committed forecast for context (so the note matches the chart), falls back to a deterministic stub on missing-key/error (keeps CI offline and never 500s), and caches by `as_of` (≈1 paid call/day). Prompt is producer-facing per the ProAg lesson — "nearby corn futures" (no invented contract month), grounded strictly in the supplied band/regime (no invented price levels), one paragraph. `MOONSHOT_API_KEY` lives on Render + local `.env` only (not a GitHub secret — so CI uses the offline fallback).

**7. Frontend polish** [done] — y-axis garbled-tick fix (`tickFormatter` rounding to integers + `allowDecimals={false}` + wider axis); model-card header/framing reframed to "Random-walk point + XGBoost quantile interval (CQR-calibrated)" so the card matches the served forecast.

**Deviations from plan**:

- **No regime-feature lift** — the central Week-5 hypothesis failed empirically. This is a *finding*, not a miss: the point forecast is the random walk, and the project's value is the calibrated interval + regime context + scenario layer, exactly the honest framing SCOPE specified.
- **`mapie` not used** — CQR hand-rolled for transparency and full control of the RW-anchoring. `mapie` drops off the sanctioned learning surface.
- **Precompute-at-refresh** replaced "API serves from DuckDB" (free-tier reality).
- **Kimi K2.6, not the newer K2.7** (K2.7 is a forced-thinking coding SKU).
- **NannyML / Evidently live monitoring deferred to v2** — coverage analysis exists in `notebooks/04_conformal.ipynb`, but live drift/performance instrumentation was not built for v1.
- **Contract structural tests validate the committed artifact**; the golden-fixture split (so a real >40% shock can't false-fail CI on the daily artifact) is deferred to v1.x. Currently safe because the default `GITHUB_TOKEN` bot commit doesn't retrigger CI.
- **Model retraining on refresh deferred** — the daily refresh updates *data* only; the model is a fixed serialized artifact.

**Deliverable**: Live MSV at the URLs above, `v1.0.0` tagged. Blog draft pending. [done]

---

## Key technical decisions captured from conversation

### Architecture decisions

- **Precompute-at-refresh** (v1, shipped): the GitHub Action computes the forecast and commits contract-shaped JSON; the API is a thin contract-validating server. Heavy deps live in the Action, not the container.
- **Stacked ensemble** (XGB + LightGBM + CatBoost -> meta) is v2. v1 ships a single XGBoost — and the *point* is the random walk, since XGBoost showed no point-skill (−0.03 vs RW).
- **Champion-challenger** is the v2 deployment story. v1 runs one fixed model.
- **NannyML + Evidently** monitoring: **deferred to v2** (manual coverage analysis only in v1).

### Modeling principles

- Walk-forward (rolling-origin) evaluation only.
- Per-year metric breakdown surfaced, not buried.
- Probabilistic outputs (quantile + **hand-rolled CQR**, marginal) over point forecasts; point anchored at the random walk.
- Regime indicators as continuous features (and they didn't lift in v1 — documented).
- Calibration tracked; coverage reported per regime, honestly, including the unfixable COVID gap.

### Data decisions

- Corn front-month (`ZC=F`) for v1. Soybean (`ZS=F`) is the v2 expansion.
- Free public sources only (yfinance, USDA WASDE, CFTC COT, NOAA Drought Monitor, FRED).
- DuckDB warehouse; `pipeline/build_panel.py` is the canonical panel builder (pinned regime breaks).
- **Term-structure shape** deferred to v2 (front-month-only). **WASDE US ending stocks in MMT** (percentiled, so unit-agnostic for modeling).

### Framing decisions

- Pitch is **"risk management infrastructure under regime uncertainty,"** never "predicts corn within X%."
- **An LLM layer does not improve forecast accuracy** — it improves interpretability and decision-readiness. The model card states this; the scenario layer honors it.
- Value is in *quantifying what it doesn't know*.

### Tooling decisions

- **Python 3.13** via **uv**. Monorepo; planning docs in `docs/`, agentic files (`README`/`CLAUDE.md`/`AGENTS.md`) at root.
- **Frontend**: Next.js + TS + Tailwind + recharts on Vercel. **Backend**: FastAPI on Render (`render.yaml`, `UV_PYTHON_DOWNLOADS=automatic` to allow the pinned 3.13.12). `NEXT_PUBLIC_API_URL` seam; CORS via `ALLOWED_ORIGIN_REGEX`.
- **Kimi K2.6** via OpenAI-compatible endpoint `https://api.moonshot.ai/v1`, instant mode, called with `httpx`.
- **`ruptures`** sanctioned for Week 3 (exploratory only — production breaks are pinned constants). **CQR hand-rolled** (no `mapie`).
- **Agentic split**: architecture/decisions in Claude chat; execution moved from **Claude Code (Haiku, paid)** to **OpenAI Codex (free student credits)**. The **Fable-5 planner experiment is dead** — Claude Fable 5 was shut down ~3 days after launch. Repo already ships `AGENTS.md`, which Codex reads.
- **Environment**: keep the repo out of OneDrive (sync corrupts `.venv`/`.next`); git is the sync.

## Post-v1.0.0 (next)

- **Blog post draft** (Sid-authored, in progress) — the journey: regime detection, the no-lift finding, RW point + calibrated interval, the LLM decision-readiness layer. The last SCOPE success criterion.
- **v1.x polish**: golden-fixture contract tests; broader mobile pass; README sections finalized.
- **v2 candidates** (see `v2-ideas.md`): NannyML/Evidently live monitoring, stacked ensemble + champion-challenger, soybean expansion, multi-horizon, conditional conformal once there's enough high-vol history, retraining on refresh.

## How to resume across chats

Open with: *"Picking up OpenAg Risk Twin — v1.0.0 is live. Today's focus: [topic]."* Update this PLAN.md at the end of meaningful work so the record stays accurate.