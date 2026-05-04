/**
 * 认证相关工具函数
 */
import Cookies from 'js-cookie'
import request from '@/utils/request'

// Token 存储的 Key
const TokenKey = 'Admin-Token'

// ==================== Token 存储操作 ====================

/**
 * 获取 Token
 * @returns {string|null}
 */
export function getToken() {
  return Cookies.get(TokenKey)
}

/**
 * 设置 Token
 * @param {string} token - Token 值
 * @returns {string}
 */
export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

/**
 * 移除 Token
 * @returns {void}
 */
export function removeToken() {
  return Cookies.remove(TokenKey)
}

// ==================== API 接口 ====================

/**
 * 用户登录
 * @param {object} data - 登录信息 { username, password }
 * @returns {Promise}
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 用户登出
 * @returns {Promise}
 */
export function logout() {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}

/**
 * 获取当前用户信息
 * @returns {Promise}
 */
export function getUserInfo() {
  return request({
    url: '/auth/current-user',
    method: 'get'
  })
}

/**
 * 获取当前用户权限
 * @returns {Promise}
 */
export function getPermissions() {
  return request({
    url: '/auth/me/permissions',
    method: 'get'
  })
}

/**
 * 刷新 Token
 * @returns {Promise}
 */
export function refreshToken() {
  return request({
    url: '/auth/refresh-token',
    method: 'post'
  })
}

// ==================== 用户管理相关接口 ====================

/**
 * 获取用户列表（分页）
 * @param {object} params - 查询参数
 * @returns {Promise}
 */
export function getUserList(params) {
  return request({
    url: '/users/',
    method: 'get',
    params
  })
}

/**
 * 获取用户详情
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export function getUserDetail(userId) {
  return request({
    url: `/users/${userId}`,
    method: 'get'
  })
}

/**
 * 创建用户
 * @param {object} data - 用户信息
 * @returns {Promise}
 */
export function createUser(data) {
  return request({
    url: '/users/',
    method: 'post',
    data
  })
}

/**
 * 更新用户
 * @param {number} userId - 用户ID
 * @param {object} data - 用户信息
 * @returns {Promise}
 */
export function updateUser(userId, data) {
  return request({
    url: `/users/${userId}`,
    method: 'put',
    data
  })
}

/**
 * 删除用户
 * @param {number} userId - 用户ID
 * @returns {Promise}
 */
export function deleteUser(userId) {
  return request({
    url: `/users/${userId}`,
    method: 'delete'
  })
}

/**
 * 分配角色给用户
 * @param {number} userId - 用户ID
 * @param {array} roleIds - 角色ID数组
 * @returns {Promise}
 */
export function assignRoles(userId, roleIds) {
  return request({
    url: `/users/${userId}/roles`,
    method: 'post',
    data: { role_ids: roleIds }
  })
}

// ==================== 角色管理相关接口 ====================

/**
 * 获取角色列表
 * @returns {Promise}
 */
export function getRoleList() {
  return request({
    url: '/roles/',
    method: 'get'
  })
}

/**
 * 获取角色详情
 * @param {number} roleId - 角色ID
 * @returns {Promise}
 */
export function getRoleDetail(roleId) {
  return request({
    url: `/roles/${roleId}`,
    method: 'get'
  })
}

/**
 * 创建角色
 * @param {object} data - 角色信息
 * @returns {Promise}
 */
export function createRole(data) {
  return request({
    url: '/roles/',
    method: 'post',
    data
  })
}

/**
 * 更新角色
 * @param {number} roleId - 角色ID
 * @param {object} data - 角色信息
 * @returns {Promise}
 */
export function updateRole(roleId, data) {
  return request({
    url: `/roles/${roleId}`,
    method: 'put',
    data
  })
}

/**
 * 删除角色
 * @param {number} roleId - 角色ID
 * @returns {Promise}
 */
