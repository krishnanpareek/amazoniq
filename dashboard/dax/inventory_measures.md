# Inventory planning DAX measures (Phase 5)

Implemented in `dashboard/AmazonIQ.SemanticModel/definition/tables/_Metrics.tmdl`.  
All measures labeled **modeled** on search-interest proxy unless noted.

## Parameters (on dashboard)

| Measure | Value |
|---------|-------|
| `Service Level Assumption` | 95% |
| `Z Score (95%)` | 1.645 |
| `Lead Time Weeks` | 2 |

## Core inventory measures

### Safety Stock (Modeled) — custom formula in DAX

Recomputes the **MAPE-adjusted** buffer (not classical textbook SS):

```dax
Safety Stock (Modeled) =
    SUMX (
        FactInventoryPlanning,
        [Z Score (95%)]
            * FactInventoryPlanning[forecast_error_std_backtest]
            * ( 1 + FactInventoryPlanning[mape_pct_baseline] / 100 )
            * SQRT ( [Lead Time Weeks] )
    )
```

### Safety Stock (Stored) — pipeline validation

```dax
Safety Stock (Stored) = SUM ( FactInventoryPlanning[safety_stock] )
```

Modeled and Stored should match per category when sliced by `DimCategory[category_name]`.

### Reorder Point (Modeled)

```dax
Reorder Point (Modeled) =
    SUMX (
        FactInventoryPlanning,
        FactInventoryPlanning[demand_during_lead_time]
            + [Z Score (95%)]
                * FactInventoryPlanning[forecast_error_std_backtest]
                * ( 1 + FactInventoryPlanning[mape_pct_baseline] / 100 )
                * SQRT ( [Lead Time Weeks] )
    )
```

### Reorder Point (Stored)

```dax
Reorder Point (Stored) = SUM ( FactInventoryPlanning[reorder_point] )
```

## Forecast accuracy measures

```dax
Baseline MAPE = AVERAGE ( FactForecastMetrics[mape_pct] )

Rolling MAPE 4W = AVERAGE ( FactRollingForecastError[rolling_mape_4w] )

Search Interest Actual =
    CALCULATE (
        SUM ( FactRollingForecastError[actual] ),
        NOT ISBLANK ( FactRollingForecastError[actual] )
    )

Search Interest Forecast = SUM ( FactRollingForecastError[predicted] )

Forecast Gap = [Search Interest Actual] - [Search Interest Forecast]
```

## Uncertainty

```dax
High Uncertainty Categories =
    CALCULATE (
        COUNTROWS ( FactInventoryPlanning ),
        FactInventoryPlanning[high_uncertainty_flag] = TRUE ()
    )

High Uncertainty Label =
    IF (
        SELECTEDVALUE ( FactInventoryPlanning[high_uncertainty_flag] ) = TRUE (),
        "High uncertainty — MAPE >= 25%",
        "Standard reorder confidence"
    )
```

## Catalog & Census (context only)

```dax
Catalog Product Count = SUM ( DimCategory[catalog_product_count] )

Catalog Share of Max = AVERAGE ( DimCategory[catalog_share_of_max] )

Census Retail Sales (M USD) = SUM ( FactCensusRetail[sales_millions_nsa] )

Census Sales YoY % =
    VAR ThisYear = [Census Retail Sales (M USD)]
    VAR LastYear =
        CALCULATE (
            [Census Retail Sales (M USD)],
            SAMEPERIODLASTYEAR ( FactCensusRetail[period] )
        )
    RETURN DIVIDE ( ThisYear - LastYear, LastYear )
```

## Display rules

- Show `uncertainty_tier` on Electronics and Clothing visuals.
- Apply [`phase5_display_rules.md`](../phase5_display_rules.md) for catalog count parity (DQ-025).
- Never label ROP/SS as Amazon warehouse units.
- See [`docs/inventory_methodology.md`](../../docs/inventory_methodology.md) for custom vs classical safety stock.
