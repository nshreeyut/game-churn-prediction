"""
Model Service
==============
Handles loading trained ML models from disk and running predictions.

WHY A SERVICE LAYER?
---------------------
Routers (api/routers/) handle HTTP concerns: parsing requests, returning responses.
Services handle business logic: loading models, making predictions, crunching numbers.

Keeping these separate means:
  - You can test prediction logic without spinning up an HTTP server
  - You can swap the model loading library without touching any router
  - Code stays readable as the project grows

HOW PREDICTIONS WORK (end to end):
------------------------------------
1. load_model()  — reads the .joblib file once, caches it in memory
2. load_scaler() — reads the StandardScaler fitted during training
3. predict_churn() is called with a player's features dict
4. Features are arranged into the correct column order
5. Scaled with the same scaler used in training (CRITICAL — wrong scaler = bad predictions)
6. model.predict_proba() returns [[prob_not_churn, prob_churn]]
7. We extract prob_churn, add a risk label, and return

CACHING WITH @lru_cache:
-------------------------
@lru_cache(maxsize=None) memoizes the function — it only runs ONCE per unique
argument. After that, it returns the cached result instantly.
This matters because joblib.load() reads from disk, which is slow.
Without caching, every prediction request would reload the model file.
"""

import joblib
import numpy as np
from functools import lru_cache

from api.registry.model_registry import MODEL_REGISTRY, DEFAULT_MODEL, get_model_info
from api.config import settings

# The feature columns in the exact order the model was trained on.
# IMPORTANT: The model expects features in this specific order.
# If you add or remove features in the ML pipeline, update this list.
# Check src/game_churn/models/train.py to find the original column order.
FEATURE_COLUMNS = [
    "games_7d",
    "games_14d",
    "games_30d",
    "playtime_hours_7d",
    "playtime_hours_14d",
    "playtime_hours_30d",
    "avg_daily_sessions_7d",
    "avg_daily_sessions_30d",
    "max_gap_days_30d",
    "games_trend_7d_vs_14d",
    "win_rate_7d",
    "win_rate_30d",
    "current_rating",
    "rating_change_30d",
    "unique_peers_30d",
    "games_with_peers_30d",
    "engagement_score",
    "days_since_last_game",
]


@lru_cache(maxsize=None)
def load_model(model_id: str = DEFAULT_MODEL):
    """
    Load a registered model from disk and cache it in memory.

    @lru_cache means the .joblib file is only read from disk ONCE per model_id.
    Every subsequent call returns the in-memory object instantly.

    TODO: Implement this function.
    Steps:
      1. Call get_model_info(model_id) to get the model's path
      2. Check that the path exists — raise FileNotFoundError with a helpful
         message if it doesn't (hint: tell them to run `make train`)
      3. Use joblib.load(path) to deserialize the model
      4. Return the model object
    """
    raise NotImplementedError("TODO: implement load_model()")


@lru_cache(maxsize=1)
def load_scaler():
    """
    Load the StandardScaler fitted during training.

    CRITICAL: You must use the EXACT scaler from training.
    The scaler subtracts the training mean and divides by training std deviation.
    If you use a different scaler (or no scaler), the model sees different numbers
    than it was trained on and predictions will be meaningless.

    TODO: Load and return settings.models_dir / "scaler.joblib" using joblib.load().
    Raise FileNotFoundError if it doesn't exist.
    """
    raise NotImplementedError("TODO: implement load_scaler()")


def predict_churn(features: dict, model_id: str = DEFAULT_MODEL) -> dict:
    """
    Given a player's features, return a churn prediction.

    Args:
        features: dict of {feature_name: value} — all keys in FEATURE_COLUMNS
        model_id: which registered model to use (default: ensemble)

    Returns:
        {
            "churn_probability": 0.73,   # float between 0 and 1
            "churn_predicted": True,      # True if probability >= 0.5
            "risk_level": "High",         # "Low" / "Medium" / "High"
            "model_used": "ensemble"
        }

    TODO: Implement this function.
    Steps:
      1. Call load_model(model_id) and load_scaler()
      2. Build a numpy array from `features` in FEATURE_COLUMNS order:
             values = [features.get(col, 0) for col in FEATURE_COLUMNS]
             X = np.array(values).reshape(1, -1)
      3. Scale: X_scaled = scaler.transform(X)
      4. Predict: proba = model.predict_proba(X_scaled)[0][1]  ← index 1 = churn prob
      5. Determine risk_level:
             < 0.4  → "Low"
             0.4–0.7 → "Medium"
             > 0.7  → "High"
      6. Return the dict described above
    """
    raise NotImplementedError("TODO: implement predict_churn()")
