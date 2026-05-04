/**
 * Vue 3 应用入口文件
 * 配置并初始化Vue应用，包括路由、状态管理、UI组件库等
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

// 创建Vue应用实例
const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用Pinia状态管理
app.use(createPinia())

// 使用Vue Router
app.use(router)

// 使用Element Plus UI库（中文语言包）
app.use(ElementPlus, {
  locale: zhCn,
  size: 'default'
})

// 挂载应用
app.mount('#app')
