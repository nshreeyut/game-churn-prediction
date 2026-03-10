"""
API Configuration
==================
All settings are loaded from environment variables so secrets (API keys)
never live in your code.

In development: create a .env file in the project root (see .env.example)
In production:  set environment variables in Render's dashboard

We use pydantic-settings — same library the ML pipeline uses.
It reads .env automatically and validates types for you.
"""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings

# Navigate from api/config.py → api/ → project root
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # Game Data API Keys
    # ---------------------------------------------------------
    steam_api_key: str = ""
    game_churn_rawg_api_key: str = ""
    # OpenDota needs no key

    # ---------------------------------------------------------
    # LLM Configuration
    # ---------------------------------------------------------
    # Switch provider via LLM_PROVIDER env var: "groq" or "openai"
    # Switch model via LLM_MODEL env var
    # Defaults to Groq + llama-3.3-70b-versatile (free, fast, good tool-calling)
    llm_provider: Literal["groq", "openai"] = "groq"
    llm_model: str = "llama-3.3-70b-versatile"

    groq_api_key: str = ""
    openai_api_key: str = ""

    # ---------------------------------------------------------
    # CORS Configuration
    # ---------------------------------------------------------
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ---------------------------------------------------------
    # Paths
    # ---------------------------------------------------------
    models_dir: Path = PROJECT_ROOT / "models"
    data_dir: Path = PROJECT_ROOT / "data"
    studios_dir: Path = PROJECT_ROOT / "data" / "studios"

    # Legacy path — used by demo studio (OpenDota + RAWG data)
    features_path: Path = PROJECT_ROOT / "data" / "03_features" / "player_features.parquet"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()


def get_llm(streaming: bool = False):
    """
    Factory that returns the configured LLM.
    Swap provider/model entirely via env vars — no code changes needed.

    Usage:
        llm = get_llm()                  # standard
        llm = get_llm(streaming=True)    # for streaming chat responses
    """
    if settings.llm_provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=settings.llm_model,
            api_key=settings.groq_api_key,
            streaming=streaming,
        )

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
        streaming=streaming,
    )
