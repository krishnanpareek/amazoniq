"""Generate Power BI Project (PBIP) TMDL semantic model and PBIR report for AmazonIQ."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DASH = ROOT / "dashboard"
SM = DASH / "AmazonIQ.SemanticModel" / "definition"
TABLES = SM / "tables"
DATA = ROOT / "data" / "processed"

# Relative from dashboard/AmazonIQ.SemanticModel/definition/ to data/processed
DATA_REL = "../../../data/processed"


def m_csv(filename: str, types: list[tuple[str, str]]) -> str:
    type_lines = ", ".join(f'{{"{c}", {t}}}' for c, t in types)
    return f"""
\t\tlet
\t\t\tSource = Csv.Document(
\t\t\t\tFile.Contents("{DATA_REL}/{filename}"),
\t\t\t\t[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
\t\t\t),
\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{{type_lines}}})
\t\tin
\t\t\t#"Changed Type\""""


TABLES.mkdir(parents=True, exist_ok=True)
(DASH / "AmazonIQ.Report" / "definition").mkdir(parents=True, exist_ok=True)

# database.tmdl
(SM / "database.tmdl").write_text(
    """database
\tcompatibilityLevel: 1567
""",
    encoding="utf-8",
)

# model.tmdl
(SM / "model.tmdl").write_text(
    """model Model
\tculture: en-US
\tdefaultPowerBIDataSourceVersion: powerBI_V3
\tsourceQueryCulture: en-US

annotation __PBI_TimeIntelligenceEnabled = 0

ref table DimCategory
ref table FactSearchInterest
ref table FactRollingForecastError
ref table FactInventoryPlanning
ref table FactForecastMetrics
ref table FactCensusRetail
ref table _Metrics
""",
    encoding="utf-8",
)

# relationships.tmdl
(SM / "relationships.tmdl").write_text(
    """relationship FactSearchInterest_DimCategory
\tfromColumn: FactSearchInterest.category_id
\ttoColumn: DimCategory.category_id

relationship FactRollingForecastError_DimCategory
\tfromColumn: FactRollingForecastError.category_id
\ttoColumn: DimCategory.category_id

relationship FactInventoryPlanning_DimCategory
\tfromColumn: FactInventoryPlanning.category_id
\ttoColumn: DimCategory.category_id

relationship FactForecastMetrics_DimCategory
\tfromColumn: FactForecastMetrics.category_id
\ttoColumn: DimCategory.category_id

relationship FactCensusRetail_DimCategory
\tfromColumn: FactCensusRetail.category_id
\ttoColumn: DimCategory.category_id
""",
    encoding="utf-8",
)

# DimCategory
(TABLES / "DimCategory.tmdl").write_text(
    f"""table DimCategory
\tlineageTag: dim-category

\tcolumn category_id
\t\tdataType: string
\t\tlineageTag: dim-category-id
\t\tsummarizeBy: none
\t\tsourceColumn: category_id

\tcolumn category_name
\t\tdataType: string
\t\tlineageTag: dim-category-name
\t\tsourceColumn: category_name

\tcolumn keyword
\t\tdataType: string
\t\tlineageTag: dim-keyword
\t\tsourceColumn: keyword

\tcolumn census_naics
\t\tdataType: string
\t\tlineageTag: dim-census-naics
\t\tsourceColumn: census_naics

\tcolumn census_label
\t\tdataType: string
\t\tlineageTag: dim-census-label
\t\tsourceColumn: census_label

\tcolumn catalog_product_count
\t\tdataType: int64
\t\tformatString: #,0
\t\tlineageTag: dim-catalog-count
\t\tsourceColumn: catalog_product_count

\tcolumn catalog_share_of_max
\t\tdataType: double
\t\tformatString: 0.0%
\t\tlineageTag: dim-catalog-share
\t\tsourceColumn: catalog_share_of_max

\tcolumn baseline_mape_pct
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: dim-baseline-mape
\t\tsourceColumn: baseline_mape_pct

\tpartition DimCategory = m
\t\tmode: import
\t\tsource = {m_csv("dim_category.csv", [
    ('category_id', 'type text'),
    ('category_name', 'type text'),
    ('keyword', 'type text'),
    ('census_naics', 'type text'),
    ('census_label', 'type text'),
    ('catalog_product_count', 'Int64.Type'),
    ('catalog_share_of_max', 'type number'),
    ('baseline_mape_pct', 'type number'),
])}

\tannotation PBI_ResultType = Table
""",
    encoding="utf-8",
)

