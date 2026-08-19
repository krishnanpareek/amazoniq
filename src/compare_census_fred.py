"""Compare Census workbook NSA values to FRED republication. Do not reconcile silently."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from category_config import CATEGORIES  # noqa: E402

CENSUS_CSV = ROOT / "data" / "processed" / "fact_census_retail_nsa.csv"
FRED_DIR = ROOT / "data" / "raw" / "census"
CHECK_PERIODS = ("2024-12-01", "2025-12-01", "2026-05-01")


def load_fred(series_id: str) -> dict[str, int]:
    path = FRED_DIR / f"{series_id}.csv"
    out: dict[str, int] = {}
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        value_col = [c for c in reader.fieldnames if c != "observation_date"][0]
        for row in reader:
            raw = row[value_col]
            if raw in (".", "", None):
                continue
            out[row["observation_date"]] = int(float(raw))
    return out


def main() -> None:
    census_rows: list[dict[str, str]] = []
    with CENSUS_CSV.open(encoding="utf-8") as f:
        census_rows = list(csv.DictReader(f))

    print("period,category,naics,census,fred,diff,status")
    mismatches = 0
    checks = 0
    for cat in CATEGORIES:
        fred = load_fred(cat["fred_nsa"])
        for period in CHECK_PERIODS:
            match = next(
                (
                    r
                    for r in census_rows
                    if r["category_id"] == cat["category_id"] and r["period"] == period
                ),
                None,
            )
            census_val = None if match is None or match["sales_millions_nsa"] == "" else int(float(match["sales_millions_nsa"]))
            fred_val = fred.get(period)
            checks += 1
            if census_val is None or fred_val is None:
                status = "GAP"
                diff = ""
                mismatches += 1
            elif census_val == fred_val:
                status = "MATCH"
                diff = 0
            else:
                status = "MISMATCH"
                diff = census_val - fred_val
                mismatches += 1
            print(
                f"{period},{cat['name']},{cat['census_naics']},{census_val},{fred_val},{diff},{status}"
            )
    print(f"checks={checks} mismatches_or_gaps={mismatches}")


if __name__ == "__main__":
    main()
