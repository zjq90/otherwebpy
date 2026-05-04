/**
 * API 配置和请求封装模块
 * 封装axios请求，提供统一的API调用接口
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
    // 可以在这里添加token等认证信息
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
    
    let message = '网络错误'
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = error.response.data?.detail || '请求参数错误'
          break
        case 404:
          message = '请求的资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = error.response.data?.detail || `请求失败 (${error.response.status})`
      }
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// API接口封装
export default {
  // ============ 会员管理 ============
  getMembers: (params = {}) => api.get('/members/', { params }),
  getMember: (id) => api.get(`/members/${id}`),
  createMember: (data) => api.post('/members/', data),
  updateMember: (id, data) => api.put(`/members/${id}`, data),
  deleteMember: (id) => api.delete(`/members/${id}`),
  validateMember: (identifier) => api.get(`/members/validate/${identifier}`),
  rechargeMember: (memberId, amount, giftAmount) => 
    api.post(`/members/recharge/${memberId}`, null, { 
      params: { amount, gift_amount: giftAmount } 
    }),

  // ============ 签到管理 ============
  verifyCheckin: (data) => api.post('/checkins/verify', data),
  getCheckins: (params = {}) => api.get('/checkins/', { params }),
  getCheckin: (id) => api.get(`/checkins/${id}`),
  getTodayStats: () => api.get('/checkins/today/stats'),
  quickCheckin: (memberId, checkInType) => 
    api.post(`/checkins/quick/${memberId}`, null, { 
      params: { check_in_type: checkInType } 
    }),

  // ============ 储物柜管理 ============
  getLockers: (params = {}) => api.get('/lockers/', { params }),
  getLocker: (id) => api.get(`/lockers/${id}`),
  createLocker: (data) => api.post('/lockers/', data),
  updateLocker: (id, data) => api.put(`/lockers/${id}`, data),
  getLockerStats: () => api.get('/lockers/stats'),
  assignLocker: (data) => api.post('/lockers/assign', data),
  returnLocker: (data) => api.post('/lockers/return', data),
  getMemberUsages: (memberId, status) => 
    api.get(`/lockers/usage/member/${memberId}`, { params: { status } }),
  getActiveUsages: (params = {}) => api.get('/lockers/usage/active', { params }),

  // ============ 收银管理 ============
  // 商品
  getProducts: (params = {}) => api.get('/cashier/products', { params }),
  createProduct: (data) => api.post('/cashier/products', data),
  updateProduct: (id, data) => api.put(`/cashier/products/${id}`, data),
  deleteProduct: (id) => api.delete(`/cashier/products/${id}`),
  
  // 优惠券
  getCoupons: (params = {}) => api.get('/cashier/coupons', { params }),
  createCoupon: (data) => api.post('/cashier/coupons', data),
  validateCoupon: (couponCode, orderAmount, memberId) => 
    api.get(`/cashier/coupons/validate/${couponCode}`, { 
      params: { order_amount: orderAmount, member_id: memberId } 
    }),
  
  // 订单
  createOrder: (data) => api.post('/cashier/orders/create', data),
  payOrder: (data) => api.post('/cashier/orders/pay', data),
  getOrders: (params = {}) => api.get('/cashier/orders', { params }),
  getOrder: (id) => api.get(`/cashier/orders/${id}`),
  
  // 对账
  getDailyReconcile: (dateStr) => 
    api.get('/cashier/reconcile/daily', { params: { date_str: dateStr } }),
  
  // 充值
  memberRecharge: (memberId, amount, giftAmount, paymentMethod, operator) => 
    api.post('/cashier/recharge', null, { 
      params: { 
        member_id: memberId, 
        amount, 
        gift_amount: giftAmount,
        payment_method: paymentMethod,
        operator
      } 
    }),

  // ============ 系统管理 ============
  healthCheck: () => api.get('/health'),
  getSystemStatus: () => api.get('/'),

  // ============ 测试功能 ============
  generateTestData: () => api.post('/test/generate-data'),
  getTestSummary: () => api.get('/test/summary'),
  getQuickTestData: () => api.get('/test/quick-test')
}