# FactSearchInterest - filter partial in PQ or DAX; keep all, flag column exists
(TABLES / "FactSearchInterest.tmdl").write_text(
    f"""table FactSearchInterest
\tlineageTag: fact-search-interest

\tcolumn week_start
\t\tdataType: dateTime
\t\tformatString: Short Date
\t\tlineageTag: fsi-week
\t\tsourceColumn: week_start

\tcolumn category_id
\t\tdataType: string
\t\tlineageTag: fsi-cat-id
\t\tsourceColumn: category_id

\tcolumn interest
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: fsi-interest
\t\tsourceColumn: interest

\tcolumn is_partial
\t\tdataType: boolean
\t\tlineageTag: fsi-partial
\t\tsourceColumn: is_partial

\tpartition FactSearchInterest = m
\t\tmode: import
\t\tsource = {m_csv("fact_search_interest.csv", [
    ('week_start', 'type datetime'),
    ('category_id', 'type text'),
    ('category_name', 'type text'),
    ('keyword', 'type text'),
    ('geo', 'type text'),
    ('timeframe', 'type text'),
    ('interest', 'Int64.Type'),
    ('is_partial', 'type logical'),
    ('source_id', 'type text'),
    ('source_file', 'type text'),
])}

\tannotation PBI_ResultType = Table
""",
    encoding="utf-8",
)

(TABLES / "FactRollingForecastError.tmdl").write_text(
    f"""table FactRollingForecastError
\tlineageTag: fact-rolling-error

\tcolumn ds
\t\tdataType: dateTime
\t\tformatString: Short Date
\t\tlineageTag: fre-ds
\t\tsourceColumn: ds

\tcolumn category_id
\t\tdataType: string
\t\tlineageTag: fre-cat-id
\t\tsourceColumn: category_id

\tcolumn actual
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: fre-actual
\t\tsourceColumn: actual

\tcolumn predicted
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: fre-predicted
\t\tsourceColumn: predicted

\tcolumn rolling_mape_4w
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: fre-rolling-mape
\t\tsourceColumn: rolling_mape_4w

\tcolumn uncertainty_tier
\t\tdataType: string
\t\tlineageTag: fre-tier
\t\tsourceColumn: uncertainty_tier

\tpartition FactRollingForecastError = m
\t\tmode: import
\t\tsource = {m_csv("fact_rolling_forecast_error.csv", [
    ('ds', 'type datetime'),
    ('category_id', 'type text'),
    ('category_name', 'type text'),
    ('keyword', 'type text'),
    ('actual', 'type number'),
    ('predicted', 'type number'),
    ('forecast_error', 'type number'),
    ('forecast_error_abs', 'type number'),
    ('forecast_error_pct', 'type number'),
    ('rolling_mape_4w', 'type number'),
    ('uncertainty_tier', 'type text'),
    ('source_id', 'type text'),
    ('model', 'type text'),
])}

\tannotation PBI_ResultType = Table
""",
    encoding="utf-8",
)