export function deleteRole(roleId) {
  return request({
    url: `/roles/${roleId}`,
    method: 'delete'
  })
}

/**
 * 分配权限给角色
 * @param {number} roleId - 角色ID
 * @param {array} permissionIds - 权限ID数组
 * @returns {Promise}
 */
export function assignPermissions(roleId, permissionIds) {
  return request({
    url: `/roles/${roleId}/permissions`,
    method: 'post',
    data: { permission_ids: permissionIds }
  })
}

// ==================== 权限管理相关接口 ====================

/**
 * 获取权限列表
 * @returns {Promise}
 */
export function getPermissionList() {
  return request({
    url: '/permissions/',
    method: 'get'
  })
}

/**
 * 获取权限详情
 * @param {number} permissionId - 权限ID
 * @returns {Promise}
 */
export function getPermissionDetail(permissionId) {
  return request({
    url: `/permissions/${permissionId}`,
    method: 'get'
  })
}

/**
 * 创建权限
 * @param {object} data - 权限信息
 * @returns {Promise}
 */
export function createPermission(data) {
  return request({
    url: '/permissions/',
    method: 'post',
    data
  })
}

/**
 * 更新权限
 * @param {number} permissionId - 权限ID
 * @param {object} data - 权限信息
 * @returns {Promise}
 */
export function updatePermission(permissionId, data) {
  return request({
    url: `/permissions/${permissionId}`,
    method: 'put',
    data
  })
}

/**
 * 删除权限
 * @param {number} permissionId - 权限ID
 * @returns {Promise}
 */
export function deletePermission(permissionId) {
  return request({
    url: `/permissions/${permissionId}`,
    method: 'delete'
  })
}

// ==================== 操作日志相关接口 ====================

/**
 * 获取操作日志列表（分页）
 * @param {object} params - 查询参数
 * @returns {Promise}
 */
export function getOperationLogList(params) {
  return request({
    url: '/operation-logs/',
    method: 'get',
    params
  })
}

/**
 * 获取操作日志详情
 * @param {number} logId - 日志ID
 * @returns {Promise}
 */
export function getOperationLogDetail(logId) {
  return request({
    url: `/operation-logs/${logId}`,
    method: 'get'
  })
}

/**
 * 获取操作日志统计
 * @param {object} params - 查询参数
 * @returns {Promise}
 */
export function getOperationLogStats(params) {
  return request({
    url: '/operation-logs/stats',
    method: 'get',
    params
  })
}

/**
 * 批量删除操作日志
 * @param {array} logIds - 日志ID数组
 * @returns {Promise}
 */
export function deleteOperationLogs(logIds) {
  return request({
    url: '/operation-logs/batch-delete',
    method: 'post',
    data: { log_ids: logIds }
  })
}

/**
 * 清理旧的操作日志
 * @param {number} daysBefore - 清理几天前的日志
 * @returns {Promise}
 */
export function cleanupOperationLogs(daysBefore) {
  return request({
    url: '/operation-logs/cleanup',
    method: 'post',
    data: { days_before: daysBefore }
  })
}

// ==================== 测试功能相关接口 ====================

/**
 * 生成测试数据
 * @param {object} data - 生成参数
 * @returns {Promise}
 */
export function generateTestData(data) {
  return request({
    url: '/test/generate-data',
    method: 'post',
    data
  })
}

/**
 * 清理测试数据
 * @returns {Promise}
 */
export function cleanupTestData() {
  return request({
    url: '/test/cleanup-test-data',
    method: 'post'
  })
}

/**
 * 测试权限
 * @param {string} permissionCode - 权限代码
 * @returns {Promise}
 */
export function testPermission(permissionCode) {
  return request({
    url: '/test/test-permission',
    method: 'get',
    params: { permission_code: permissionCode }
  })
}

/**
 * 获取系统信息
 * @returns {Promise}
 */
export function getSystemInfo() {
  return request({
    url: '/test/system-info',
    method: 'get'
  })
}
