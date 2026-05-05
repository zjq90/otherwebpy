import { createSSRApp } from 'vue'
import App from './App.vue'

// 导入全局配置
import '@/utils/config.js'
// 导入API封装
import { http } from '@/utils/http.js'
// 导入权限工具
import { auth } from '@/utils/auth.js'

export function createApp() {
  const app = createSSRApp(App)
  
  // 将全局方法挂载到app上
  app.config.globalProperties.$http = http
  app.config.globalProperties.$auth = auth
  
  return {
    app
  }
}
