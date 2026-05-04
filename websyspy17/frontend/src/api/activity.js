import request from '@/utils/request'

export const activityApi = {
  createActivity(data) {
    return request.post('/activities/', data)
  },

  getActivities(params = {}) {
    return request.get('/activities/', { params })
  },

  getPublishedActivities(params = {}) {
    return request.get('/activities/published', { params })
  },

  getActivityById(id) {
    return request.get(`/activities/${id}`)
  },

  updateActivity(id, data) {
    return request.put(`/activities/${id}`, data)
  },

  deleteActivity(id) {
    return request.delete(`/activities/${id}`)
  },

  publishActivity(id) {
    return request.post(`/activities/${id}/publish`)
  },

  closeRegistration(id) {
    return request.post(`/activities/${id}/close-registration`)
  },

  registerActivity(id, data) {
    return request.post(`/activities/${id}/register`, data)
  },

  cancelRegistration(id) {
    return request.delete(`/activities/${id}/register`)
  },

  getActivityRegistrations(id) {
    return request.get(`/activities/${id}/registrations`)
  },

  getMyRegistrations() {
    return request.get('/activities/my/registrations')
  }
}
