# Phase 5 — dashboard display rules

Items flagged in Phase 2 that must carry through to the Power BI dashboard.

## DQ-025 — Catalog category parity

**Do not imply equal category assortment depth.**

| AmazonIQ category | Full mapped product count (SRC-KAGGLE-002) |
|-------------------|-------------------------------------------|
| Clothing & Accessories | 141,291 |
| Toys & Games | 83,133 |
| Electronics | 49,452 |
| Health & Personal Care | 31,423 |
| Home & Kitchen | 17,717 |
| Patio, Lawn & Garden | 5,345 |

Garden is **26.4× smaller** than Clothing in the source catalog (5,345 ÷ 141,291).

The processed sample is **500 rows per category** (equal by design) and does **not** reflect catalog parity.

**Dashboard options (pick one or combine):**

1. Show raw mapped product counts per category (recommended transparency).
2. Normalize visuals (e.g., share of catalog, index to category max).
3. Add a footnote on any category comparison visual: “Sample sizes equal; catalog depth varies up to 26×.”

Never label categories as “comparable volume” without this context.
