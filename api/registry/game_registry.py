"""
Game Registry
==============
This is the SINGLE place where you register all supported gaming platforms.

WHY A REGISTRY?
---------------
Without a registry, adding a new game (e.g., Steam) means editing multiple
files across the codebase: the router, the frontend dropdown, the agent, etc.

With a registry, you edit THIS file only. Everything else reads from here.
This is the Open/Closed Principle: open for extension, closed for modification.

HOW TO ADD A NEW GAME:
-----------------------
1. Build your collector in src/game_churn/collectors/your_game.py
   (use the existing collectors as a template — they all inherit BaseCollector)
2. Add a standardizer in src/game_churn/features/standardize.py
   (converts your game's raw JSON → the shared PlayerActivity format)
3. Add an entry to GAME_REGISTRY below

That's it. The API endpoint GET /api/v1/players/games returns this list,
and the React frontend uses it to build the platform dropdown dynamically.
No frontend code change needed when you add a new game.
"""

GAME_REGISTRY: dict[str, dict] = {
    "chess_com": {
        "display_name": "Chess.com",
        "collector_class": "game_churn.collectors.chess_com.ChessComCollector",
        "requires_api_key": False,
        "player_id_label": "Username",
        "player_id_example": "hikaru",  # shown as placeholder in the search input
    },
    "opendota": {
        "display_name": "OpenDota (Dota 2)",
        "collector_class": "game_churn.collectors.opendota.OpenDotaCollector",
        "requires_api_key": False,
        "player_id_label": "Account ID",
        "player_id_example": "87278757",
    },
    "riot_lol": {
        "display_name": "Riot Games (League of Legends)",
        "collector_class": "game_churn.collectors.riot.RiotCollector",
        "requires_api_key": True,
        "player_id_label": "Riot ID (name#tag)",
        "player_id_example": "Faker#KR1",
    },
    # ──────────────────────────────────────────────────────────
    # TO ADD STEAM (example):
    # ──────────────────────────────────────────────────────────
    # Step 1: create src/game_churn/collectors/steam.py
    # Step 2: add a standardize_steam() in features/standardize.py
    # Step 3: uncomment and fill in the entry below
    #
    # "steam": {
    #     "display_name": "Steam",
    #     "collector_class": "game_churn.collectors.steam.SteamCollector",
    #     "requires_api_key": True,
    #     "player_id_label": "Steam 64-bit ID",
    #     "player_id_example": "76561198012345678",
    # },
}


def get_supported_games() -> list[dict]:
    """
    Returns all registered games as a list, suitable for JSON serialization.
    Called by GET /api/v1/players/games — the frontend uses this to build
    the platform dropdown without any hardcoded values.
    """
    return [{"id": game_id, **metadata} for game_id, metadata in GAME_REGISTRY.items()]


def get_game(game_id: str) -> dict:
    """Look up a single game by its registry ID. Raises KeyError if not found."""
    if game_id not in GAME_REGISTRY:
        raise KeyError(
            f"Unknown game: '{game_id}'. Supported: {list(GAME_REGISTRY.keys())}"
        )
    return GAME_REGISTRY[game_id]
