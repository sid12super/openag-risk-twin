# pipeline/check_duckdb.py
"""Quick sanity check on the built DuckDB: row counts, date coverage, a peek."""

import duckdb

DATE_COL = {
    "prices": "Date",
    "wasde": "ReportDate",
    "cftc": "report_date",
    "drought": "mapDate",
    "macro": "date",
}


def main():
    con = duckdb.connect("data/openag.duckdb", read_only=True)
    for t, dc in DATE_COL.items():
        n = con.sql(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        lo, hi = con.sql(
            "SELECT MIN(strptime(ReportDate,'%B %Y')), MAX(strptime(ReportDate,'%B %Y')) FROM wasde"
        ).fetchone()
        print(f"{t:<8} {n:>7,} rows   {lo}  →  {hi}")
    print("\nlatest prices:")
    print(con.sql('SELECT * FROM prices ORDER BY "Date" DESC LIMIT 3').df())
    print("\nwasde commodities present (should be corn only):")
    print(con.sql("SELECT DISTINCT Commodity FROM wasde").df())
    con.close()


if __name__ == "__main__":
    main()
