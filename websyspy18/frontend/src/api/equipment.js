/**
 * 工程维保管理API
 * 包含设备台账、巡检计划、保养计划、故障维修等接口
 */
import { http } from '@/utils/request'

const API_PREFIX = '/equipment'

// ==================== 设备台账 ====================

/**
 * 获取设备列表
 * @param {Object} params - 查询参数
 * @param {number} params.skip - 跳过数量
 * @param {number} params.limit - 返回数量
 * @param {string} params.category - 设备类别
 * @param {string} params.status - 设备状态
 * @param {string} params.keyword - 关键词
 */
export function getEquipmentList(params) {
  return http.get(`${API_PREFIX}/equipment/`, params)
}

/**
 * 获取单个设备详情
 * @param {number} id - 设备ID
 */
export function getEquipmentById(id) {
  return http.get(`${API_PREFIX}/equipment/${id}`)
}

/**
 * 创建设备
 * @param {Object} data - 设备数据
 */
export function createEquipment(data) {
  return http.post(`${API_PREFIX}/equipment/`, data)
}

/**
 * 更新设备
 * @param {number} id - 设备ID
 * @param {Object} data - 更新数据
 */
export function updateEquipment(id, data) {
  return http.put(`${API_PREFIX}/equipment/${id}`, data)
}

/**
 * 删除设备
 * @param {number} id - 设备ID
 */
export function deleteEquipment(id) {
  return http.delete(`${API_PREFIX}/equipment/${id}`)
}

// ==================== 巡检计划 ====================

/**
 * 获取巡检计划列表
 */
export function getInspectionPlanList(params) {
  return http.get(`${API_PREFIX}/inspection-plans/`, params)
}

/**
 * 获取单个巡检计划
 */
export function getInspectionPlanById(id) {
  return http.get(`${API_PREFIX}/inspection-plans/${id}`)
}

/**
 * 创建巡检计划
 */
export function createInspectionPlan(data) {
  return http.post(`${API_PREFIX}/inspection-plans/`, data)
}

/**
 * 更新巡检计划
 */
export function updateInspectionPlan(id, data) {
  return http.put(`${API_PREFIX}/inspection-plans/${id}`, data)
}

/**
 * 删除巡检计划
 */
export function deleteInspectionPlan(id) {
  return http.delete(`${API_PREFIX}/inspection-plans/${id}`)
}

// ==================== 巡检记录 ====================

/**
 * 获取巡检记录列表
 */
export function getInspectionRecordList(params) {
  return http.get(`${API_PREFIX}/inspection-records/`, params)
}

/**
 * 创建巡检记录
 */
export function createInspectionRecord(data) {
  return http.post(`${API_PREFIX}/inspection-records/`, data)
}

// ==================== 保养计划 ====================

/**
 * 获取保养计划列表
 */
export function getMaintenancePlanList(params) {
  return http.get(`${API_PREFIX}/maintenance-plans/`, params)
}

/**
 * 获取单个保养计划
 */
export function getMaintenancePlanById(id) {
  return http.get(`${API_PREFIX}/maintenance-plans/${id}`)
}

/**
 * 创建保养计划
 */
export function createMaintenancePlan(data) {
  return http.post(`${API_PREFIX}/maintenance-plans/`, data)
}

/**
 * 更新保养计划
 */
export function updateMaintenancePlan(id, data) {
  return http.put(`${API_PREFIX}/maintenance-plans/${id}`, data)
}

/**
 * 删除保养计划
 */
export function deleteMaintenancePlan(id) {
  return http.delete(`${API_PREFIX}/maintenance-plans/${id}`)
}

// ==================== 保养记录 ====================

/**
 * 获取保养记录列表
 */
export function getMaintenanceRecordList(params) {
  return http.get(`${API_PREFIX}/maintenance-records/`, params)
}

/**
 * 创建保养记录
 */
export function createMaintenanceRecord(data) {
  return http.post(`${API_PREFIX}/maintenance-records/`, data)
}

// ==================== 故障维修记录 ====================

/**
 * 获取故障维修记录列表
 */
export function getFaultRecordList(params) {
  return http.get(`${API_PREFIX}/fault-records/`, params)
}

/**
 * 获取单个故障记录
 */
export function getFaultRecordById(id) {
  return http.get(`${API_PREFIX}/fault-records/${id}`)
}

/**
 * 创建故障记录
 */
export function createFaultRecord(data) {
  return http.post(`${API_PREFIX}/fault-records/`, data)
}

/**
 * 更新故障记录
 */
export function updateFaultRecord(id, data) {
  return http.put(`${API_PREFIX}/fault-records/${id}`, data)
}

/**
 * 删除故障记录
 */
export function deleteFaultRecord(id) {
  return http.delete(`${API_PREFIX}/fault-records/${id}`)
}

// ==================== 统计相关 ====================

/**
 * 获取费用统计
 */
export function getCostStatistics() {
  return http.get(`${API_PREFIX}/statistics/cost`)
}

/**
 * 获取设备状态统计
 */
export function getEquipmentStatusStatistics() {
  return http.get(`${API_PREFIX}/statistics/equipment/status`)
}

/**
 * 获取故障类型统计
 */
export function getFaultTypeStatistics() {
  return http.get(`${API_PREFIX}/statistics/fault-type`)
}
