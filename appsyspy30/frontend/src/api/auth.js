/**
 * 认证相关API
 */
import { get, post, put } from '../utils/request'

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @param {string} data.username - 用户名
 * @param {string} data.email - 邮箱
 * @param {string} data.password - 密码
 * @param {string} data.nickname - 昵称
 * @param {string} data.invite_code - 邀请码（可选）
 */
export function register(data) {
    return post('/auth/register', data, {
        showLoading: true,
        loadingText: '注册中...'
    })
}

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户名或邮箱
 * @param {string} data.password - 密码
 */
export function login(data) {
    return post('/auth/login', data, {
        showLoading: true,
        loadingText: '登录中...'
    })
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
    return get('/auth/me', {}, {
        showLoading: false
    })
}

/**
 * 更新当前用户信息
 * @param {Object} data - 用户数据
 * @param {string} data.nickname - 昵称
 * @param {string} data.bio - 个人简介
 * @param {string} data.phone - 手机号
 * @param {string} data.avatar - 头像
 */
export function updateCurrentUser(data) {
    return put('/auth/me', data, {
        showLoading: true,
        loadingText: '更新中...'
    })
}

/**
 * 用户登出
 */
export function logout() {
    return post('/auth/logout', {}, {
        showLoading: false
    })
}

/**
 * 刷新Token
 */
export function refreshToken() {
    return post('/auth/refresh', {}, {
        showLoading: false
    })
}

export const authApi = {
    register,
    login,
    getCurrentUser,
    updateCurrentUser,
    logout,
    refreshToken
}

export default authApi
