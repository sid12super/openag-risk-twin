"""Reachability + schema checks for each data source. Run before building the pipeline."""
from pipeline.sources import prices_yf, wasde

SOURCES = {
    "yfinance ZC=F": prices_yf,
    "USDA WASDE":    wasde,
    # cftc, drought, macro_fred added as their modules land
}

def main():
    results = {}
    for name, mod in SOURCES.items():
        try:
            df = mod.fetch()
            mod.validate(df)
            results[name] = f"OK   ({len(df):,} rows)"
        except Exception as e:
            results[name] = f"FAIL  {type(e).__name__}: {e}"
    w = max(len(n) for n in results)
    for name, status in results.items():
        print(f"{name:<{w}}  {status}")
    if any(s.startswith("FAIL") for s in results.values()):
        raise SystemExit(1)   # non-zero exit → CI fails when a source breaks

if __name__ == "__main__":
    main()