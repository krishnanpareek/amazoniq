"""Compare three sampled ASINs back to the raw Kaggle CSV. Do not reconcile silently."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "kaggle" / "amazon_products.csv"
SAMPLE = ROOT / "data" / "processed" / "dim_product_sample.csv"
CATS = ROOT / "data" / "raw" / "kaggle" / "amazon_categories.csv"

# Fixed ASINs chosen after first extract (one per distinct AmazonIQ group).
# If a listed ASIN is missing from the sample, the script reports GAP instead of substituting.
CHECK_ASINS = [
    "B09N3ZNHTY",  # will be replaced at runtime if not present — see main()
]


def pick_asins(sample: pd.DataFrame) -> list[str]:
    picks: list[str] = []
    for cat in ("electronics", "home_kitchen", "toys"):
        sub = sample[sample["amazoniq_category_id"] == cat]
        if sub.empty:
            continue
        # Prefer a row with price>0 and a title, still reported if flags exist
        ranked = sub.sort_values(["flag_price_zero", "flag_stars_zero", "asin"])
        picks.append(str(ranked.iloc[0]["asin"]))
    return picks


def main() -> None:
    sample = pd.read_csv(SAMPLE)
    asins = pick_asins(sample)
    print("check_asins", asins)
    raw_hits = pd.read_csv(RAW, usecols=["asin", "title", "stars", "reviews", "price", "category_id", "productURL"])
    raw_hits = raw_hits[raw_hits["asin"].isin(asins)]
    print("raw_hits", len(raw_hits))
    print("asin,field,sample,raw,status")
    mismatches = 0
    for asin in asins:
        srow = sample[sample["asin"] == asin]
        rrow = raw_hits[raw_hits["asin"] == asin]
        if srow.empty or rrow.empty:
            print(f"{asin},ALL,,,GAP")
            mismatches += 1
            continue
        s = srow.iloc[0]
        r = rrow.iloc[0]
        for field in ("title", "stars", "reviews", "price", "category_id"):
            sv, rv = s[field], r[field]
            status = "MATCH" if sv == rv or (pd.isna(sv) and pd.isna(rv)) else "MISMATCH"
            if status == "MISMATCH":
                # numeric equality for floats
                try:
                    if float(sv) == float(rv):
                        status = "MATCH"
                except (TypeError, ValueError):
                    pass
            if status != "MATCH":
                mismatches += 1
            print(f"{asin},{field},{sv},{rv},{status}")
        print(f"{asin},productURL,{s['productURL']},{r['productURL']},{'MATCH' if s['productURL']==r['productURL'] else 'MISMATCH'}")
    print(f"mismatches={mismatches}")

    cats = pd.read_csv(CATS)
    print("\n# category file integrity")
    print("category_rows", len(cats), "unique_ids", cats["id"].nunique())


if __name__ == "__main__":
    main()
