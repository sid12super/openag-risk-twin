# pipeline/sources/prices_yf.py
"""yfinance source: CME corn front-month (ZC=F) daily settlements."""

import yfinance as yf
import pandas as pd

TICKER = "ZC=F"
EXPECTED = {"Open", "High", "Low", "Close", "Volume"}


def fetch(period: str = "10y") -> pd.DataFrame:
    df = yf.download(
        TICKER, period=period, interval="1d", auto_adjust=False, progress=False
    )
    return df.reset_index()


def validate(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("ZC=F returned no rows")
    cols = {
        c[0] if isinstance(c, tuple) else c for c in df.columns
    }  # flatten multiindex
    missing = EXPECTED - cols
    if missing:
        raise ValueError(f"ZC=F missing columns: {missing}")
