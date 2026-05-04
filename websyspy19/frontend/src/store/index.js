/**
 * Vuex 状态管理入口文件
 */
import Vue from 'vue'
import Vuex from 'vuex'
import user from './modules/user'

// 使用 Vuex
Vue.use(Vuex)

// 创建 store 实例
export default new Vuex.Store({
  modules: {
    user
  },
  getters: {
    // 用户相关
    token: state => state.user.token,
    userInfo: state => state.user.userInfo,
    roles: state => state.user.roles,
    permissions: state => state.user.permissions
  }
})
