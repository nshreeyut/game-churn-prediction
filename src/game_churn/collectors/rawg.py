"""RAWG.io game metadata API collector.

API docs: https://rawg.io/apidocs
Requires RAWG_API_KEY in environment / .env file.
"""

from __future__ import annotations

from pathlib import Path

from game_churn.collectors.base import BaseCollector
from game_churn.utils.config import settings

BASE_URL = "https://api.rawg.io/api"


class RawgCollector(BaseCollector):
    """Collect game metadata from RAWG.io API."""

    platform = "rawg"

    def search_game(self, query: str, page_size: int = 5) -> dict:
        """Search for games by name."""
        return self._get(
            f"{BASE_URL}/games",
            params={"key": settings.rawg_api_key, "search": query, "page_size": page_size},
        )

    def get_game(self, game_id: int) -> dict:
        """Fetch detailed game metadata."""
        return self._get(
            f"{BASE_URL}/games/{game_id}",
            params={"key": settings.rawg_api_key},
        )

    def get_game_by_slug(self, slug: str) -> dict:
        """Fetch game by slug (e.g., 'dota-2', 'league-of-legends')."""
        return self._get(
            f"{BASE_URL}/games/{slug}",
            params={"key": settings.rawg_api_key},
        )

    def collect(self, player_id: str) -> list[Path]:
        """Collect game metadata. player_id is treated as a game slug.

        Args:
            player_id: Game slug (e.g., 'dota-2', 'chess')

        Returns:
            List of saved file paths
        """
        saved: list[Path] = []
        slug = player_id.lower()

        game = self.get_game_by_slug(slug)
        saved.append(self._save_json(game, f"{slug}_metadata.json"))

        return saved
