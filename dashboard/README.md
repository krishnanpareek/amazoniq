# Dashboard — AmazonIQ

**Primary DAX deliverable:** [`AmazonIQ.pbip`](AmazonIQ.pbip) — semantic model + four-page report with **real DAX measures** in `_Metrics` (not pass-through columns).

**Interactive web companion (Phase 7):** [`web/index.html`](web/index.html) (dev) · **GitHub Pages:** [`docs/index.html`](../docs/index.html). See [`web/README.md`](web/README.md) and [`docs/GITHUB_PAGES.md`](../docs/GITHUB_PAGES.md).

## Open in Power BI Desktop

1. Install [Power BI Desktop](https://powerbi.microsoft.com/desktop/) (August 2024 or later recommended).
2. Enable preview: **File → Options → Preview features → Store reports using enhanced metadata format (PBIR)**.
3. Open `dashboard/AmazonIQ.pbip` from this repo root (paths to CSVs are relative to the semantic model folder).
4. **Refresh** the model — CSV sources load from `data/processed/`.
5. If a page visual fails validation, re-save once in Desktop (PBIR preview may normalize schema versions).

## Regenerate from Python

```powershell
python src/export_dim_category.py
python src/build_pbip_model.py
```

Run after updating processed CSVs or DAX in `src/build_pbip_model.py`.

## Report pages

| Page | Focus | Key measures |
|------|-------|--------------|
| Executive Overview | MAPE, uncertainty count, ROP/SS snapshot | `Baseline MAPE`, `High Uncertainty Categories`, `Safety Stock (Modeled)` |
| Forecast vs Actual | Holdout actual vs Prophet predicted | `Search Interest Actual`, `Search Interest Forecast`, `Rolling MAPE 4W` |
| Inventory Planning | Custom MAPE-adjusted buffers | `Safety Stock (Modeled)` vs `Safety Stock (Stored)`, `High Uncertainty Label` |
| Seasonality & Catalog Context | Trends + Census + catalog depth | `Search Interest (Complete Weeks)`, `Catalog Product Count`, `Census Sales YoY %` |

## DAX measures (`_Metrics` table)

Full definitions live in [`AmazonIQ.SemanticModel/definition/tables/_Metrics.tmdl`](AmazonIQ.SemanticModel/definition/tables/_Metrics.tmdl). Human-readable notes: [`dax/inventory_measures.md`](dax/inventory_measures.md).

**Custom safety stock (not classical):** `Safety Stock (Modeled)` recomputes  
`z × σ_backtest × (1 + MAPE/100) × √lead_time` in DAX. See [`docs/inventory_methodology.md`](../docs/inventory_methodology.md).

## Display rules

- **DQ-025:** Show raw catalog counts or normalized share — never imply category parity. See [`phase5_display_rules.md`](phase5_display_rules.md).
- Label all ROP/SS as **illustrative planning on search-interest proxy**, not warehouse units.
- Amazon-adjacent color/tone is fine. **No** Amazon logo, smile mark, or trademarked assets. No implied Amazon affiliation.

## Design constraint

Public-data portfolio only. Census MRTS is context on the Seasonality page — not an input to inventory formulas.
