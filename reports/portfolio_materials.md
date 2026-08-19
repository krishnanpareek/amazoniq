# Portfolio Materials

Use these as copy-ready starting points. Keep the accuracy constraints:

- Deliverable is a **Power BI Project** (`AmazonIQ.pbip`) with real DAX, not HTML/CSS/JS (that is the Tesla project).
- **Public data only.** No Amazon affiliation, Seller Central, warehouse units, or GMV.
- Forecast target is **Google Trends search interest**, not orders.
- Safety stock is a **custom MAPE-adjusted** formula, not the classical textbook formula.
- LinkedIn post below: no em dashes; Unicode bold on methodology terms; Cursor credited; claims scoped to this repo.

---

## Resume bullets (pick 3–5)

- Built AmazonIQ, a public-data demand-forecasting and inventory-planning Power BI model for six Amazon-style e-commerce categories (Prophet backtest on U.S. Google Trends, Census MRTS seasonality context, Kaggle 2023 catalog structure only).
- Caught and documented source defects before modeling: rejected an India/INR “Amazon Sales Dataset” that would have mixed geographies; flagged `reviews` = 0 on 79.3% of 1.4M listings; recorded Sennheiser HD 600 snapshot $299.95 vs live $268.90; kept a Galison identifier that redirects to a different ASIN.
- Backtested Prophet on a 26-week holdout and reported MAPE by category (Health 14.5% to Clothing 40.0%); flagged Electronics and Clothing as high-uncertainty rather than dropping weak series.
- Implemented custom MAPE-adjusted safety stock at a stated 95% service level (z = 1.645) and 2-week illustrative lead time; Clothing buffer 77.4 vs Health 26.3 on the same service level; DAX `Safety Stock (Modeled)` matches stored pipeline values for all six categories.
- Authored a TMDL semantic model and DAX measures (reorder point, rolling 4-week MAPE, Census YoY, catalog product count) and displayed raw catalog depth so a 26.4× garden-vs-clothing imbalance is not implied as parity.

**Skills line (accurate):** Python, Prophet, time-series backtesting, Power BI, DAX, TMDL/PBIP, public-data sourcing, data-quality documentation, inventory planning (service level, safety stock, reorder point).

**Do not list for this project:** Amazon intern tools, Seller Central, warehouse WMS, “Amazon demand,” scraped live catalog as the source of truth, classical safety stock as if it were unmodified, or HTML/CSS/JS dashboarding (use the Tesla project for that).

---

## LinkedIn post

Built AmazonIQ: a 𝗽𝘂𝗯𝗹𝗶𝗰 𝗱𝗮𝘁𝗮 𝗼𝗻𝗹𝘆 demand-planning Power BI model for six Amazon-style product categories. Not an Amazon product. Not Seller Central. Not warehouse units.

The part I would lead with in an interview is not the chart. It is the 𝗱𝗮𝘁𝗮-𝗾𝘂𝗮𝗹𝗶𝘁𝘆 catches:

- The tutorial Kaggle "Amazon Sales Dataset" is Amazon.in / INR. I rejected it so U.S. 𝗚𝗼𝗼𝗴𝗹𝗲 𝗧𝗿𝗲𝗻𝗱𝘀 and U.S. Census would not be mixed with India listings.
- `reviews` is 0 on 79.3% of 1,426,337 catalog rows. That is not a review count.
- Sennheiser HD 600 snapshot price $299.95 vs live Amazon.com $268.90. Snapshot is not current.
- Galison identifier 0735372888 redirects to a different product (0735388059). I kept the snapshot row.
- Garden mapped catalog is 5,345 products vs 141,291 clothing (26.4x). The dashboard shows raw counts so equal samples do not imply parity.

Forecast target is 𝘀𝗲𝗮𝗿𝗰𝗵 𝗶𝗻𝘁𝗲𝗿𝗲𝘀𝘁 (0-100 index), not orders. 𝗣𝗿𝗼𝗽𝗵𝗲𝘁 26-week holdout 𝗠𝗔𝗣𝗘: Health 14.5%, Clothing 40.0%. Weak categories stayed in the model and were flagged.

Inventory math uses a stated 𝟵𝟱% 𝘀𝗲𝗿𝘃𝗶𝗰𝗲 𝗹𝗲𝘃𝗲𝗹 and a 2-week illustrative lead time. 𝘀𝗮𝗳𝗲𝘁𝘆 𝘀𝘁𝗼𝗰𝗸 is 𝗠𝗔𝗣𝗘-𝗮𝗱𝗷𝘂𝘀𝘁𝗲𝗱 (custom, not the classical textbook formula). Same service level, wider buffers where backtest error is worse. Clothing SS 77.4 vs Health 26.3. 𝗗𝗔𝗫 `Safety Stock (Modeled)` matches the Python stored values for all six categories.

