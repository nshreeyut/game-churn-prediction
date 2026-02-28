/**
 * Vite Configuration
 * ===================
 * Vite is a modern build tool that makes React development fast.
 * It provides Hot Module Replacement (HMR) — changes appear in the browser
 * instantly without a full page reload.
 *
 * KEY CONCEPT: The Dev Server Proxy
 * -----------------------------------
 * In development:
 *   React runs on  → localhost:5173
 *   FastAPI runs on → localhost:8000
 *
 * These are different "origins" (different ports = different origin).
 * Browsers block cross-origin requests for security (CORS policy).
 *
 * The proxy below tells Vite's dev server:
 *   "Any request to /api/* — forward it to localhost:8000"
 *
 * So in your React code you write:
 *   fetch('/api/v1/players/chess_com/hikaru')
 *
 * And Vite silently proxies it to:
 *   http://localhost:8000/api/v1/players/chess_com/hikaru
 *
 * In production (Vercel + Render), there's no proxy — the browser calls
 * the Render URL directly. That's configured via VITE_API_URL in .env.
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // All /api requests are forwarded to FastAPI during development
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
