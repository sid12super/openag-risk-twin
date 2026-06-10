# pipeline/build_duckdb.py
import duckdb
from pathlib import Path
from pipeline.sources import prices_yf, wasde, cftc, drought, macro_fred

DB_PATH = Path("data/openag.duckdb")


def write_table(con, name, df, key):
    df = df.copy()
    df.columns = [
        c[0] if isinstance(c, tuple) else c for c in df.columns
    ]  # flatten yfinance multiindex
    subset = [k for k in key if k in df.columns]
    df = df.drop_duplicates(
        subset=subset or None, keep="last"
    )  # `or None` = dedupe on all cols
    con.register("_df", df)
    con.execute(
        f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM _df"
    )  # idempotent rebuild
    con.unregister("_df")
    print(f"  {name:<8} {len(df):>7,} rows · {len(df.columns)} cols")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    print("building openag.duckdb ...")
    write_table(con, "prices", prices_yf.fetch(period="10y"), key=["Date"])
    write_table(
        con,
        "wasde",
        wasde.fetch_all(start_year=2021, download=False),
        key=[
            "ReportDate",
            "Attribute",
            "Region",
            "MarketYear",
            "ProjEstFlag",
            "AnnualQuarterFlag",
        ],
    )
    write_table(con, "cftc", cftc.fetch_all(start_year=2021), key=["report_date"])
    write_table(
        con,
        "drought",
        drought.fetch(start="1/1/2016", end="12/31/2026"),
        key=["mapDate"],
    )
    write_table(con, "macro", macro_fred.fetch(start="2016-01-01"), key=["date"])
    con.close()
    print(f"done → {DB_PATH}")


if __name__ == "__main__":
    main()
