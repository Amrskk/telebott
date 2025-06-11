import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// frontend/vite.config.js
export default {
  server: {
    proxy: {
      '/chat': 'http://localhost:8000',
      '/teach': 'http://localhost:8000',
      '/register': 'http://localhost:8000',
      '/login': 'http://localhost:8000',
    },
  },
}
