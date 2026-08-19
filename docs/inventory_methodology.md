# Inventory planning methodology

**Phase 4.** Illustrative reorder logic built on **Google Trends search interest** (0–100 index), not Amazon warehouse units or Kaggle catalog sales.

## Stated assumptions (defaults)

| Parameter | Value | Label |
|-----------|-------|-------|
| Target service level | **95%** | stated assumption |
| Normal z-score (one-sided) | **1.645** | calculated from 95% service level |
| Lead time | **2 weeks** | estimated — illustrative e-commerce replenishment |
| Demand proxy | Weekly search-interest index (`yhat` / actual from Trends) | modeled |
| Forecast error σ | Std dev of `(actual − predicted)` from Prophet 26-week holdout | calculated per category |
| Rolling error window | **4 weeks** | calculated |

These are **not** Amazon fulfillment parameters. Dashboard copy must say “illustrative planning on search-interest proxy.”

## Safety stock — not uniform across categories

Base formula (normal approximation):

```
safety_stock = z × σ_adjusted × √(lead_time_weeks)
```

where `z = 1.645` for the **95% service level**.

**MAPE adjustment (required):** σ is not shared. Each category uses its own backtest error spread, then a **MAPE buffer multiplier** widens safety stock for high-error forecasts:

```
σ_adjusted = σ_backtest × (1 + MAPE% / 100)
```

Examples from Phase 3 baseline:

| Category | MAPE | Multiplier on σ |
|----------|------|-----------------|
| Health | 14.5% | 1.145× |
| Toys | 16.7% | 1.167× |
| Electronics | 30.2% | 1.302× |
| Clothing | 40.0% | 1.400× |

High-MAPE categories therefore carry **wider buffers** than low-MAPE categories at the same stated 95% service level.

## Custom MAPE-adjusted formula vs classical safety stock

**This project uses a custom / modified safety-stock approach.** It is **not** the textbook classical formula applied uniformly across categories.

### What we use (custom)

```
σ_adjusted = σ_backtest × (1 + MAPE% / 100)
safety_stock = z × σ_adjusted × √(lead_time_weeks)
```

- `σ_backtest` = standard deviation of **Prophet holdout forecast errors** `(actual − predicted)` for that category.
- `(1 + MAPE% / 100)` = **MAPE buffer multiplier** that widens safety stock when backtest accuracy is poor.
- Same **95% service level** (`z = 1.645`) for all categories, but **different effective buffers** because σ and MAPE differ by category.

**Rationale:** Scaling the buffer by backtested forecast confidence prevents treating Electronics (30.2% MAPE) and Clothing (40.0% MAPE) the same as Health (14.5% MAPE). High-error categories get a wider safety-stock band and a **high-uncertainty flag** on reorder recommendations rather than a single policy that ignores forecast quality.

### What classical safety stock would use instead

The classical approach (e.g., inventory textbooks / standard SAP-style safety stock) typically assumes:

```
safety_stock = z × σ_demand × √(lead_time)
```

where:

- `σ_demand` = standard deviation of **demand during the replenishment period**, often from historical **unit sales** or order quantities.
- `z` comes from a stated service level (here, 95% → 1.645).
- No explicit **forecast-accuracy** term — demand variability alone drives the buffer, usually from a stationary demand history.

Classical methods would **not** multiply σ by `(1 + MAPE/100)` unless forecast error were folded into σ_demand through a separate forecast-error distribution. They also would **not** use Google Trends search interest as the demand series.

### Why we modified it

| Aspect | Classical | AmazonIQ (this repo) |
|--------|-----------|----------------------|
| Demand signal | Historical unit demand | Google Trends index (search interest proxy) |
| σ source | Demand variability | Prophet backtest forecast-error σ |
| Forecast accuracy | Implicit in demand history | Explicit MAPE multiplier per category |
| Cross-category policy | Same formula, category-specific σ_d only | Same z and lead time, but **MAPE-adjusted σ** |
| Weak forecasts | Not typically flagged in SS formula | Wider buffer + `high_uncertainty_flag` |

Dashboard DAX includes both **stored** values (`fact_inventory_planning`) and a **recalculated** measure (`Safety Stock (Modeled)`) so reviewers can verify the custom formula in the semantic model.

## Reorder point

```
reorder_point = (avg_weekly_demand × lead_time_weeks) + safety_stock
```

`avg_weekly_demand` = mean of the last 4 complete weeks of actual search interest (excluding partial weeks).

## Uncertainty flag (in addition to buffer widening)

| Tier | Condition | Dashboard treatment |
|------|-----------|---------------------|
| Standard | MAPE < 15% | Normal reorder recommendation |
| Elevated | 15% ≤ MAPE < 25% | Wider SS already applied; note moderate forecast error |
| High | MAPE ≥ 25% | Wider SS + **high-uncertainty flag** on reorder recommendation |

Electronics and Clothing are **High** under Phase 3 baseline.

## Rolling forecast vs actual error

Four-week rolling MAPE computed on backtest actuals vs Prophet predictions. Becomes the `Rolling_MAPE_4W` DAX input in Phase 5.

## What this is not

- Not units sold, not GMV, not Seller Central inventory
- Not a uniform safety-stock policy ignoring forecast accuracy
- Census MRTS is not an input to these formulas (seasonality context only)

Script: `src/inventory_planning.py`
