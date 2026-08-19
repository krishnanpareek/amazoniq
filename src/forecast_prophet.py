"""Prophet backtest on Google Trends search interest by category.

Forecast target: weekly U.S. search interest (0-100 index), not catalog or Census sales.
Does not drop partial weeks silently — excludes is_partial=True from fit and test.
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from category_config import CATEGORIES  # noqa: E402

TRENDS_CSV = ROOT / "data" / "processed" / "fact_search_interest.csv"
OUT_FORECAST = ROOT / "data" / "processed" / "fact_forecast_prophet.csv"
OUT_METRICS = ROOT / "data" / "processed" / "fact_forecast_metrics.csv"
OUT_BACKTEST = ROOT / "data" / "processed" / "fact_forecast_backtest.csv"

TEST_WEEKS = 26  # ~6 months holdout
MIN_TRAIN_WEEKS = 52


def mape(actual: pd.Series, predicted: pd.Series) -> float:
    mask = actual.notna() & predicted.notna() & (actual != 0)
    if mask.sum() == 0:
        return float("nan")
    return float((abs(actual[mask] - predicted[mask]) / actual[mask]).mean() * 100)


def weak_reason(category_id: str, mape_val: float, series: pd.DataFrame) -> str | None:
    if pd.isna(mape_val):
        return "insufficient non-zero test points for MAPE"
    reasons: list[str] = []
    if mape_val >= 25:
        reasons.append(f"MAPE {mape_val:.1f}% exceeds 25% threshold")
    if category_id == "electronics":
        reasons.append("April 2026 spike (DQ-011) — atypical vs holiday seasonality")
    if category_id == "health":
        reasons.append("July 2026 spike (DQ-013) — peak outside expected January window")
    if category_id == "garden":
        reasons.append("Strong spring seasonality; keyword 'lawn mower' is narrow vs Census garden analog")
    if series["interest"].std() < 8:
        reasons.append("low volatility (std < 8) — MAPE sensitive to small absolute errors")
    if not reasons and mape_val >= 15:
        reasons.append(f"moderate MAPE {mape_val:.1f}%")
    return "; ".join(reasons) if reasons else None


def fit_category(cat: dict, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    from prophet import Prophet

    sub = df[df["category_id"] == cat["category_id"]].copy()
    sub = sub[~sub["is_partial"].astype(str).str.lower().eq("true")]
    sub["ds"] = pd.to_datetime(sub["week_start"])
    sub["y"] = sub["interest"].astype(float)
    sub = sub.sort_values("ds")

    if len(sub) < MIN_TRAIN_WEEKS + TEST_WEEKS:
        raise ValueError(f"{cat['category_id']}: only {len(sub)} complete weeks")

    train = sub.iloc[: -TEST_WEEKS].copy()
    test = sub.iloc[-TEST_WEEKS:].copy()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = Prophet(
            weekly_seasonality=True,
            yearly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
        )
        model.fit(train[["ds", "y"]])

    future = model.make_future_dataframe(periods=TEST_WEEKS, freq="W-SUN", include_history=False)
    forecast = model.predict(future)
    forecast = forecast.merge(test[["ds", "y"]], on="ds", how="left")

    backtest = forecast[["ds", "y", "yhat", "yhat_lower", "yhat_upper"]].copy()
    backtest["category_id"] = cat["category_id"]
    backtest["category_name"] = cat["name"]
    backtest["keyword"] = cat["trends_keyword"]
    backtest["actual"] = backtest["y"]
    backtest["predicted"] = backtest["yhat"].clip(lower=0)
    backtest["abs_pct_error"] = (
        (backtest["actual"] - backtest["predicted"]).abs() / backtest["actual"].replace(0, pd.NA) * 100
    )
    backtest["source_id"] = "SRC-TRENDS-001"
    backtest["model"] = "prophet"

    mape_val = mape(backtest["actual"], backtest["predicted"])
    metrics = {
        "category_id": cat["category_id"],
        "category_name": cat["name"],
        "keyword": cat["trends_keyword"],
        "model": "prophet",
        "train_weeks": len(train),
        "test_weeks": len(test),
        "test_start": test["ds"].min().date().isoformat(),
        "test_end": test["ds"].max().date().isoformat(),
        "mape_pct": round(mape_val, 2) if pd.notna(mape_val) else None,
        "weak_accuracy_flag": weak_reason(cat["category_id"], mape_val, sub) is not None
        and (pd.isna(mape_val) or mape_val >= 15),
        "weak_accuracy_reason": weak_reason(cat["category_id"], mape_val, sub),
        "source_id": "SRC-TRENDS-001",
    }

    # Full-series refit for forward forecast (same params)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model_full = Prophet(
            weekly_seasonality=True,
            yearly_seasonality=True,
            daily_seasonality=False,
            seasonality_mode="multiplicative",
        )
        model_full.fit(sub[["ds", "y"]])
    future_all = model_full.make_future_dataframe(periods=13, freq="W-SUN")
    fc_all = model_full.predict(future_all)
    fc_all["category_id"] = cat["category_id"]
    fc_all["category_name"] = cat["name"]
    fc_all["keyword"] = cat["trends_keyword"]
    fc_all["source_id"] = "SRC-TRENDS-001"
    fc_all["model"] = "prophet"

    return backtest, fc_all, metrics


def main() -> None:
    df = pd.read_csv(TRENDS_CSV)
    backtests: list[pd.DataFrame] = []
    forecasts: list[pd.DataFrame] = []
    metrics_rows: list[dict] = []

    for cat in CATEGORIES:
        print(f"fitting {cat['category_id']} ({cat['trends_keyword']}) ...")
        bt, fc, m = fit_category(cat, df)
        backtests.append(bt)
        forecasts.append(fc)
        metrics_rows.append(m)
        print(f"  MAPE={m['mape_pct']}% weak={m['weak_accuracy_flag']}")

    backtest_df = pd.concat(backtests, ignore_index=True)
    forecast_df = pd.concat(forecasts, ignore_index=True)
    metrics_df = pd.DataFrame(metrics_rows)

    OUT_BACKTEST.parent.mkdir(parents=True, exist_ok=True)
    backtest_df.to_csv(OUT_BACKTEST, index=False)
    forecast_df.to_csv(OUT_FORECAST, index=False)
    metrics_df.to_csv(OUT_METRICS, index=False)

    print(f"\nwrote {OUT_BACKTEST}")
    print(f"wrote {OUT_FORECAST}")
    print(f"wrote {OUT_METRICS}")
    print("\nMAPE by category:")
    print(metrics_df[["category_id", "mape_pct", "weak_accuracy_flag", "weak_accuracy_reason"]].to_string(index=False))


if __name__ == "__main__":
    main()
