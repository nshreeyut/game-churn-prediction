/**
 * AnalyticsPanel Component
 * =========================
 * Displays all analytics for a looked-up player.
 * This is the left column of the home page.
 *
 * PROPS:
 *   player  — the full response from fetchPlayerAnalytics (or null if not loaded)
 *   loading — boolean, true while the API call is in flight
 *   error   — string error message, or null
 *
 * WHAT TO DISPLAY (build these in order — start simple, add detail):
 *
 * 1. LOADING STATE
 *    Show a spinner or skeleton while data is being fetched.
 *    CSS skeleton loaders are a good touch: https://css-tricks.com/building-skeleton-screens-css-custom-properties/
 *
 * 2. ERROR STATE
 *    Show a clear error message if the player wasn't found or the API failed.
 *    e.g., "Player 'xyz' not found on Chess.com. Check the spelling and try again."
 *
 * 3. PLAYER HEADER (once data is loaded)
 *    - Player ID and platform name
 *    - Risk level badge (color coded: green=Low, yellow=Medium, red=High)
 *
 * 4. PREDICTION CARD
 *    - Churn probability as a large number: "73%"
 *    - A simple progress bar or gauge showing the probability visually
 *    - "Churned" / "Active" label based on churn_predicted
 *
 * 5. KEY STATS GRID
 *    Show the most important features as labeled cards:
 *      - Engagement Score (0–100)
 *      - Days Since Last Game
 *      - Games in Last 7 Days
 *      - Win Rate (7 days)
 *    Use player.features to access these values.
 *
 * 6. SHAP CHART
 *    Import and render <ShapChart shapValues={player.shap_values} />
 *    This shows which features are driving the prediction.
 *
 * DATA SHAPE (what player looks like):
 *   player = {
 *     player_id: "hikaru",
 *     platform:  "chess_com",
 *     features:  { games_7d: 14, engagement_score: 72.3, days_since_last_game: 1, ... },
 *     prediction: { churn_probability: 0.18, churn_predicted: false, risk_level: "Low", model_used: "ensemble" },
 *     shap_values: [{ feature: "...", label: "...", shap_value: 0.42, direction: "increases_churn" }, ...]
 *   }
 *
 * TODO: Implement this component, section by section.
 */

import ShapChart from '../ShapChart/ShapChart'
import './AnalyticsPanel.css'

function AnalyticsPanel({ player, loading, error }) {
  // 1. Loading state
  if (loading) {
    return <div className="analytics-panel loading">Loading player analytics…</div>
    // TODO: Replace with a proper skeleton loader
  }

  // 2. Error state
  if (error) {
    return <div className="analytics-panel error">{error}</div>
    // TODO: Style this as a proper error card with an icon
  }

  // 3. Empty state (no search yet, or player is null)
  if (!player) {
    return null
  }

  const { features, prediction, shap_values } = player

  return (
    <div className="analytics-panel">
      {/* TODO: Build each section described above */}
      <p>TODO: Render player analytics for {player.player_id} on {player.platform}</p>

      {/* Churn probability — hint: (prediction.churn_probability * 100).toFixed(1) + "%" */}

      {/* Key stats grid — hint: use Object.entries(features) or pick specific keys */}

      {/* SHAP chart */}
      {shap_values && <ShapChart shapValues={shap_values} />}
    </div>
  )
}

export default AnalyticsPanel
