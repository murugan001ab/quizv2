import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/auth': 'http://localhost:8000',
      '/user': 'http://localhost:8000',
      '/ws': { target: 'ws://localhost:8000', ws: true },

      // For /admin routes: only proxy to backend when it's a fetch/XHR API call.
      // Browser page refreshes send Accept: text/html — those should fall through
      // to Vite's SPA index.html, NOT get forwarded to FastAPI (which returns 404).
      '/admin': {
        target: 'http://localhost:8000',
        bypass(req) {
          const accept = req.headers['accept'] || ''
          // Browser navigation requests include text/html — serve index.html instead
          if (accept.includes('text/html')) {
            return '/index.html'
          }
          // fetch/XHR calls (application/json etc.) → proxy to FastAPI
        },
      },
    },
  },
})
