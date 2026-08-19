# GitHub Pages — AmazonIQ interactive companion

This folder serves **two roles**:

| Role | Files |
|------|--------|
| **GitHub Pages site** (live dashboard) | `index.html`, `style.css`, `script.js`, `data.js`, `.nojekyll` |
| **Project documentation** | `*.md` checkpoints, methodology, data-quality log, etc. |

The site root is `index.html`. Markdown docs remain in-repo for GitHub browsing but are not part of the dashboard UI.

## Before each deploy

```powershell
python src/build_web_data.py
git add docs/index.html docs/style.css docs/script.js docs/data.js docs/.nojekyll
git commit -m "Sync web companion for GitHub Pages"
git push origin main
```

Edit HTML/CSS/JS in `dashboard/web/` first; the build script copies them here.

## Enable GitHub Pages

1. Push the repo to GitHub (if not already).
2. Open the repo on GitHub → **Settings** → **Pages** (left sidebar under *Code and automation*).
3. Under **Build and deployment** → **Source**, choose **Deploy from a branch**.
4. **Branch:** `main` (or your default branch).
5. **Folder:** **`/docs`**.
6. Click **Save**.

GitHub builds the site (usually 1–3 minutes). Refresh **Settings → Pages** to see the live URL when status is green.

## Live URL format

For a **project site** (repo name `amazoniq`, owner `krishnanpareek`):

```text
https://krishnanpareek.github.io/amazoniq/
```

General pattern:

```text
https://<github-username>.github.io/<repository-name>/
```

- Username/org comes from the account that owns the repo.
- Repository name is the repo slug (case-insensitive in the URL).
- Trailing slash is optional; `index.html` is served at the root.

**Not** `https://<username>.github.io/` unless the repo is named `<username>.github.io` (user/org site).

## Untouched by Pages deploy

- `dashboard/AmazonIQ.pbip` and semantic model
- `data/processed/` (read-only input to `build_web_data.py`)
