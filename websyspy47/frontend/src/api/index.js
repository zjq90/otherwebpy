import request from '@/utils/request'

export function getDashboardStats() {
  return request({
    url: '/statistics/dashboard',
    method: 'get'
  })
}

export function getRecyclingTrend(days = 30) {
  return request({
    url: '/statistics/recycling-trend',
    method: 'get',
    params: { days }
  })
}

export function getUserGrowth(days = 30) {
  return request({
    url: '/statistics/user-growth',
    method: 'get',
    params: { days }
  })
}

export function getCategoryStats() {
  return request({
    url: '/statistics/category-stats',
    method: 'get'
  })
}

export function getPointsExchangeStats(days = 30) {
  return request({
    url: '/statistics/points-exchange-stats',
    method: 'get',
    params: { days }
  })
}

export function getRecyclerPerformance(limit = 10) {
  return request({
    url: '/statistics/recycler-performance',
    method: 'get',
    params: { limit }
  })
}

export function getUserList(params) {
  return request({
    url: '/users/',
    method: 'get',
    params
  })
}

export function getUserById(id) {
  return request({
    url: `/users/${id}`,
    method: 'get'
  })
}

export function createUser(data) {
  return request({
    url: '/users/',
    method: 'post',
    data
  })
}

export function updateUser(id, data) {
  return request({
    url: `/users/${id}`,
    method: 'put',
    data
  })
}

export function deleteUser(id) {
  return request({
    url: `/users/${id}`,
    method: 'delete'
  })
}

export function getFeedbackList(params) {
  return request({
    url: '/users/feedbacks/',
    method: 'get',
    params
  })
}

export function updateFeedback(id, data) {
  return request({
    url: `/users/feedbacks/${id}`,
    method: 'put',
    data
  })
}

export function getOrderList(params) {
  return request({
    url: '/orders/',
    method: 'get',
    params
  })
}

export function getOrderById(id) {
  return request({
    url: `/orders/${id}`,
    method: 'get'
  })
}

export function createOrder(data) {
  return request({
    url: '/orders/',
    method: 'post',
    data
  })
}

export function updateOrder(id, data) {
  return request({
    url: `/orders/${id}`,
    method: 'put',
    data
  })
}

export function assignOrder(orderId, recyclerId) {
  return request({
    url: `/orders/${orderId}/assign/${recyclerId}`,
    method: 'post'
  })
}

export function getOrderStats() {
  return request({
    url: '/orders/statistics/overview',
    method: 'get'
  })
}

export function getDailyStats(days = 30) {
  return request({
    url: '/orders/statistics/daily',
    method: 'get',
    params: { days }
  })
}

export function getRecyclerList(params) {
  return request({
    url: '/recyclers/',
    method: 'get',
    params
  })
}

export function getRecyclerById(id) {
  return request({
    url: `/recyclers/${id}`,
    method: 'get'
  })
}

export function createRecycler(data) {
  return request({
    url: '/recyclers/',
    method: 'post',
    data
  })
}

export function updateRecycler(id, data) {
  return request({
    url: `/recyclers/${id}`,
    method: 'put',
    data
  })
}

export function deleteRecycler(id) {
  return request({
    url: `/recyclers/${id}`,
    method: 'delete'
  })
}

export function getPerformanceList(params) {
  return request({
    url: '/recyclers/performances/',
    method: 'get',
    params
  })
}

export function createPerformance(data) {
  return request({
    url: '/recyclers/performances/',
    method: 'post',
    data
  })
}

export function getCategoryList(parentId = 0, status = null) {
  const params = { parent_id: parentId }
  if (status !== null) params.status = status
  return request({
    url: '/categories/',
    method: 'get',
    params
  })
}

export function getCategoryById(id) {
  return request({
    url: `/categories/${id}`,
    method: 'get'
  })
}

export function createCategory(data) {
  return request({
    url: '/categories/',
    method: 'post',
    data
  })
}

