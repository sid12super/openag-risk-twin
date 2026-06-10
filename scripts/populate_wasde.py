# scripts/populate_wasde.py
"""Local backfill of WASDE monthly CSVs into data/raw/.

USDA bot-blocks plain HTTP clients from this network, so we impersonate a
browser via curl_cffi. Run from anywhere: `uv run python scripts/populate_wasde.py`.
"""

from pathlib import Path
from curl_cffi import requests

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
BASE = "https://www.usda.gov/sites/default/files/documents/oce-wasde-report-data-{}-{:02d}{}.csv"

for year in range(2021, 2027):
    for month in range(1, 13):
        if list(RAW.glob(f"oce-wasde-report-data-{year}-{month:02d}*.csv")):
            continue
        for suffix in ("", "-V2", "-V3"):
            try:
                r = requests.get(
                    BASE.format(year, month, suffix), impersonate="chrome", timeout=30
                )
                r.raise_for_status()
            except Exception:
                continue
            (RAW / f"oce-wasde-report-data-{year}-{month:02d}{suffix}.csv").write_bytes(
                r.content
            )
            print(f"got {year}-{month:02d}{suffix}")
            break
