"""Riot Games (League of Legends) API collector.

API docs: https://developer.riotgames.com/
Requires RIOT_API_KEY in environment / .env file.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from game_churn.collectors.base import BaseCollector
from game_churn.utils.config import settings

AMERICAS_URL = "https://americas.api.riotgames.com"
NA1_URL = "https://na1.api.riotgames.com"


class RiotCollector(BaseCollector):
    """Collect player data from Riot Games API (League of Legends)."""

    platform = "riot_lol"

    def __init__(self, region_url: str = NA1_URL, routing_url: str = AMERICAS_URL) -> None:
        super().__init__()
        self.region_url = region_url
        self.routing_url = routing_url
        if settings.riot_api_key:
            self.client.headers.update({"X-Riot-Token": settings.riot_api_key})

    def _get_riot(self, base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
        return self._get(f"{base_url}{path}", params=params)

    def get_account_by_riot_id(self, game_name: str, tag_line: str) -> dict:
        """Fetch account by Riot ID (gameName#tagLine)."""
        return self._get_riot(
            self.routing_url,
            f"/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}",
        )

    def get_summoner_by_puuid(self, puuid: str) -> dict:
        """Fetch summoner profile by PUUID."""
        return self._get_riot(
            self.region_url,
            f"/lol/summoner/v4/summoners/by-puuid/{puuid}",
        )

    def get_league_entries(self, summoner_id: str) -> list[dict]:
        """Fetch ranked league entries."""
        return self._get_riot(
            self.region_url,
            f"/lol/league/v4/entries/by-summoner/{summoner_id}",
        )

    def get_match_ids(self, puuid: str, count: int = 100, start: int = 0) -> list[str]:
        """Fetch list of match IDs."""
        return self._get_riot(
            self.routing_url,
            f"/lol/match/v5/matches/by-puuid/{puuid}/ids",
            params={"count": min(count, 100), "start": start},
        )

    def get_match(self, match_id: str) -> dict:
        """Fetch match details."""
        return self._get_riot(
            self.routing_url,
            f"/lol/match/v5/matches/{match_id}",
        )

    def collect(self, player_id: str) -> list[Path]:
        """Collect all data for a LoL player.

        Args:
            player_id: Riot ID in format 'GameName#TagLine'

        Returns:
            List of saved file paths
        """
        saved: list[Path] = []

        if "#" not in player_id:
            raise ValueError("player_id must be in 'GameName#TagLine' format")

        game_name, tag_line = player_id.split("#", 1)
        safe_name = f"{game_name}_{tag_line}".lower()

        account = self.get_account_by_riot_id(game_name, tag_line)
        saved.append(self._save_json(account, f"{safe_name}_account.json"))
        puuid = account["puuid"]

        summoner = self.get_summoner_by_puuid(puuid)
        saved.append(self._save_json(summoner, f"{safe_name}_summoner.json"))

        league = self.get_league_entries(summoner["id"])
        saved.append(self._save_json(league, f"{safe_name}_league.json"))

        match_ids = self.get_match_ids(puuid, count=100)
        saved.append(self._save_json(match_ids, f"{safe_name}_match_ids.json"))

        # Fetch details for last 20 matches to avoid rate limits
        matches = []
        for mid in match_ids[:20]:
            try:
                match_data = self.get_match(mid)
                matches.append(match_data)
            except Exception:
                continue
        saved.append(self._save_json(matches, f"{safe_name}_matches.json"))

        return saved
