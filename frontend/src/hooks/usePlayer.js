/**
 * usePlayer — Custom React Hook
 * ==============================
 * Manages all state and data fetching for a player lookup.
 *
 * WHAT IS A CUSTOM HOOK?
 * -----------------------
 * A custom hook is a function that uses React's built-in hooks (useState,
 * useEffect, etc.) to encapsulate reusable logic.
 *
 * WITHOUT this hook, any component that needs player data would repeat:
 *   - useState for data, loading, error
 *   - useEffect to fetch when IDs change
 *   - try/catch for error handling
 *
 * WITH this hook, a component just does:
 *   const { player, loading, error } = usePlayer('chess_com', 'hikaru')
 *
 * NAMING: Custom hooks MUST start with "use" — React enforces this.
 * The prefix tells React to apply the rules of hooks to this function.
 *
 * LEARN MORE:
 *   Custom hooks:  https://react.dev/learn/reusing-logic-with-custom-hooks
 *   useEffect:     https://react.dev/reference/react/useEffect
 *   Dependency array: the second argument to useEffect controls when it re-runs.
 *     []              → runs once on mount only
 *     [a, b]          → runs when a or b changes
 *     (no argument)   → runs after every render (usually not what you want)
 */

import { useState, useEffect } from 'react'
import { fetchPlayerAnalytics } from '../api/players'

/**
 * @param {string|null} platform  - e.g., "chess_com" (null until user searches)
 * @param {string|null} playerId  - e.g., "hikaru"    (null until user searches)
 * @param {string}      modelId   - which model to use for the prediction
 *
 * @returns {{
 *   player:  object|null,   // the full API response from fetchPlayerAnalytics
 *   loading: boolean,       // true while the request is in flight
 *   error:   string|null,   // error message if the request failed
 *   refetch: Function       // call this to manually re-fetch (e.g., if user changes model)
 * }}
 *
 * TODO: Implement this hook.
 * Steps:
 *   1. Create state:
 *        const [player, setPlayer] = useState(null)
 *        const [loading, setLoading] = useState(false)
 *        const [error, setError] = useState(null)
 *
 *   2. Write a fetchPlayer async function:
 *        async function fetchPlayer() {
 *          setLoading(true)
 *          setError(null)
 *          try {
 *            const data = await fetchPlayerAnalytics(platform, playerId, modelId)
 *            setPlayer(data)
 *          } catch (err) {
 *            setError(err.response?.data?.detail || 'Player not found.')
 *            setPlayer(null)
 *          } finally {
 *            setLoading(false)
 *          }
 *        }
 *
 *   3. useEffect to call fetchPlayer when platform or playerId changes:
 *        useEffect(() => {
 *          if (!platform || !playerId) return  // don't fetch if nothing is selected
 *          fetchPlayer()
 *        }, [platform, playerId, modelId])
 *
 *   4. Return { player, loading, error, refetch: fetchPlayer }
 */
export function usePlayer(platform, playerId, modelId = 'ensemble') {
  const [player, setPlayer] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // TODO: Add useEffect and fetchPlayer logic here

  return { player, loading, error, refetch: () => {} }
}
