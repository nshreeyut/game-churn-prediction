"""Prefect pipeline orchestration for the game churn prediction workflow."""

from __future__ import annotations

import logging

from prefect import flow, task

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


@task(name="collect-data", retries=2, retry_delay_seconds=30)
def collect_data() -> None:
    """Run all API data collectors."""
    from game_churn.collectors.run_all import main as run_collectors

    run_collectors()


@task(name="build-features")
def build_features() -> None:
    """Build feature set from raw data."""
    from game_churn.features.build import build_all_features

    build_all_features()


@task(name="train-models")
def train_models() -> None:
    """Train all ML models."""
    from game_churn.models.train import main as run_training

    run_training()


@flow(name="game-churn-pipeline", log_prints=True)
def churn_pipeline(skip_collection: bool = False) -> None:
    """Full churn prediction pipeline.

    Args:
        skip_collection: If True, skip data collection and use existing raw data.
    """
    if not skip_collection:
        collect_data()

    build_features()
    train_models()

    log.info("Pipeline complete!")


if __name__ == "__main__":
    churn_pipeline()
