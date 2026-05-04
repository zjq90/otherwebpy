/**
 * 认证工具类
 * 处理Token和用户信息的存储与获取
 */

const TOKEN_KEY = 'token'
const USER_INFO_KEY = 'userInfo'
const BASE_URL_KEY = 'baseUrl'

// 默认API地址
const DEFAULT_BASE_URL = 'http://localhost:8000'

/**
 * 获取API基础地址
 */
export function getBaseUrl() {
    return uni.getStorageSync(BASE_URL_KEY) || DEFAULT_BASE_URL
}

/**
 * 设置API基础地址
 */
export function setBaseUrl(url) {
    uni.setStorageSync(BASE_URL_KEY, url)
}

/**
 * 获取Token
 */
export function getToken() {
    return uni.getStorageSync(TOKEN_KEY)
}

/**
 * 设置Token
 */
export function setToken(token) {
    uni.setStorageSync(TOKEN_KEY, token)
}

/**
 * 移除Token
 */
export function removeToken() {
    uni.removeStorageSync(TOKEN_KEY)
}

/**
 * 获取用户信息
 */
export function getUserInfo() {
    const userInfo = uni.getStorageSync(USER_INFO_KEY)
    return userInfo ? JSON.parse(userInfo) : null
}

/**
 * 设置用户信息
 */
export function setUserInfo(userInfo) {
    uni.setStorageSync(USER_INFO_KEY, JSON.stringify(userInfo))
}

/**
 * 移除用户信息
 */
export function removeUserInfo() {
    uni.removeStorageSync(USER_INFO_KEY)
}

/**
 * 清除所有认证信息
 */
export function clearAuth() {
    removeToken()
    removeUserInfo()
}

/**
 * 检查是否已登录
 */
export function isLoggedIn() {
    return !!getToken()
}

/**
 * 跳转到登录页
 */
export function navigateToLogin() {
    uni.navigateTo({
        url: '/pages/login/login'
    })
}

/**
 * 跳转到首页
 */
export function navigateToHome() {
    uni.switchTab({
        url: '/pages/index/index'
    })
}
