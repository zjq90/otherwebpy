/**
 * API请求封装模块
 * 统一管理所有API接口调用
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('响应错误:', error)
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// ==================== 仪表盘API ====================

export const dashboardApi = {
  /**
   * 获取统计数据
   */
  getStats() {
    return api.get('/dashboard/stats')
  }
}

// ==================== 物业项目API ====================

export const propertyProjectApi = {
  /**
   * 获取物业项目列表
   * @param {Object} params - 查询参数
   * @param {number} params.skip - 跳过条数
   * @param {number} params.limit - 每页条数
   * @param {string} params.name - 搜索关键词
   */
  getList(params = {}) {
    return api.get('/property-projects/', { params })
  },

  /**
   * 获取单个物业项目详情
   * @param {number} id - 项目ID
   */
  getById(id) {
    return api.get(`/property-projects/${id}`)
  },

  /**
   * 创建物业项目
   * @param {Object} data - 项目数据
   */
  create(data) {
    return api.post('/property-projects/', data)
  },

  /**
   * 更新物业项目
   * @param {number} id - 项目ID
   * @param {Object} data - 更新数据
   */
  update(id, data) {
    return api.put(`/property-projects/${id}`, data)
  },

  /**
   * 删除物业项目
   * @param {number} id - 项目ID
   */
  delete(id) {
    return api.delete(`/property-projects/${id}`)
  }
}

// ==================== 房产信息API ====================

export const propertyApi = {
  /**
   * 获取房产列表
   * @param {Object} params - 查询参数
   */
  getList(params = {}) {
    return api.get('/properties/', { params })
  },

  /**
   * 获取单个房产详情
   * @param {number} id - 房产ID
   */
  getById(id) {
    return api.get(`/properties/${id}`)
  },

  /**
   * 创建房产信息
   * @param {Object} data - 房产数据
   */
  create(data) {
    return api.post('/properties/', data)
  },

  /**
   * 更新房产信息
   * @param {number} id - 房产ID
   * @param {Object} data - 更新数据
   */
  update(id, data) {
    return api.put(`/properties/${id}`, data)
  },

  /**
   * 删除房产信息
   * @param {number} id - 房产ID
   */
  delete(id) {
    return api.delete(`/properties/${id}`)
  }
}

// ==================== 业主/住户API ====================

export const ownerApi = {
  /**
   * 获取业主列表
   * @param {Object} params - 查询参数
   */
  getList(params = {}) {
    return api.get('/owners/', { params })
  },

  /**
   * 获取单个业主详情
   * @param {number} id - 业主ID
   */
  getById(id) {
    return api.get(`/owners/${id}`)
  },

  /**
   * 创建业主信息
   * @param {Object} data - 业主数据
   */
  create(data) {
    return api.post('/owners/', data)
  },

  /**
   * 更新业主信息
   * @param {number} id - 业主ID
   * @param {Object} data - 更新数据
   */
  update(id, data) {
    return api.put(`/owners/${id}`, data)
  },

  /**
   * 删除业主信息
   * @param {number} id - 业主ID
   */
  delete(id) {
    return api.delete(`/owners/${id}`)
  },

  /**
   * 添加家庭成员
   * @param {number} ownerId - 业主ID
   * @param {Object} data - 家庭成员数据
   */
  addFamilyMember(ownerId, data) {
    return api.post(`/owners/${ownerId}/family-members`, data)
  },

  /**
   * 删除家庭成员
   * @param {number} memberId - 家庭成员ID
   */
  deleteFamilyMember(memberId) {
    return api.delete(`/owners/family-members/${memberId}`)
  },

  /**
   * 添加车辆信息
   * @param {number} ownerId - 业主ID
   * @param {Object} data - 车辆数据
   */
  addVehicle(ownerId, data) {
    return api.post(`/owners/${ownerId}/vehicles`, data)
  },

  /**
   * 删除车辆信息
   * @param {number} vehicleId - 车辆ID
   */
  deleteVehicle(vehicleId) {
    return api.delete(`/owners/vehicles/${vehicleId}`)
  }
}

// ==================== 测试数据API ====================

export const testDataApi = {
  /**
   * 生成测试数据
   * @param {boolean} clearExisting - 是否清除现有数据
   */
  generate(clearExisting = true) {
    return api.post('/test-data/generate', null, {
      params: { clear_existing: clearExisting }
    })
  }
}

export default api
