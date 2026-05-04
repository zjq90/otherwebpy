/**
 * 用户模块 - Vuex 状态管理
 */
import { login, logout, getUserInfo, getPermissions } from '@/utils/auth'
import { getToken, setToken, removeToken } from '@/utils/auth'

const state = {
  // Token
  token: getToken(),
  // 用户信息
  userInfo: {},
  // 用户角色
  roles: [],
  // 用户权限
  permissions: []
}

const mutations = {
  // 设置 Token
  SET_TOKEN: (state, token) => {
    state.token = token
  },
  // 设置用户信息
  SET_USER_INFO: (state, userInfo) => {
    state.userInfo = userInfo
  },
  // 设置角色
  SET_ROLES: (state, roles) => {
    state.roles = roles
  },
  // 设置权限
  SET_PERMISSIONS: (state, permissions) => {
    state.permissions = permissions
  },
  // 重置状态
  RESET_STATE: (state) => {
    state.token = ''
    state.userInfo = {}
    state.roles = []
    state.permissions = []
  }
}

const actions = {
  // 用户登录
  login({ commit }, userInfo) {
    const { username, password } = userInfo
    return new Promise((resolve, reject) => {
      login({ username: username.trim(), password: password })
        .then(response => {
          const { data } = response
          commit('SET_TOKEN', data.access_token)
          setToken(data.access_token)
          resolve()
        })
        .catch(error => {
          reject(error)
        })
    })
  },
  
  // 获取用户信息
  getUserInfo({ commit, state }) {
    return new Promise((resolve, reject) => {
      getUserInfo()
        .then(response => {
          const { data } = response
          
          if (!data) {
            reject('验证失败，请重新登录')
          }
          
          // 设置用户信息
          commit('SET_USER_INFO', data)
          
          // 设置角色
          if (data.roles && data.roles.length > 0) {
            commit('SET_ROLES', data.roles)
          } else {
            commit('SET_ROLES', [])
          }
          
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },
  
  // 获取用户权限
  getPermissions({ commit, state }) {
    return new Promise((resolve, reject) => {
      getPermissions()
        .then(response => {
          const { data } = response
          
          // 设置权限
          const permissionCodes = data.map(item => item.code)
          commit('SET_PERMISSIONS', permissionCodes)
          
          resolve(data)
        })
        .catch(error => {
          reject(error)
        })
    })
  },
  
  // 用户登出
  logout({ commit, state }) {
    return new Promise((resolve, reject) => {
      logout()
        .then(() => {
          // 清除 Token
          removeToken()
          // 重置状态
          commit('RESET_STATE')
          resolve()
        })
        .catch(error => {
          reject(error)
        })
    })
  },
  
  // 重置 Token
  resetToken({ commit }) {
    return new Promise(resolve => {
      // 清除 Token
      removeToken()
      // 重置状态
      commit('RESET_STATE')
      resolve()
    })
  }
}

export default {
  namespaced: true,
  state,
  mutations,
  actions
}
