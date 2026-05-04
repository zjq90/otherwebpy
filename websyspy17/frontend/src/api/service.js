import request from '@/utils/request'

export const serviceApi = {
  createServiceRequest(data) {
    return request.post('/service-requests/', data)
  },

  getServiceRequests(params = {}) {
    return request.get('/service-requests/', { params })
  },

  getMyServiceRequests(params = {}) {
    return request.get('/service-requests/my', { params })
  },

  getAssignedServiceRequests(params = {}) {
    return request.get('/service-requests/assigned', { params })
  },

  getServiceRequestById(id) {
    return request.get(`/service-requests/${id}`)
  },

  updateServiceRequest(id, data) {
    return request.put(`/service-requests/${id}`, data)
  },

  deleteServiceRequest(id) {
    return request.delete(`/service-requests/${id}`)
  },

  assignServiceRequest(id, assigneeId) {
    return request.post(`/service-requests/${id}/assign?assignee_id=${assigneeId}`)
  },

  updateServiceStatus(id, status) {
    return request.post(`/service-requests/${id}/status?new_status=${status}`)
  },

  getServiceProgress(id) {
    return request.get(`/service-requests/${id}/progress`)
  }
}
