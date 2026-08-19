# AmazonIQ — E-Commerce Demand Forecasting & Inventory Planning

Public-data portfolio project that forecasts **category-level demand** for Amazon-style e-commerce merchandise groups, then turns those forecasts into inventory planning measures (reorder point, safety stock, rolling forecast error) in a Power BI model.

**Audience:** Demand Planning Analyst, Inventory Analyst, Supply Chain Analyst, Operations Analyst, and Business Analyst roles.

**Primary deliverable:** A Power BI Project in [`dashboard/AmazonIQ.pbip`](dashboard/AmazonIQ.pbip) with real DAX measures — not pass-through columns. **Interactive companion:** [`dashboard/web/index.html`](dashboard/web/index.html) (shareable HTML/CSS/JS). Recruiter writeup: [`reports/executive_summary.md`](reports/executive_summary.md).

**What this is not:** Not an Amazon product, not an Amazon-internal tool, and not a claim of access to Amazon Seller Central, retail forecasts, warehouse inventory, or any non-public Amazon system. The name “AmazonIQ” describes the *problem setting* (multi-category e-commerce demand planning). It does **not** imply affiliation, endorsement, or official data access.

**Data policy:** Only verifiable public sources (Kaggle product-catalog snapshot, Google Trends search interest, U.S. Census Bureau Monthly Retail Trade / related public retail series). No scraped live Amazon pages. No fabricated values. Metrics will be labeled **reported**, **calculated**, **estimated**, or **modeled**. Every externally sourced number must map to a row in [`docs/source_inventory.md`](docs/source_inventory.md).

## Current status

**Phase 7 — Interactive web companion (approved).** GitHub Pages deploy from `/docs`. See [`docs/GITHUB_PAGES.md`](docs/GITHUB_PAGES.md).

## How the three sources are used

| Source | Role | What it is **not** |
|--------|------|--------------------|
| Kaggle Amazon-style product catalog | SKU / category structure, price, rating, review-count snapshot | Not a sales time series. Not Amazon-internal units or revenue. |
| Google Trends (U.S.) | Weekly search-interest time series — the actual forecasting signal | Not orders, not units sold, not Amazon search rank. |
| U.S. Census Monthly Retail Trade (MRTS) | Independent monthly retail-sales series by kind of business, used to sanity-check seasonality | Not Amazon category sales. Not e-commerce-only at the category grain. |

Census quarterly e-commerce estimates are mostly **aggregate** (total U.S. retail e-commerce). Category-level official time series come from MRTS kinds of business (all retail channels). That distinction is intentional and will stay labeled in the dashboard.

## Repository structure

```
data/raw/           Untouched source files (large files gitignored; URLs documented)
data/processed/     Cleaned fact / dimension tables (CSV)
notebooks/          Exploration, backtests, and model diagnostics
src/                Reproducible extract / transform / forecast scripts
dashboard/          Power BI PBIP + web companion (dashboard/web/)
docs/               Source inventory, limitations, category scope, data-quality log
reports/            Executive summary and portfolio talking points
```

## Portfolio materials

| File | Purpose |
|------|---------|
| [`reports/executive_summary.md`](reports/executive_summary.md) | Recruiter writeup (leads with Phase 2 data-quality catches) |
| [`reports/portfolio_materials.md`](reports/portfolio_materials.md) | Resume bullets, LinkedIn post, 2-minute interview script |
| [`docs/limitations.md`](docs/limitations.md) | What public data cannot answer |
| [`docs/data_quality_log.md`](docs/data_quality_log.md) | Source rejects, drift, and flags |

## Phases

| Phase | Focus | Gate |
|-------|-------|------|
| 1 | Repo setup + category confirmation | **Complete** |
| 2 | Pull, clean, and cross-check ≥3 points per source against the original | **Complete** — see [`docs/phase2_checkpoint.md`](docs/phase2_checkpoint.md) |
| 3 | Prophet forecasts; MAPE by category | **Complete** — see [`docs/phase3_checkpoint.md`](docs/phase3_checkpoint.md) |
| 4 | Reorder point, safety stock (95% service level, MAPE-adjusted), rolling error | **Complete** — see [`docs/phase4_checkpoint.md`](docs/phase4_checkpoint.md) |
| 5 | Power BI dashboard with real DAX | **Complete** — see [`docs/phase5_checkpoint.md`](docs/phase5_checkpoint.md) |
| 6 | Portfolio writeup + LinkedIn draft | **Complete** — see [`docs/phase6_checkpoint.md`](docs/phase6_checkpoint.md) |
| 7 | Interactive HTML companion (shareable link) | **Complete** — see [`docs/phase7_checkpoint.md`](docs/phase7_checkpoint.md) |

## License / disclaimer

Public data for educational and portfolio purposes only. This project does **not** claim access to Amazon internal systems, seller accounts, warehouse inventory, or confidential demand plans. Independent verification of headline figures against primary sources is encouraged.
