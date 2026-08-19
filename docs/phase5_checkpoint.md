# Phase 5 checkpoint — pause for review

**Status:** Complete. Power BI Project (PBIP) with TMDL semantic model, `_Metrics` DAX measures, and four report pages.

## Deliverable

Open [`dashboard/AmazonIQ.pbip`](../dashboard/AmazonIQ.pbip) in Power BI Desktop.

| Artifact | Path |
|----------|------|
| PBIP root | `dashboard/AmazonIQ.pbip` |
| Semantic model (TMDL) | `dashboard/AmazonIQ.SemanticModel/` |
| Report (PBIR) | `dashboard/AmazonIQ.Report/definition/` |
| DAX source of truth | `dashboard/AmazonIQ.SemanticModel/definition/tables/_Metrics.tmdl` |
| Build script | `src/build_pbip_model.py` |

## Star schema

| Table | Role |
|-------|------|
| `DimCategory` | 6 categories — keyword, Census NAICS, catalog counts, baseline MAPE |
| `FactSearchInterest` | Weekly Google Trends index (partial weeks flagged) |
| `FactRollingForecastError` | Holdout actual vs predicted + 4-week rolling MAPE |
| `FactInventoryPlanning` | ROP, safety stock, uncertainty tier, MAPE multiplier |
| `FactForecastMetrics` | Phase 3 holdout MAPE per category |
| `FactCensusRetail` | Monthly MRTS sales (2021+, NSA) — seasonality context only |
| `_Metrics` | **All dashboard measures (DAX)** |

Relationships: every fact → `DimCategory[category_id]`.

## Real DAX measures (not pass-through)

| Measure | Purpose |
|---------|---------|
| `Safety Stock (Modeled)` | Recomputes custom MAPE-adjusted formula in DAX |
| `Safety Stock (Stored)` | Sum from Python pipeline — should match Modeled |
| `Reorder Point (Modeled)` | demand during lead time + modeled SS |
| `Reorder Point (Stored)` | Sum from pipeline |
| `Baseline MAPE` | Phase 3 holdout average |
| `Rolling MAPE 4W` | Backtest rolling error |
| `High Uncertainty Categories` | Count where MAPE ≥ 25% |
| `High Uncertainty Label` | Card/table label for flagged categories |
| `Catalog Product Count` | Raw Kaggle mapped counts (DQ-025) |
| `Catalog Share of Max` | Normalized catalog depth |
| `Search Interest (Complete Weeks)` | Trends index excluding partial weeks |
| `Census Retail Sales (M USD)` | MRTS context series |
| `Census Sales YoY %` | YoY on selected Census period |

Assumption measures: `Service Level Assumption` (95%), `Z Score (95%)` (1.645), `Lead Time Weeks` (2).

## Custom vs classical safety stock

Documented in [`inventory_methodology.md`](inventory_methodology.md) § *Custom MAPE-adjusted formula vs classical safety stock*. Dashboard uses the **custom** approach; `Safety Stock (Modeled)` lets reviewers verify the formula in the semantic model.

## Report pages

1. **Executive Overview** — KPI cards + MAPE bar + ROP/SS by category  
2. **Forecast vs Actual** — actual vs predicted lines + rolling MAPE  
3. **Inventory Planning** — modeled vs stored SS/ROP + uncertainty table  
4. **Seasonality & Catalog Context** — Trends seasonality, Census sales, **raw catalog counts**

## DQ-025 compliance

Garden (5,345 products) vs Clothing (141,291) = **26.4×** imbalance. Seasonality page shows **raw** `Catalog Product Count` and `Catalog Share of Max`. Report annotation `catalogParityNote` in `report.json` records the rule.

## Stated assumptions (unchanged from Phase 4)

- **95% service level** (z = 1.645)  
- **2-week illustrative lead time**  
- Demand proxy = Google Trends search interest  
- Not Amazon warehouse units  

## Closed 2026-08-17

User independently recomputed `Safety Stock (Modeled)` by hand against `fact_inventory_planning.csv`. Matches `Safety Stock (Stored)` for all six categories (within rounding). Phase 6 writeup: [`phase6_checkpoint.md`](phase6_checkpoint.md).
