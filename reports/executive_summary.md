# Executive Summary

**Project:** AmazonIQ — E-Commerce Demand Forecasting & Inventory Planning  
**Deliverable:** Power BI Project (`dashboard/AmazonIQ.pbip`) with TMDL semantic model and real DAX measures  
**Data:** Public sources only (Kaggle 2023 Amazon.com-style catalog snapshot, Google Trends US, U.S. Census Monthly Retail Trade)  
**Audience:** Demand planning, inventory, supply chain, operations, and business analyst roles

## The differentiator: data-quality catches (Phase 2)

This writeup leads with what usually gets hidden. Every catch below is logged in [`docs/data_quality_log.md`](../docs/data_quality_log.md) with a source ID, a before/after or exact count, and a resolution that is **keep / reject / flag** — not silent interpolation.

| Catch | What we found | What we did |
|-------|----------------|-------------|
| **Wrong geography (DQ-001)** | The popular Kaggle “Amazon Sales Dataset” is Amazon.in / INR, not a U.S. sales time series. | **Rejected** as primary catalog. Pairing it with U.S. Trends and U.S. Census would mix marketplaces. |
| **`reviews` is not review count (DQ-018)** | `reviews` is 0 on **79.3%** of 1,426,337 products (garden sample 99.6%). Stars still populate on most rows. | Kept the column, labeled unreliable. Prefer `stars` / `boughtInLastMonth`. Did not fill from live Amazon. |
| **Snapshot ≠ live price (DQ-022)** | Sennheiser HD 600 (`B00004SY4H`): CSV **$299.95** (Sep 2023) vs live Amazon.com **$268.90** on 2026-08-17 (−10.4%). Stars still 4.7. | Kept snapshot values. Live check is existence/drift only. |
| **ASIN redirect (DQ-023)** | Galison identifier `0735372888` (Flower Market puzzle, $16.99) **redirects** on live Amazon.com to `0735388059` (Blooming Meadow — a different product). | Kept the snapshot row. Did not replace with the redirected ASIN. |
| **Catalog imbalance (DQ-019 / DQ-025)** | No “Patio, Lawn & Garden” browse node. Analogical leaf map totals **5,345** garden products vs **141,291** clothing — **26.4×**. Equal 500-row samples hide that. | Locked the analogical map. Dashboard shows **raw** mapped counts (or share of max). Never imply category parity. |
| **FRED table vs series (DQ-009)** | A FRED *release-table* HTML snippet disagreed with FRED series pages/CSVs (e.g. May 2026 furniture 11,519 vs 11,508). Census xlsx vs FRED CSV: **18/18** match (`DQ-008`). | Cite series page + CSV, not the release-table HTML. Primary fact is the Census workbook. |
| **Atypical Trends peaks (DQ-011–013)** | `headphones` hits 100 on week **2026-04-12** (not December). `vitamins` hits 100 on **2026-07-12**. Shared April peak with `running shoes` / `lawn mower`. | **Kept as reported.** No smoothing. Flagged for MAPE. |

Those catches are the interview story. The model and DAX sit on top of them.

## Problem

Demand-planning portfolios often treat a Kaggle “Amazon sales” file as units sold, then drop weak categories and paste inventory formulas into Power BI as columns. Recruiters cannot tell whether the builder can (1) refuse a geographically wrong source, (2) backtest a forecast and **show** MAPE, or (3) implement safety stock as DAX rather than a spreadsheet pass-through.

AmazonIQ is scoped to the **problem setting** of multi-category e-commerce planning. It is **not** an Amazon product, not Seller Central, and not warehouse units.

## Approach

1. Inventory public sources with URL, access date, and limitations (`docs/source_inventory.md`).
2. Cross-check ≥3 points per source against the original (Census vs FRED, Trends vs UI, Kaggle sample vs raw CSV + three live listing URLs).
3. Forecast **Google Trends search interest** (0–100 index) with Prophet; 26-week holdout MAPE per category; weak accuracy flagged, not dropped.
4. Convert backtest error into illustrative inventory measures at a **stated 95% service level** and **2-week lead time**, using a **custom MAPE-adjusted safety stock** (not the classical textbook formula).
5. Implement those measures as DAX in a Power BI semantic model (`_Metrics`), with modeled vs stored pairs for audit.