(TABLES / "FactInventoryPlanning.tmdl").write_text(
    f"""table FactInventoryPlanning
\tlineageTag: fact-inventory

\tcolumn category_id
\t\tdataType: string
\t\tlineageTag: fip-cat-id
\t\tsourceColumn: category_id

\tcolumn safety_stock
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: fip-ss
\t\tsourceColumn: safety_stock

\tcolumn reorder_point
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: fip-rop
\t\tsourceColumn: reorder_point

\tcolumn mape_pct_baseline
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: fip-mape
\t\tsourceColumn: mape_pct_baseline

\tcolumn mape_buffer_multiplier
\t\tdataType: double
\t\tformatString: 0.000
\t\tlineageTag: fip-mape-mult
\t\tsourceColumn: mape_buffer_multiplier

\tcolumn forecast_error_std_backtest
\t\tdataType: double
\t\tformatString: 0.0000
\t\tlineageTag: fip-sigma
\t\tsourceColumn: forecast_error_std_backtest

\tcolumn high_uncertainty_flag
\t\tdataType: boolean
\t\tlineageTag: fip-high-flag
\t\tsourceColumn: high_uncertainty_flag

\tcolumn uncertainty_tier
\t\tdataType: string
\t\tlineageTag: fip-tier
\t\tsourceColumn: uncertainty_tier

\tcolumn service_level_pct
\t\tdataType: double
\t\tformatString: 0
\t\tlineageTag: fip-sl
\t\tsourceColumn: service_level_pct

\tcolumn lead_time_weeks
\t\tdataType: int64
\t\tformatString: 0
\t\tlineageTag: fip-lt
\t\tsourceColumn: lead_time_weeks

\tcolumn demand_during_lead_time
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: fip-ddlt
\t\tsourceColumn: demand_during_lead_time

\tpartition FactInventoryPlanning = m
\t\tmode: import
\t\tsource = {m_csv("fact_inventory_planning.csv", [
    ('category_id', 'type text'),
    ('category_name', 'type text'),
    ('keyword', 'type text'),
    ('service_level_pct', 'type number'),
    ('z_score', 'type number'),
    ('lead_time_weeks', 'Int64.Type'),
    ('avg_weekly_demand_proxy', 'type number'),
    ('demand_during_lead_time', 'type number'),
    ('forecast_error_std_backtest', 'type number'),
    ('mape_pct_baseline', 'type number'),
    ('mape_buffer_multiplier', 'type number'),
    ('forecast_error_std_adjusted', 'type number'),
    ('safety_stock', 'type number'),
    ('reorder_point', 'type number'),
    ('uncertainty_tier', 'type text'),
    ('high_uncertainty_flag', 'type logical'),
    ('metric_label', 'type text'),
    ('assumption_note', 'type text'),
    ('source_id', 'type text'),
])}

\tannotation PBI_ResultType = Table
""",
    encoding="utf-8",
)

(TABLES / "FactForecastMetrics.tmdl").write_text(
    f"""table FactForecastMetrics
\tlineageTag: fact-forecast-metrics

\tcolumn category_id
\t\tdataType: string
\t\tlineageTag: ffm-cat-id
\t\tsourceColumn: category_id

\tcolumn mape_pct
\t\tdataType: double
\t\tformatString: 0.0
\t\tlineageTag: ffm-mape
\t\tsourceColumn: mape_pct

\tcolumn weak_accuracy_flag
\t\tdataType: boolean
\t\tlineageTag: ffm-weak
\t\tsourceColumn: weak_accuracy_flag

\tpartition FactForecastMetrics = m
\t\tmode: import
\t\tsource = {m_csv("fact_forecast_metrics.csv", [
    ('category_id', 'type text'),
    ('category_name', 'type text'),
    ('keyword', 'type text'),
    ('model', 'type text'),
    ('train_weeks', 'Int64.Type'),
    ('test_weeks', 'Int64.Type'),
    ('test_start', 'type text'),
    ('test_end', 'type text'),
    ('mape_pct', 'type number'),
    ('weak_accuracy_flag', 'type logical'),
    ('weak_accuracy_reason', 'type text'),
    ('source_id', 'type text'),
])}

\tannotation PBI_ResultType = Table
""",
    encoding="utf-8",
)

# Census - recent 5 years only in PQ to keep model lean
(TABLES / "FactCensusRetail.tmdl").write_text(
    f"""table FactCensusRetail
\tlineageTag: fact-census

\tcolumn period
\t\tdataType: dateTime
\t\tformatString: Short Date
\t\tlineageTag: fcr-period
\t\tsourceColumn: period

\tcolumn category_id
\t\tdataType: string
\t\tlineageTag: fcr-cat-id
\t\tsourceColumn: category_id

\tcolumn sales_millions_nsa
\t\tdataType: double
\t\tformatString: #,0
\t\tlineageTag: fcr-sales
\t\tsourceColumn: sales_millions_nsa

\tcolumn preliminary_flag
\t\tdataType: boolean
\t\tlineageTag: fcr-prelim
\t\tsourceColumn: preliminary_flag

\tpartition FactCensusRetail = m
\t\tmode: import
\t\tsource =
\t\tlet
\t\t\tSource = Csv.Document(
\t\t\t\tFile.Contents("{DATA_REL}/fact_census_retail_nsa.csv"),
\t\t\t\t[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]
\t\t\t),
\t\t\t#"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
\t\t\t#"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{
\t\t\t\t{{"period", type datetime}},
\t\t\t\t{{"category_id", type text}},
\t\t\t\t{{"sales_millions_nsa", type number}},
\t\t\t\t{{"preliminary_flag", type logical}}
\t\t\t}}),
\t\t\t#"Filtered Rows" = Table.SelectRows(#"Changed Type", each [sales_millions_nsa] <> null and [period] >= #datetime(2021, 1, 1, 0, 0, 0))
\t\tin
\t\t\t#"Filtered Rows"

\tannotation PBI_ResultType = Table
""",
    encoding="utf-8",
)

