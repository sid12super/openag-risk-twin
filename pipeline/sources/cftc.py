# pipeline/sources/cftc.py
import cot_reports as cot
import pandas as pd

def fetch(year: int = 2026) -> pd.DataFrame:
    df = cot.cot_year(year=year, cot_report_type="legacy_fut")
    market_col = next((c for c in df.columns
                       if "market" in c.lower() and "exchange" in c.lower()), None)
    if market_col is None:
        raise ValueError(f"no market/exchange column; got {list(df.columns)[:8]}")
    return df[df[market_col].str.contains("CORN", case=False, na=False)]

def validate(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("CFTC COT returned no corn rows")  # fetch already filtered to corn