/**
 * 认证相关API
 */

import request from '../utils/request'

/**
 * 发送验证码
 * @param {String} phone 手机号
 */
export const sendCode = (phone) => {
    return request.post('/auth/send-code', { phone }, { auth: false })
}

/**
 * 账号密码登录
 * @param {String} username 用户名
 * @param {String} password 密码
 */
export const loginWithPassword = (username, password) => {
    return request.post('/auth/login/password', { username, password }, { auth: false })
}

/**
 * 手机号验证码登录
 * @param {String} phone 手机号
 * @param {String} code 验证码
 */
export const loginWithPhone = (phone, code) => {
    return request.post('/auth/login/phone', { phone, code }, { auth: false })
}

/**
 * 实名认证
 * @param {String} realName 真实姓名
 * @param {String} idCard 身份证号
 */
export const realNameVerify = (realName, idCard) => {
    return request.post('/auth/real-name-verify', { real_name: realName, id_card: idCard }, { auth: true })
}

/**
 * 获取当前用户信息
 */
export const getCurrentUser = () => {
    return request.get('/auth/me', {}, { auth: true })
}

/**
 * 获取当前用户权限
 */
export const getCurrentPermissions = () => {
    return request.get('/auth/permissions', {}, { auth: true })
}

/**
 * 修改密码
 * @param {String} oldPassword 旧密码
 * @param {String} newPassword 新密码
 */
export const changePassword = (oldPassword, newPassword) => {
    return request.post('/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword
    }, { auth: true })
}

/**
 * 退出登录
 */
export const logout = () => {
    return request.post('/auth/logout', {}, { auth: true })
}

/**
 * 获取测试账号列表（仅用于开发测试）
 */
export const getTestAccounts = () => {
    return request.get('/test/test-accounts', {}, { auth: false })
}
