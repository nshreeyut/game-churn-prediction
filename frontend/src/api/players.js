/**
 * Players API Module
 * ===================
 * All API calls related to players, games, and models live here.
 *
 * WHY SEPARATE API FUNCTIONS FROM COMPONENTS?
 * --------------------------------------------
 * Components should only care about rendering — not URLs, HTTP methods,
 * or response shapes. These functions are the contract between your UI
 * and your backend.
 *
 * If the backend changes an endpoint (e.g., adds a /v2 prefix), you update
 * this file only — no component needs to change.
 *
 * HOW TO USE THESE IN A COMPONENT:
 * ----------------------------------
 * Direct (in a useEffect):
 *   const data = await fetchPlayerAnalytics('chess_com', 'hikaru')
 *
 * Better — use the usePlayer() custom hook, which wraps these functions
 * and automatically manages loading/error state for you.
 * See src/hooks/usePlayer.js.
 */

import client from './client'

/**
 * Fetch the list of supported gaming platforms.
 * Powers the platform dropdown in PlayerSearch — fetched dynamically
 * so adding a new game to the backend registry appears without a frontend deploy.
 *
 * Returns: [{ id: "chess_com", display_name: "Chess.com", player_id_example: "hikaru", ... }]
 *
 * TODO: Implement using client.get('/api/v1/players/games')
 * Return response.data
 */
export async function fetchSupportedGames() {
  throw new Error('TODO: implement fetchSupportedGames()')
}

/**
 * Fetch all registered ML models.
 * Use this to populate a model selector (if you want users to pick a model).
 *
 * Returns: [{ id: "ensemble", display_name: "Soft-Voting Ensemble", description: "..." }]
 *
 * TODO: Implement using client.get('/api/v1/players/models')
 */
export async function fetchModels() {
  throw new Error('TODO: implement fetchModels()')
}

/**
 * Fetch full analytics for one player. This is the main call.
 * Powers the entire AnalyticsPanel and provides context to the ChatPanel.
 *
 * @param {string} platform  - e.g., "chess_com"
 * @param {string} playerId  - e.g., "hikaru"
 * @param {string} modelId   - e.g., "ensemble" (optional)
 *
 * Returns:
 * {
 *   player_id:   "hikaru",
 *   platform:    "chess_com",
 *   features:    { games_7d: 14, engagement_score: 72.3, ... },
 *   prediction:  { churn_probability: 0.18, risk_level: "Low", ... },
 *   shap_values: [{ feature: "days_since_last_game", shap_value: -0.31, direction: "decreases_churn" }, ...]
 * }
 *
 * TODO: Implement using client.get(`/api/v1/players/${platform}/${playerId}`)
 * Pass modelId as a query param: { params: { model_id: modelId } }
 * Return response.data
 */
export async function fetchPlayerAnalytics(platform, playerId, modelId = 'ensemble') {
  throw new Error('TODO: implement fetchPlayerAnalytics()')
}

/**
 * Browse players in the dataset. Optionally filter by platform.
 *
 * TODO: Implement using client.get('/api/v1/players', { params: { platform, limit } })
 */
export async function fetchPlayers(platform = null, limit = 50) {
  throw new Error('TODO: implement fetchPlayers()')
}
