# Phase 3 checkpoint — pause for review

**Method:** Prophet (multiplicative seasonality, weekly + yearly) on Google Trends search interest only.  
**Holdout:** last 26 complete weeks (2026-02-15 through 2026-08-09). Partial week 2026-08-16 excluded from fit and test.  
**Not used as forecast input:** Kaggle catalog, Census MRTS (Census remains a separate seasonality sanity-check series).

April headphones and July vitamins spikes were **not** smoothed or removed (`DQ-026`).

## MAPE by category (26-week holdout)

| Category | Keyword | MAPE | Weak? | Likely cause |
|----------|---------|------|-------|--------------|
| Health & Personal Care | vitamins | **14.5%** | No | Best fit; relatively stable series despite July peak |
| Toys & Games | toys | 16.7% | Yes | Moderate error; holiday seasonality |
| Patio, Lawn & Garden | lawn mower | 18.9% | Yes | Strong spring seasonality; narrow keyword |
| Home & Kitchen | air fryer | 19.6% | Yes | Moderate error |
| Electronics | headphones | **30.2%** | Yes | April 2026 spike (DQ-011) — model misses atypical peak |
| Clothing & Accessories | running shoes | **40.0%** | Yes | Highest error; shares April 2026 peak week with headphones (DQ-012) |

**Threshold:** `weak_accuracy_flag=True` when MAPE ≥ 15% or insufficient test points.

## Outputs

| File | Description |
|------|-------------|
| `data/processed/fact_forecast_metrics.csv` | One row per category — MAPE, flags, reasons |
| `data/processed/fact_forecast_backtest.csv` | Weekly actual vs predicted for holdout window |
| `data/processed/fact_forecast_prophet.csv` | Full fitted series + 13-week forward forecast |

Script: `src/forecast_prophet.py`

## Interpretation (not hidden)

- **Clothing and Electronics** are the weakest — both likely hurt by the shared April 2026 interest spike that Prophet treats as out-of-pattern.
- **Health** is the strongest despite the July vitamins peak; low baseline volatility helps MAPE.
- These are **search-interest** forecasts, not units or revenue. Weak MAPE is a finding for the portfolio writeup, not a reason to drop categories silently.

## Confirmed from Phase 2 (logged)

- **Sennheiser B00004SY4H:** snapshot **$299.95** → live **$268.90** (`DQ-022`)
- **Galison 0735372888** → redirected to **0735388059** on live Amazon (`DQ-023`)
- **Garden catalog imbalance:** 5,345 vs 141,291 clothing (**26.4×**) — Phase 5 display rule in `dashboard/phase5_display_rules.md` (`DQ-025`)

## What I need from you to close Phase 3

1. Accept these MAPE results as the portfolio baseline (including flagged weak categories).
2. Confirm Phase 4 — reorder point, safety stock (stated service level), rolling forecast error for DAX inputs.
