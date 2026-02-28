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
from pydantic_settings import BaseSettings

# Navigate from api/config.py → api/ → project root
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    # ---------------------------------------------------------
    # LLM Configuration
    # ---------------------------------------------------------
    # The LangChain agent needs an LLM to power the chatbot.
    # We use OpenAI by default — you can swap the model in agents/churn_analyst.py.
    # gpt-4o-mini is cheap and fast; upgrade to gpt-4o for better reasoning.
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # ---------------------------------------------------------
    # CORS Configuration
    # ---------------------------------------------------------
    # Which frontend URLs are allowed to call this API.
    # In dev: Vite runs on 5173. In prod: your Vercel deployment URL.
    #
    # TODO: Add your Vercel URL here before deploying:
    #   "https://your-app.vercel.app"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # ---------------------------------------------------------
    # Paths — computed from PROJECT_ROOT, no need to change these
    # ---------------------------------------------------------
    models_dir: Path = PROJECT_ROOT / "models"
    data_dir: Path = PROJECT_ROOT / "data"
    features_path: Path = PROJECT_ROOT / "data" / "03_features" / "player_features.parquet"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
