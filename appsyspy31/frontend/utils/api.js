import { get, post, put, del } from './request'

export const authApi = {
    login: (data) => post('/auth/login', data),
    register: (data) => post('/auth/register', data),
    logout: () => post('/auth/logout'),
    refreshToken: () => post('/auth/refresh'),
    getCurrentUser: () => get('/auth/me'),
    changePassword: (data) => put('/auth/change-password', data)
}

export const userApi = {
    getList: (params) => get('/users', params),
    getDetail: (id) => get(`/users/${id}`),
    update: (id, data) => put(`/users/${id}`, data),
    delete: (id) => del(`/users/${id}`),
    toggleStatus: (id) => put(`/users/${id}/toggle-status`),
    getStats: () => get('/users/stats')
}

export const courseApi = {
    getList: (params) => get('/courses', params),
    getDetail: (id) => get(`/courses/${id}`),
    create: (data) => post('/courses', data),
    update: (id, data) => put(`/courses/${id}`, data),
    delete: (id) => del(`/courses/${id}`),
    toggleStatus: (id) => put(`/courses/${id}/toggle-status`),
    getCategories: () => get('/courses/categories/list'),
    getPopular: (limit) => get('/courses/list/popular', { limit }),
    getNew: (limit) => get('/courses/list/new', { limit })
}

export const coachApi = {
    getList: (params) => get('/coaches', params),
    getDetail: (id) => get(`/coaches/${id}`),
    create: (data) => post('/coaches', data),
    update: (id, data) => put(`/coaches/${id}`, data),
    delete: (id) => del(`/coaches/${id}`),
    getReviews: (coachId, params) => get(`/coaches/${coachId}/reviews`, params),
    getPopular: (limit) => get('/coaches/list/popular', { limit })
}

export const bookingApi = {
    getList: (params) => get('/bookings', params),
    getDetail: (id) => get(`/bookings/${id}`),
    create: (data) => post('/bookings', data),
    updateStatus: (id, data) => put(`/bookings/${id}/status`, data),
    cancel: (id) => put(`/bookings/${id}/cancel`),
    getMy: (params) => get('/bookings/my', params),
    getPendingCount: () => get('/bookings/pending/count')
}

export const messageApi = {
    getList: (params) => get('/messages', params),
    getDetail: (id) => get(`/messages/${id}`),
    markAsRead: (id) => put(`/messages/${id}/read`),
    markBatchAsRead: (data) => put('/messages/batch-read', data),
    getUnreadCount: () => get('/messages/unread/count'),
    delete: (id) => del(`/messages/${id}`),
    send: (data) => post('/messages', data),
    sendBatch: (data) => post('/messages/batch', data)
}

export const chatApi = {
    getSessions: (params) => get('/chat/sessions', params),
    createSession: (data) => post('/chat/sessions', data),
    getSessionDetail: (id) => get(`/chat/sessions/${id}`),
    closeSession: (id) => put(`/chat/sessions/${id}/close`),
    getMessages: (sessionId, params) => get(`/chat/sessions/${sessionId}/messages`, params),
    sendMessage: (data) => post('/chat/messages', data),
    getUnreadCount: () => get('/chat/unread/count'),
    getAvailableStaff: () => get('/chat/staff/available')
}

export const reviewApi = {
    getList: (params) => get('/reviews', params),
    getDetail: (id) => get(`/reviews/${id}`),
    create: (data) => post('/reviews', data),
    update: (id, data) => put(`/reviews/${id}`, data),
    delete: (id) => del(`/reviews/${id}`),
    reply: (id, data) => put(`/reviews/${id}/reply`, data),
    getMy: (params) => get('/reviews/list/my', params),
    getPending: () => get('/reviews/pending/list')
}

export const recommendationApi = {
    get: (type, limit) => get('/recommendations', { recommendation_type: type, limit }),
    getHistory: (params) => get('/recommendations/history', params),
    markViewed: (id) => put(`/recommendations/${id}/view`),
    markClicked: (id) => put(`/recommendations/${id}/click`),
    getPersonalized: () => get('/recommendations/personalized/all')
}

export const productApi = {
    getList: (params) => get('/products', params),
    getDetail: (id) => get(`/products/${id}`),
    create: (data) => post('/products', data),
    update: (id, data) => put(`/products/${id}`, data),
    delete: (id) => del(`/products/${id}`),
    toggleStatus: (id) => put(`/products/${id}/toggle-status`),
    toggleRecommended: (id) => put(`/products/${id}/toggle-recommended`),
    getCategories: () => get('/products/categories/list'),
    getRecommended: (limit) => get('/products/list/recommended', { limit }),
    getPopular: (limit) => get('/products/list/popular', { limit }),
    getStats: () => get('/products/stats/overview')
}

export const preferenceApi = {
    getMy: () => get('/preferences/my'),
    createOrUpdate: (data) => post('/preferences/my', data),
    update: (data) => put('/preferences/my', data),
    clear: () => del('/preferences/my'),
    getByUser: (userId) => get(`/preferences/user/${userId}`),
    getOptions: () => get('/preferences/options/config')
}

export const testApi = {
    generateAll: () => post('/test/generate-all'),
    generateUsers: (params) => post('/test/generate/users', null, { params }),
    generateCourses: () => post('/test/generate/courses'),
    generateCoaches: () => post('/test/generate/coaches'),
    generateProducts: () => post('/test/generate/products'),
    clearAll: () => post('/test/clear-all'),
    getAccounts: () => get('/test/accounts'),
    getApiInfo: () => get('/test/api-info')
}
