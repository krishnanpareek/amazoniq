# Limitations

This project uses **public data only**. It does not claim access to Amazon internal systems, Seller Central, warehouse inventory, vendor forecasts, or confidential demand plans.

## Standing constraints

1. **No Amazon-confidential access.** Catalog attributes come from a public Kaggle snapshot of listings. Demand history comes from Google Trends. Seasonality checks come from Census retail series. None of these are Amazon-internal units or GMV.
2. **Search interest ≠ units sold.** Google Trends is a 0–100 relative index. Forecasts are of that index unless a later note explicitly scales it. Do not label Trends as “Amazon demand” or “orders.”
3. **Catalog snapshot ≠ sales history.** Kaggle files are point-in-time product listings (price, rating, review count, category). Review count is a stock, not a weekly sales quantity.
4. **Census kind of business ≠ Amazon category.** MRTS 443 is electronics *and appliance stores*, not Amazon’s Electronics browse node. Mapping is analogical and will stay labeled as such.
5. **Census category sales are not e-commerce-only.** Quarterly e-commerce estimates are mostly aggregate. Category monthly series are all-channel retail.
6. **India vs U.S. geography.** The classic Kaggle Amazon Sales Dataset is Amazon.in / INR. It is rejected as the primary catalog so U.S. Trends and U.S. Census are not mixed with an India listing file.
7. **Missing values stay null.** No silent interpolation or dropping of gaps. Phase 2 must flag inconsistencies before any fill rule is applied.
8. **Forecast error will be shown, including weak categories.** MAPE is reported per category. Weak accuracy is a finding, not something to hide.
9. **Inventory math is illustrative.** Reorder point and safety stock use a stated service level and a demand proxy, not Amazon fulfillment-center inventory.
10. **No Amazon trademarks.** Dashboard colors may be Amazon-adjacent. Do not use the Amazon logo, smile mark, or copy that implies official affiliation.
11. **Correlation ≠ causation.** Seasonality alignment between Trends and Census does not prove that search caused retail sales.

## What this project can support in interviews

- Traceability from KPI → fact row → source file / URL / date
- Explicit metric labels (reported / calculated / estimated / modeled)
- Time-series backtesting with MAPE by category
- Inventory planning measures implemented as DAX, not spreadsheet pass-throughs
- Documented data-quality rejects (same standard as the Tesla public-data project)

## What this project cannot answer

- True Amazon units, GMV, or in-stock rates by ASIN
- Fulfillment-center replenishment or vendor lead times
- Seller-level Buy Box or advertising effects
- Causal “what lifted demand” claims from search interest alone
