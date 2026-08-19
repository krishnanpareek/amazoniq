"""Compute MAPE-adjusted safety stock and reorder points from Prophet backtest.

95% service level is explicit (z = 1.645). Safety stock widens per category MAPE;
high-MAPE categories also receive an uncertainty tier flag.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from category_config import CATEGORIES  # noqa: E402

# --- Stated assumptions (documented in docs/inventory_methodology.md) ---
SERVICE_LEVEL = 0.95
Z_SCORE_95 = 1.645  # one-sided normal for 95% cycle service level
LEAD_TIME_WEEKS = 2
ROLLING_WINDOW = 4

METRICS_CSV = ROOT / "data" / "processed" / "fact_forecast_metrics.csv"
BACKTEST_CSV = ROOT / "data" / "processed" / "fact_forecast_backtest.csv"
TRENDS_CSV = ROOT / "data" / "processed" / "fact_search_interest.csv"
OUT_PLAN = ROOT / "data" / "processed" / "fact_inventory_planning.csv"
OUT_ROLLING = ROOT / "data" / "processed" / "fact_rolling_forecast_error.csv"


def uncertainty_tier(mape_pct: float) -> str:
    if mape_pct >= 25:
        return "high"
    if mape_pct >= 15:
        return "elevated"
    return "standard"


def rolling_mape(actual: pd.Series, predicted: pd.Series, window: int) -> pd.Series:
    def _mape(a: np.ndarray, p: np.ndarray) -> float:
        mask = (a != 0) & ~np.isnan(a) & ~np.isnan(p)
        if mask.sum() == 0:
            return np.nan
        return float(np.mean(np.abs(a[mask] - p[mask]) / a[mask]) * 100)

    out = []
    for i in range(len(actual)):
        if i + 1 < window:
            out.append(np.nan)
        else:
            a = actual.iloc[i - window + 1 : i + 1].to_numpy()
            p = predicted.iloc[i - window + 1 : i + 1].to_numpy()
            out.append(_mape(a, p))
    return pd.Series(out, index=actual.index)


def main() -> None:
    metrics = pd.read_csv(METRICS_CSV)
    backtest = pd.read_csv(BACKTEST_CSV)
    trends = pd.read_csv(TRENDS_CSV)
    trends = trends[~trends["is_partial"].astype(str).str.lower().eq("true")]

    rolling_frames: list[pd.DataFrame] = []
    plan_rows: list[dict] = []

    for cat in CATEGORIES:
        cid = cat["category_id"]
        m = metrics[metrics["category_id"] == cid].iloc[0]
        mape_pct = float(m["mape_pct"])

        bt = backtest[backtest["category_id"] == cid].sort_values("ds").copy()
        bt["forecast_error"] = bt["actual"] - bt["predicted"]
        sigma_backtest = float(bt["forecast_error"].std(ddof=1))

        mape_multiplier = 1.0 + mape_pct / 100.0
        sigma_adjusted = sigma_backtest * mape_multiplier

        safety_stock = Z_SCORE_95 * sigma_adjusted * np.sqrt(LEAD_TIME_WEEKS)

        act = trends[trends["category_id"] == cid].sort_values("week_start")
        recent = act.tail(ROLLING_WINDOW)
        avg_weekly_demand = float(recent["interest"].mean())

        demand_during_lead_time = avg_weekly_demand * LEAD_TIME_WEEKS
        reorder_point = demand_during_lead_time + safety_stock

        tier = uncertainty_tier(mape_pct)
        high_uncertainty_flag = tier == "high"

        plan_rows.append(
            {
                "category_id": cid,
                "category_name": cat["name"],
                "keyword": cat["trends_keyword"],
                "service_level_pct": SERVICE_LEVEL * 100,
                "z_score": Z_SCORE_95,
                "lead_time_weeks": LEAD_TIME_WEEKS,
                "avg_weekly_demand_proxy": round(avg_weekly_demand, 2),
                "demand_during_lead_time": round(demand_during_lead_time, 2),
                "forecast_error_std_backtest": round(sigma_backtest, 4),
                "mape_pct_baseline": round(mape_pct, 2),
                "mape_buffer_multiplier": round(mape_multiplier, 4),
                "forecast_error_std_adjusted": round(sigma_adjusted, 4),
                "safety_stock": round(safety_stock, 2),
                "reorder_point": round(reorder_point, 2),
                "uncertainty_tier": tier,
                "high_uncertainty_flag": high_uncertainty_flag,
                "metric_label": "modeled",
                "assumption_note": (
                    f"95% service level (z={Z_SCORE_95}); "
                    f"{LEAD_TIME_WEEKS}-week lead time; "
                    f"σ widened by MAPE multiplier {mape_multiplier:.3f}"
                ),
                "source_id": "SRC-TRENDS-001",
            }
        )

        bt["rolling_mape_4w"] = rolling_mape(bt["actual"], bt["predicted"], ROLLING_WINDOW)
        bt["forecast_error_abs"] = (bt["actual"] - bt["predicted"]).abs()
        bt["forecast_error_pct"] = bt["abs_pct_error"]
        bt["uncertainty_tier"] = tier
        rolling_frames.append(
            bt[
                [
                    "ds",
                    "category_id",
                    "category_name",
                    "keyword",
                    "actual",
                    "predicted",
                    "forecast_error",
                    "forecast_error_abs",
                    "forecast_error_pct",
                    "rolling_mape_4w",
                    "uncertainty_tier",
                    "source_id",
                    "model",
                ]
            ]
        )

    plan_df = pd.DataFrame(plan_rows)
    rolling_df = pd.concat(rolling_frames, ignore_index=True)

    OUT_PLAN.parent.mkdir(parents=True, exist_ok=True)
    plan_df.to_csv(OUT_PLAN, index=False)
    rolling_df.to_csv(OUT_ROLLING, index=False)

    print(f"wrote {OUT_PLAN}")
    print(f"wrote {OUT_ROLLING}")
    print("\nInventory planning summary:")
    cols = [
        "category_id",
        "mape_pct_baseline",
        "mape_buffer_multiplier",
        "safety_stock",
        "reorder_point",
        "uncertainty_tier",
        "high_uncertainty_flag",
    ]
    print(plan_df[cols].to_string(index=False))


if __name__ == "__main__":
    main()
