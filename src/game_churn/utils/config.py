"""Project configuration and settings."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "01_raw"
PROCESSED_DIR = DATA_DIR / "02_processed"
FEATURES_DIR = DATA_DIR / "03_features"
PREDICTIONS_DIR = DATA_DIR / "04_predictions"
MODELS_DIR = PROJECT_ROOT / "models"
MLFLOW_DIR = PROJECT_ROOT / ".mlflow"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = {"env_prefix": "GAME_CHURN_", "env_file": ".env"}

    riot_api_key: str = Field(default="", description="Riot Games API key")
    rawg_api_key: str = Field(default="", description="RAWG.io API key")

    churn_threshold_days: int = Field(default=14, description="Days inactive to label as churned")
    request_timeout: int = Field(default=30, description="HTTP request timeout in seconds")
    max_retries: int = Field(default=3, description="Max API request retries")


settings = Settings()
