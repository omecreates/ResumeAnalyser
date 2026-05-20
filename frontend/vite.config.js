// ============================================================
// vite.config.js — Vite Build Tool Configuration
// ============================================================
//
// Vite is our frontend build tool. It does two things:
//
// 1. DEV MODE (npm run dev):
//    Starts a lightning-fast local server at localhost:5173
//    with Hot Module Replacement (HMR) — changes appear
//    instantly in the browser without a full page reload.
//
// 2. BUILD MODE (npm run build):
//    Bundles all your React code into optimized static files
//    (HTML + CSS + JS) that can be deployed to Vercel.
//
// ============================================================

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // react() plugin enables JSX support and React Fast Refresh

  server: {
    port: 5173,
    // The port your dev server runs on.
    // Open http://localhost:5173 during development.

    proxy: {
      // PROXY: During development, when React sends a request
      // to /analyze or /health, Vite forwards it to Flask
      // at localhost:5000. This avoids CORS issues in dev.
      //
      // Example: React calls /analyze
      //   → Vite intercepts it
      //   → Forwards to http://localhost:5000/analyze
      //   → Returns response to React
      //
      // In production (Vercel + Render), we use the full
      // Render URL instead (via VITE_API_URL env variable).
      '/analyze': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    }
  },

  build: {
    outDir: 'dist',
    // Where Vite puts the built files.
    // Vercel looks for this 'dist' folder automatically.
  }
})