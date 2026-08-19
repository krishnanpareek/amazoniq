# Category scope (confirmed 2026-08-17)

**Status:** Confirmed. Phase 2 may pull only the sources and keywords listed here.

**Locked decisions**

| Decision | Choice |
|----------|--------|
| Category set | Option A — six categories, each with a distinct Census MRTS series |
| Primary catalog | SRC-KAGGLE-002 (2023 Amazon.com products snapshot, sampled) |
| Rejected catalog | SRC-KAGGLE-001 (Amazon.in “Amazon Sales Dataset”) — documented reject only |
| Trends keywords | Defaults below (`lawn mower` is the garden keyword; `yoga mat` is not used) |
| Horizon | 5 years, weekly Trends, geo=US; Census monthly aligned to the same window |

## Confirmed set (6)

| # | AmazonIQ category | Catalog match (sampled from SRC-KAGGLE-002) | Google Trends keyword (U.S., weekly) | Census MRTS kind of business |
|---|-------------------|---------------------------------------------|--------------------------------------|------------------------------|
| 1 | Electronics | Electronics / related browse nodes | `headphones` | 443 — Electronics and Appliance Stores |
| 2 | Home & Kitchen | Home and Kitchen | `air fryer` | 442 — Furniture and Home Furnishings Stores |
| 3 | Clothing & Accessories | Clothing, Shoes and Jewelry | `running shoes` | 448 — Clothing and Clothing Accessories Stores |
| 4 | Health & Personal Care | Health and Personal Care / Beauty | `vitamins` | 446 — Health and Personal Care Stores |
| 5 | Patio, Lawn & Garden | Patio, Lawn and Garden | `lawn mower` | 444 — Building Material and Garden Equipment and Supplies Dealers |
| 6 | Toys & Games | Toys and Games | `toys` | 451 — Sporting Goods, Hobby, Book, and Music Stores |

`lawn mower` is the default garden keyword so Option A does not inherit the Sports `yoga mat` term.

## Standing mapping rules

1. Trends is the forecast target and is labeled **search interest**, not units sold.
2. Census MRTS is the seasonality sanity check and is labeled **U.S. retail sales by kind of business**, not Amazon GMV.
3. The Kaggle file is a **listing snapshot** used for category structure and attributes only.
4. Quarterly Census e-commerce (SRC-CENSUS-002) is optional aggregate context, not a category series.
