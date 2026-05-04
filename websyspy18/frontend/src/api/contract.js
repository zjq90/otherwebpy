/**
 * 合同与供应商管理API
 * 包含供应商管理、合同管理、付款记录、服务质量评估等接口
 */
import { http } from '@/utils/request'

const API_PREFIX = '/contract'

// ==================== 供应商管理 ====================

/**
 * 获取供应商列表
 * @param {Object} params - 查询参数
 */
export function getSupplierList(params) {
  return http.get(`${API_PREFIX}/suppliers/`, params)
}

/**
 * 获取单个供应商
 */
export function getSupplierById(id) {
  return http.get(`${API_PREFIX}/suppliers/${id}`)
}

/**
 * 创建供应商
 */
export function createSupplier(data) {
  return http.post(`${API_PREFIX}/suppliers/`, data)
}

/**
 * 更新供应商
 */
export function updateSupplier(id, data) {
  return http.put(`${API_PREFIX}/suppliers/${id}`, data)
}

/**
 * 删除供应商
 */
export function deleteSupplier(id) {
  return http.delete(`${API_PREFIX}/suppliers/${id}`)
}

/**
 * 获取供应商评估统计
 */
export function getSupplierStatistics(id) {
  return http.get(`${API_PREFIX}/suppliers/${id}/statistics`)
}

// ==================== 合同管理 ====================

/**
 * 获取合同列表
 */
export function getContractList(params) {
  return http.get(`${API_PREFIX}/contracts/`, params)
}

/**
 * 获取单个合同
 */
export function getContractById(id) {
  return http.get(`${API_PREFIX}/contracts/${id}`)
}

/**
 * 创建合同
 */
export function createContract(data) {
  return http.post(`${API_PREFIX}/contracts/`, data)
}

/**
 * 更新合同
 */
export function updateContract(id, data) {
  return http.put(`${API_PREFIX}/contracts/${id}`, data)
}

/**
 * 删除合同
 */
export function deleteContract(id) {
  return http.delete(`${API_PREFIX}/contracts/${id}`)
}

// ==================== 合同付款 ====================

/**
 * 获取付款记录列表
 */
export function getContractPaymentList(params) {
  return http.get(`${API_PREFIX}/payments/`, params)
}

/**
 * 获取单个付款记录
 */
export function getContractPaymentById(id) {
  return http.get(`${API_PREFIX}/payments/${id}`)
}

/**
 * 创建付款记录
 */
export function createContractPayment(data) {
  return http.post(`${API_PREFIX}/payments/`, data)
}

/**
 * 更新付款记录
 */
export function updateContractPayment(id, data) {
  return http.put(`${API_PREFIX}/payments/${id}`, data)
}

/**
 * 删除付款记录
 */
export function deleteContractPayment(id) {
  return http.delete(`${API_PREFIX}/payments/${id}`)
}

// ==================== 服务质量评估 ====================

/**
 * 获取评估列表
 */
export function getServiceEvaluationList(params) {
  return http.get(`${API_PREFIX}/evaluations/`, params)
}

/**
 * 获取单个评估记录
 */
export function getServiceEvaluationById(id) {
  return http.get(`${API_PREFIX}/evaluations/${id}`)
}

/**
 * 创建评估记录
 */
export function createServiceEvaluation(data) {
  return http.post(`${API_PREFIX}/evaluations/`, data)
}

/**
 * 更新评估记录
 */
export function updateServiceEvaluation(id, data) {
  return http.put(`${API_PREFIX}/evaluations/${id}`, data)
}

/**
 * 删除评估记录
 */
export function deleteServiceEvaluation(id) {
  return http.delete(`${API_PREFIX}/evaluations/${id}`)
}
