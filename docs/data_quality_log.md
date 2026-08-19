# Data-quality log

Tesla-project style catch log. **Do not silently interpolate or drop data.**

## Pre-download findings (Phase 1, 2026-08-17)

| ID | Source | Finding | Resolution |
|----|--------|---------|------------|
| DQ-001 | SRC-KAGGLE-001 | Widely used “Amazon Sales Dataset” is Amazon.in / INR and is not a time series. Category mix is concentrated in three groups. | Rejected as primary catalog. Not paired with U.S. Census or U.S. Trends. |
| DQ-002 | SRC-CENSUS-002 | Quarterly e-commerce report is aggregate, not category-level. | Use MRTS kinds of business (SRC-CENSUS-001) for category seasonality. Quarterly e-commerce stays optional total-context only. |
| DQ-003 | SRC-BLS-001 | BLS CPI/PPI are prices, not retail unit demand. | Not used as the category demand series. |
| DQ-004 | SRC-CENSUS-001 | Toys and Sports share NAICS 451; Electronics and Computers share 443. | Confirmed Option A so each modeled category has a distinct Census series. |

## Phase 2 findings (2026-08-17)

| ID | Source | Finding | Resolution |
|----|--------|---------|------------|
| DQ-005 | SRC-KAGGLE-002 | No Kaggle API token on first attempt. | Resolved 2026-08-17 after token was added. Dataset downloaded. |
| DQ-006 | SRC-CENSUS-001 | June 2026 columns are labeled `(p)` preliminary in the Census workbook. | Kept. `preliminary_flag=True` on those rows. Not dropped. |
| DQ-007 | SRC-CENSUS-001 | NAICS 4422 / 44221 / 442299 cells are `(S)` suppressed. | Not used. Parent 442 is populated and is the scoped series. `(S)` was not filled. |
| DQ-008 | SRC-CENSUS-001 vs FRED | Census xlsx vs FRED CSV: 18/18 match on Dec 2024, Dec 2025, May 2026 for all six NAICS. FRED series pages match the same May/Jun 2026 electronics, furniture, and clothing values. | Accepted. Primary fact table is the Census workbook extract. |
| DQ-009 | FRED release-table HTML | A FRED *release table* snippet showed May 2026 furniture 11,519 / clothing 29,211 / health 39,718 / garden 47,449 / sporting 8,809. Series pages and CSVs show 11,508 / 29,282 / 39,686 / 47,565 / 8,764. | Treat the **series page + CSV** as the FRED number. Do not cite the release-table HTML. Likely a different vintage or a misread column in the table view. |
| DQ-010 | SRC-TRENDS-001 | First Trends UI request returned HTTP 429 after the pytrends batch. | Waited and retried. Later UI loads succeeded. Documented so a 429 is not mistaken for missing data. |
| DQ-011 | SRC-TRENDS-001 | `headphones` peaks at 100 on week 2026-04-12; December weeks are 45. Confirmed on the Trends UI and on a second pytrends pull. | **Kept as reported.** Unusual vs holiday electronics seasonality. Do not smooth. Flag for Phase 3 MAPE. |
| DQ-012 | SRC-TRENDS-001 | `headphones`, `running shoes`, and `lawn mower` all hit 100 on 2026-04-12. Lawn mower in April is expected. Headphones in April is not. Each series is independently scaled. | Kept. Shared peak week is a coincidence risk, not proof of a shared event. |
| DQ-013 | SRC-TRENDS-001 | `vitamins` peaks at 100 on 2026-07-12, not in January. Min interest is 48 (least volatile series). | Kept as reported. Flag for Phase 3. |
| DQ-014 | SRC-TRENDS-001 | Week 2026-08-16 is `isPartial=True` on all six series. | Kept and labeled. Not dropped. |
| DQ-015 | SRC-TRENDS-001 | Toys / headphones / lawn mower UI table values matched pytrends on every checked week (11 points). | Accepted for those keywords. Latest week for toys also matched (46). |
| DQ-016 | SRC-CENSUS-001 | Toys & Games maps to NAICS 451 (sporting goods, hobby, book, and music stores), not a toys-only monthly series. | Already scoped. Label in dashboard copy must stay “U.S. retail sales by kind of business,” not “toy store sales.” |
| DQ-017 | SRC-KAGGLE-002 | Local file sizes match the Kaggle listing exactly: categories 6,828 bytes; products 375,936,400 bytes. Product row count is 1,426,337 (uploader says “1.4M”). | Accepted. Use the exact row count, not the rounded marketing figure. |
| DQ-018 | SRC-KAGGLE-002 | `reviews` is 0 on **79.3%** of all 1,426,337 products (1,130,503 rows). Sample rates: garden 99.6%, health 89.8%, home_kitchen 90.4%, toys 80.0%, clothing 73.6%, electronics 55.6%. Stars are often still populated (only 9.2% stars=0). | **Kept.** Do not treat `reviews` as review count. Do not fill from live Amazon. Flag column as unreliable. Prefer `stars` and `boughtInLastMonth` for catalog attributes. |
| DQ-019 | SRC-KAGGLE-002 | No “Patio, Lawn & Garden” browse node. Closest leaves: Smart Home: Lawn and Garden (76 products), Outdoor Recreation (3,550), Tools & Home Improvement (1,719). Combined garden map is only **5,345** products vs **141,291** clothing — a **26.4×** catalog imbalance (141,291 ÷ 5,345). | **Accepted 2026-08-17.** Analogical map locked. See DQ-025 for sample/dashboard implications. |
| DQ-020 | SRC-KAGGLE-002 | Catalog is 248 leaf browse nodes, not six store departments. Electronics has no parent row; Headphones & Earbuds (71) has 9,242 products. | Explicit leaf rollup in `src/category_config.py`. Mapping is analogical. |
| DQ-021 | SRC-KAGGLE-002 | Three sampled ASINs match the raw CSV on title, stars, reviews, price, category_id, and productURL (0 mismatches). | Sample extract accepted against the source file. |
| DQ-022 | SRC-KAGGLE-002 vs live Amazon.com | **Sennheiser B00004SY4H price drift:** snapshot **$299.95** (Sep 2023 CSV) vs live Amazon.com **$268.90** on 2026-08-17 (−$31.05, −10.4%). Stars unchanged at **4.7**. Title drift: snapshot “Sennheiser HD 600 - Audiophile Hi-Res Open Back Dynamic Headphone, Black” vs live “Sennheiser HD600 Headphones \| Open-back design…”. Holmes B00006IV11: snapshot **$5.72** vs live **$7.99** (+$2.27); stars **4.0** both. | Snapshot prices are **not** current Amazon prices. Do not overwrite CSV values. Live check is existence/drift only. |
| DQ-023 | SRC-KAGGLE-002 vs live Amazon.com | **Galison ASIN redirect:** snapshot identifier **0735372888** — title “Galison Flower Market 1000 Piece Puzzle…”, price **$16.99**, stars **4.4**, category_id **227** (Puzzles). Live Amazon.com (2026-08-17) **redirected to 0735388059** — “Galison - Blooming Meadow 1000 Piece Jigsaw Puzzle…”, a different product. Not all `asin` values are B0-style ASINs. | Keep snapshot row **0735372888** as-is. Do not replace with redirected ASIN **0735388059**. |
| DQ-024 | SRC-KAGGLE-002 | `price` is 0 on 2.3% of products; `stars` is 0 on 9.2%. | Kept with flags. Not dropped. |
| DQ-025 | SRC-KAGGLE-002 | **Catalog sample-size imbalance:** full mapped counts are clothing **141,291** vs garden **5,345** (**26.4×**). Processed sample is **500 rows per AmazonIQ category** (equal by design) and therefore **does not** reflect catalog parity. | **Phase 5 requirement:** dashboard must show raw mapped product counts per category or normalize display explicitly. Do **not** imply equal category assortment depth. Re-flag at Phase 5. |