Stack: Python extracts -> CSV star schema -> Prophet -> 𝗗𝗔𝗫 measures in a PBIP semantic model. Built in Cursor (AI pair-programming on extracts, TMDL, and docs). I still hand-checked Census vs FRED, Trends vs the UI, and the safety-stock formula against `fact_inventory_planning.csv`.

If you work in demand planning, inventory, or supply chain analytics and care about "where did that number come from," I would like feedback.

#SupplyChain #DemandPlanning #PowerBI #DAX #Python #PublicData #PortfolioProject

---

## Two-minute interview explanation

**0:00–0:25 — Hook**  
“AmazonIQ is a public-data demand-planning project: six Amazon-style categories, Prophet on U.S. Google Trends search interest, then reorder point and safety stock in Power BI with real DAX. It is not Amazon-internal data. The name is the problem setting, not an affiliation.”

**0:25–0:55 — Lead with DQ**  
“Before any forecast I treated source quality the way I did on the Tesla dashboard. I rejected the popular India Amazon Sales Dataset so I would not mix INR listings with U.S. Trends and Census. On the U.S. catalog snapshot, reviews is zero on 79% of 1.4 million rows, a Sennheiser price drifted from $299.95 to $268.90 live, and a Galison identifier redirects to a different puzzle. Garden is 26 times smaller than clothing in the mapped catalog, so the dashboard shows raw counts.”

**0:55–1:20 — Forecast honesty**  
“The forecast is search interest, 0 to 100, not units. 26-week Prophet holdout MAPE runs from 14.5% on vitamins to 40% on running shoes. Electronics and clothing are flagged high uncertainty, partly because of an April 2026 spike I did not smooth. Weak MAPE stayed in the writeup.”

**1:20–1:45 — Inventory + DAX**  
“Safety stock is custom: I scale backtest error σ by one plus MAPE over 100, then apply z = 1.645 and square root of a two-week lead time. That is not the classical z times demand σ formula. Clothing gets a wider buffer than health at the same 95% service level. The DAX measure recomputes that formula and matches the Python file.”

**1:45–2:00 — Close**  
“Happy to walk a source lineage — Sennheiser drift, the garden 26× catalog rule, or why I would not treat Trends as Amazon orders.”

### Likely follow-ups (short answers)

| Question | Answer |
|----------|--------|
| Is this Amazon data? | “No. Kaggle listing snapshot, Google Trends, Census MRTS. Public only. I do not claim Seller Central or warehouse units.” |
| Why not classical safety stock? | “Classical uses demand-history σ and no explicit MAPE term. I only have a search-interest proxy and uneven forecast quality, so I documented a MAPE-adjusted σ and labeled it custom.” |
| Why keep 40% MAPE clothing? | “Dropping it would hide the worst series. The dashboard flags high uncertainty and widens the buffer instead.” |
| Why reject the famous Kaggle Amazon file? | “It is Amazon.in and INR. Pairing it with U.S. Census and U.S. Trends mixes geographies. That is DQ-001.” |
| Did AI build this? | “I used Cursor as a pair-programming copilot for scripts and the PBIP/TMDL files. Spot-checks, formula audit, and source rejects are mine to defend.” |

### Unicode bold used in the LinkedIn post

Paste as-is. LinkedIn does not support markdown bold in all surfaces; these are mathematical sans-serif bold characters.

| Term | Unicode |
|------|---------|
| public data only | 𝗽𝘂𝗯𝗹𝗶𝗰 𝗱𝗮𝘁𝗮 𝗼𝗻𝗹𝘆 |
| data-quality | 𝗱𝗮𝘁𝗮-𝗾𝘂𝗮𝗹𝗶𝘁𝘆 |
| Google Trends | 𝗚𝗼𝗼𝗴𝗹𝗲 𝗧𝗿𝗲𝗻𝗱𝘀 |
| search interest | 𝘀𝗲𝗮𝗿𝗰𝗵 𝗶𝗻𝘁𝗲𝗿𝗲𝘀𝘁 |
| Prophet | 𝗣𝗿𝗼𝗽𝗵𝗲𝘁 |
| MAPE | 𝗠𝗔𝗣𝗘 |
| 95% service level | 𝟵𝟱% 𝘀𝗲𝗿𝘃𝗶𝗰𝗲 𝗹𝗲𝘃𝗲𝗹 |
| safety stock | 𝘀𝗮𝗳𝗲𝘁𝘆 𝘀𝘁𝗼𝗰𝗸 |
| MAPE-adjusted | 𝗠𝗔𝗣𝗘-𝗮𝗱𝗷𝘂𝘀𝘁𝗲𝗱 |
| DAX | 𝗗𝗔𝗫 |
