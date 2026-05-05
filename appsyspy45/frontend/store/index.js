import { createPinia } from 'pinia'
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    userInfo: uni.getStorageSync('userInfo') || null,
    hasLogin: !!uni.getStorageSync('token')
  }),
  
  getters: {
    isLoggedIn: (state) => state.hasLogin,
    getToken: (state) => state.token,
    getUserInfo: (state) => state.userInfo
  },
  
  actions: {
    login(token, userInfo) {
      this.token = token
      this.userInfo = userInfo
      this.hasLogin = true
      
      uni.setStorageSync('token', token)
      uni.setStorageSync('userInfo', userInfo)
      
      const app = getApp()
      app.globalData.hasLogin = true
      app.globalData.userInfo = userInfo
    },
    
    logout() {
      this.token = ''
      this.userInfo = null
      this.hasLogin = false
      
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
      
      const app = getApp()
      app.globalData.hasLogin = false
      app.globalData.userInfo = null
    },
    
    updateUserInfo(userInfo) {
      this.userInfo = { ...this.userInfo, ...userInfo }
      uni.setStorageSync('userInfo', this.userInfo)
      
      const app = getApp()
      app.globalData.userInfo = this.userInfo
    }
  }
})

const pinia = createPinia()

export default pinia
