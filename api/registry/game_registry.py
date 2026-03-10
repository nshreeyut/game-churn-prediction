"""
Game Registry
==============
Single source of truth for all active data sources.

To add a new platform:
  1. Build collector in src/game_churn/collectors/your_platform.py
  2. Add standardize_*() in src/game_churn/features/standardize.py
  3. Add entry here

The frontend dropdown and agent tools both read from this registry —
no other files need to change when you add a platform.
"""

GAME_REGISTRY: dict[str, dict] = {
    "opendota": {
        "display_name": "Dota 2 (OpenDota)",
        "collector_class": "game_churn.collectors.opendota.OpenDotaCollector",
        "requires_api_key": False,
        "player_id_label": "Account ID",
        "player_id_example": "87278757",
        "description": "Dota 2 match history, MMR progression, and social graph via OpenDota API",
    },
    "steam": {
        "display_name": "Steam",
        "collector_class": "game_churn.collectors.steam.SteamCollector",
        "requires_api_key": True,
        "player_id_label": "Steam 64-bit ID",
        "player_id_example": "76561198012345678",
        "description": "Steam playtime, recently played games, and friend list",
    },
    # RAWG is a review source — feeds the NLP agent, not the player lookup flow
    # It does not appear in the player search dropdown
}


def get_supported_games() -> list[dict]:
    """Returns all registered platforms as a list for the frontend dropdown."""
    return [{"id": game_id, **metadata} for game_id, metadata in GAME_REGISTRY.items()]


def get_game(game_id: str) -> dict:
    """Look up a platform by registry ID. Raises KeyError if not found."""
    if game_id not in GAME_REGISTRY:
        raise KeyError(
            f"Unknown platform: '{game_id}'. Supported: {list(GAME_REGISTRY.keys())}"
        )
    return GAME_REGISTRY[game_id]
