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

    def get_game_reviews(self, game_id: int | str, page: int = 1, page_size: int = 20) -> dict:
        """Fetch one page of user reviews for a game.

        Args:
            game_id: RAWG game ID or slug
            page: Page number (1-indexed)
            page_size: Results per page (max 40)
        """
        return self._get(
            f"{BASE_URL}/games/{game_id}/reviews",
            params={"key": settings.rawg_api_key, "page": page, "page_size": page_size},
        )

    def get_all_reviews(self, game_id: int | str, max_pages: int = 5) -> list[dict]:
        """Fetch multiple pages of reviews and return a flat list.

        Args:
            game_id: RAWG game ID or slug
            max_pages: Maximum number of pages to fetch (each page = 20 reviews)

        Returns:
            Flat list of review objects
        """
        reviews: list[dict] = []
        for page in range(1, max_pages + 1):
            data = self.get_game_reviews(game_id, page=page)
            results = data.get("results", [])
            reviews.extend(results)
            if not data.get("next"):
                break
        return reviews

    def collect(self, player_id: str, max_review_pages: int = 5) -> list[Path]:
        """Collect game metadata and reviews. player_id is treated as a game slug.

        Args:
            player_id: Game slug (e.g., 'dota-2', 'chess')
            max_review_pages: Number of review pages to fetch (20 reviews each)

        Returns:
            List of saved file paths
        """
        saved: list[Path] = []
        slug = player_id.lower()

        game = self.get_game_by_slug(slug)
        saved.append(self._save_json(game, f"{slug}_metadata.json"))

        reviews = self.get_all_reviews(slug, max_pages=max_review_pages)
        saved.append(self._save_json(reviews, f"{slug}_reviews.json"))

        return saved
