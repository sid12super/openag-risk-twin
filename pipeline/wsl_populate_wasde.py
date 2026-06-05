# wsl_populate_wasde.py — swap urllib for curl_cffi
from curl_cffi import requests          # impersonates a browser
import pathlib
RAW = pathlib.Path("data/raw"); RAW.mkdir(parents=True, exist_ok=True)
B = "https://www.usda.gov/sites/default/files/documents/oce-wasde-report-data-{}-{:02d}{}.csv"
for y in range(2021, 2027):
    for m in range(1, 13):
        if list(RAW.glob(f"oce-wasde-report-data-{y}-{m:02d}*.csv")): continue
        for suf in ("", "-V2", "-V3"):
            try:
                r = requests.get(B.format(y, m, suf), impersonate="chrome", timeout=30)
                r.raise_for_status()
            except Exception:
                continue
            (RAW / f"oce-wasde-report-data-{y}-{m:02d}{suf}.csv").write_bytes(r.content)
            print(f"got {y}-{m:02d}{suf}"); break