export function updateCategory(id, data) {
  return request({
    url: `/categories/${id}`,
    method: 'put',
    data
  })
}

export function deleteCategory(id) {
  return request({
    url: `/categories/${id}`,
    method: 'delete'
  })
}

export function getPricingRuleList(params) {
  return request({
    url: '/categories/pricing-rules/',
    method: 'get',
    params
  })
}

export function createPricingRule(data) {
  return request({
    url: '/categories/pricing-rules/',
    method: 'post',
    data
  })
}

export function updatePricingRule(id, data) {
  return request({
    url: `/categories/pricing-rules/${id}`,
    method: 'put',
    data
  })
}

export function deletePricingRule(id) {
  return request({
    url: `/categories/pricing-rules/${id}`,
    method: 'delete'
  })
}

export function getProductList(params) {
  return request({
    url: '/products/',
    method: 'get',
    params
  })
}

export function getProductById(id) {
  return request({
    url: `/products/${id}`,
    method: 'get'
  })
}

export function createProduct(data) {
  return request({
    url: '/products/',
    method: 'post',
    data
  })
}

export function updateProduct(id, data) {
  return request({
    url: `/products/${id}`,
    method: 'put',
    data
  })
}

export function deleteProduct(id) {
  return request({
    url: `/products/${id}`,
    method: 'delete'
  })
}

export function getPointsRuleList(params) {
  return request({
    url: '/products/points-rules/',
    method: 'get',
    params
  })
}

export function createPointsRule(data) {
  return request({
    url: '/products/points-rules/',
    method: 'post',
    data
  })
}

export function updatePointsRule(id, data) {
  return request({
    url: `/products/points-rules/${id}`,
    method: 'put',
    data
  })
}

export function getPointsExchangeList(params) {
  return request({
    url: '/products/points-exchanges/',
    method: 'get',
    params
  })
}

export function updatePointsExchange(id, data) {
  return request({
    url: `/products/points-exchanges/${id}`,
    method: 'put',
    data
  })
}

export function getAnnouncementList(params) {
  return request({
    url: '/announcements/',
    method: 'get',
    params
  })
}

export function getAnnouncementById(id) {
  return request({
    url: `/announcements/${id}`,
    method: 'get'
  })
}

export function createAnnouncement(data) {
  return request({
    url: '/announcements/',
    method: 'post',
    data
  })
}

export function updateAnnouncement(id, data) {
  return request({
    url: `/announcements/${id}`,
    method: 'put',
    data
  })
}

export function deleteAnnouncement(id) {
  return request({
    url: `/announcements/${id}`,
    method: 'delete'
  })
}

export function publishAnnouncement(id) {
  return request({
    url: `/announcements/${id}/publish`,
    method: 'post'
  })
}

export function getCsStaffList(params) {
  return request({
    url: '/customer-service/staffs/',
    method: 'get',
    params
  })
}

export function createCsStaff(data) {
  return request({
    url: '/customer-service/staffs/',
    method: 'post',
    data
  })
}

export function updateCsStaff(id, data) {
  return request({
    url: `/customer-service/staffs/${id}`,
    method: 'put',
    data
  })
}

export function deleteCsStaff(id) {
  return request({
    url: `/customer-service/staffs/${id}`,
    method: 'delete'
  })
}

export function getConsultationList(params) {
  return request({
    url: '/customer-service/consultations/',
    method: 'get',
    params
  })
}

export function getConsultationById(id) {
  return request({
    url: `/customer-service/consultations/${id}`,
    method: 'get'
  })
}

export function updateConsultation(id, data) {
  return request({
    url: `/customer-service/consultations/${id}`,
    method: 'put',
    data
  })
}

export function getConsultationMessages(consultationId) {
  return request({
    url: `/customer-service/consultations/${consultationId}/messages`,
    method: 'get'
  })
}

export function createConsultationMessage(consultationId, data) {
  return request({
    url: `/customer-service/consultations/${consultationId}/messages`,
    method: 'post',
    data
  })
}
