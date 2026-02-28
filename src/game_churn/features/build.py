"""Build features from raw data and save to disk.

Usage: python -m game_churn.features.build
"""

from __future__ import annotations

import logging

import polars as pl

from game_churn.features.engineer import build_features_for_player
from game_churn.features.standardize import load_all_activities
from game_churn.utils.config import FEATURES_DIR, RAW_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def build_all_features() -> pl.DataFrame:
    """Load raw data, standardize, and build features for all players."""
    log.info("Loading and standardizing raw activity data...")
    activities = load_all_activities()

    if activities.is_empty():
        log.warning("No activity data found. Run collectors first.")
        return pl.DataFrame()

    log.info("Loaded %d activity records", len(activities))

    # Get unique player-platform combos
    player_platforms = activities.select("player_id", "platform").unique().to_dicts()
    log.info("Building features for %d players...", len(player_platforms))

    all_features: list[dict] = []
    for pp in player_platforms:
        features = build_features_for_player(
            activities,
            pp["player_id"],
            pp["platform"],
            raw_dir=RAW_DIR,
        )
        all_features.append(features)

    features_df = pl.DataFrame(all_features)

    # Save
    FEATURES_DIR.mkdir(parents=True, exist_ok=True)
    output_path = FEATURES_DIR / "player_features.parquet"
    features_df.write_parquet(output_path)
    log.info(
        "Saved features to %s (%d rows, %d cols)",
        output_path,
        len(features_df),
        len(features_df.columns),
    )

    return features_df


if __name__ == "__main__":
    build_all_features()
