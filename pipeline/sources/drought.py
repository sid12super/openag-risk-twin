# pipeline/sources/drought.py
"""US Drought Monitor: weekly drought severity, corn-belt state (Iowa)."""

import requests
import pandas as pd

USDM = (
    "https://usdmdataservices.unl.edu/api/StateStatistics/"
    "GetDroughtSeverityStatisticsByAreaPercent"
)


def fetch(
    aoi: str = "19", start: str = "1/1/2016", end: str = "6/1/2026"
) -> pd.DataFrame:
    params = {"aoi": aoi, "startdate": start, "enddate": end, "statisticsType": "1"}
    r = requests.get(
        USDM, params=params, headers={"Accept": "application/json"}, timeout=30
    )
    r.raise_for_status()
    return pd.DataFrame(r.json())


def validate(df: pd.DataFrame) -> None:
    if df.empty:
        raise ValueError("USDM returned no rows")
    needed = {"mapDate", "d0", "d4"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"USDM missing columns: {missing}")
