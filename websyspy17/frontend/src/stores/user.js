import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const token = ref(localStorage.getItem('token') || '')

  const isLoggedIn = computed(() => !!token.value)
  
  const isAdmin = computed(() => {
    return user.value && ['admin', 'property'].includes(user.value.role)
  })

  const isResident = computed(() => {
    return user.value && user.value.role === 'resident'
  })

  async function login(credentials) {
    const response = await authApi.login(credentials)
    token.value = response.access_token
    user.value = response.user
    
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    
    return response
  }

  async function register(userData) {
    return await authApi.register(userData)
  }

  function logout() {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  async function fetchCurrentUser() {
    try {
      const response = await authApi.getCurrentUser()
      user.value = response
      localStorage.setItem('user', JSON.stringify(user.value))
      return response
    } catch (error) {
      logout()
      throw error
    }
  }

  return {
    user,
    token,
    isLoggedIn,
    isAdmin,
    isResident,
    login,
    register,
    logout,
    fetchCurrentUser
  }
})
