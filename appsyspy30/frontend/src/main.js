/**
 * 健身社交系统前端App入口文件
 */
import { createSSRApp } from 'vue'
import App from './App.vue'

// 全局API配置
import { setToken, getToken, removeToken, getBaseUrl } from './utils/auth'
import { request } from './utils/request'

export function createApp() {
    const app = createSSRApp(App)
    
    // 全局方法
    app.config.globalProperties.$request = request
    app.config.globalProperties.$getToken = getToken
    app.config.globalProperties.$setToken = setToken
    app.config.globalProperties.$removeToken = removeToken
    app.config.globalProperties.$baseUrl = getBaseUrl()
    
    return {
        app
    }
}
