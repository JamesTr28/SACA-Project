import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5173,  // 前端端口
    proxy: {
      '/nlp': {
        target: 'http://localhost:8000',  // ✅ 改为 8000
        changeOrigin: true,
      },
      '/predict': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/translate': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/asr': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
