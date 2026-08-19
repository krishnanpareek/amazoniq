"""Sample SRC-KAGGLE-002 into category and product tables.

Does not interpolate. Zero prices, zero stars, and zero reviews stay in the file
with explicit flags. Garden mapping is analogical (see category_config).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from category_config import CATEGORIES, SAMPLE_PER_CATEGORY, SAMPLE_SEED  # noqa: E402

RAW_CATS = ROOT / "data" / "raw" / "kaggle" / "amazon_categories.csv"
RAW_PRODS = ROOT / "data" / "raw" / "kaggle" / "amazon_products.csv"
OUT_DIM = ROOT / "data" / "processed" / "dim_catalog_category.csv"
OUT_SAMPLE = ROOT / "data" / "processed" / "dim_product_sample.csv"
OUT_COUNTS = ROOT / "data" / "processed" / "fact_catalog_category_counts.csv"

ID_TO_AMAZONIQ = {}
for cat in CATEGORIES:
    for leaf_id in cat["catalog_category_ids"]:
        ID_TO_AMAZONIQ[int(leaf_id)] = cat


def main() -> None:
    cats = pd.read_csv(RAW_CATS)
    wanted = set(ID_TO_AMAZONIQ)
    frames: list[pd.DataFrame] = []
    leaf_counts: dict[int, int] = {i: 0 for i in wanted}

    usecols = [
        "asin",
        "title",
        "productURL",
        "stars",
        "reviews",
        "price",
        "listPrice",
        "category_id",
        "isBestSeller",
        "boughtInLastMonth",
    ]
    for chunk in pd.read_csv(RAW_PRODS, usecols=usecols, chunksize=200000):
        sub = chunk[chunk["category_id"].isin(wanted)].copy()
        if sub.empty:
            continue
        vc = sub["category_id"].value_counts()
        for cid, n in vc.items():
            leaf_counts[int(cid)] += int(n)
        frames.append(sub)

    mapped = pd.concat(frames, ignore_index=True)
    mapped["category_id"] = mapped["category_id"].astype(int)
    mapped["amazoniq_category_id"] = mapped["category_id"].map(lambda i: ID_TO_AMAZONIQ[int(i)]["category_id"])
    mapped["amazoniq_category_name"] = mapped["category_id"].map(lambda i: ID_TO_AMAZONIQ[int(i)]["name"])
    mapped["source_leaf_name"] = mapped["category_id"].map(
        dict(zip(cats["id"].astype(int), cats["category_name"]))
    )
    mapped["flag_reviews_zero"] = mapped["reviews"] == 0
    mapped["flag_price_zero"] = mapped["price"] == 0
    mapped["flag_stars_zero"] = mapped["stars"] == 0
    mapped["source_id"] = "SRC-KAGGLE-002"
    mapped["source_file"] = RAW_PRODS.name

    parts = []
    for _, group in mapped.groupby("amazoniq_category_id"):
        parts.append(group.sample(n=min(SAMPLE_PER_CATEGORY, len(group)), random_state=SAMPLE_SEED))
    samples = pd.concat(parts, ignore_index=True)

    dim_rows = []
    for cat in CATEGORIES:
        for leaf_id in cat["catalog_category_ids"]:
            name = cats.loc[cats["id"] == leaf_id, "category_name"]
            dim_rows.append(
                {
                    "amazoniq_category_id": cat["category_id"],
                    "amazoniq_category_name": cat["name"],
                    "source_category_id": leaf_id,
                    "source_category_name": name.iloc[0] if len(name) else None,
                    "mapping_note": (
                        "analogical — no Patio/Lawn & Garden browse node"
                        if cat["category_id"] == "garden"
                        else "leaf node rolled to AmazonIQ category"
                    ),
                    "source_id": "SRC-KAGGLE-002",
                }
            )
    dim = pd.DataFrame(dim_rows)

    counts = dim.copy()
    counts["product_count_full"] = counts["source_category_id"].map(leaf_counts)
    counts["product_count_full"] = counts["product_count_full"].fillna(0).astype(int)

    OUT_DIM.parent.mkdir(parents=True, exist_ok=True)
    dim.to_csv(OUT_DIM, index=False)
    samples.to_csv(OUT_SAMPLE, index=False)
    counts.to_csv(OUT_COUNTS, index=False)

    print(f"mapped_products {len(mapped)}")
    print(f"sample_products {len(samples)} -> {OUT_SAMPLE}")
    print(samples.groupby("amazoniq_category_id").size().to_string())
    print("\n# full mapped counts by AmazonIQ category")
    print(mapped.groupby("amazoniq_category_id").size().to_string())
    print("\n# sample quality flags")
    print(
        samples.groupby("amazoniq_category_id")[["flag_reviews_zero", "flag_price_zero", "flag_stars_zero"]]
        .mean()
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    main()
