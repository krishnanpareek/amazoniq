# Source inventory

Traceability log for every externally sourced dataset in this project.

**Rules:** Every externally sourced number must map to a `Source_ID` below (URL, publication/update context, reporting period). If a field cannot be verified yet, it is marked **MANUAL LOCATE**. Do not invent values. Access date for this inventory pass: **2026-08-17**.

**Metric labels used later in facts:** reported | calculated | estimated | modeled.

**Phase 1 status:** Landing-page URLs verified. Files **not** downloaded. Category confirmation required before Phase 2 extracts.

---

## Column definitions

| Column | Meaning |
|--------|---------|
| Source_ID | Stable project key |
| Dataset_Name | Human-readable dataset name |
| Organization | Publishing organization |
| Source_URL | Verified landing or download URL |
| Reporting_Period | Time coverage of the data |
| Data_Definition | What the dataset represents |
| Primary/Secondary | Primary = core fact input; Secondary = supporting/context |
| Status | `URL verified` / `pending download` / `rejected` / `MANUAL LOCATE required` |

---

## SRC-KAGGLE-001 — Classic “Amazon Sales Dataset” (rejected as primary catalog)

| Field | Value |
|-------|-------|
| Source_ID | SRC-KAGGLE-001 |
| Dataset_Name | Amazon Sales Dataset |
| Organization | Kaggle user karkavelrajaj (community upload of Amazon.in listing snapshot) |
| Source_URL | https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset |
| Reporting_Period | Point-in-time product snapshot (not a panel) |
| Data_Fields | product_id, product_name, category, discounted_price, actual_price, discount_percentage, rating, rating_count, reviews, product_link |
| Data_Definition | ~1K+ Amazon.in product listings with price, rating, and review counts. Category is a breadcrumb string (e.g. `Electronics\|WearableTechnology\|SmartWatches`). |
| Primary/Secondary | Rejected as primary catalog |
| Access_Date | 2026-08-17 |
| Reliability_Notes | Widely used in tutorials. Prices are INR. Marketplace is India. Category mix is concentrated in Electronics, Computers & Accessories, and Home & Kitchen. |
| Limitations | Not U.S. catalog. Not a sales time series. Pairing with U.S. Census / U.S. Trends would mix geographies. |
| Status | URL verified. **Rejected as primary catalog** (confirmed Phase 1). Kept as a documented reject. |

## SRC-KAGGLE-002 — Amazon.com product catalog snapshot (proposed primary)

| Field | Value |
|-------|-------|
| Source_ID | SRC-KAGGLE-002 |
| Dataset_Name | Amazon Products Dataset 2023 (1.4M Products) |
| Organization | Kaggle user asaniczka (community upload; Amazon.com-oriented listing snapshot, Sep 2023) |
| Source_URL | https://www.kaggle.com/datasets/asaniczka/amazon-products-dataset-2023-1-4m-products |
| Reporting_Period | Snapshot dated Sep 2023 by the uploader |
| Data_Fields | asin, title, imgUrl, productURL, stars, reviews, price, listPrice, category_id, isBestSeller, boughtInLastMonth |
| Data_Definition | Large Amazon.com-style product catalog used **only** for category structure and listing attributes. Not treated as a sales history. |
| Primary/Secondary | Primary → `Dim_Product` / `Dim_Category` (sampled) |
| Access_Date | 2026-08-17 |
| Reliability_Notes | Downloaded 2026-08-17. File sizes match Kaggle listing. `reviews` is 0 on 79.3% of rows (`DQ-018`). Prices are a Sep 2023 snapshot (`DQ-022`). |
| Limitations | Still a snapshot, not units sold. Leaf browse nodes, not six store departments. Garden has no matching node (`DQ-019`). Not Amazon-internal data. |
| Status | Downloaded and sampled. Spot-checked vs raw CSV and three live Amazon URLs (`DQ-017`–`DQ-024`). |

## SRC-TRENDS-001 — Google Trends search interest

