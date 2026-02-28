"""Generate synthetic player feature data for model development."""

from __future__ import annotations

import numpy as np
import polars as pl


def generate_synthetic_data(n_players: int = 2000, seed: int = 42) -> pl.DataFrame:
    """Generate realistic synthetic player features with churn labels.

    Creates a dataset where feature distributions differ meaningfully
    between churned and active players, enabling model training.
    """
    rng = np.random.default_rng(seed)

    # Split into churned and active
    n_churned = int(n_players * 0.3)
    n_active = n_players - n_churned

    platforms = ["chess_com", "opendota", "riot_lol"]

    records: list[dict] = []

    for is_churned, count in [(False, n_active), (True, n_churned)]:
        for _ in range(count):
            platform = rng.choice(platforms)

            if is_churned:
                # Churned players: low recent activity, declining trends
                games_30d = int(rng.poisson(3))
                games_14d = min(int(rng.poisson(1)), games_30d)
                games_7d = min(int(rng.poisson(0.5)), games_14d)
                playtime_30d = max(0, rng.normal(2, 1.5))
                playtime_14d = max(0, rng.normal(0.5, 0.5))
                playtime_7d = max(0, rng.normal(0.1, 0.2))
                avg_sessions_30d = max(0, rng.normal(0.1, 0.08))
                avg_sessions_14d = max(0, rng.normal(0.05, 0.05))
                avg_sessions_7d = max(0, rng.normal(0.02, 0.03))
                max_gap = rng.uniform(10, 30)
                win_rate_7d = max(0, min(1, rng.normal(0.35, 0.15)))
                win_rate_30d = max(0, min(1, rng.normal(0.4, 0.12)))
                rating_change = int(rng.normal(-50, 30))
                peers = int(max(0, rng.poisson(2)))
                peer_games = int(max(0, rng.poisson(3)))
                days_since = rng.uniform(14, 90)
                engagement = max(0, rng.normal(15, 10))
            else:
                # Active players: high recent activity, stable/increasing trends
                games_30d = int(rng.poisson(25))
                games_14d = min(int(rng.poisson(15)), games_30d)
                games_7d = min(int(rng.poisson(8)), games_14d)
                playtime_30d = max(0, rng.normal(20, 8))
                playtime_14d = max(0, rng.normal(12, 5))
                playtime_7d = max(0, rng.normal(6, 3))
                avg_sessions_30d = max(0, rng.normal(0.6, 0.2))
                avg_sessions_14d = max(0, rng.normal(0.65, 0.2))
                avg_sessions_7d = max(0, rng.normal(0.7, 0.2))
                max_gap = rng.uniform(0.5, 5)
                win_rate_7d = max(0, min(1, rng.normal(0.52, 0.1)))
                win_rate_30d = max(0, min(1, rng.normal(0.51, 0.08)))
                rating_change = int(rng.normal(10, 25))
                peers = int(max(0, rng.poisson(8)))
                peer_games = int(max(0, rng.poisson(15)))
                days_since = rng.uniform(0, 5)
                engagement = max(0, min(100, rng.normal(55, 15)))

            # Trend features
            games_trend = games_7d / max(games_14d, 1)
            playtime_trend = playtime_7d / max(playtime_14d, 0.01)

            records.append(
                {
                    "player_id": f"synthetic_{len(records)}",
                    "platform": platform,
                    "games_7d": games_7d,
                    "games_14d": games_14d,
                    "games_30d": games_30d,
                    "playtime_7d_hours": round(playtime_7d, 2),
                    "playtime_14d_hours": round(playtime_14d, 2),
                    "playtime_30d_hours": round(playtime_30d, 2),
                    "avg_daily_sessions_7d": round(avg_sessions_7d, 3),
                    "avg_daily_sessions_14d": round(avg_sessions_14d, 3),
                    "avg_daily_sessions_30d": round(avg_sessions_30d, 3),
                    "max_gap_days_30d": round(max_gap, 2),
                    "games_trend_7d_vs_14d": round(games_trend, 3),
                    "playtime_trend_7d_vs_14d": round(playtime_trend, 3),
                    "win_rate_7d": round(win_rate_7d, 3),
                    "win_rate_30d": round(win_rate_30d, 3),
                    "rating_current": int(rng.normal(1500, 300)),
                    "rating_change_30d": rating_change,
                    "unique_peers_30d": peers,
                    "peer_games_30d": peer_games,
                    "engagement_score": round(engagement, 2),
                    "days_since_last_game": round(days_since, 2),
                    "churned": is_churned,
                }
            )

    return pl.DataFrame(records)
