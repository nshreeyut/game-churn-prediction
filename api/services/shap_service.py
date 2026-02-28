"""
SHAP Service
=============
Handles loading and formatting SHAP (SHapley Additive exPlanations) values.

WHAT IS SHAP?
-------------
SHAP answers: "WHY did the model predict this player would churn?"

Each feature gets a SHAP value representing its contribution to the prediction:
  - Positive value  → pushed the prediction TOWARD churn
  - Negative value  → pushed the prediction AWAY from churn
  - Larger magnitude = stronger influence on this specific prediction

Example for a high-risk player:
  days_since_last_game: +0.42  ← biggest churn driver
  engagement_score:     +0.31  ← also pushing toward churn
  games_7d:             -0.18  ← slightly protective (still playing some)
  win_rate_7d:          -0.05  ← minor protective factor

HOW SHAP VALUES WERE GENERATED:
---------------------------------
In src/game_churn/models/train.py, after training XGBoost:
  import shap
  explainer = shap.TreeExplainer(xgboost_model)
  shap_values = explainer.shap_values(X_test)
  joblib.dump({"values": shap_values, "player_ids": test_ids}, "models/shap_values.joblib")

So models/shap_values.joblib contains a dict with:
  - "values":     numpy array of shape (n_players, n_features)
  - "player_ids": list of player IDs aligned with the rows

NOTE: If this structure differs from what train.py actually saved,
look at train.py and adjust get_player_shap() accordingly.
"""

import joblib
import numpy as np
from functools import lru_cache

from api.config import settings
from api.services.model_service import FEATURE_COLUMNS

# Human-readable labels for each feature.
# Used by the LangChain agent to generate plain-English explanations.
FEATURE_LABELS = {
    "games_7d":              "Games played in the last 7 days",
    "games_14d":             "Games played in the last 14 days",
    "games_30d":             "Games played in the last 30 days",
    "playtime_hours_7d":     "Hours played in the last 7 days",
    "playtime_hours_14d":    "Hours played in the last 14 days",
    "playtime_hours_30d":    "Hours played in the last 30 days",
    "avg_daily_sessions_7d": "Average daily sessions (last 7 days)",
    "avg_daily_sessions_30d":"Average daily sessions (last 30 days)",
    "max_gap_days_30d":      "Longest break between games (last 30 days)",
    "games_trend_7d_vs_14d": "Activity trend (recent vs earlier — above 0.5 = increasing)",
    "win_rate_7d":           "Win rate in the last 7 days",
    "win_rate_30d":          "Win rate in the last 30 days",
    "current_rating":        "Current skill rating",
    "rating_change_30d":     "Rating change over last 30 days",
    "unique_peers_30d":      "Unique teammates in the last 30 days",
    "games_with_peers_30d":  "Games played with teammates (last 30 days)",
    "engagement_score":      "Overall engagement score (0–100 composite)",
    "days_since_last_game":  "Days since their last game",
}


@lru_cache(maxsize=1)
def load_shap_values():
    """
    Load pre-computed SHAP values from disk (cached after first load).

    TODO: Load and return settings.models_dir / "shap_values.joblib" using joblib.load().
    Raise FileNotFoundError if the file doesn't exist.
    """
    raise NotImplementedError("TODO: implement load_shap_values()")


def get_player_shap(player_id: str, platform: str) -> list[dict] | None:
    """
    Get SHAP feature contributions for a specific player, sorted by impact.

    Returns a list of feature contributions (most impactful first):
    [
        {
            "feature":     "days_since_last_game",
            "label":       "Days since their last game",
            "shap_value":  0.42,
            "direction":   "increases_churn",   # positive SHAP = toward churn
        },
        {
            "feature":     "games_7d",
            "label":       "Games played in the last 7 days",
            "shap_value":  -0.18,
            "direction":   "decreases_churn",   # negative SHAP = away from churn
        },
        ...
    ]

    Returns None if the player isn't found in the SHAP data.

    TODO: Implement this.
    Steps:
      1. shap_data = load_shap_values()
         It's a dict: {"values": np.array, "player_ids": list}
      2. Build a combined key to match the player:
         key = f"{player_id}_{platform}"
         Look it up in shap_data["player_ids"]
      3. If not found, return None
      4. Get the player's SHAP row: shap_data["values"][index]
      5. Pair each SHAP value with its feature name (use FEATURE_COLUMNS for order)
      6. Sort by abs(shap_value) descending
      7. Add "label" from FEATURE_LABELS and "direction" based on sign
      8. Return as a list of dicts
    """
    raise NotImplementedError("TODO: implement get_player_shap()")
