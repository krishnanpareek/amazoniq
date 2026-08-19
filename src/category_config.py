"""Confirmed AmazonIQ category mappings. Do not expand without updating docs/category_scope.md."""

from __future__ import annotations

CATEGORIES: list[dict[str, str]] = [
    {
        "category_id": "electronics",
        "name": "Electronics",
        "trends_keyword": "headphones",
        "census_naics": "443",
        "census_label": "Electronics and Appliance Stores",
        "fred_nsa": "MRTSSM443USN",
        "catalog_match_terms": ("electronics", "headphones", "headphone"),
        "catalog_category_ids": (68, 69, 71, 73, 75, 79, 82),
    },
    {
        "category_id": "home_kitchen",
        "name": "Home & Kitchen",
        "trends_keyword": "air fryer",
        "census_naics": "442",
        "census_label": "Furniture and Home Furnishings Stores",
        "fred_nsa": "MRTSSM442USN",
        "catalog_match_terms": ("home & kitchen", "home and kitchen", "kitchen"),
        "catalog_category_ids": (166, 170, 201),
    },
    {
        "category_id": "clothing",
        "name": "Clothing & Accessories",
        "trends_keyword": "running shoes",
        "census_naics": "448",
        "census_label": "Clothing and Clothing Accessories Stores",
        "fred_nsa": "MRTSSM448USN",
        "catalog_match_terms": ("clothing", "shoes", "jewelry", "apparel"),
        "catalog_category_ids": (84, 90, 91, 97, 110, 114, 116, 122),
    },
    {
        "category_id": "health",
        "name": "Health & Personal Care",
        "trends_keyword": "vitamins",
        "census_naics": "446",
        "census_label": "Health and Personal Care Stores",
        "fred_nsa": "MRTSSM446USN",
        "catalog_match_terms": ("health", "personal care", "beauty", "vitamin"),
        "catalog_category_ids": (45, 47, 49, 52, 131, 132, 136),
    },
    {
        "category_id": "garden",
        "name": "Patio, Lawn & Garden",
        "trends_keyword": "lawn mower",
        "census_naics": "444",
        "census_label": "Building Material and Garden Equipment and Supplies Dealers",
        "fred_nsa": "MRTSSM444USN",
        "catalog_match_terms": ("patio", "lawn", "garden", "outdoor"),
        "catalog_category_ids": (195, 199, 215),
    },
    {
        "category_id": "toys",
        "name": "Toys & Games",
        "trends_keyword": "toys",
        "census_naics": "451",
        "census_label": "Sporting Goods, Hobby, Book, and Music Stores",
        "fred_nsa": "MRTSSM451USN",
        "catalog_match_terms": ("toys", "games", "toy"),
        "catalog_category_ids": (217, 218, 220, 221, 223, 224, 227, 229, 230, 270),
    },
]

# Leaf-node map is analogical. Garden has no Patio/Lawn & Garden browse node in this file.
SAMPLE_PER_CATEGORY = 500
SAMPLE_SEED = 17


TRENDS_GEO = "US"
TRENDS_TIMEFRAME = "today 5-y"
CENSUS_XLSX_URL = "https://www.census.gov/retail/mrts/www/mrtssales92-present.xlsx"
KAGGLE_DATASET = "asaniczka/amazon-products-dataset-2023-1-4m-products"
