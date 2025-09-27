import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// Avoid Node type deps; compute alias path with URL

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': new URL('./src', import.meta.url).pathname,
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:9000',
        changeOrigin: true,
        ws: true,
      },
      '/text2sql': {
        target: 'http://localhost:9000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
}) 