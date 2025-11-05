import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  root: 'frontend',
  build: {
    outDir: '../backend/dist',
    emptyOutDir: true,
    rollupOptions: {
      input: path.resolve('frontend/index.html'),
    },
    // Add these options to force clean builds
    manifest: true,
    write: true,
    sourcemap: true,
    // Disable caching during build
    cacheDir: null,
  },
  // Clear cache on start
  clearScreen: true,
  // Disable caching
  optimizeDeps: {
    force: true
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        secure: false,
      },
    },
  },
});


