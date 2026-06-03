# AGENTS.md — OpenAg Risk Twin

Agent guidance for this repo. The full project context lives in **`CLAUDE.md`** at the repo root — read it first; it applies to all agents, not just Claude Code.

The non-negotiables, inlined so they're never missed:

- **Env**: Python 3.13 via uv (`pyproject.toml` + `uv.lock`). Not pip, not conda.
- **Scope**: build only what's in `docs/SCOPE.md`. New ideas go to `docs/v2-ideas.md` — never into v1.
- **Evaluation**: walk-forward only, never k-fold on time series.
- **Output**: probabilistic (quantile + conformal), never bare point forecasts.
- **Framing**: this is risk infrastructure under regime uncertainty, not a price predictor. Keep all docs, code, and comments consistent with that.
- **Data**: free public sources only; raw cached in `data/raw/` (gitignored), DuckDB regenerable from raw.

For locked decisions, code conventions, target structure, and current phase, see `CLAUDE.md`.
