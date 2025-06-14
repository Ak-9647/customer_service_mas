import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8080',
      '/run': 'http://localhost:8080',
      '/run_sse': 'http://localhost:8080',
      '/list-apps': 'http://localhost:8080',
      '/health': 'http://localhost:8080',
      '/apps': 'http://localhost:8080'
    },
  },
})
