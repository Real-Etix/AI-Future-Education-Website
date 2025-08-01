import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
// import { resolve } from 'node:path'

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  build: { 
    cssCodeSplit: true,
    minify: false, // Added to stop compacting
    // target: 'modules',
    rollupOptions: {
      // external: ['vue'],
      // input: {
        // main: resolve(__dirname, 'index.html'),
        // sidebar: resolve(__dirname, 'src/components/sidebar.html'),
        // home: resolve(__dirname, 'src/views/home/index.html')
      // },
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
        manualChunks: undefined,
        // globals: {
          // vue: 'Vue'
        // }
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