| Field | Value |
|-------|-------|
| Source_ID | SRC-TRENDS-001 |
| Dataset_Name | Google Trends interest over time |
| Organization | Google Trends |
| Source_URL | https://trends.google.com/trends/ |
| Access method (planned) | `pytrends` and/or manual CSV export from the Trends UI (both must reconcile) |
| Reporting_Period | Proposed: last 5 years, weekly, geo=US |
| Data_Fields | date, keyword, interest (0–100 index) |
| Data_Definition | Relative search interest for a keyword in the United States. Scaled by Google within the requested window. |
| Primary/Secondary | Primary forecasting signal → `Fact_Search_Interest` |
| Access_Date | 2026-08-17 |
| Reliability_Notes | Index is relative, not absolute volume. Sampling can differ slightly between API and UI pulls — Phase 2 will cross-check ≥3 weeks per keyword against the Trends UI. |
| Limitations | Not orders. Not Amazon search rank. Keyword choice affects the series. Google may throttle automated pulls. |
| Status | URL verified. Pulled 2026-08-17 via pytrends; reconciled to Trends UI for toys, headphones, and lawn mower (`DQ-010`–`DQ-015`). |

## SRC-CENSUS-001 — Monthly Retail Trade Survey (category retail sales)

| Field | Value |
|-------|-------|
| Source_ID | SRC-CENSUS-001 |
| Dataset_Name | Monthly Retail Trade — sales time series by kind of business |
| Organization | U.S. Census Bureau |
| Source_URL | https://www.census.gov/retail/marts/www/timeseries.html |
| Related landing | https://www.census.gov/retail/sales.html |
| Reporting_Period | Monthly, 1992–present (project will use a recent multi-year window aligned to Trends) |
| Data_Fields | year-month, kind of business (NAICS), sales (seasonally adjusted and not adjusted) |
| Data_Definition | Estimated U.S. retail sales for employer firms by kind of business. Includes store and nonstore channels. Not Amazon-only. |
| Primary/Secondary | Primary seasonality sanity check → `Fact_Census_Retail` |
| Access_Date | 2026-08-17 |
| Reliability_Notes | Official statistical release. Landing page verified 2026-08-17. Advance vs final monthly estimates revise. Prefer not-seasonally-adjusted series when comparing raw seasonality to Trends. |
| Limitations | Kind-of-business ≠ Amazon browse node. Not e-commerce-only at this grain. |
| Status | URL verified. Downloaded 2026-08-17 (`mrtssales92-present.xlsx`). Spot-checked vs FRED CSVs and series pages (`DQ-006`–`DQ-009`). |

## SRC-CENSUS-002 — Quarterly retail e-commerce (aggregate context)

| Field | Value |
|-------|-------|
| Source_ID | SRC-CENSUS-002 |
| Dataset_Name | Quarterly Retail E-Commerce Sales |
| Organization | U.S. Census Bureau |
| Source_URL | https://www.census.gov/retail/ecommerce.html |
| Reporting_Period | Quarterly |
| Data_Definition | Estimate of total U.S. retail e-commerce sales (and share of total retail). |
| Primary/Secondary | Secondary context KPI only |
| Access_Date | 2026-08-17 |
| Reliability_Notes | Official release. Category breakouts are **not** the published grain of this report. |
| Limitations | Cannot sanity-check category seasonality by itself. |
| Status | URL verified. Optional Phase 2 pull for a single total-e-commerce context series. |

## SRC-BLS-001 — Not used as a demand series

| Field | Value |
|-------|-------|
| Source_ID | SRC-BLS-001 |
| Dataset_Name | BLS CPI / PPI (price indexes) |
| Organization | U.S. Bureau of Labor Statistics |
| Source_URL | https://www.bls.gov/ |
| Data_Definition | Price indexes, not unit demand or retail sales. |
| Primary/Secondary | Out of scope unless a later phase needs a price deflator |
| Status | Reviewed. **Not a substitute** for Census category sales. Documented so the “Census / BLS” brief is answered explicitly. |
