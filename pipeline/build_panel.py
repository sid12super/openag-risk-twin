#!/usr/bin/env python3
"""Build the modeling `panel` table in openag.duckdb.

Reads the five raw source tables, does the as-of joins onto the trading
calendar, engineers the price/vol features, assigns the fixed validated
regime labels, and writes the `panel` table that generate_forecast.py
and the notebooks read.

Run from the repo root:  uv run python -m pipeline.build_panel

This is the single source of truth for panel construction. It mirrors
notebooks/01_regime_analysis exactly — keep them in sync if the regime
breaks or feature set ever change. No `ruptures` dependency: the breaks
are the pinned, validated changepoint dates, not re-detected each run, so
historical regime labels stay stable and new dates fall into low_23_26.
"""

from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

# --- validated regime boundaries (from 01_regime_analysis, Cell 7) ---
REGIME_BREAKS = pd.to_datetime(
    [
        "2021-01-05",  # trend wall up
        "2021-04-16",  # vol up
        "2021-07-20",  # vol down
        "2022-09-20",  # vol down
        "2023-05-10",  # vol up
        "2023-07-31",  # trend wall down + vol down
    ]
)
REGIME_LABELS = [
    "calm_16_21",
    "breakout_21",
    "burst_spr21",
    "high_21_22",
    "cooling_22_23",
    "burst_spr23",
    "low_23_26",
]


def locate_root() -> Path:
    return next(
        p for p in [Path.cwd(), *Path.cwd().parents] if (p / "pyproject.toml").exists()
    )


def to_ns(s):
    return pd.to_datetime(s).astype("datetime64[ns]")


def load_prices(con) -> pd.DataFrame:
    prices = con.sql('SELECT "Date", "Close" FROM prices ORDER BY "Date"').df()
    prices["Date"] = pd.to_datetime(prices["Date"])
    prices = prices.set_index("Date")
    prices["Close"] = pd.to_numeric(prices["Close"], errors="coerce")
    prices = prices.dropna(subset=["Close"])
    prices["log_ret"] = np.log(prices["Close"]).diff()
    prices["rolling_vol"] = prices["log_ret"].rolling(21).std() * np.sqrt(252)
    return prices


def prep_wasde(wasde_raw: pd.DataFrame) -> pd.DataFrame:
    w = wasde_raw.copy()
    # text "Month Year" -> real date
    w["ReportDate"] = pd.to_datetime(w["ReportDate"], format="%B %Y", errors="coerce")
    es = w[
        w["Commodity"].astype(str).str.contains("corn", case=False, na=False)
        & w["Attribute"].astype(str).str.strip().eq("Ending Stocks")
        & w["Region"].astype(str).str.contains("United States", case=False, na=False)
    ].copy()
    es = es[es["AnnualQuarterFlag"].astype(str).str.contains("Annual", case=False, na=False)]
    es = es[es["MarketYear"].astype(str).str.contains("/")]  # drop NaN-marketing-year aggregate
    es["Value"] = pd.to_numeric(es["Value"], errors="coerce")
    es = (
        es.sort_values(["ReportDate", "MarketYear"])
        .groupby("ReportDate", as_index=False)
        .last()[["ReportDate", "Value"]]
        .rename(columns={"Value": "corn_ending_stocks_mmt"})
        .sort_values("ReportDate")
    )
    es["ReportDate"] = to_ns(es["ReportDate"])
    return es


def prep_cftc(cftc_raw: pd.DataFrame) -> pd.DataFrame:
    cftc = cftc_raw.copy()
    cftc["report_date"] = to_ns(cftc["report_date"])
    cftc["spec_net"] = cftc["noncomm_long"] - cftc["noncomm_short"]
    cftc["spec_net_pct_oi"] = cftc["spec_net"] / cftc["open_interest"]
    return cftc.sort_values("report_date")[["report_date", "spec_net", "spec_net_pct_oi"]]


def prep_drought(drought_raw: pd.DataFrame) -> pd.DataFrame:
    dr = drought_raw.copy()
    dr["mapDate"] = to_ns(dr["mapDate"])
    dr["drought_stress"] = pd.to_numeric(dr.get("d2"), errors="coerce")
    return dr.sort_values("mapDate")[["mapDate", "drought_stress"]]


def prep_macro(macro_raw: pd.DataFrame) -> pd.DataFrame:
    mac = macro_raw.copy()
    mac["date"] = to_ns(mac["date"])
    return mac.sort_values("date")


def build_panel(prices, cftc, dr, mac, es) -> pd.DataFrame:
    panel = prices.reset_index()[["Date", "Close", "log_ret", "rolling_vol"]].copy()
    panel["Date"] = to_ns(panel["Date"])
    panel = panel.sort_values("Date")
    panel = pd.merge_asof(panel, cftc, left_on="Date", right_on="report_date", direction="backward")
    panel = pd.merge_asof(panel, dr, left_on="Date", right_on="mapDate", direction="backward")
    panel = pd.merge_asof(panel, mac, left_on="Date", right_on="date", direction="backward")
    panel = pd.merge_asof(panel, es, left_on="Date", right_on="ReportDate", direction="backward")
    panel = panel.set_index("Date").drop(
        columns=["report_date", "mapDate", "date", "ReportDate"], errors="ignore"
    )
    # fixed validated breaks -> regime label per row (no PELT re-run)
    codes = np.searchsorted(REGIME_BREAKS.values, panel.index.values, side="right")
    panel["regime"] = pd.Categorical.from_codes(codes, categories=REGIME_LABELS, ordered=True)
    return panel


def main():
    root = locate_root()
    db_path = root / "data" / "openag.duckdb"
    print(f"building panel from {db_path}")

    con = duckdb.connect(str(db_path))  # read-write
    prices = load_prices(con)
    wasde_raw = con.sql("SELECT * FROM wasde").df()
    cftc_raw = con.sql("SELECT * FROM cftc").df()
    drought_raw = con.sql("SELECT * FROM drought").df()
    macro_raw = con.sql("SELECT * FROM macro").df()

    es = prep_wasde(wasde_raw)
    cftc = prep_cftc(cftc_raw)
    dr = prep_drought(drought_raw)
    mac = prep_macro(macro_raw)

    panel = build_panel(prices, cftc, dr, mac, es)

    out = panel.reset_index()
    out["regime"] = out["regime"].astype(str)  # categorical -> varchar for DuckDB
    con.register("panel_df", out)
    con.execute("CREATE OR REPLACE TABLE panel AS SELECT * FROM panel_df")
    con.unregister("panel_df")
    con.close()

    print(f"wrote table 'panel' · {panel.shape[0]} rows × {panel.shape[1]} cols")
    print(f"  range: {panel.index.min().date()} → {panel.index.max().date()}")
    print(f"  latest regime: {panel['regime'].iloc[-1]}")


if __name__ == "__main__":
    main()