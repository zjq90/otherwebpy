/**
 * 权限管理工具
 * 处理用户登录、登出、权限判断等
 */

import config from './config.js'
import { http } from './http.js'

/**
 * 获取当前登录用户信息
 */
const getUserInfo = () => {
  const userInfo = uni.getStorageSync(config.userInfoKey)
  return userInfo || null
}

/**
 * 获取当前登录用户Token
 */
const getToken = () => {
  const token = uni.getStorageSync(config.tokenKey)
  return token || null
}

/**
 * 检查是否已登录
 */
const isLoggedIn = () => {
  const token = getToken()
  const userInfo = getUserInfo()
  return !!token && !!userInfo
}

/**
 * 获取当前用户角色
 */
const getCurrentRole = () => {
  const userInfo = getUserInfo()
  return userInfo ? userInfo.role : null
}

/**
 * 判断当前用户是否是管理员
 */
const isAdmin = () => {
  return getCurrentRole() === config.roles.ADMIN
}

/**
 * 判断当前用户是否是调度员
 */
const isDispatcher = () => {
  return getCurrentRole() === config.roles.DISPATCHER
}

/**
 * 判断当前用户是否是司机
 */
const isDriver = () => {
  return getCurrentRole() === config.roles.DRIVER
}

/**
 * 判断是否有权限（任意一个角色匹配即可）
 * @param {Array} roles - 允许的角色列表
 */
const hasAnyRole = (roles = []) => {
  const currentRole = getCurrentRole()
  return roles.includes(currentRole)
}

/**
 * 判断是否拥有所有指定权限
 * @param {Array} roles - 必须拥有的角色列表
 */
const hasAllRoles = (roles = []) => {
  const currentRole = getCurrentRole()
  return roles.every(role => role === currentRole)
}

/**
 * 登录
 * @param {String} username - 用户名
 * @param {String} password - 密码
 */
const login = async (username, password) => {
  const formData = new FormData()
  formData.append('username', username)
  formData.append('password', password)
  
  // 注意：登录接口需要使用form-data格式
  // 这里使用普通的post请求，需要在后端支持
  const res = await http.post('/api/auth/login', {
    username,
    password
  }, {
    showLoading: false,
    header: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  })
  
  if (res.code === 200) {
    // 保存Token
    uni.setStorageSync(config.tokenKey, res.data.access_token)
    
    // 获取用户信息
    const userRes = await http.get('/api/auth/me')
    if (userRes.code === 200) {
      uni.setStorageSync(config.userInfoKey, userRes.data)
    }
    
    return {
      success: true,
      data: res.data
    }
  }
  
  return {
    success: false,
    message: res.message || '登录失败'
  }
}

/**
 * 登出
 */
const logout = () => {
  // 清除本地存储
  uni.removeStorageSync(config.tokenKey)
  uni.removeStorageSync(config.userInfoKey)
  
  // 跳转到登录页
  uni.redirectTo({
    url: '/pages/login/login'
  })
}

/**
 * 刷新Token
 */
const refreshToken = async () => {
  const res = await http.post('/api/auth/refresh')
  if (res.code === 200) {
    uni.setStorageSync(config.tokenKey, res.data.access_token)
    return {
      success: true,
      data: res.data
    }
  }
  return {
    success: false,
    message: res.message || '刷新Token失败'
  }
}

/**
 * 获取角色显示名称
 * @param {String} role - 角色标识
 */
const getRoleName = (role) => {
  const roleNames = {
    [config.roles.ADMIN]: '管理员',
    [config.roles.DISPATCHER]: '调度员',
    [config.roles.DRIVER]: '司机'
  }
  return roleNames[role] || '未知角色'
}

/**
 * 获取任务状态样式类名
 * @param {String} status - 任务状态
 */
const getTaskStatusClass = (status) => {
  return `status-${status}`
}

/**
 * 获取任务状态显示文本
 * @param {String} status - 任务状态
 */
const getTaskStatusText = (status) => {
  return config.taskStatusText[status] || '未知状态'
}

/**
 * 获取车辆状态样式类名
 * @param {String} status - 车辆状态
 */
const getVehicleStatusClass = (status) => {
  const statusClassMap = {
    [config.vehicleStatus.IDLE]: 'status-pending',
    [config.vehicleStatus.IN_TRANSIT]: 'status-departed',
    [config.vehicleStatus.MAINTENANCE]: 'status-assigned',
    [config.vehicleStatus.DISABLED]: 'status-cancelled'
  }
  return statusClassMap[status] || 'status-cancelled'
}

/**
 * 获取车辆状态显示文本
 * @param {String} status - 车辆状态
 */
const getVehicleStatusText = (status) => {
  return config.vehicleStatusText[status] || '未知状态'
}

// 导出权限工具
const auth = {
  getUserInfo,
  getToken,
  isLoggedIn,
  getCurrentRole,
  isAdmin,
  isDispatcher,
  isDriver,
  hasAnyRole,
  hasAllRoles,
  login,
  logout,
  refreshToken,
  getRoleName,
  getTaskStatusClass,
  getTaskStatusText,
  getVehicleStatusClass,
  getVehicleStatusText
}

// 挂载到全局
uni.$auth = auth

export { auth }
