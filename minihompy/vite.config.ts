import { resolve } from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        // 앱과 디자인 미리보기를 같이 낸다. 미리보기는 Supabase 없이도
        // 열리므로 모양을 확인하거나 남에게 보여줄 때 쓴다.
        main: resolve(__dirname, 'index.html'),
        preview: resolve(__dirname, 'preview.html'),
      },
    },
  },
})
