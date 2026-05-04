/**
 * Vite 配置文件
 * 配置Vue 3项目的构建选项
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  // 使用Vue 3插件
  plugins: [vue()],
  
  // 配置路径别名
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  
  // 开发服务器配置
  server: {
    port: 3000,
    host: '0.0.0.0',
    open: true,
    
    // 代理配置，解决跨域问题
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  
  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild'
  }
})
