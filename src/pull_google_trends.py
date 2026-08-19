"""Pull weekly US Google Trends for confirmed keywords.

Each keyword is requested separately so scale is 0-100 within that keyword's window.
Do not drop weeks. Missing dates are written with interest=null and a note.
"""

from __future__ import annotations

import csv
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from category_config import CATEGORIES, TRENDS_GEO, TRENDS_TIMEFRAME  # noqa: E402

RAW_DIR = ROOT / "data" / "raw" / "google_trends"
OUT_CSV = ROOT / "data" / "processed" / "fact_search_interest.csv"


def pull_one(keyword: str):
    from pytrends.request import TrendReq

    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload([keyword], timeframe=TRENDS_TIMEFRAME, geo=TRENDS_GEO)
    df = pytrends.interest_over_time()
    if df is None or df.empty:
        raise RuntimeError(f"Empty Trends response for {keyword!r}")
    return df


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict[str, object]] = []
    for i, cat in enumerate(CATEGORIES):
        keyword = cat["trends_keyword"]
        print(f"pulling {keyword!r} ...")
        df = pull_one(keyword)
        raw_path = RAW_DIR / f"{cat['category_id']}_{keyword.replace(' ', '_')}.csv"
        df.to_csv(raw_path)
        print(f"  raw -> {raw_path} rows={len(df)}")
        for ts, row in df.iterrows():
            is_partial = bool(row.get("isPartial", False))
            all_rows.append(
                {
                    "week_start": ts.date().isoformat(),
                    "category_id": cat["category_id"],
                    "category_name": cat["name"],
                    "keyword": keyword,
                    "geo": TRENDS_GEO,
                    "timeframe": TRENDS_TIMEFRAME,
                    "interest": int(row[keyword]) if keyword in row else None,
                    "is_partial": is_partial,
                    "source_id": "SRC-TRENDS-001",
                    "source_file": raw_path.name,
                }
            )
        if i < len(CATEGORIES) - 1:
            time.sleep(8)
    fieldnames = list(all_rows[0].keys())
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"wrote {len(all_rows)} rows -> {OUT_CSV}")


if __name__ == "__main__":
    main()
