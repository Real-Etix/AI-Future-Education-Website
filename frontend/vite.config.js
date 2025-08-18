import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  base: '/AI-Future-Education-Website',
  build: { 
    cssCodeSplit: true,
    rollupOptions: {
      output: {
        dir: 'dist/',
        entryFileNames: 'static/js/[name]-entry.js',
        assetFileNames: ({names = []}) => {
          const [name = ''] = names;
          if (/\.(gif|jpe?g|png|svg)$/.test(name)) {
            return 'static/images/[name][extname]';
          }
          if (/\.css$/.test(name)) {
            return 'static/css/[name]-asset[extname]';
          }
          return 'static/[name]-[hash][extname]';
        },
        chunkFileNames: 'static/js/[name]-chunk.js',
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            // Group node_modules into a 'vendor' chunk
            return id.toString().split('node_modules/')[1].split('/')[0].toString();
          }
        },
      },
    },
  },
  plugins: [
    vue(),
    vueJsx(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})
