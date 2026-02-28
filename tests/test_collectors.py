"""Tests for data collectors."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from game_churn.collectors.chess_com import ChessComCollector
from game_churn.collectors.opendota import OpenDotaCollector
from game_churn.collectors.riot import RiotCollector


def test_chess_com_collect(tmp_path: object) -> None:
    """Test Chess.com collector produces expected files."""
    with patch.object(ChessComCollector, "_get") as mock_get:
        mock_get.side_effect = [
            {"username": "testuser", "player_id": 1},  # profile
            {"chess_rapid": {"last": {"rating": 1500}}},  # stats
            {"archives": ["https://api.chess.com/pub/player/testuser/games/2024/01"]},
            {"games": [{"url": "game1", "end_time": 1700000000}]},  # month games
        ]
        collector = ChessComCollector()
        collector.output_dir = tmp_path  # type: ignore[assignment]
        paths = collector.collect("testuser")
        assert len(paths) == 3
        assert all(p.exists() for p in paths)


def test_opendota_collect(tmp_path: object) -> None:
    """Test OpenDota collector produces expected files."""
    with patch.object(OpenDotaCollector, "_get") as mock_get:
        mock_get.side_effect = [
            {"profile": {"account_id": 12345}},  # player
            {"win": 100, "lose": 50},  # wl
            [{"match_id": 1, "player_slot": 0}],  # matches
            [{"account_id": 99, "games": 10}],  # peers
            [{"account_id": 12345, "solo_competitive_rank": 3000}],  # ratings
        ]
        collector = OpenDotaCollector()
        collector.output_dir = tmp_path  # type: ignore[assignment]
        paths = collector.collect("12345")
        assert len(paths) == 5


def test_riot_collect_requires_hash() -> None:
    """Test Riot collector requires GameName#TagLine format."""
    import pytest

    collector = RiotCollector()
    with pytest.raises(ValueError, match="GameName#TagLine"):
        collector.collect("InvalidNoHash")


def test_riot_collect(tmp_path: object) -> None:
    """Test Riot collector produces expected files."""
    with patch.object(RiotCollector, "_get") as mock_get:
        mock_get.side_effect = [
            {"puuid": "abc123", "gameName": "Test", "tagLine": "NA1"},  # account
            {"id": "summ1", "puuid": "abc123", "accountId": "acc1"},  # summoner
            [{"queueType": "RANKED_SOLO_5x5", "tier": "GOLD"}],  # league
            ["NA1_123", "NA1_456"],  # match ids
            {"info": {"gameId": 123}},  # match 1
            {"info": {"gameId": 456}},  # match 2
        ]
        collector = RiotCollector()
        collector.output_dir = tmp_path  # type: ignore[assignment]
        mock_client = MagicMock()
        mock_client.headers = {}
        collector.client = mock_client
        # Re-patch _get since we replaced client
        with patch.object(collector, "_get", side_effect=mock_get.side_effect):
            paths = collector.collect("Test#NA1")
            assert len(paths) == 5
