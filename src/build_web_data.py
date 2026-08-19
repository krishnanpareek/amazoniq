"""Embed processed CSVs into dashboard/web/data.js and docs/data.js for static viewing.

Reads only from data/processed/. Does not modify source CSVs.
GitHub Pages serves from docs/ (index.html at site root).
"""

from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
WEB_SRC = ROOT / "dashboard" / "web"
DOCS = ROOT / "docs"
OUT_PATHS = [
    WEB_SRC / "data.js",
    DOCS / "data.js",
]
WEB_STATIC = ("index.html", "style.css", "script.js")


def read_csv(name: str) -> list[dict]:
    path = PROCESSED / name
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def num(row: dict, key: str, default=None):
    raw = row.get(key, "")
    if raw in ("", None):
        return default
    if raw in ("True", "False"):
        return raw == "True"
    try:
        if "." in str(raw):
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def main() -> None:
    inventory = read_csv("fact_inventory_planning.csv")
    metrics = read_csv("fact_forecast_metrics.csv")
    backtest = read_csv("fact_forecast_backtest.csv")
    categories = read_csv("dim_category.csv")
    census_rows = read_csv("fact_census_retail_nsa.csv")

    # Recent census only (2023+) to keep payload lean
    census_recent = [
        {
            "period": r["period"][:10],
            "category_id": r["category_id"],
            "category_name": r["category_name"],
            "sales_millions_nsa": num(r, "sales_millions_nsa"),
        }
        for r in census_rows
        if r["period"] >= "2023-01-01" and r.get("sales_millions_nsa") not in ("", None)
    ]

    backtest_by_cat: dict[str, list] = {}
    for row in backtest:
        cid = row["category_id"]
        backtest_by_cat.setdefault(cid, []).append(
            {
                "ds": row["ds"][:10],
                "actual": num(row, "actual"),
                "predicted": num(row, "predicted"),
            }
        )
    for pts in backtest_by_cat.values():
        pts.sort(key=lambda x: x["ds"])

    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "disclaimer": (
            "Illustrative planning on Google Trends search-interest proxy. "
            "Not Amazon warehouse units. Public data only."
        ),
        "companion_note": (
            "Interactive companion to the Power BI / DAX semantic model "
            "(dashboard/AmazonIQ.pbip)."
        ),
        "categories": [
            {
                "category_id": r["category_id"],
                "category_name": r["category_name"],
                "keyword": r["keyword"],
                "catalog_product_count": num(r, "catalog_product_count"),
                "baseline_mape_pct": num(r, "baseline_mape_pct"),
                "catalog_share_of_max": num(r, "catalog_share_of_max"),
            }
            for r in categories
        ],
        "forecast_metrics": [
            {
                "category_id": r["category_id"],
                "category_name": r["category_name"],
                "keyword": r["keyword"],
                "mape_pct": num(r, "mape_pct"),
                "weak_accuracy_flag": num(r, "weak_accuracy_flag"),
                "weak_accuracy_reason": r.get("weak_accuracy_reason", ""),
            }
            for r in metrics
        ],
        "inventory_planning": [
            {
                "category_id": r["category_id"],
                "category_name": r["category_name"],
                "keyword": r["keyword"],
                "safety_stock": num(r, "safety_stock"),
                "reorder_point": num(r, "reorder_point"),
                "mape_pct_baseline": num(r, "mape_pct_baseline"),
                "uncertainty_tier": r["uncertainty_tier"],
                "high_uncertainty_flag": num(r, "high_uncertainty_flag"),
                "service_level_pct": num(r, "service_level_pct"),
                "lead_time_weeks": num(r, "lead_time_weeks"),
            }
            for r in inventory
        ],
        "forecast_backtest": backtest_by_cat,
        "census_recent": census_recent,
        "dq_highlights": [
            {
                "id": "DQ-001",
                "title": "Rejected India / INR Kaggle catalog",
                "detail": (
                    'The popular "Amazon Sales Dataset" is Amazon.in / INR, not a U.S. '
                    "sales time series. Rejected so U.S. Google Trends and Census "
                    "would not mix geographies."
                ),
                "severity": "reject",
            },
            {
                "id": "DQ-018",
                "title": "reviews = 0 on 79.3% of catalog rows",
                "detail": (
                    "On 1,426,337 products in SRC-KAGGLE-002, reviews is zero on "
                    "79.3% of rows. Stars often still populate. Column kept, labeled "
                    "unreliable — not treated as review count."
                ),
                "severity": "flag",
            },
            {
                "id": "DQ-022",
                "title": "Sennheiser HD 600 price drift",
                "detail": (
                    "ASIN B00004SY4H: Sep 2023 snapshot $299.95 vs live Amazon.com "
                    "$268.90 on 2026-08-17 (−10.4%). Snapshot kept; live check is "
                    "existence/drift only."
                ),
                "severity": "flag",
            },
            {
                "id": "DQ-023",
                "title": "Galison identifier redirect",
                "detail": (
                    "Snapshot 0735372888 (Flower Market puzzle) redirects on live "
                    "Amazon.com to 0735388059 (Blooming Meadow — different product). "
                    "Snapshot row kept as-is."
                ),
                "severity": "flag",
            },
            {
                "id": "DQ-025",
                "title": "26.4× catalog imbalance (garden vs clothing)",
                "detail": (
                    "Mapped garden catalog: 5,345 products vs clothing 141,291. "
                    "Equal 500-row samples hide parity. Dashboard shows raw mapped counts."
                ),
                "severity": "flag",
            },
        ],
    }

    content = (
        "/* Generated by src/build_web_data.py — do not edit by hand */\n"
        f"window.AMAZONIQ_DATA = {json.dumps(payload, indent=2)};\n"
    )
    for out in OUT_PATHS:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")
        print(f"Wrote {out} ({out.stat().st_size:,} bytes)")

    for name in WEB_STATIC:
        src = WEB_SRC / name
        dst = DOCS / name
        shutil.copy2(src, dst)
        print(f"Synced {src} -> {dst}")

    nojekyll = DOCS / ".nojekyll"
    if not nojekyll.exists():
        nojekyll.write_text("", encoding="utf-8")
        print(f"Created {nojekyll}")


if __name__ == "__main__":
    main()