## Phase 3 findings (2026-08-17)

| ID | Source | Finding | Resolution |
|----|--------|---------|------------|
| DQ-026 | SRC-TRENDS-001 | April 2026 headphones spike (100 on 2026-04-12) and July 2026 vitamins spike (100 on 2026-07-12) confirmed kept by user. | Used as-is in Prophet backtest. No smoothing. |
| DQ-027 | SRC-TRENDS-001 | Prophet 26-week holdout MAPE: health **14.5%** (best), toys 16.7%, garden 18.9%, home_kitchen 19.6%, electronics **30.2%**, clothing **40.0%** (weakest). | Weak categories flagged in `fact_forecast_metrics.csv`. Clothing + electronics likely hurt by April 2026 shared peak (DQ-011/012). Not hidden. |
| DQ-028 | SRC-TRENDS-001 | Phase 4 safety stock uses **95% service level (z=1.645)** with **MAPE-adjusted σ**: `σ_adj = σ_backtest × (1 + MAPE/100)`. Not a uniform formula. Electronics SS **70.8** vs Health **26.3** at same service level. Clothing flagged **high uncertainty**. | Documented in `docs/inventory_methodology.md`. Assumptions explicit. |

## Phase 5 reminders (from Phase 2)

| ID | Reminder |
|----|----------|
| DQ-025 | Dashboard must show raw catalog counts or normalize — **26.4×** garden vs clothing imbalance. See `dashboard/phase5_display_rules.md`. |
