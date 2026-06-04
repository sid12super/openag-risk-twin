# pipeline/sources/wasde.py
"""USDA WASDE source: monthly CSV, filtered to corn (long/tidy format).

Cache-first: reads data/raw/ if present (local dev — usda.gov blocks direct hits here),
else downloads and caches (CI path). Normal months: oce-wasde-report-data-YYYY-MM.csv;
reposted months carry a version suffix, e.g. ...-2026-05-V2.csv.
"""
import io
from pathlib import Path
import pandas as pd
import requests

BASE = ("https://www.usda.gov/sites/default/files/documents/"
        "oce-wasde-report-data-{year}-{month:02d}.csv")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; openag-risk-twin/0.1)",
    "Referer": "https://www.usda.gov/historical-wasde-report-data-3",
}
RAW_DIR = Path("data/raw")
EXPECTED = {"Commodity", "Attribute", "Value", "MarketYear", "ReportDate"}

def url_for(year: int, month: int) -> str:
    return BASE.format(year=year, month=month)

def fetch(year: int = 2026, month: int = 5) -> pd.DataFrame:
    cached = sorted(RAW_DIR.glob(f"oce-wasde-report-data-{year}-{month:02d}*.csv"))  # matches -V2
    if cached:
        return pd.read_csv(cached[-1])
    r = requests.get(url_for(year, month), headers=HEADERS, timeout=30)
    r.raise_for_status()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    (RAW_DIR / f"oce-wasde-report-data-{year}-{month:02d}.csv").write_text(r.text)
    return pd.read_csv(io.StringIO(r.text))

def validate(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("WASDE returned no rows")
    missing = EXPECTED - set(df.columns)
    if missing:
        raise ValueError(f"WASDE missing columns: {missing}")
    if not df["Commodity"].astype(str).str.contains("corn", case=False).any():
        raise ValueError("no corn rows in WASDE data")