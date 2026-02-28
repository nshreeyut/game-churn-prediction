"""Chess.com public API collector.

API docs: https://www.chess.com/news/view/published-data-api
No authentication required.
"""

from __future__ import annotations

from pathlib import Path

from game_churn.collectors.base import BaseCollector

BASE_URL = "https://api.chess.com/pub/player"


class ChessComCollector(BaseCollector):
    """Collect player data from Chess.com public API."""

    platform = "chess_com"

    def __init__(self) -> None:
        super().__init__()
        self.client.headers.update({"User-Agent": "game-churn-prediction/0.1"})

    def get_profile(self, username: str) -> dict:
        """Fetch player profile."""
        return self._get(f"{BASE_URL}/{username}")

    def get_stats(self, username: str) -> dict:
        """Fetch player stats (ratings across time controls)."""
        return self._get(f"{BASE_URL}/{username}/stats")

    def get_monthly_archives(self, username: str) -> list[str]:
        """Get list of monthly archive URLs."""
        data = self._get(f"{BASE_URL}/{username}/games/archives")
        return data.get("archives", [])

    def get_games_for_month(self, archive_url: str) -> dict:
        """Fetch games for a specific monthly archive."""
        return self._get(archive_url)

    def collect(self, player_id: str) -> list[Path]:
        """Collect all available data for a Chess.com player.

        Args:
            player_id: Chess.com username

        Returns:
            List of saved file paths
        """
        saved: list[Path] = []
        username = player_id.lower()

        profile = self.get_profile(username)
        saved.append(self._save_json(profile, f"{username}_profile.json"))

        stats = self.get_stats(username)
        saved.append(self._save_json(stats, f"{username}_stats.json"))

        archives = self.get_monthly_archives(username)
        all_games: list[dict] = []
        # Collect last 6 months of games to keep data manageable
        for archive_url in archives[-6:]:
            month_data = self.get_games_for_month(archive_url)
            games = month_data.get("games", [])
            all_games.extend(games)

        saved.append(self._save_json(all_games, f"{username}_games.json"))
        return saved
