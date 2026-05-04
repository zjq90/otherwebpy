/**
 * 应用入口文件
 * 初始化Vue应用，配置路由、Element Plus等
 */
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用Element Plus，配置中文语言
app.use(ElementPlus, { locale: zhCn })
app.use(router)

app.mount('#app')
