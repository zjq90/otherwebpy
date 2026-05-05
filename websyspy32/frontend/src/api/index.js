import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.response.use(
  response => response,
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

export const siloApi = {
  getList: (params = {}) => api.get('/silos/', { params }),
  getById: (id) => api.get(`/silos/${id}`),
  create: (data) => api.post('/silos/', data),
  update: (id, data) => api.put(`/silos/${id}`, data),
  delete: (id) => api.delete(`/silos/${id}`),
  adjustInventory: (data) => api.post(`/silos/${data.silo_id}/adjust`, data),
  getLowInventory: () => api.get('/silos/inventory/low-alert'),
  getRecords: (params = {}) => api.get('/silos/inventory/records', { params }),
  getByMaterial: (materialType) => api.get('/silos/inventory/by-material', { params: { material_type: materialType } })
}

export const productionApi = {
  getPlans: (params = {}) => api.get('/production/plans/', { params }),
  getPlanById: (id) => api.get(`/production/plans/${id}`),
  createPlan: (data) => api.post('/production/plans/', data),
  updatePlan: (id, data) => api.put(`/production/plans/${id}`, data),
  deletePlan: (id) => api.delete(`/production/plans/${id}`),
  getPendingPlans: () => api.get('/production/plans/pending'),
  getPlansByDate: (date) => api.get('/production/plans/by-date', { params: { plan_date: date } }),
  generateDemands: (planId) => api.post(`/production/plans/${planId}/generate-demands`),
  
  getDemands: (params = {}) => api.get('/production/demands/', { params }),
  getDemandById: (id) => api.get(`/production/demands/${id}`),
  getPendingDemands: () => api.get('/production/demands/pending'),
  getDemandsByMaterial: (materialType) => api.get('/production/demands/by-material', { params: { material_type: materialType } })
}

export const supplierApi = {
  getList: (params = {}) => api.get('/suppliers/', { params }),
  getById: (id) => api.get(`/suppliers/${id}`),
  create: (data) => api.post('/suppliers/', data),
  update: (id, data) => api.put(`/suppliers/${id}`, data),
  delete: (id) => api.delete(`/suppliers/${id}`),
  getByMaterial: (materialType) => api.get('/suppliers/by-material', { params: { material_type: materialType } }),
  
  createRating: (data) => api.post('/suppliers/ratings/', data),
  getRatingsBySupplier: (supplierId, params = {}) => api.get(`/suppliers/ratings/by-supplier/${supplierId}`, { params }),
  getRatingById: (id) => api.get(`/suppliers/ratings/${id}`),
  
  getOrders: (params = {}) => api.get('/suppliers/orders/', { params }),
  getOrderById: (id) => api.get(`/suppliers/orders/${id}`),
  createOrder: (data) => api.post('/suppliers/orders/', data),
  updateOrder: (id, data) => api.put(`/suppliers/orders/${id}`, data),
  deleteOrder: (id) => api.delete(`/suppliers/orders/${id}`),
  getPendingOrders: () => api.get('/suppliers/orders/pending'),
  getOrdersBySupplier: (supplierId) => api.get(`/suppliers/orders/by-supplier/${supplierId}`),
  getOrdersByStatus: (status) => api.get('/suppliers/orders/by-status', { params: { status } })
}

export const settlementApi = {
  getList: (params = {}) => api.get('/settlements/', { params }),
  getById: (id) => api.get(`/settlements/${id}`),
  create: (data) => api.post('/settlements/', data),
  update: (id, data) => api.put(`/settlements/${id}`, data),
  delete: (id) => api.delete(`/settlements/${id}`),
  getPendingPayments: () => api.get('/settlements/pending-payments'),
  getByPurchaseOrder: (orderId) => api.get(`/settlements/by-purchase-order/${orderId}`),
  pay: (id, amount) => api.post(`/settlements/${id}/pay`, { amount })
}

export const dashboardApi = {
  getStats: () => api.get('/dashboard')
}

export default api
