# AmazonIQ — Interactive Web Companion (source)

Lightweight **HTML/CSS/JS companion** to the primary Power BI / DAX deliverable (`../AmazonIQ.pbip`). Same processed facts; shareable via GitHub Pages.

**Development source:** edit files here, then run:

```powershell
python src/build_web_data.py
```

That regenerates `data.js` and **syncs** `index.html`, `style.css`, and `script.js` into `docs/` for GitHub Pages.

## View locally

Open either:

- `dashboard/web/index.html` (file://)
- `docs/index.html` (same content after sync)

## GitHub Pages

Deploy from **`/docs`** on the `main` branch. See [`docs/GITHUB_PAGES.md`](../../docs/GITHUB_PAGES.md).

## Disclosure

Public data only. Not an Amazon product. Interactive **companion** — the PBIP remains the primary DAX proof.
