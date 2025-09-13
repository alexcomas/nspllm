import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://0.0.0.0:8000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://0.0.0.0:8000',
        ws: true,
      },
    },
  },
  build: {
    outDir: '../environment/frontend_server/static/app',
    emptyOutDir: true,
  },
})