"""Run all data collectors.

Usage: python -m game_churn.collectors.run_all
"""

from __future__ import annotations

import logging

from game_churn.collectors.chess_com import ChessComCollector
from game_churn.collectors.opendota import OpenDotaCollector
from game_churn.collectors.rawg import RawgCollector
from game_churn.collectors.riot import RiotCollector
from game_churn.utils.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Sample player IDs for demonstration
SAMPLE_PLAYERS = {
    "chess_com": ["hikaru", "magnuscarlsen", "gothamchess"],
    "opendota": ["87278757", "86745912", "120269134"],
    "riot_lol": [],  # Requires API key; add "Name#Tag" entries
    "rawg_games": ["dota-2", "league-of-legends", "chess-com"],
}


def main() -> None:
    """Run all collectors with sample player IDs."""
    # Chess.com (no auth needed)
    log.info("=== Chess.com Collector ===")
    with ChessComCollector() as collector:
        for username in SAMPLE_PLAYERS["chess_com"]:
            try:
                paths = collector.collect(username)
                log.info("Collected %d files for Chess.com/%s", len(paths), username)
            except Exception:
                log.exception("Failed to collect Chess.com/%s", username)

    # OpenDota (no auth needed)
    log.info("=== OpenDota Collector ===")
    with OpenDotaCollector() as collector:
        for account_id in SAMPLE_PLAYERS["opendota"]:
            try:
                paths = collector.collect(account_id)
                log.info("Collected %d files for OpenDota/%s", len(paths), account_id)
            except Exception:
                log.exception("Failed to collect OpenDota/%s", account_id)

    # Riot (requires API key)
    if settings.riot_api_key:
        log.info("=== Riot LoL Collector ===")
        with RiotCollector() as collector:
            for riot_id in SAMPLE_PLAYERS["riot_lol"]:
                try:
                    paths = collector.collect(riot_id)
                    log.info("Collected %d files for Riot/%s", len(paths), riot_id)
                except Exception:
                    log.exception("Failed to collect Riot/%s", riot_id)
    else:
        log.warning("Skipping Riot collector: GAME_CHURN_RIOT_API_KEY not set")

    # RAWG game metadata
    if settings.rawg_api_key:
        log.info("=== RAWG Metadata Collector ===")
        with RawgCollector() as collector:
            for slug in SAMPLE_PLAYERS["rawg_games"]:
                try:
                    paths = collector.collect(slug)
                    log.info("Collected %d files for RAWG/%s", len(paths), slug)
                except Exception:
                    log.exception("Failed to collect RAWG/%s", slug)
    else:
        log.warning("Skipping RAWG collector: GAME_CHURN_RAWG_API_KEY not set")

    log.info("Collection complete.")


if __name__ == "__main__":
    main()