# _Metrics table - all real DAX measures
(TABLES / "_Metrics.tmdl").write_text(
    """table _Metrics
\tlineageTag: metrics-table

\t/// Stated default service level assumption (95%).
\tmeasure 'Service Level Assumption' = 0.95
\t\tformatString: 0.0%

\t/// Z-score for 95% one-sided service level.
\tmeasure 'Z Score (95%)' = 1.645
\t\tformatString: 0.000

\t/// Illustrative lead time in weeks.
\tmeasure 'Lead Time Weeks' = 2
\t\tformatString: 0

\t/// Custom MAPE-adjusted safety stock recomputed in DAX (not a pass-through).
\tmeasure 'Safety Stock (Modeled)' =
\t\t\tSUMX (
\t\t\t    FactInventoryPlanning,
\t\t\t    [Z Score (95%)]
\t\t\t        * FactInventoryPlanning[forecast_error_std_backtest]
\t\t\t        * ( 1 + FactInventoryPlanning[mape_pct_baseline] / 100 )
\t\t\t        * SQRT ( [Lead Time Weeks] )
\t\t\t)
\t\tformatString: #,0.0

\t/// Stored safety stock from Python pipeline (should match Modeled).
\tmeasure 'Safety Stock (Stored)' = SUM ( FactInventoryPlanning[safety_stock] )
\t\tformatString: #,0.0

\t/// Reorder point recomputed: demand during lead time + modeled safety stock.
\tmeasure 'Reorder Point (Modeled)' =
\t\t\tSUMX (
\t\t\t    FactInventoryPlanning,
\t\t\t    FactInventoryPlanning[demand_during_lead_time]
\t\t\t        + [Z Score (95%)]
\t\t\t            * FactInventoryPlanning[forecast_error_std_backtest]
\t\t\t            * ( 1 + FactInventoryPlanning[mape_pct_baseline] / 100 )
\t\t\t            * SQRT ( [Lead Time Weeks] )
\t\t\t)
\t\tformatString: #,0.0

\tmeasure 'Reorder Point (Stored)' = SUM ( FactInventoryPlanning[reorder_point] )
\t\tformatString: #,0.0

\t/// Phase 3 holdout MAPE by category context.
\tmeasure 'Baseline MAPE' = AVERAGE ( FactForecastMetrics[mape_pct] )
\t\tformatString: 0.0

\t/// Four-week rolling MAPE from backtest window.
\tmeasure 'Rolling MAPE 4W' = AVERAGE ( FactRollingForecastError[rolling_mape_4w] )
\t\tformatString: 0.0

\t/// Actual search interest (complete weeks).
\tmeasure 'Search Interest Actual' =
\t\t\tCALCULATE (
\t\t\t    SUM ( FactRollingForecastError[actual] ),
\t\t\t    NOT ISBLANK ( FactRollingForecastError[actual] )
\t\t\t)
\t\tformatString: 0.0

\tmeasure 'Search Interest Forecast' = SUM ( FactRollingForecastError[predicted] )
\t\tformatString: 0.0

\tmeasure 'Forecast Gap' = [Search Interest Actual] - [Search Interest Forecast]
\t\tformatString: 0.0

\t/// Categories with MAPE >= 25% (Electronics, Clothing).
\tmeasure 'High Uncertainty Categories' =
\t\t\tCALCULATE (
\t\t\t    COUNTROWS ( FactInventoryPlanning ),
\t\t\t    FactInventoryPlanning[high_uncertainty_flag] = TRUE ()
\t\t\t)
\t\tformatString: 0

\tmeasure 'High Uncertainty Label' =
\t\t\tIF (
\t\t\t    SELECTEDVALUE ( FactInventoryPlanning[high_uncertainty_flag] ) = TRUE (),
\t\t\t    "High uncertainty — MAPE >= 25%",
\t\t\t    "Standard reorder confidence"
\t\t\t)

\t/// Raw catalog depth — do not imply parity (DQ-025).
\tmeasure 'Catalog Product Count' = SUM ( DimCategory[catalog_product_count] )
\t\tformatString: #,0

\t/// Normalized catalog display helper.
\tmeasure 'Catalog Share of Max' = AVERAGE ( DimCategory[catalog_share_of_max] )
\t\tformatString: 0.0%

\t/// Census retail sales sanity-check series (millions USD, NSA).
\tmeasure 'Census Retail Sales (M USD)' = SUM ( FactCensusRetail[sales_millions_nsa] )
\t\tformatString: #,0

\t/// Year-over-year change in Census sales for selected period.
\tmeasure 'Census Sales YoY %' =
\t\t\tVAR ThisYear = [Census Retail Sales (M USD)]
\t\t\tVAR LastYear =
\t\t\t    CALCULATE (
\t\t\t        [Census Retail Sales (M USD)],
\t\t\t        SAMEPERIODLASTYEAR ( FactCensusRetail[period] )
\t\t\t    )
\t\t\tRETURN
\t\t\t    DIVIDE ( ThisYear - LastYear, LastYear )
\t\tformatString: 0.0%

\t/// Trends interest for seasonality page (excludes partial weeks).
\tmeasure 'Search Interest (Complete Weeks)' =
\t\t\tCALCULATE (
\t\t\t    SUM ( FactSearchInterest[interest] ),
\t\t\t    FactSearchInterest[is_partial] = FALSE ()
\t\t\t)
\t\tformatString: 0

\tcolumn Dummy
\t\tisHidden
\t\tsourceColumn: [Dummy]

\tpartition _Metrics = calculated
\t\tmode: import
\t\tsource = ROW ( "Dummy", BLANK () )

\tannotation PBI_ResultType = Table
""",
    encoding="utf-8",
)

