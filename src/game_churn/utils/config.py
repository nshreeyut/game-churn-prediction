"""Project configuration and settings."""

from pathlib import Path

from pydantic import AliasChoices, Field
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

    # validation_alias overrides the GAME_CHURN_ prefix so both configs
    # and .env.example can use the same bare key names
    steam_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("STEAM_API_KEY", "GAME_CHURN_STEAM_API_KEY"),
        description="Steam Web API key",
    )
    rawg_api_key: str = Field(
        default="",
        validation_alias=AliasChoices("GAME_CHURN_RAWG_API_KEY", "RAWG_API_KEY"),
        description="RAWG.io API key",
    )
    # OpenDota needs no key

    churn_threshold_days: int = Field(default=14, description="Days inactive to label as churned")
    request_timeout: int = Field(default=30, description="HTTP request timeout in seconds")
    max_retries: int = Field(default=3, description="Max API request retries")


settings = Settings()
