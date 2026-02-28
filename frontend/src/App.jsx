/**
 * App Component — Root of your component tree
 * =============================================
 * This file defines the top-level structure of your app:
 *   - Which routes exist and what component each renders
 *   - Any layout that wraps every page (e.g., a navbar)
 *
 * React Router replaces traditional server-side routing.
 * <Routes> looks at the current URL and renders the matching <Route>.
 * Navigation is instant — no page reload, no server round-trip.
 *
 * As your app grows, add more <Route> entries here.
 *
 * LEARN MORE:
 *   React Router basics: https://reactrouter.com/en/main/start/overview
 *   useNavigate hook:    https://reactrouter.com/en/main/hooks/use-navigate
 */

import { Routes, Route } from 'react-router-dom'
import Home from './pages/Home'

// TODO: Once you build the Navbar component, import and add it here.
// import Navbar from './components/Navbar/Navbar'

function App() {
  return (
    <div className="app">
      {/*
        TODO: Add <Navbar /> here so it appears on every page.
        It should show the project name and any global navigation links.
      */}

      <main>
        <Routes>
          {/* The home page — player search + analytics + chat */}
          <Route path="/" element={<Home />} />

          {/*
            TODO: If you want each player to have a shareable URL, add a route like:
              <Route path="/:platform/:playerId" element={<Home />} />

            Then in Home.jsx you can read the URL params with useParams():
              import { useParams } from 'react-router-dom'
              const { platform, playerId } = useParams()

            This lets users bookmark or share a link to a specific player.
          */}
        </Routes>
      </main>
    </div>
  )
}

export default App