# PBIP root
(DASH / "AmazonIQ.pbip").write_text(
    """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
  "version": "1.0",
  "artifacts": [
    {
      "report": {
        "path": "AmazonIQ.Report"
      }
    },
    {
      "dataset": {
        "path": "AmazonIQ.SemanticModel"
      }
    }
  ],
  "settings": {
    "enableAutoRecovery": true
  }
}
""",
    encoding="utf-8",
)

# Semantic model pbism
(DASH / "AmazonIQ.SemanticModel" / "definition.pbism").write_text(
    """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbism/1.0.0/schema.json",
  "version": "1.0",
  "settings": {}
}
""",
    encoding="utf-8",
)

VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/visualContainer/2.4.0/schema.json"
)
PAGE_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
    "definition/page/2.1.0/schema.json"
)


def _col(entity: str, prop: str) -> dict:
    return {
        "Column": {
            "Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop,
        }
    }


def _measure(entity: str, prop: str) -> dict:
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Entity": entity}},
            "Property": prop,
        }
    }


def _proj(field: dict, query_ref: str, native_ref: str | None = None) -> dict:
    return {
        "field": field,
        "queryRef": query_ref,
        "nativeQueryRef": native_ref or query_ref.split(".")[-1],
    }


def _visual(
    visual_type: str,
    x: int,
    y: int,
    w: int,
    h: int,
    query_state: dict,
    z: int = 1000,
) -> tuple[str, dict]:
    vid = uuid.uuid4().hex[:20]
    return vid, {
        "$schema": VISUAL_SCHEMA,
        "name": vid,
        "position": {
            "x": x,
            "y": y,
            "z": z,
            "width": w,
            "height": h,
            "tabOrder": z,
        },
        "visual": {
            "visualType": visual_type,
            "query": {"queryState": query_state},
            "drillFilterOtherVisuals": True,
        },
    }


