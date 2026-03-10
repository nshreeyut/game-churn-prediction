"""Demo Service
==============
Serves synthetic player data for demo mode.

This is completely separate from the real data pipeline.
It is only called by api/routers/demo.py — never by production routes.

On first call, _load_demo_assets() generates 50 synthetic players,
runs them through the real trained models, computes SHAP values, and
caches everything in memory. Subsequent calls are instant.

The frontend shows a clear "DEMO MODE" banner when using these endpoints
so users always know they are looking at synthetic data.
"""

from __future__ import annotations

from functools import lru_cache

import joblib
import numpy as np
import polars as pl

from game_churn.models.synthetic import generate_synthetic_data
from game_churn.utils.config import MODELS_DIR

# Must match the exact column order used in train.py
FEATURE_COLS = [
    "games_7d",
    "games_14d",
    "games_30d",
    "playtime_7d_hours",
    "playtime_14d_hours",
    "playtime_30d_hours",
    "avg_daily_sessions_7d",
    "avg_daily_sessions_14d",
    "avg_daily_sessions_30d",
    "max_gap_days_30d",
    "games_trend_7d_vs_14d",
    "playtime_trend_7d_vs_14d",
    "win_rate_7d",
    "win_rate_30d",
    "rating_change_30d",
    "unique_peers_30d",
    "peer_games_30d",
    "engagement_score",
    "days_since_last_game",
]

FEATURE_LABELS: dict[str, str] = {
    "days_since_last_game": "Days Since Last Game",
    "engagement_score": "Engagement Score",
    "games_7d": "Games (Last 7 Days)",
    "games_14d": "Games (Last 14 Days)",
    "games_30d": "Games (Last 30 Days)",
    "playtime_7d_hours": "Playtime Hours (7 Days)",
    "playtime_14d_hours": "Playtime Hours (14 Days)",
    "playtime_30d_hours": "Playtime Hours (30 Days)",
    "avg_daily_sessions_7d": "Avg Daily Sessions (7 Days)",
    "avg_daily_sessions_14d": "Avg Daily Sessions (14 Days)",
    "avg_daily_sessions_30d": "Avg Daily Sessions (30 Days)",
    "max_gap_days_30d": "Max Inactivity Gap (Days)",
    "games_trend_7d_vs_14d": "Activity Trend (7d vs 14d)",
    "playtime_trend_7d_vs_14d": "Playtime Trend (7d vs 14d)",
    "win_rate_7d": "Win Rate (7 Days)",
    "win_rate_30d": "Win Rate (30 Days)",
    "rating_change_30d": "Rating Change (30 Days)",
    "unique_peers_30d": "Unique Teammates (30 Days)",
    "peer_games_30d": "Games with Teammates (30 Days)",
}


def _risk_label(prob: float) -> str:
    if prob > 0.7:
        return "High"
    if prob > 0.4:
        return "Medium"
    return "Low"


@lru_cache(maxsize=1)
def _load_demo_assets() -> tuple[pl.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """Generate synthetic players, score them, compute SHAP. Cached after first call."""
    import shap

    df = generate_synthetic_data(n_players=50, seed=42)

    scaler = joblib.load(MODELS_DIR / "scaler.joblib")
    ensemble = joblib.load(MODELS_DIR / "ensemble.joblib")
    xgb = joblib.load(MODELS_DIR / "xgboost.joblib")

    X = df.select(FEATURE_COLS).fill_null(0).to_numpy()
    X_scaled = scaler.transform(X)

    probas = ensemble.predict_proba(X_scaled)[:, 1]

    explainer = shap.TreeExplainer(xgb)
    shap_values = explainer.shap_values(X_scaled)

    return df, X_scaled, probas, shap_values


def _format_shap(shap_row: np.ndarray) -> list[dict]:
    """Convert a SHAP values array into a sorted, labelled list."""
    pairs = [
        {
            "feature": col,
            "label": FEATURE_LABELS.get(col, col),
            "shap_value": round(float(shap_row[i]), 4),
            "direction": "increases_churn" if shap_row[i] > 0 else "decreases_churn",
        }
        for i, col in enumerate(FEATURE_COLS)
    ]
    return sorted(pairs, key=lambda x: abs(x["shap_value"]), reverse=True)[:8]


def list_demo_players(platform: str | None = None, limit: int = 20) -> list[dict]:
    """Return a list of demo players with basic churn info.

    Args:
        platform: filter by "opendota" or "steam" (None = all)
        limit:    max players to return
    """
    df, _, probas, _ = _load_demo_assets()
    rows = df.to_dicts()

    results = []
    for i, row in enumerate(rows):
        if platform and row.get("platform") != platform:
            continue
        prob = float(probas[i])
        results.append({
            "player_id": row["player_id"],
            "platform": row["platform"],
            "churn_probability": round(prob, 4),
            "risk_level": _risk_label(prob),
            "days_since_last_game": row["days_since_last_game"],
            "engagement_score": row["engagement_score"],
        })
        if len(results) >= limit:
            break

    return sorted(results, key=lambda x: x["churn_probability"], reverse=True)


def get_demo_player(player_id: str) -> dict | None:
    """Return full analytics for a single demo player including SHAP.

    Args:
        player_id: synthetic player ID e.g. "synthetic_0"

    Returns:
        Full player dict with prediction + shap_values, or None if not found
    """
    df, _, probas, shap_values = _load_demo_assets()
    rows = df.to_dicts()

    for i, row in enumerate(rows):
        if row["player_id"] != player_id:
            continue

        prob = float(probas[i])
        return {
            **row,
            "churn_probability": round(prob, 4),
            "churn_predicted": prob >= 0.5,
            "risk_level": _risk_label(prob),
            "model_used": "ensemble",
            "shap_values": _format_shap(shap_values[i]),
            "_demo": True,
        }

    return None


def get_demo_summary() -> dict:
    """Return fleet-level stats across all demo players."""
    df, _, probas, _ = _load_demo_assets()

    total = len(probas)
    churned = int(np.sum(probas >= 0.5))
    high_risk = int(np.sum(probas > 0.7))
    medium_risk = int(np.sum((probas > 0.4) & (probas <= 0.7)))
    low_risk = int(np.sum(probas <= 0.4))

    platform_counts = df.group_by("platform").agg(pl.len().alias("count")).to_dicts()

    return {
        "total_players": total,
        "churn_rate": round(churned / total, 3),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "avg_churn_probability": round(float(np.mean(probas)), 3),
        "platforms": {row["platform"]: row["count"] for row in platform_counts},
        "_demo": True,
    }
