/**
 * Vue 配置文件
 */
const path = require('path')

module.exports = {
  // 基本路径
  publicPath: '/',
  
  // 输出文件目录
  outputDir: 'dist',
  
  // 静态资源目录
  assetsDir: 'assets',
  
  // 是否在开发环境下通过 eslint-loader 在每次保存时 lint 代码
  lintOnSave: process.env.NODE_ENV !== 'production',
  
  // 生产环境的 source map
  productionSourceMap: false,
  
  // webpack-dev-server 相关配置
  devServer: {
    port: 3000,
    open: true,
    https: false,
    hot: true,
    proxy: {
      // 配置跨域
      '/api': {
        target: 'http://localhost:8000',
        ws: true,
        changeOrigin: true,
        pathRewrite: {
          '^/api': '/api'
        }
      }
    }
  },
  
  // css相关配置
  css: {
    // 是否使用css分离插件 ExtractTextPlugin
    extract: true,
    // 开启 CSS source maps?
    sourceMap: false,
    // css预设器配置项
    loaderOptions: {
      sass: {
        // 全局引入变量文件
        // additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  
  // webpack配置
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  },
  
  // 第三方插件配置
  pluginOptions: {
    // ...
  }
}
