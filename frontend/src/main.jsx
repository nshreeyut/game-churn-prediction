/**
 * React Entry Point
 * ==================
 * This is where React "mounts" onto the HTML page.
 * index.html has <div id="root"></div> — React takes control of that div
 * and renders your entire app inside it.
 *
 * StrictMode (development only):
 *   - Detects common mistakes and deprecated API usage
 *   - Intentionally runs effects twice to surface bugs early
 *   - Has zero effect on production builds — safe to keep on
 *
 * BrowserRouter:
 *   - Enables client-side routing via react-router-dom
 *   - Without it, navigating between pages reloads the whole page from the server
 *   - With it, React intercepts navigation and renders the right component instantly
 *   - Reads the browser's URL bar and keeps it in sync with what's rendered
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
)
