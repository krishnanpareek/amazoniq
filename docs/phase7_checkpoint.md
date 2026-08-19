# Phase 7 checkpoint — pause for review

**Status:** Complete. Interactive HTML companion added alongside the Power BI PBIP (unchanged).

## Deliverables

| File | Purpose |
|------|---------|
| [`dashboard/web/index.html`](../dashboard/web/index.html) | Single-page interactive dashboard |
| [`dashboard/web/style.css`](../dashboard/web/style.css) | Warm dark editorial theme (distinct from Tesla) |
| [`dashboard/web/script.js`](../dashboard/web/script.js) | Chart.js charts and section logic |
| [`dashboard/web/data.js`](../dashboard/web/data.js) | Embedded CSV data (generated) |
| [`dashboard/web/README.md`](../dashboard/web/README.md) | Local viewing + GitHub Pages notes |
| [`src/build_web_data.py`](../src/build_web_data.py) | Reads `data/processed/`, writes `data.js` only |

## Not changed

- `data/processed/` — read only
- `dashboard/AmazonIQ.pbip` and semantic model — untouched

## Sections (mirrors Power BI)

1. **Executive overview** — MAPE range 14.5%–40.0%, weak/high-uncertainty counts, search-interest framing
2. **Forecast vs actual** — category dropdown, Prophet vs actual line chart, per-category MAPE badge
3. **Inventory planning** — SS/ROP bar charts colored by `uncertainty_tier`, planning table
4. **Data quality** — prominent DQ cards (DQ-001, DQ-018, DQ-022, DQ-023, DQ-025)

## View locally

```powershell
python src/build_web_data.py
# Open docs/index.html or dashboard/web/index.html in a browser (file:// works)
```

## GitHub Pages (approved)

Deploy from **`/docs`** on `main`. Steps: [`GITHUB_PAGES.md`](GITHUB_PAGES.md).

Live URL (after enable): `https://<github-username>.github.io/amazoniq/`

## What I need from you

1. Push to GitHub and enable Pages per `GITHUB_PAGES.md`.
2. Confirm live URL, then Phase 6 writeup can reference it as companion to the PBIP.

**Not done yet (per your request):** updates to `reports/executive_summary.md` or `reports/portfolio_materials.md` with the live URL.
