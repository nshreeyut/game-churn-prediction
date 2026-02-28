/**
 * PlayerSearch Component
 * =======================
 * A form where users select a gaming platform and enter a player ID.
 * When submitted, it calls onSearch(platform, playerId) to notify the parent.
 *
 * PROPS:
 *   onSearch(platform, playerId) — called when the form is submitted
 *
 * STATE (local to this component):
 *   platform  — the selected platform ID (e.g., "chess_com")
 *   playerId  — what the user typed
 *   games     — list of platforms fetched from the API (for the dropdown)
 *
 * DATA FLOW:
 *   1. On mount, fetch supported games from GET /api/v1/players/games
 *   2. Populate the <select> dropdown dynamically from the response
 *   3. When the user selects a platform, update the input placeholder
 *      using the platform's player_id_example (e.g., "hikaru" for Chess.com)
 *   4. On form submit, call props.onSearch(platform, playerId)
 *   5. Parent (Home.jsx) updates state → usePlayer hook triggers a fetch
 *
 * WHY FETCH GAMES DYNAMICALLY?
 * ------------------------------
 * The platform list comes from api/registry/game_registry.py.
 * If you add a new game there, the dropdown updates automatically —
 * no frontend code change, no redeployment needed.
 *
 * TODO: Implement this component.
 * Steps:
 *   1. Add useState for: platform (''), playerId (''), games ([]), loadingGames (false)
 *
 *   2. Add useEffect to fetch games on mount:
 *        useEffect(() => {
 *          fetchSupportedGames().then(setGames).catch(console.error)
 *        }, [])   // [] = run once on mount only
 *
 *   3. Render a <form onSubmit={handleSubmit}>:
 *        a. A <select> for platform:
 *             map over games → <option key={g.id} value={g.id}>{g.display_name}</option>
 *        b. An <input> for playerId:
 *             placeholder = the selected game's player_id_example
 *             (find it with: games.find(g => g.id === platform)?.player_id_example)
 *        c. A <button type="submit">Look Up Player</button>
 *
 *   4. handleSubmit:
 *        function handleSubmit(e) {
 *          e.preventDefault()                  // prevent page reload
 *          if (!platform || !playerId) return  // basic validation
 *          onSearch(platform, playerId.trim())
 *        }
 */

import { useState, useEffect } from 'react'
import { fetchSupportedGames } from '../../api/players'
import './PlayerSearch.css'

function PlayerSearch({ onSearch }) {
  const [platform, setPlatform] = useState('')
  const [playerId, setPlayerId] = useState('')
  const [games, setGames] = useState([])

  // TODO: Add useEffect to fetch games on mount

  // TODO: Get the placeholder text from the selected game
  const selectedGame = games.find(g => g.id === platform)

  function handleSubmit(e) {
    e.preventDefault()
    // TODO: validate and call onSearch(platform, playerId.trim())
  }

  return (
    <form onSubmit={handleSubmit} className="player-search">
      {/*
        TODO: Build the form UI here.
        Suggested structure:
          <div className="search-row">
            <select ...> platforms </select>
            <input ...> player ID </input>
            <button type="submit">Look Up Player</button>
          </div>
        Add a validation message if platform or playerId is empty on submit.
      */}
      <p>TODO: Build the player search form</p>
    </form>
  )
}

export default PlayerSearch
