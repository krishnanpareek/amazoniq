"""Print coverage, zeros, peaks, and holiday-window values. Does not alter data."""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "processed" / "fact_search_interest.csv"

rows = list(csv.DictReader(PATH.open(encoding="utf-8")))
by_cat: dict[str, list[dict[str, str]]] = defaultdict(list)
for row in rows:
    by_cat[row["category_id"]].append(row)

print("category,keyword,n,min_week,max_week,zeros,partials,min,max,peak_week")
for cat_id, items in by_cat.items():
    items.sort(key=lambda r: r["week_start"])
    interests = [int(r["interest"]) for r in items if r["interest"] != ""]
    zeros = sum(1 for v in interests if v == 0)
    partials = sum(1 for r in items if r["is_partial"].lower() == "true")
    peak = max(items, key=lambda r: int(r["interest"] or -1))
    print(
        f"{cat_id},{items[0]['keyword']},{len(items)},{items[0]['week_start']},{items[-1]['week_start']},"
        f"{zeros},{partials},{min(interests)},{max(interests)},{peak['week_start']}"
    )

print("\n# December weeks (toys / headphones / air fryer seasonality check)")
for cat_id in ("toys", "electronics", "home_kitchen", "garden"):
    dec = [r for r in by_cat[cat_id] if r["week_start"][5:7] == "12"]
    dec.sort(key=lambda r: int(r["interest"] or 0), reverse=True)
    top = ", ".join(f"{r['week_start']}={r['interest']}" for r in dec[:3])
    print(f"{cat_id} top Dec: {top}")

print("\n# April-June weeks (lawn mower seasonality check)")
garden = [r for r in by_cat["garden"] if r["week_start"][5:7] in {"04", "05", "06"}]
garden.sort(key=lambda r: int(r["interest"] or 0), reverse=True)
print("garden top spring:", ", ".join(f"{r['week_start']}={r['interest']}" for r in garden[:5]))

print("\n# Spot-check candidates (first week, a mid week, peak, latest complete)")
for cat_id, items in by_cat.items():
    items.sort(key=lambda r: r["week_start"])
    complete = [r for r in items if r["is_partial"].lower() != "true"]
    peak = max(items, key=lambda r: int(r["interest"] or -1))
    mid = items[len(items) // 2]
    print(
        f"{cat_id}: first {items[0]['week_start']}={items[0]['interest']}; "
        f"mid {mid['week_start']}={mid['interest']}; "
        f"peak {peak['week_start']}={peak['interest']}; "
        f"last_complete {complete[-1]['week_start']}={complete[-1]['interest']}"
    )
