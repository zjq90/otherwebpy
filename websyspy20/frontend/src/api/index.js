import axios from 'axios'
import { ElMessage } from 'element-plus'

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
    console.error('API Error:', error)
    const message = error.response?.data?.detail || error.message || '请求失败'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default api

export const feeItemApi = {
  getList: (params = {}) => api.get('/fee-items/', { params }),
  getById: (id) => api.get(`/fee-items/${id}`),
  create: (data) => api.post('/fee-items/', data),
  update: (id, data) => api.put(`/fee-items/${id}`, data),
  delete: (id) => api.delete(`/fee-items/${id}`),
  toggle: (id) => api.post(`/fee-items/${id}/toggle`)
}

export const propertyApi = {
  getList: (params = {}) => api.get('/properties/', { params }),
  getById: (id) => api.get(`/properties/${id}`),
  getByNumber: (number) => api.get(`/properties/search/by-number/${number}`),
  create: (data) => api.post('/properties/', data),
  update: (id, data) => api.put(`/properties/${id}`, data),
  delete: (id) => api.delete(`/properties/${id}`),
  toggle: (id) => api.post(`/properties/${id}/toggle`)
}

export const billApi = {
  getList: (params = {}) => api.get('/bills/', { params }),
  getById: (id) => api.get(`/bills/${id}`),
  getByProperty: (propertyId, params = {}) => api.get(`/bills/property/${propertyId}`, { params }),
  getOverdue: (params = {}) => api.get('/bills/overdue/list', { params }),
  create: (data) => api.post('/bills/', data),
  update: (id, data) => api.put(`/bills/${id}`, data),
  pay: (id, data) => api.post(`/bills/${id}/pay`, data),
  batchGenerate: (data) => api.post('/bills/batch-generate', data)
}

export const reminderApi = {
  getList: (params = {}) => api.get('/reminders/', { params }),
  getById: (id) => api.get(`/reminders/${id}`),
  getByBill: (billId) => api.get(`/reminders/bill/${billId}/history`),
  create: (data) => api.post('/reminders/', data),
  sendReminder: (billId, params = {}) => api.post(`/reminders/bill/${billId}`, null, { params }),
  batchRemindOverdue: (params = {}) => api.post('/reminders/batch-overdue', null, { params }),
  getStats: () => api.get('/reminders/stats/summary')
}

export const invoiceApi = {
  getList: (params = {}) => api.get('/invoices/', { params }),
  getById: (id) => api.get(`/invoices/${id}`),
  getByBill: (billId) => api.get(`/invoices/bill/${billId}`),
  create: (data) => api.post('/invoices/', data),
  issue: (id, params = {}) => api.post(`/invoices/issue/${id}`, null, { params }),
  void: (id) => api.post(`/invoices/void/${id}`),
  createFromBill: (billId, params = {}) => api.post(`/invoices/from-bill/${billId}`, null, { params }),
  getFinancialStats: (params = {}) => api.get('/invoices/stats/financial', { params }),
  getPendingBills: (params = {}) => api.get('/invoices/pending/list', { params }),
  batchIssue: (data) => api.post('/invoices/batch-issue', data),
  getPreview: (billId, invoiceType = 'invoice') => api.get(`/invoices/invoice-preview/${billId}`, { params: { invoice_type: invoiceType } }),
  getOverview: (params = {}) => api.get('/invoices/stats/overview', { params })
}
