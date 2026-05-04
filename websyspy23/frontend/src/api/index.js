import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api/v1',
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
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// ==================== 卡类型API ====================
export const cardTypeApi = {
  getList: (params) => api.get('/cards/types', { params }),
  getById: (id) => api.get(`/cards/types/${id}`),
  create: (data) => api.post('/cards/types', data),
  update: (id, data) => api.put(`/cards/types/${id}`, data),
  delete: (id) => api.delete(`/cards/types/${id}`)
}

// ==================== 卡项API ====================
export const cardApi = {
  getList: (params) => api.get('/cards', { params }),
  getById: (id) => api.get(`/cards/${id}`),
  create: (data) => api.post('/cards', data),
  update: (id, data) => api.put(`/cards/${id}`, data),
  delete: (id) => api.delete(`/cards/${id}`)
}

// ==================== 课程类型API ====================
export const courseTypeApi = {
  getList: (params) => api.get('/courses/types', { params }),
  getById: (id) => api.get(`/courses/types/${id}`),
  create: (data) => api.post('/courses/types', data),
  update: (id, data) => api.put(`/courses/types/${id}`, data),
  delete: (id) => api.delete(`/courses/types/${id}`)
}

// ==================== 课程API ====================
export const courseApi = {
  getList: (params) => api.get('/courses', { params }),
  getById: (id) => api.get(`/courses/${id}`),
  create: (data) => api.post('/courses', data),
  update: (id, data) => api.put(`/courses/${id}`, data),
  delete: (id) => api.delete(`/courses/${id}`)
}

// ==================== 课程排期API ====================
export const scheduleApi = {
  getList: (params) => api.get('/schedules', { params }),
  getById: (id) => api.get(`/schedules/${id}`),
  create: (data) => api.post('/schedules', data),
  update: (id, data) => api.put(`/schedules/${id}`, data),
  delete: (id) => api.delete(`/schedules/${id}`)
}

// ==================== 场地API ====================
export const venueApi = {
  getList: (params) => api.get('/venues', { params }),
  getById: (id) => api.get(`/venues/${id}`),
  create: (data) => api.post('/venues', data),
  update: (id, data) => api.put(`/venues/${id}`, data),
  delete: (id) => api.delete(`/venues/${id}`)
}

// ==================== 会员API ====================
export const memberApi = {
  getList: (params) => api.get('/members', { params }),
  getById: (id) => api.get(`/members/${id}`),
  create: (data) => api.post('/members', data),
  update: (id, data) => api.put(`/members/${id}`, data),
  delete: (id) => api.delete(`/members/${id}`)
}

// ==================== 会员卡API ====================
export const memberCardApi = {
  getList: (params) => api.get('/members/cards', { params }),
  getById: (id) => api.get(`/members/cards/${id}`),
  create: (data) => api.post('/members/cards', data),
  update: (id, data) => api.put(`/members/cards/${id}`, data),
  delete: (id) => api.delete(`/members/cards/${id}`)
}

export default api
