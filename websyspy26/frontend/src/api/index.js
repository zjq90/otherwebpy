/**
 * API接口封装
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
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

// 会员相关API
export const memberApi = {
  // 获取会员列表
  getList: (params) => api.get('/members/', { params }),
  // 获取会员详情
  getById: (id) => api.get(`/members/${id}`),
  // 创建会员
  create: (data) => api.post('/members/', data),
  // 更新会员
  update: (id, data) => api.put(`/members/${id}`, data),
  // 删除会员
  delete: (id) => api.delete(`/members/${id}`),
  // 获取会员的会员卡
  getCards: (memberId) => api.get(`/members/${memberId}/cards`),
  // 创建会员卡
  createCard: (data) => api.post('/members/cards/', data),
  // 更新会员卡
  updateCard: (cardId, data) => api.put(`/members/cards/${cardId}`, data),
  // 删除会员卡
  deleteCard: (cardId) => api.delete(`/members/cards/${cardId}`),
  // 会员卡续费
  renewCard: (cardId, params) => api.post(`/members/cards/${cardId}/renew`, null, { params })
}

// 促销活动相关API
export const promotionApi = {
  // 获取活动列表
  getList: (params) => api.get('/promotions/', { params }),
  // 获取进行中的活动
  getActive: () => api.get('/promotions/active'),
  // 获取活动详情
  getById: (id) => api.get(`/promotions/${id}`),
  // 创建活动
  create: (data) => api.post('/promotions/', data),
  // 更新活动
  update: (id, data) => api.put(`/promotions/${id}`, data),
  // 删除活动
  delete: (id) => api.delete(`/promotions/${id}`),
  // 开始活动
  start: (id) => api.post(`/promotions/${id}/start`),
  // 结束活动
  end: (id) => api.post(`/promotions/${id}/end`),
  // 获取活动优惠券
  getCoupons: (promotionId) => api.get(`/promotions/${promotionId}/coupons`),
  // 批量生成优惠券
  generateCoupons: (promotionId, quantity) => 
    api.post(`/promotions/${promotionId}/generate-coupons`, null, { params: { quantity } }),
  // 定向发放优惠券
  distribute: (promotionId) => api.post(`/promotions/${promotionId}/distribute`),
  // 获取会员的优惠券
  getMemberCoupons: (memberId, status) => 
    api.get(`/promotions/members/${memberId}/coupons`, { params: { status } })
}

// 续费提醒相关API
export const reminderApi = {
  // 获取提醒列表
  getList: (params) => api.get('/reminders/', { params }),
  // 获取待发送的提醒
  getPending: () => api.get('/reminders/pending'),
  // 获取提醒详情
  getById: (id) => api.get(`/reminders/${id}`),
  // 创建提醒
  create: (data) => api.post('/reminders/', data),
  // 更新提醒
  update: (id, data) => api.put(`/reminders/${id}`, data),
  // 标记为已发送
  markAsSent: (id) => api.post(`/reminders/${id}/send`),
  // 标记为发送失败
  markAsFailed: (id, errorMessage) => 
    api.post(`/reminders/${id}/fail`, null, { params: { error_message: errorMessage } }),
  // 标记为已续费
  markAsRenewed: (id, renewalMethod) => 
    api.post(`/reminders/${id}/renewed`, null, { params: { renewal_method: renewalMethod } }),
  // 为即将到期的会员卡生成提醒
  generateForExpiring: () => api.post('/reminders/generate-for-expiring'),
  // 发送所有待发送的提醒
  sendPending: () => api.post('/reminders/send-pending')
}

// 测试功能API
export const testApi = {
  // 生成测试会员
  generateMembers: (count) => 
    api.post('/test/generate-members', null, { params: { count } }),
  // 生成测试会员卡
  generateMemberCards: (memberCount, cardsPerMember) => 
    api.post('/test/generate-member-cards', null, { 
      params: { member_count: memberCount, cards_per_member: cardsPerMember } 
    }),
  // 生成测试活动
  generatePromotions: (count) => 
    api.post('/test/generate-promotions', null, { params: { count } }),
  // 生成即将到期的会员卡
  generateExpiringCards: (count) => 
    api.post('/test/generate-expiring-cards', null, { params: { count } }),
  // 一键生成所有测试数据
  generateAll: (memberCount) => 
    api.post('/test/generate-all', null, { params: { member_count: memberCount } }),
  // 获取系统统计
  getStats: () => api.get('/test/stats')
}

export default api
