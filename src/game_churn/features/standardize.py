"""Standardize raw API data into unified PlayerActivity records."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import polars as pl

from game_churn.features.schema import PlayerActivity
from game_churn.utils.config import RAW_DIR


def _load_json(path: Path) -> list | dict:
    return json.loads(path.read_text())


def standardize_chess_com(username: str, raw_dir: Path | None = None) -> list[PlayerActivity]:
    """Convert Chess.com raw game data to PlayerActivity records."""
    base = (raw_dir or RAW_DIR) / "chess_com"
    games_path = base / f"{username.lower()}_games.json"
    if not games_path.exists():
        return []

    games = _load_json(games_path)
    activities: list[PlayerActivity] = []

    for game in games:
        ts = game.get("end_time", 0)
        game_dt = datetime.fromtimestamp(ts, tz=UTC) if ts else datetime.now(tz=UTC)

        # Determine result for the player
        white = game.get("white", {})
        black = game.get("black", {})
        is_white = white.get("username", "").lower() == username.lower()
        player_data = white if is_white else black

        result_str = player_data.get("result", "unknown")
        if result_str == "win":
            result = "win"
        elif result_str in ("checkmated", "timeout", "resigned", "abandoned"):
            result = "loss"
        else:
            result = "draw"

        rating = player_data.get("rating")
        time_control = game.get("time_class", "unknown")

        activities.append(
            PlayerActivity(
                player_id=username.lower(),
                platform="chess_com",
                game_timestamp=game_dt,
                duration_seconds=0,  # Chess.com doesn't provide duration directly
                result=result,
                rating=rating,
                game_mode=time_control,
            )
        )

    return activities


def standardize_opendota(account_id: str, raw_dir: Path | None = None) -> list[PlayerActivity]:
    """Convert OpenDota raw match data to PlayerActivity records."""
    base = (raw_dir or RAW_DIR) / "opendota"
    matches_path = base / f"{account_id}_matches.json"
    if not matches_path.exists():
        return []

    matches = _load_json(matches_path)
    activities: list[PlayerActivity] = []

    for match in matches:
        start_time = match.get("start_time", 0)
        game_dt = (
            datetime.fromtimestamp(start_time, tz=UTC) if start_time else datetime.now(tz=UTC)
        )
        duration = match.get("duration", 0)

        # Determine win/loss from player_slot and radiant_win
        player_slot = match.get("player_slot", 0)
        radiant_win = match.get("radiant_win", False)
        is_radiant = player_slot < 128
        won = (is_radiant and radiant_win) or (not is_radiant and not radiant_win)

        activities.append(
            PlayerActivity(
                player_id=account_id,
                platform="opendota",
                game_timestamp=game_dt,
                duration_seconds=duration,
                result="win" if won else "loss",
                rating=None,
                game_mode=str(match.get("game_mode", "unknown")),
            )
        )

    return activities


def standardize_riot(
    game_name: str, tag_line: str, raw_dir: Path | None = None
) -> list[PlayerActivity]:
    """Convert Riot LoL raw match data to PlayerActivity records."""
    base = (raw_dir or RAW_DIR) / "riot_lol"
    safe_name = f"{game_name}_{tag_line}".lower()
    matches_path = base / f"{safe_name}_matches.json"
    account_path = base / f"{safe_name}_account.json"

    if not matches_path.exists() or not account_path.exists():
        return []

    account = _load_json(account_path)
    puuid = account.get("puuid", "")
    matches = _load_json(matches_path)
    activities: list[PlayerActivity] = []

    for match in matches:
        info = match.get("info", {})
        game_dt = datetime.fromtimestamp(info.get("gameCreation", 0) / 1000, tz=UTC)
        duration = info.get("gameDuration", 0)

        # Find this player's participant data
        participants = info.get("participants", [])
        player_data = next((p for p in participants if p.get("puuid") == puuid), None)
        if player_data is None:
            continue

        activities.append(
            PlayerActivity(
                player_id=safe_name,
                platform="riot_lol",
                game_timestamp=game_dt,
                duration_seconds=duration,
                result="win" if player_data.get("win") else "loss",
                rating=None,
                game_mode=info.get("gameMode", "unknown"),
            )
        )

    return activities


def load_all_activities(raw_dir: Path | None = None) -> pl.DataFrame:
    """Load and standardize all raw data into a single Polars DataFrame."""
    base = raw_dir or RAW_DIR
    all_activities: list[PlayerActivity] = []

    # Chess.com
    chess_dir = base / "chess_com"
    if chess_dir.exists():
        for f in chess_dir.glob("*_games.json"):
            username = f.stem.replace("_games", "")
            all_activities.extend(standardize_chess_com(username, raw_dir))

    # OpenDota
    dota_dir = base / "opendota"
    if dota_dir.exists():
        for f in dota_dir.glob("*_matches.json"):
            account_id = f.stem.replace("_matches", "")
            all_activities.extend(standardize_opendota(account_id, raw_dir))

    # Riot
    riot_dir = base / "riot_lol"
    if riot_dir.exists():
        for f in riot_dir.glob("*_account.json"):
            safe_name = f.stem.replace("_account", "")
            parts = safe_name.rsplit("_", 1)
            if len(parts) == 2:
                all_activities.extend(standardize_riot(parts[0], parts[1], raw_dir))

    if not all_activities:
        return pl.DataFrame(
            schema={
                "player_id": pl.Utf8,
                "platform": pl.Utf8,
                "game_timestamp": pl.Datetime("us", "UTC"),
                "duration_seconds": pl.Int64,
                "result": pl.Utf8,
                "rating": pl.Int64,
                "game_mode": pl.Utf8,
            }
        )

    records = [a.model_dump() for a in all_activities]
    return pl.DataFrame(records).sort("game_timestamp")
