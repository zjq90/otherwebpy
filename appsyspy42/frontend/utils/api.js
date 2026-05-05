/**
 * API接口封装
 * 统一管理所有API接口
 */
import request from './request.js'
import config from './config.js'

const api = {
    // ==================== 认证相关 ====================
    
    /**
     * 用户登录
     * @param {Object} data { username, password }
     */
    login(data) {
        return request.post('/auth/login', data)
    },

    /**
     * 用户注册
     * @param {Object} data 用户信息
     */
    register(data) {
        return request.post('/auth/register', data)
    },

    /**
     * 获取当前用户信息
     */
    getCurrentUser() {
        return request.get('/auth/me')
    },

    /**
     * 更新当前用户信息
     * @param {Object} data 用户信息
     */
    updateCurrentUser(data) {
        return request.put('/auth/me', data)
    },

    // ==================== 库存相关 ====================

    /**
     * 获取原材料列表
     * @param {Object} params { material_type, keyword, page, page_size }
     */
    getMaterials(params = {}) {
        return request.get('/inventory/materials', params)
    },

    /**
     * 获取原材料详情
     * @param {Number} id 原材料ID
     */
    getMaterial(id) {
        return request.get(`/inventory/materials/${id}`)
    },

    /**
     * 创建原材料
     * @param {Object} data 原材料信息
     */
    createMaterial(data) {
        return request.post('/inventory/materials', data)
    },

    /**
     * 获取料仓列表
     * @param {Object} params { is_active, page, page_size }
     */
    getWarehouses(params = {}) {
        return request.get('/inventory/warehouses', params)
    },

    /**
     * 获取库存列表
     * @param {Object} params { material_type, material_name, warehouse_id, is_low_stock, page, page_size }
     */
    getInventoryList(params = {}) {
        return request.get('/inventory/list', params)
    },

    /**
     * 获取库存详情
     * @param {Number} id 库存ID
     */
    getInventoryDetail(id) {
        return request.get(`/inventory/list/${id}`)
    },

    /**
     * 获取低库存预警列表
     * @param {Object} params { is_read, is_handled }
     */
    getLowStockAlerts(params = {}) {
        return request.get('/inventory/alerts', params)
    },

    /**
     * 获取库存统计数据
     */
    getInventoryStats() {
        return request.get('/inventory/statistics')
    },

    // ==================== 采购申请相关 ====================

    /**
     * 获取采购申请列表
     * @param {Object} params { status, material_type, page, page_size }
     */
    getPurchaseList(params = {}) {
        return request.get('/purchase/list', params)
    },

    /**
     * 获取采购申请详情
     * @param {Number} id 采购申请ID
     */
    getPurchaseDetail(id) {
        return request.get(`/purchase/list/${id}`)
    },

    /**
     * 提交采购申请
     * @param {Object} data 采购申请信息
     */
    createPurchase(data) {
        return request.post('/purchase/list', data)
    },

    /**
     * 更新采购申请
     * @param {Number} id 采购申请ID
     * @param {Object} data 更新信息
     */
    updatePurchase(id, data) {
        return request.put(`/purchase/list/${id}`, data)
    },

    /**
     * 取消采购申请
     * @param {Number} id 采购申请ID
     */
    cancelPurchase(id) {
        return request.post(`/purchase/list/${id}/cancel`)
    },

    /**
     * 审批采购申请（管理员）
     * @param {Number} id 采购申请ID
     * @param {Object} data { status, approval_comment }
     */
    approvePurchase(id, data) {
        return request.post(`/purchase/list/${id}/approve`, data)
    },

    /**
     * 获取待审批数量
     */
    getPendingCount() {
        return request.get('/purchase/pending-count')
    },

    /**
     * 获取我的采购申请
     * @param {Object} params { status, page, page_size }
     */
    getMyPurchases(params = {}) {
        return request.get('/purchase/my', params)
    },

    // ==================== 供应商相关 ====================

    /**
     * 获取供应商列表
     * @param {Object} params { keyword, is_active, page, page_size }
     */
    getSupplierList(params = {}) {
        return request.get('/supplier/list', params)
    },

    /**
     * 获取供应商详情
     * @param {Number} id 供应商ID
     */
    getSupplierDetail(id) {
        return request.get(`/supplier/list/${id}`)
    },

    /**
     * 创建供应商
     * @param {Object} data 供应商信息
     */
    createSupplier(data) {
        return request.post('/supplier/list', data)
    },

    /**
     * 更新供应商
     * @param {Number} id 供应商ID
     * @param {Object} data 更新信息
     */
    updateSupplier(id, data) {
        return request.put(`/supplier/list/${id}`, data)
    },

    /**
     * 删除供应商
     * @param {Number} id 供应商ID
     */
    deleteSupplier(id) {
        return request.delete(`/supplier/list/${id}`)
    },

    /**
     * 获取供货记录列表
     * @param {Object} params { supplier_id, material_id, quality_status, page, page_size }
     */
    getSupplyRecords(params = {}) {
        return request.get('/supplier/supply-records', params)
    },

    /**
     * 创建供货记录
     * @param {Object} data 供货记录信息
     */
    createSupplyRecord(data) {
        return request.post('/supplier/supply-records', data)
    },

    /**
     * 获取供应商评价列表
     * @param {Object} params { supplier_id, page, page_size }
     */
    getEvaluations(params = {}) {
        return request.get('/supplier/evaluations', params)
    },

    /**
     * 创建供应商评价
     * @param {Object} data 评价信息
     */
    createEvaluation(data) {
        return request.post('/supplier/evaluations', data)
    },

    /**
     * 获取供应商统计数据
     */
    getSupplierStats() {
        return request.get('/supplier/statistics')
    }
}

export default api
