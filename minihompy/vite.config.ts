import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    react(),
    // 지하철에서도 열려야 한다. 껍데기와 아이콘은 캐시에서 즉시 뜨고,
    // 데이터는 연결이 있으면 새로 받고 없으면 마지막으로 받아둔 걸 보여준다.
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['apple-touch-icon.png', 'icon-192.png', 'icon-512.png'],
      manifest: false,               // public/manifest.webmanifest 를 그대로 쓴다
      workbox: {
        globPatterns: ['**/*.{js,css,html,png,webmanifest}'],
        navigateFallback: '/index.html',
        // 미리보기 페이지는 앱이 아니므로 오프라인 진입점으로 쓰지 않는다
        navigateFallbackDenylist: [/^\/preview/],
        runtimeCaching: [
          {
            // 내 글과 사진은 연결이 있으면 새 것, 없으면 마지막 것.
            urlPattern: ({ url }) => url.hostname.endsWith('.supabase.co'),
            handler: 'NetworkFirst',
            options: {
              cacheName: 'minihompy-data',
              networkTimeoutSeconds: 4,
              expiration: { maxEntries: 260, maxAgeSeconds: 60 * 60 * 24 * 14 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
          {
            urlPattern: ({ url }) => url.hostname.includes('youtube'),
            handler: 'NetworkOnly',   // 영상은 캐시해봐야 소용없다
          },
        ],
      },
      devOptions: { enabled: false },
    }),
  ],
  build: {
    outDir: 'dist',
    rollupOptions: {
      output: {
        // 라이브러리는 거의 안 바뀌므로 따로 떼어 캐시가 오래 살게 하고,
        // 껍데기가 먼저 그려진 뒤에 데이터 계층이 붙게 한다.
        manualChunks(id) {
          if (!id.includes('node_modules')) return
          if (id.includes('@supabase')) return 'supabase'
          if (id.includes('react')) return 'react'
        },
      },
      input: {
        main: resolve(__dirname, 'index.html'),
        preview: resolve(__dirname, 'preview.html'),
      },
    },
  },
})
