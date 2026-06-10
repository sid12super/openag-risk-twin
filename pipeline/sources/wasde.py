# pipeline/sources/wasde.py
"""USDA WASDE source: monthly CSV, filtered to corn (long/tidy format).

Cache-first: reads data/raw/ if present (local dev — usda.gov blocks direct hits here),
else downloads and caches (CI path). Normal months: oce-wasde-report-data-YYYY-MM.csv;
reposted months carry a version suffix, e.g. ...-2026-05-V2.csv.
"""

import io
from pathlib import Path
import pandas as pd
from curl_cffi import requests
from datetime import date

BASE = (
    "https://www.usda.gov/sites/default/files/documents/"
    "oce-wasde-report-data-{year}-{month:02d}.csv"
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; openag-risk-twin/0.1)",
    "Referer": "https://www.usda.gov/historical-wasde-report-data-3",
}
RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw"
EXPECTED = {"Commodity", "Attribute", "Value", "MarketYear", "ReportDate"}


def url_for(year: int, month: int) -> str:
    return BASE.format(year=year, month=month)


def fetch(year: int = 2026, month: int = 5) -> pd.DataFrame:
    """Single month, cache-first with version fallback (used by healthcheck)."""
    df = _read_or_download(year, month, download=True)
    if df is None:
        raise ValueError(f"WASDE {year}-{month:02d} unavailable (tried base + -V2/-V3)")
    return df


def validate(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("WASDE returned no rows")
    missing = EXPECTED - set(df.columns)
    if missing:
        raise ValueError(f"WASDE missing columns: {missing}")
    if not df["Commodity"].astype(str).str.contains("corn", case=False).any():
        raise ValueError("no corn rows in WASDE data")


def _read_or_download(year, month, download=True):
    cached = sorted(RAW_DIR.glob(f"oce-wasde-report-data-{year}-{month:02d}*.csv"))
    if cached:
        return pd.read_csv(cached[-1])
    if not download:
        return None  # cache-only: skip, no network
    base = url_for(year, month).removesuffix(".csv")
    for suffix in ("", "-V2", "-V3"):
        try:
            r = requests.get(base + suffix + ".csv", impersonate="chrome", timeout=30)
            r.raise_for_status()
        except Exception:  # was: except requests.RequestException
            continue
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        (RAW_DIR / f"oce-wasde-report-data-{year}-{month:02d}{suffix}.csv").write_text(
            r.text
        )
        return pd.read_csv(io.StringIO(r.text))
    return None


def fetch_all(start_year=2021, download=True):
    today, frames = date.today(), []
    for year in range(start_year, today.year + 1):
        for month in range(1, 13):
            if year == today.year and month > today.month:
                break
            df = _read_or_download(year, month, download=download)
            if df is not None:
                print(
                    f"  wasde {year}-{month:02d}: {len(df):,} rows", flush=True
                )  # visibility
                frames.append(
                    df[
                        df["Commodity"]
                        .astype(str)
                        .str.contains("corn", case=False, na=False)
                    ]
                )
    if not frames:
        raise ValueError("no WASDE in data/raw/ — populate it first")
    return pd.concat(frames, ignore_index=True)