def _write_page(
    pages_dir: Path,
    page_name: str,
    display_name: str,
    visuals: list[tuple[str, dict]],
) -> None:
    page_dir = pages_dir / page_name
    vis_dir = page_dir / "visuals"
    vis_dir.mkdir(parents=True, exist_ok=True)
    (page_dir / "page.json").write_text(
        json.dumps(
            {
                "$schema": PAGE_SCHEMA,
                "name": page_name,
                "displayName": display_name,
                "displayOption": "FitToPage",
                "height": 720,
                "width": 1280,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    for vid, vdef in visuals:
        vpath = vis_dir / vid / "visual.json"
        vpath.parent.mkdir(parents=True, exist_ok=True)
        vpath.write_text(json.dumps(vdef, indent=2), encoding="utf-8")


def build_report_pages() -> None:
    """Create PBIR pages with visuals bound to _Metrics DAX measures."""
    report_def = DASH / "AmazonIQ.Report" / "definition"
    pages_dir = report_def / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)

    exec_visuals = [
        _visual(
            "card",
            40,
            40,
            280,
            120,
            {
                "Values": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Baseline MAPE"),
                            "_Metrics.Baseline MAPE",
                        )
                    ]
                }
            },
        ),
        _visual(
            "card",
            340,
            40,
            280,
            120,
            {
                "Values": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "High Uncertainty Categories"),
                            "_Metrics.High Uncertainty Categories",
                        )
                    ]
                }
            },
        ),
        _visual(
            "card",
            640,
            40,
            280,
            120,
            {
                "Values": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Service Level Assumption"),
                            "_Metrics.Service Level Assumption",
                        )
                    ]
                }
            },
        ),
        _visual(
            "card",
            940,
            40,
            300,
            120,
            {
                "Values": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Lead Time Weeks"),
                            "_Metrics.Lead Time Weeks",
                        )
                    ]
                }
            },
        ),
        _visual(
            "clusteredBarChart",
            40,
            200,
            600,
            480,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "baseline_mape_pct"),
                            "Sum(DimCategory.baseline_mape_pct)",
                            "baseline_mape_pct",
                        )
                    ]
                },
            },
        ),
        _visual(
            "clusteredBarChart",
            680,
            200,
            560,
            480,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Safety Stock (Modeled)"),
                            "_Metrics.Safety Stock (Modeled)",
                        ),
                        _proj(
                            _measure("_Metrics", "Reorder Point (Modeled)"),
                            "_Metrics.Reorder Point (Modeled)",
                        ),
                    ]
                },
            },
        ),
    ]

    forecast_visuals = [
        _visual(
            "lineChart",
            40,
            40,
            1200,
            400,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("FactRollingForecastError", "ds"),
                            "FactRollingForecastError.ds",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _col("FactRollingForecastError", "actual"),
                            "Sum(FactRollingForecastError.actual)",
                            "actual",
                        ),
                        _proj(
                            _col("FactRollingForecastError", "predicted"),
                            "Sum(FactRollingForecastError.predicted)",
                            "predicted",
                        ),
                    ]
                },
                "Series": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
            },
        ),
        _visual(
            "lineChart",
            40,
            480,
            1200,
            200,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("FactRollingForecastError", "ds"),
                            "FactRollingForecastError.ds",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Rolling MAPE 4W"),
                            "_Metrics.Rolling MAPE 4W",
                        )
                    ]
                },
                "Series": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
            },
        ),
    ]

    inventory_visuals = [
        _visual(
            "clusteredBarChart",
            40,
            40,
            620,
            360,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Safety Stock (Modeled)"),
                            "_Metrics.Safety Stock (Modeled)",
                        ),
                        _proj(
                            _measure("_Metrics", "Safety Stock (Stored)"),
                            "_Metrics.Safety Stock (Stored)",
                        ),
                    ]
                },
            },
        ),
        _visual(
            "clusteredBarChart",
            680,
            40,
            560,
            360,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Reorder Point (Modeled)"),
                            "_Metrics.Reorder Point (Modeled)",
                        ),
                        _proj(
                            _measure("_Metrics", "Reorder Point (Stored)"),
                            "_Metrics.Reorder Point (Stored)",
                        ),
                    ]
                },
            },
        ),
        _visual(
            "tableEx",
            40,
            420,
            1200,
            260,
            {
                "Values": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        ),
                        _proj(
                            _col("FactInventoryPlanning", "uncertainty_tier"),
                            "FactInventoryPlanning.uncertainty_tier",
                        ),
                        _proj(
                            _col("FactInventoryPlanning", "mape_pct_baseline"),
                            "Sum(FactInventoryPlanning.mape_pct_baseline)",
                            "mape_pct_baseline",
                        ),
                        _proj(
                            _col("FactInventoryPlanning", "mape_buffer_multiplier"),
                            "Average(FactInventoryPlanning.mape_buffer_multiplier)",
                            "mape_buffer_multiplier",
                        ),
                        _proj(
                            _col("FactInventoryPlanning", "high_uncertainty_flag"),
                            "FactInventoryPlanning.high_uncertainty_flag",
                        ),
                        _proj(
                            _measure("_Metrics", "High Uncertainty Label"),
                            "_Metrics.High Uncertainty Label",
                        ),
                    ]
                }
            },
        ),
    ]

    season_visuals = [
        _visual(
            "lineChart",
            40,
            40,
            780,
            320,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("FactSearchInterest", "week_start"),
                            "FactSearchInterest.week_start",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Search Interest (Complete Weeks)"),
                            "_Metrics.Search Interest (Complete Weeks)",
                        )
                    ]
                },
                "Series": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
            },
        ),
        _visual(
            "clusteredBarChart",
            840,
            40,
            400,
            320,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Catalog Product Count"),
                            "_Metrics.Catalog Product Count",
                        )
                    ]
                },
            },
        ),
        _visual(
            "lineChart",
            40,
            380,
            780,
            300,
            {
                "Category": {
                    "projections": [
                        _proj(
                            _col("FactCensusRetail", "period"),
                            "FactCensusRetail.period",
                        )
                    ]
                },
                "Y": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Census Retail Sales (M USD)"),
                            "_Metrics.Census Retail Sales (M USD)",
                        )
                    ]
                },
                "Series": {
                    "projections": [
                        _proj(
                            _col("DimCategory", "category_name"),
                            "DimCategory.category_name",
                        )
                    ]
                },
            },
        ),
        _visual(
            "card",
            840,
            380,
            400,
            140,
            {
                "Values": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Catalog Share of Max"),
                            "_Metrics.Catalog Share of Max",
                        )
                    ]
                }
            },
        ),
        _visual(
            "card",
            840,
            540,
            400,
            140,
            {
                "Values": {
                    "projections": [
                        _proj(
                            _measure("_Metrics", "Census Sales YoY %"),
                            "_Metrics.Census Sales YoY %",
                        )
                    ]
                }
            },
        ),
    ]

    _write_page(pages_dir, "ExecutiveOverview", "Executive Overview", exec_visuals)
    _write_page(
        pages_dir, "ForecastPerformance", "Forecast vs Actual", forecast_visuals
    )
    _write_page(
        pages_dir, "InventoryPlanning", "Inventory Planning", inventory_visuals
    )
    _write_page(
        pages_dir,
        "SeasonalityContext",
        "Seasonality & Catalog Context",
        season_visuals,
    )

    (pages_dir / "pages.json").write_text(
        json.dumps(
            {
                "$schema": (
                    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
                    "definition/pagesMetadata/1.0.0/schema.json"
                ),
                "pageOrder": [
                    "ExecutiveOverview",
                    "ForecastPerformance",
                    "InventoryPlanning",
                    "SeasonalityContext",
                ],
                "activePageName": "ExecutiveOverview",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (report_def / "version.json").write_text(
        json.dumps(
            {
                "$schema": (
                    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
                    "definition/versionMetadata/1.0.0/schema.json"
                ),
                "version": "1.0.0",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    (report_def / "report.json").write_text(
        json.dumps(
            {
                "$schema": (
                    "https://developer.microsoft.com/json-schemas/fabric/item/report/"
                    "definition/report/1.0.0/schema.json"
                ),
                "themeCollection": {
                    "baseTheme": {
                        "name": "CY24SU10",
                        "reportVersionAtImport": "5.59",
                        "type": "SharedResources",
                    }
                },
                "layoutOptimization": "None",
                "annotations": [
                    {
                        "name": "disclaimer",
                        "value": (
                            "Illustrative planning on Google Trends search-interest "
                            "proxy. Not Amazon warehouse units. Custom MAPE-adjusted "
                            "safety stock — see docs/inventory_methodology.md."
                        ),
                    },
                    {
                        "name": "catalogParityNote",
                        "value": (
                            "DQ-025: Garden catalog 26.4x smaller than Clothing — "
                            "raw counts shown; do not imply parity."
                        ),
                    },
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


# Upgrade definition.pbir for PBIR format support
(DASH / "AmazonIQ.Report" / "definition.pbir").write_text(
    """{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
  "version": "4.0",
  "datasetReference": {
    "byPath": {
      "path": "../AmazonIQ.SemanticModel"
    }
  }
}
""",
    encoding="utf-8",
)

build_report_pages()

print("PBIP semantic model and report written to", DASH)