Census MRTS is a **seasonality sanity-check** series (U.S. retail sales by kind of business). It is not the forecast input and not Amazon GMV.

## What the numbers actually are

**Forecast target:** weekly U.S. Google Trends interest for one keyword per category (`headphones`, `air fryer`, `running shoes`, `vitamins`, `lawn mower`, `toys`). Not orders, not units, not Amazon rank.

**Prophet 26-week holdout MAPE** (complete weeks 2026-02-15 through 2026-08-09):

| Category | MAPE | Uncertainty (inventory) |
|----------|------|-------------------------|
| Health & Personal Care | 14.5% | Standard |
| Toys & Games | 16.7% | Elevated |
| Patio, Lawn & Garden | 18.9% | Elevated |
| Home & Kitchen | 19.6% | Elevated |
| Electronics | 30.2% | **High** |
| Clothing & Accessories | 40.0% | **High** |

Clothing and Electronics are the weakest. Both share the April 2026 interest spike that Prophet treats as out-of-pattern (`DQ-011` / `DQ-012`). That is a finding, not a reason to drop them.

**Custom safety stock** (search-interest index units, illustrative):

```
σ_adjusted = σ_backtest × (1 + MAPE% / 100)
safety_stock = 1.645 × σ_adjusted × √2
```

Same 95% service level for all six categories; **different buffers**. Clothing SS **77.4** vs Health **26.3**. Independently recomputed: DAX `Safety Stock (Modeled)` matches `Safety Stock (Stored)` for all six categories (within rounding).

Classical textbook SS would use demand-history σ and would **not** multiply by `(1 + MAPE/100)`. See [`docs/inventory_methodology.md`](../docs/inventory_methodology.md).

## Dashboard pages

| Page | Business question | Core DAX / facts |
|------|-------------------|------------------|
| Executive Overview | Where is forecast confidence high vs weak? | `Baseline MAPE`, `High Uncertainty Categories`, modeled SS / ROP |
| Forecast vs Actual | How does Prophet track holdout actuals? | Rolling actual vs predicted, `Rolling MAPE 4W` |
| Inventory Planning | Does DAX match the Python pipeline? | `Safety Stock (Modeled)` vs `(Stored)`, uncertainty table |
| Seasonality & Catalog Context | What do Trends, Census, and catalog depth show? | `Search Interest (Complete Weeks)`, `Census Sales YoY %`, **raw** `Catalog Product Count` (DQ-025) |

Open [`dashboard/AmazonIQ.pbip`](../dashboard/AmazonIQ.pbip) in Power BI Desktop (PBIR preview). How-to: [`dashboard/README.md`](../dashboard/README.md).

## Skills demonstrated (accurate framing)

- Public-source research and Tesla-style DQ logging (reject / keep / flag with exact values)
- Python extracts → analysis-ready fact tables (`data/processed/`)
- Prophet backtesting with MAPE by category; weak models shown
- Inventory math with **stated** service level and lead time; custom vs classical SS documented
- Power BI semantic model (TMDL) and **real DAX** (`SUMX`, `CALCULATE`, `SAMEPERIODLASTYEAR`) — not pass-through columns
- Metric labels: reported / calculated / estimated / modeled

**Not claimed:** Amazon affiliation, Seller Central, warehouse units, GMV, causal “search caused sales,” or that MAPE-adjusted SS is the industry-standard formula.

## Limitations (summary)

Search interest ≠ units sold. Kaggle is a Sep 2023 listing snapshot, not a sales history. Census NAICS kinds of business are analogical (e.g. toys → 451 sporting/hobby/book/music stores), all-channel retail, not Amazon browse nodes. Lead time is illustrative. Full list: [`docs/limitations.md`](../docs/limitations.md).

## How to review

1. Read this page, then [`docs/data_quality_log.md`](../docs/data_quality_log.md) for DQ-001, DQ-018, DQ-022, DQ-023, DQ-025.
2. Open `dashboard/AmazonIQ.pbip`, refresh, compare `Safety Stock (Modeled)` vs `Safety Stock (Stored)`.
3. Cross-check headline MAPE and SS against `data/processed/fact_forecast_metrics.csv` and `fact_inventory_planning.csv`.
4. Confirm garden vs clothing catalog counts on the Seasonality page (5,345 vs 141,291).
