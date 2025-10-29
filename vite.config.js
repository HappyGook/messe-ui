import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  root: 'frontend',
  build: {
    outDir: '../backend/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve('frontend/index.html'),
    }
  },
  server: {
    port:5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

