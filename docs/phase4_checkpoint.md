# Phase 4 checkpoint — pause for review

**Status:** Complete. Inventory measures are modeled on Google Trends search interest, not warehouse units.

## Stated default: 95% service level

Documented in [`inventory_methodology.md`](inventory_methodology.md):

- **Service level:** 95%
- **z-score:** 1.645 (one-sided normal)
- **Lead time:** 2 weeks (estimated, illustrative)
- **Demand proxy:** last 4 weeks of actual search interest

## MAPE-adjusted safety stock (not uniform)

Each category uses its own backtest forecast-error σ, then:

`σ_adjusted = σ_backtest × (1 + MAPE% / 100)`

`safety_stock = 1.645 × σ_adjusted × √2`

| Category | MAPE | σ multiplier | Safety stock | Reorder point | Uncertainty |
|----------|------|--------------|--------------|---------------|-------------|
| Health & Personal Care | 14.5% | 1.145× | 26.3 | 155.3 | Standard |
| Toys & Games | 16.7% | 1.167× | 20.9 | 112.9 | Elevated |
| Patio, Lawn & Garden | 18.9% | 1.189× | 32.2 | 135.2 | Elevated |
| Home & Kitchen | 19.6% | 1.196× | 33.5 | 142.5 | Elevated |
| Electronics | 30.2% | 1.302× | **70.8** | 132.8 | **High** |
| Clothing & Accessories | 40.0% | 1.400× | **77.4** | 131.4 | **High** |

Electronics and Clothing get the **widest buffers** and `high_uncertainty_flag=True`. Health gets the narrowest buffer at the same 95% service level because its MAPE is lowest.

## Outputs

| File | Rows | Purpose |
|------|------|---------|
| `fact_inventory_planning.csv` | 6 | Category ROP / safety stock / uncertainty tier |
| `fact_rolling_forecast_error.csv` | 156 | Weekly actual vs predicted + 4-week rolling MAPE |

Script: `src/inventory_planning.py`

## Phase 5 DAX inputs (preview)

Core measures to implement from these facts:

- `Safety Stock` — from `fact_inventory_planning[safety_stock]`
- `Reorder Point` — from `fact_inventory_planning[reorder_point]`
- `Rolling MAPE (4W)` — from `fact_rolling_forecast_error[rolling_mape_4w]`
- `High Uncertainty Flag` — from `fact_inventory_planning[high_uncertainty_flag]`

## What I need from you to close Phase 4

1. Accept the 95% / 2-week-lead-time assumptions (or specify different values).
2. Confirm Phase 5 — Power BI dashboard with real DAX measures.
