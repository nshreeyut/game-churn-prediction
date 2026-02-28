/**
 * Home Page
 * ==========
 * The main page — combines the search, analytics, and chat in one view.
 *
 * PAGE LAYOUT:
 * ┌──────────────────────────────────────────────────────┐
 * │                   PlayerSearch                        │  ← top: platform + player ID input
 * ├─────────────────────────────┬────────────────────────┤
 * │      AnalyticsPanel         │      ChatPanel          │
 * │      (left ~60%)            │      (right ~40%)       │
 * │                             │                         │
 * │  • Churn probability        │  • Message history      │
 * │  • Risk level badge         │  • Streaming response   │
 * │  • SHAP chart               │  • Text input + send    │
 * │  • Feature stats            │                         │
 * └─────────────────────────────┴────────────────────────┘
 *
 * WHY STATE LIVES HERE ("lifting state up"):
 * -------------------------------------------
 * The selected player data is needed by BOTH AnalyticsPanel AND ChatPanel.
 * The ChatPanel needs it to give the LLM context.
 * The AnalyticsPanel needs it to display the charts and scores.
 *
 * In React, when multiple sibling components share data, that data must
 * live in their closest common ancestor (this component) and be passed
 * down as props. This is called "lifting state up."
 *
 * LEARN MORE:
 *   Lifting state up:  https://react.dev/learn/sharing-state-between-components
 *   props:             https://react.dev/learn/passing-props-to-a-component
 */

import { useState } from 'react'
import PlayerSearch from '../components/PlayerSearch/PlayerSearch'
import AnalyticsPanel from '../components/AnalyticsPanel/AnalyticsPanel'
import ChatPanel from '../components/ChatPanel/ChatPanel'
import { usePlayer } from '../hooks/usePlayer'
import './Home.css'

function Home() {
  // Tracks which player the user has searched for
  const [selectedPlatform, setSelectedPlatform] = useState(null)
  const [selectedPlayerId, setSelectedPlayerId] = useState(null)

  // usePlayer fetches analytics whenever platform or playerId changes
  const { player, loading, error } = usePlayer(selectedPlatform, selectedPlayerId)

  // Called by PlayerSearch when the user submits the form
  function handleSearch(platform, playerId) {
    setSelectedPlatform(platform)
    setSelectedPlayerId(playerId)
  }

  return (
    <div className="home-page">
      <PlayerSearch onSearch={handleSearch} />

      {/*
        Show the two-column layout only after a search has been triggered.
        Before that, show an empty state to explain what the app does.
      */}
      {!selectedPlayerId ? (
        <div className="empty-state">
          {/*
            TODO: Design a welcoming empty state here.
            Ideas:
              - Project title + one-line description
              - A brief explainer: "Search for a player to see their churn risk
                and chat with the AI analyst about what it means."
              - Maybe an example: "Try: Chess.com → hikaru"
          */}
          <p>TODO: Add an empty state / welcome message here.</p>
        </div>
      ) : (
        <div className="results-layout">
          {/* Left column: analytics charts and stats */}
          <div className="analytics-column">
            <AnalyticsPanel player={player} loading={loading} error={error} />
          </div>

          {/* Right column: chatbot, pre-loaded with this player's context */}
          <div className="chat-column">
            <ChatPanel playerContext={player} />
          </div>
        </div>
      )}
    </div>
  )
}

export default Home
