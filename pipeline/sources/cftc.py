# pipeline/sources/cftc.py
import cot_reports as cot
import pandas as pd
from datetime import date


def fetch(year: int = 2026) -> pd.DataFrame:
    df = cot.cot_year(year=year, cot_report_type="legacy_fut")
    market_col = next(
        (c for c in df.columns if "market" in c.lower() and "exchange" in c.lower()),
        None,
    )
    if market_col is None:
        raise ValueError(f"no market/exchange column; got {list(df.columns)[:8]}")
    return df[df[market_col].str.contains("CORN", case=False, na=False)]


def validate(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError(
            "CFTC COT returned no corn rows"
        )  # fetch already filtered to corn


RENAME = {
    "As of Date in Form YYYY-MM-DD": "report_date",
    "Open Interest (All)": "open_interest",
    "Noncommercial Positions-Long (All)": "noncomm_long",
    "Noncommercial Positions-Short (All)": "noncomm_short",
    "Commercial Positions-Long (All)": "comm_long",
    "Commercial Positions-Short (All)": "comm_short",
}


def fetch_all(start_year: int = 2021) -> pd.DataFrame:
    frames = []
    for year in range(start_year, date.today().year + 1):
        df = cot.cot_year(year=year, cot_report_type="legacy_fut")
        mcol = next(
            c for c in df.columns if "market" in c.lower() and "exchange" in c.lower()
        )
        df = df[df[mcol].str.contains("CORN", case=False, na=False)].rename(
            columns=RENAME
        )
        frames.append(df[list(RENAME.values())])
    return pd.concat(frames, ignore_index=True)
