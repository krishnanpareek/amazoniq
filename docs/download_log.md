# Download log

Access date for this pass: **2026-08-17**.

| Local file | Source_ID | URL | Retrieved | Notes |
|------------|-----------|-----|-----------|-------|
| `data/raw/census/mrtssales92-present.xlsx` | SRC-CENSUS-001 | https://www.census.gov/retail/mrts/www/mrtssales92-present.xlsx | 2026-08-17 | Census file `Last-Modified: Fri, 14 Aug 2026 12:30:12 GMT`. Size 440,847 bytes. Year sheets 1992–2026. June 2026 labeled `(p)` preliminary. |
| `data/raw/census/MRTSSM443USN.csv` | SRC-CENSUS-001 (FRED republication) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MRTSSM443USN | 2026-08-17 | Independent access path for spot-check only. |
| `data/raw/census/MRTSSM442USN.csv` | SRC-CENSUS-001 (FRED republication) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MRTSSM442USN | 2026-08-17 | Spot-check only. |
| `data/raw/census/MRTSSM448USN.csv` | SRC-CENSUS-001 (FRED republication) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MRTSSM448USN | 2026-08-17 | Spot-check only. |
| `data/raw/census/MRTSSM446USN.csv` | SRC-CENSUS-001 (FRED republication) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MRTSSM446USN | 2026-08-17 | Spot-check only. |
| `data/raw/census/MRTSSM444USN.csv` | SRC-CENSUS-001 (FRED republication) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MRTSSM444USN | 2026-08-17 | Spot-check only. |
| `data/raw/census/MRTSSM451USN.csv` | SRC-CENSUS-001 (FRED republication) | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MRTSSM451USN | 2026-08-17 | Spot-check only. |
| `data/raw/google_trends/*.csv` | SRC-TRENDS-001 | https://trends.google.com/trends/ via `pytrends` (`today 5-y`, geo=US) | 2026-08-17 | One file per keyword. 262 weekly rows each. Latest week `2026-08-16` is `isPartial=True`. |
| `data/raw/kaggle/amazon_categories.csv` | SRC-KAGGLE-002 | https://www.kaggle.com/datasets/asaniczka/amazon-products-dataset-2023-1-4m-products | 2026-08-17 | 6,828 bytes — matches Kaggle file listing exactly. 248 category rows. License ODC-By. |
| `data/raw/kaggle/amazon_products.csv` | SRC-KAGGLE-002 | same | 2026-08-17 | 375,936,400 bytes — matches Kaggle file listing exactly. 1,426,337 product rows. |

Processed outputs:

| File | Rows | Script |
|------|------|--------|
| `data/processed/fact_census_retail_nsa.csv` | 2,484 (6 series × 414 months, 1992-01 through 2026-06) | `src/extract_census.py` |
| `data/processed/fact_search_interest.csv` | 1,572 (6 keywords × 262 weeks) | `src/pull_google_trends.py` |
| `data/processed/dim_catalog_category.csv` | 38 leaf-to-AmazonIQ maps | `src/extract_kaggle_catalog.py` |
| `data/processed/fact_catalog_category_counts.csv` | 38 leaf counts from the full file | `src/extract_kaggle_catalog.py` |
| `data/processed/dim_product_sample.csv` | 3,000 (500 per AmazonIQ category) | `src/extract_kaggle_catalog.py` |
| `data/processed/fact_forecast_metrics.csv` | 6 (MAPE per category) | `src/forecast_prophet.py` |
| `data/processed/fact_forecast_backtest.csv` | 156 (26 weeks × 6 categories) | `src/forecast_prophet.py` |
| `data/processed/fact_forecast_prophet.csv` | Full fit + 13-week forward | `src/forecast_prophet.py` |
| `data/processed/fact_inventory_planning.csv` | 6 (ROP, MAPE-adjusted SS, uncertainty tier) | `src/inventory_planning.py` |
| `data/processed/fact_rolling_forecast_error.csv` | 156 (weekly error + 4W rolling MAPE) | `src/inventory_planning.py` |
