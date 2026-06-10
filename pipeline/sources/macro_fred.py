# pipeline/sources/macro_fred.py
"""FRED macro series: USD index, 10Y Treasury, energy proxy."""

import pandas as pd
from dotenv import load_dotenv
from fredapi import Fred

load_dotenv()  # picks up FRED_API_KEY from .env

SERIES = {
    "usd_broad": "DTWEXBGS",  # Nominal Broad U.S. Dollar Index
    "treasury_10y": "DGS10",  # 10-Year Treasury yield
    "wti_crude": "DCOILWTICO",  # WTI crude — energy proxy
}


def fetch(start: str = "2016-01-01") -> pd.DataFrame:
    fred = Fred()
    df = pd.DataFrame(
        {
            name: fred.get_series(code, observation_start=start)
            for name, code in SERIES.items()
        }
    )
    return df.rename_axis("date").reset_index()


def validate(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("FRED returned no rows")
    missing = set(SERIES) - set(df.columns)
    if missing:
        raise ValueError(f"FRED missing series: {missing}")
