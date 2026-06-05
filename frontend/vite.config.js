import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// alvo do proxy de dev configuravel por ambiente:
//  - local (host):   http://localhost:8000  (default)
//  - docker compose: VITE_PROXY_TARGET=http://backend:8000  (nome do servico backend)
const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: process.env.VITE_HOST || '127.0.0.1',
    port: Number(process.env.VITE_PORT) || 5173,
    proxy: {
      '/api': { target: proxyTarget, changeOrigin: true },
      '/files': { target: proxyTarget, changeOrigin: true },
      '/generated': { target: proxyTarget, changeOrigin: true },
    },
  },
})
