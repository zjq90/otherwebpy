import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API接口封装
export const api = {
  // ========== 教练相关 ==========
  coach: {
    // 获取教练列表
    getList: (params) => request.get('/coaches/', { params }),
    // 获取单个教练
    getById: (id) => request.get(`/coaches/${id}`),
    // 创建教练
    create: (data) => request.post('/coaches/', data),
    // 更新教练
    update: (id, data) => request.put(`/coaches/${id}`, data),
    // 删除教练
    delete: (id) => request.delete(`/coaches/${id}`),
    // 获取教练排班
    getSchedules: (coachId, params) => request.get(`/coaches/${coachId}/schedules/`, { params }),
    // 创建排班
    createSchedule: (data) => request.post('/coaches/schedules/', data),
    // 更新排班
    updateSchedule: (id, data) => request.put(`/coaches/schedules/${id}`, data),
    // 删除排班
    deleteSchedule: (id) => request.delete(`/coaches/schedules/${id}`)
  },

  // ========== 会员相关 ==========
  member: {
    // 获取会员列表
    getList: (params) => request.get('/members/', { params }),
    // 获取单个会员
    getById: (id) => request.get(`/members/${id}`),
    // 创建会员
    create: (data) => request.post('/members/', data),
    // 更新会员
    update: (id, data) => request.put(`/members/${id}`, data),
    // 删除会员
    delete: (id) => request.delete(`/members/${id}`),
    // 获取会员的课程包
    getPackages: (memberId, params) => request.get(`/members/${memberId}/packages/`, { params })
  },

  // ========== 课程包相关 ==========
  package: {
    // 获取课程包列表
    getList: (params) => request.get('/members/packages/', { params }),
    // 获取单个课程包
    getById: (id) => request.get(`/members/packages/${id}`),
    // 创建课程包（购买）
    create: (data) => request.post('/members/packages/', data),
    // 更新课程包
    update: (id, data) => request.put(`/members/packages/${id}`, data)
  },

  // ========== 课时记录相关 ==========
  lesson: {
    // 获取课时记录列表
    getList: (params) => request.get('/lessons/', { params }),
    // 获取单个课时记录
    getById: (id) => request.get(`/lessons/${id}`),
    // 创建课时记录（预约）
    create: (data) => request.post('/lessons/', data),
    // 完成课时（核销）
    complete: (id, data) => request.post(`/lessons/${id}/complete`, data),
    // 更新课时记录
    update: (id, data) => request.put(`/lessons/${id}`, data),
    // 取消预约
    cancel: (id) => request.post(`/lessons/${id}/cancel`)
  },

  // ========== 补课相关 ==========
  makeup: {
    // 获取补课记录列表
    getList: (params) => request.get('/lessons/makeups/', { params }),
    // 获取单个补课记录
    getById: (id) => request.get(`/lessons/makeups/${id}`),
    // 申请补课
    create: (data) => request.post('/lessons/makeups/', data),
    // 审批补课
    approve: (id, data) => request.post(`/lessons/makeups/${id}/approve`, data)
  },

  // ========== 冻结相关 ==========
  freeze: {
    // 获取冻结记录列表
    getList: (params) => request.get('/lessons/freezes/', { params }),
    // 冻结课程包
    create: (data) => request.post('/lessons/freezes/', data),
    // 解冻课程包
    unfreeze: (id) => request.post(`/lessons/freezes/${id}/unfreeze`)
  },

  // ========== 业绩相关 ==========
  performance: {
    // 获取教练统计数据
    getStats: (coachId) => request.get(`/performance/stats/${coachId}`),
    // 生成月度业绩记录
    generateMonthly: (params) => request.post('/performance/generate/monthly', null, { params }),
    // 获取业绩记录列表
    getRecords: (params) => request.get('/performance/records/', { params }),
    // 获取业绩排名
    getRanking: (params) => request.get('/performance/ranking/', { params }),
    // 获取月度汇总
    getMonthlySummary: (params) => request.get('/performance/monthly-summary/', { params })
  },

  // ========== 测试数据相关 ==========
  test: {
    // 生成所有测试数据
    generateAll: (params) => request.post('/test/generate/all', null, { params }),
    // 生成教练数据
    generateCoaches: (params) => request.post('/test/generate/coaches', null, { params }),
    // 生成会员数据
    generateMembers: (params) => request.post('/test/generate/members', null, { params }),
    // 清空所有测试数据
    clearAll: () => request.delete('/test/clear')
  }
}

export default request
