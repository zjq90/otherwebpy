import { defineStore } from 'pinia'
import request from '@/utils/request'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: uni.getStorageSync('token') || '',
    userInfo: uni.getStorageSync('userInfo') || null,
    isLoggedIn: !!uni.getStorageSync('token')
  }),

  getters: {
    isMember: (state) => state.userInfo?.role === 'member',
    isCoach: (state) => state.userInfo?.role === 'coach',
    isAdmin: (state) => state.userInfo?.role === 'admin'
  },

  actions: {
    async login(username, password) {
      try {
        const res = await request.post('/auth/login-password', {
          username,
          password
        })
        
        this.token = res.access_token
        this.isLoggedIn = true
        uni.setStorageSync('token', res.access_token)

        const userInfo = await request.get('/auth/me')
        this.userInfo = userInfo
        uni.setStorageSync('userInfo', userInfo)

        return { success: true, data: userInfo }
      } catch (error) {
        return { success: false, message: error.message }
      }
    },

    async register(userData) {
      try {
        const res = await request.post('/auth/register', userData)
        return { success: true, data: res }
      } catch (error) {
        return { success: false, message: error.message }
      }
    },

    async getCurrentUser() {
      try {
        const res = await request.get('/auth/me')
        this.userInfo = res
        uni.setStorageSync('userInfo', res)
        return { success: true, data: res }
      } catch (error) {
        return { success: false, message: error.message }
      }
    },

    logout() {
      this.token = ''
      this.userInfo = null
      this.isLoggedIn = false
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
      
      uni.reLaunch({
        url: '/pages/login/login'
      })
    },

    updateUserInfo(userInfo) {
      this.userInfo = { ...this.userInfo, ...userInfo }
      uni.setStorageSync('userInfo', this.userInfo)
    }
  }
})
