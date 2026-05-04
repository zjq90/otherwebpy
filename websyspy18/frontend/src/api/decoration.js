/**
 * 装修管理API
 * 包含装修申请、押金管理、装修巡检等接口
 */
import { http } from '@/utils/request'

const API_PREFIX = '/decoration'

// ==================== 装修申请 ====================

/**
 * 获取装修申请列表
 * @param {Object} params - 查询参数
 */
export function getDecorationApplicationList(params) {
  return http.get(`${API_PREFIX}/applications/`, params)
}

/**
 * 获取单个装修申请
 */
export function getDecorationApplicationById(id) {
  return http.get(`${API_PREFIX}/applications/${id}`)
}

/**
 * 创建装修申请
 */
export function createDecorationApplication(data) {
  return http.post(`${API_PREFIX}/applications/`, data)
}

/**
 * 更新装修申请
 */
export function updateDecorationApplication(id, data) {
  return http.put(`${API_PREFIX}/applications/${id}`, data)
}

/**
 * 删除装修申请
 */
export function deleteDecorationApplication(id) {
  return http.delete(`${API_PREFIX}/applications/${id}`)
}

// ==================== 装修押金 ====================

/**
 * 获取押金列表
 */
export function getDecorationDepositList(params) {
  return http.get(`${API_PREFIX}/deposits/`, params)
}

/**
 * 获取单个押金记录
 */
export function getDecorationDepositById(id) {
  return http.get(`${API_PREFIX}/deposits/${id}`)
}

/**
 * 创建押金记录
 */
export function createDecorationDeposit(data) {
  return http.post(`${API_PREFIX}/deposits/`, data)
}

/**
 * 更新押金记录
 */
export function updateDecorationDeposit(id, data) {
  return http.put(`${API_PREFIX}/deposits/${id}`, data)
}

/**
 * 删除押金记录
 */
export function deleteDecorationDeposit(id) {
  return http.delete(`${API_PREFIX}/deposits/${id}`)
}

// ==================== 装修巡检 ====================

/**
 * 获取巡检列表
 */
export function getDecorationInspectionList(params) {
  return http.get(`${API_PREFIX}/inspections/`, params)
}

/**
 * 获取单个巡检记录
 */
export function getDecorationInspectionById(id) {
  return http.get(`${API_PREFIX}/inspections/${id}`)
}

/**
 * 创建巡检记录
 */
export function createDecorationInspection(data) {
  return http.post(`${API_PREFIX}/inspections/`, data)
}

/**
 * 更新巡检记录
 */
export function updateDecorationInspection(id, data) {
  return http.put(`${API_PREFIX}/inspections/${id}`, data)
}

/**
 * 删除巡检记录
 */
export function deleteDecorationInspection(id) {
  return http.delete(`${API_PREFIX}/inspections/${id}`)
}
