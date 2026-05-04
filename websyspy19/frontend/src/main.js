/**
 * 前端入口文件
 */
import Vue from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'

// 引入 Element UI
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'

// 引入进度条
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

// 引入全局样式
// import '@/styles/index.scss'

// 配置 NProgress
NProgress.configure({ showSpinner: false })

// 使用 Element UI
Vue.use(ElementUI, { size: 'medium', zIndex: 3000 })

// 阻止显示生产模式的消息
Vue.config.productionTip = false

// 路由守卫
router.beforeEach((to, from, next) => {
  // 开启进度条
  NProgress.start()
  
  // 白名单，不需要登录的路由
  const whiteList = ['/login', '/404', '/403']
  
  // 检查是否需要登录
  if (whiteList.indexOf(to.path) !== -1) {
    // 在白名单中，直接访问
    next()
  } else {
    // 检查是否有 Token
    const token = store.getters.token
    if (token) {
      // 有 Token，检查是否有用户信息
      if (!store.getters.userInfo || !store.getters.userInfo.id) {
        // 没有用户信息，获取用户信息
        store.dispatch('user/getUserInfo')
          .then(() => {
            // 检查路由是否需要权限
            next()
          })
          .catch(() => {
            // 获取用户信息失败，清除 Token 并跳转到登录页
            store.dispatch('user/resetToken')
            next(`/login?redirect=${to.path}`)
            NProgress.done()
          })
      } else {
        // 有用户信息，直接访问
        next()
      }
    } else {
      // 没有 Token，跳转到登录页
      next(`/login?redirect=${to.path}`)
      NProgress.done()
    }
  }
})

// 路由后置守卫
router.afterEach(() => {
  // 关闭进度条
  NProgress.done()
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
