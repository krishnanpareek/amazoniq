"""Export DimCategory for Power BI star schema."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from category_config import CATEGORIES  # noqa: E402

COUNTS = ROOT / "data" / "processed" / "fact_catalog_category_counts.csv"
METRICS = ROOT / "data" / "processed" / "fact_forecast_metrics.csv"
OUT = ROOT / "data" / "processed" / "dim_category.csv"


def main() -> None:
    counts = pd.read_csv(COUNTS)
    metrics = pd.read_csv(METRICS)
    agg = counts.groupby(["amazoniq_category_id", "amazoniq_category_name"], as_index=False)[
        "product_count_full"
    ].sum()
    agg = agg.rename(
        columns={
            "amazoniq_category_id": "category_id",
            "amazoniq_category_name": "category_name",
            "product_count_full": "catalog_product_count",
        }
    )
    rows = []
    for cat in CATEGORIES:
        row = {
            "category_id": cat["category_id"],
            "category_name": cat["name"],
            "keyword": cat["trends_keyword"],
            "census_naics": cat["census_naics"],
            "census_label": cat["census_label"],
        }
        match = agg[agg["category_id"] == cat["category_id"]]
        row["catalog_product_count"] = int(match["catalog_product_count"].iloc[0]) if len(match) else 0
        m = metrics[metrics["category_id"] == cat["category_id"]]
        row["baseline_mape_pct"] = float(m["mape_pct"].iloc[0]) if len(m) else None
        rows.append(row)
    dim = pd.DataFrame(rows)
    max_count = dim["catalog_product_count"].max()
    dim["catalog_share_of_max"] = (dim["catalog_product_count"] / max_count).round(4)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    dim.to_csv(OUT, index=False)
    print(f"wrote {OUT}")
    print(dim.to_string(index=False))


if __name__ == "__main__":
    main()
