"""Inspect SRC-KAGGLE-002 structure and quality. Does not write a sample."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CATS = ROOT / "data" / "raw" / "kaggle" / "amazon_categories.csv"
PRODS = ROOT / "data" / "raw" / "kaggle" / "amazon_products.csv"

cats = pd.read_csv(CATS)
print("categories_rows", len(cats))
print("categories_cols", list(cats.columns))
print("category_id_min_max", cats["id"].min(), cats["id"].max())
print("duplicate_ids", int(cats["id"].duplicated().sum()))
print("duplicate_names", int(cats["category_name"].duplicated().sum()))

# Stream products — 1.4M rows, keep memory bounded
usecols = [
    "asin",
    "title",
    "stars",
    "reviews",
    "price",
    "listPrice",
    "category_id",
    "isBestSeller",
    "boughtInLastMonth",
]
print("\n# product dtypes / nulls (first 50k preview + full category counts)")
preview = pd.read_csv(PRODS, nrows=50000)
print("preview_cols", list(pd.read_csv(PRODS, nrows=0).columns))
print(preview[usecols].describe(include="all").transpose().to_string())
print("preview_reviews_eq_0", int((preview["reviews"] == 0).sum()), "/", len(preview))
print("preview_price_eq_0", int((preview["price"] == 0).sum()), "/", len(preview))
print("preview_stars_eq_0", int((preview["stars"] == 0).sum()), "/", len(preview))

counts: Counter[int] = Counter()
reviews_zero = 0
price_zero = 0
stars_zero = 0
n = 0
dup_asin: Counter[str] = Counter()
for chunk in pd.read_csv(PRODS, usecols=["asin", "stars", "reviews", "price", "category_id"], chunksize=200000):
    n += len(chunk)
    counts.update(chunk["category_id"].tolist())
    reviews_zero += int((chunk["reviews"] == 0).sum())
    price_zero += int((chunk["price"] == 0).sum())
    stars_zero += int((chunk["stars"] == 0).sum())
    dup_asin.update(chunk["asin"].tolist())

print("\n# full file")
print("product_rows", n)
print("reviews_eq_0", reviews_zero, f"({reviews_zero/n:.1%})")
print("price_eq_0", price_zero, f"({price_zero/n:.1%})")
print("stars_eq_0", stars_zero, f"({stars_zero/n:.1%})")
print("duplicate_asins", sum(1 for a, c in dup_asin.items() if c > 1))

cat_name = dict(zip(cats["id"], cats["category_name"]))
print("\n# top 15 categories by product count")
for cid, c in counts.most_common(15):
    print(f"{cid}\t{c}\t{cat_name.get(cid, 'UNKNOWN')}")

print("\n# counts for candidate mapped ids")
watch = [45, 71, 110, 114, 116, 122, 131, 132, 135, 166, 170, 195, 199, 201, 215, 270]
for cid in watch:
    print(f"{cid}\t{counts.get(cid, 0)}\t{cat_name.get(cid, 'MISSING')}")
