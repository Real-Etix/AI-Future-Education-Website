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
        entryFileNames: 'assets/js/[name]-entry.js',
        // assetFileNames: 'assets/css/[name]-asset.css',
        assetFileNames: (assetInfo) => {
          return assetInfo.names[0];
        },
        chunkFileNames: 'assets/js/[name]-chunk.js',
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
