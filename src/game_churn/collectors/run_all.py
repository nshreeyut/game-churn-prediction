"""Run active data collectors.

Active platforms: OpenDota (Dota 2), RAWG.io (reviews), Steam (coming soon)

Usage: python -m game_churn.collectors.run_all
"""

from __future__ import annotations

import logging

from game_churn.collectors.opendota import OpenDotaCollector
from game_churn.collectors.rawg import RawgCollector
from game_churn.collectors.steam import SteamCollector
from game_churn.utils.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Sample player IDs for demonstration
SAMPLE_PLAYERS = {
    "opendota": ["87278757", "86745912", "120269134"],
    "rawg_games": ["dota-2", "counter-strike-2", "pubg-battlegrounds"],
    "steam": ["76561198085505863", "76561198006920295"],  # public profiles for demo
}


def main() -> None:
    """Run all active collectors with sample player IDs."""
    # OpenDota — no auth needed
    log.info("=== OpenDota Collector ===")
    with OpenDotaCollector() as collector:
        for account_id in SAMPLE_PLAYERS["opendota"]:
            try:
                paths = collector.collect(account_id)
                log.info("Collected %d files for OpenDota/%s", len(paths), account_id)
            except Exception:
                log.exception("Failed to collect OpenDota/%s", account_id)

    # RAWG — game metadata + reviews
    if settings.rawg_api_key:
        log.info("=== RAWG Metadata + Reviews Collector ===")
        with RawgCollector() as collector:
            for slug in SAMPLE_PLAYERS["rawg_games"]:
                try:
                    paths = collector.collect(slug)
                    log.info("Collected %d files for RAWG/%s", len(paths), slug)
                except Exception:
                    log.exception("Failed to collect RAWG/%s", slug)
    else:
        log.warning("Skipping RAWG collector: GAME_CHURN_RAWG_API_KEY not set")

    # Steam — requires STEAM_API_KEY
    if settings.steam_api_key:
        log.info("=== Steam Collector ===")
        with SteamCollector() as collector:
            for steam_id in SAMPLE_PLAYERS["steam"]:
                try:
                    paths = collector.collect(steam_id)
                    log.info("Collected %d files for Steam/%s", len(paths), steam_id)
                except Exception:
                    log.exception("Failed to collect Steam/%s", steam_id)
    else:
        log.warning("Skipping Steam collector: STEAM_API_KEY not set")

    log.info("Collection complete.")


if __name__ == "__main__":
    main()
