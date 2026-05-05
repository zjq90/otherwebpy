/**
 * API接口封装模块
 * 统一管理所有API接口
 */

import request from './request.js'

// ==================== 认证相关接口 ====================
const auth = {
	/**
	 * 用户登录
	 * @param {String} username - 用户名
	 * @param {String} password - 密码
	 * @returns {Promise}
	 */
	login(username, password) {
		// 使用form-urlencoded格式
		const formData = new URLSearchParams()
		formData.append('username', username)
		formData.append('password', password)
		
		return request.post('/auth/login', formData, {
			header: {
				'Content-Type': 'application/x-www-form-urlencoded'
			}
		})
	},
	
	/**
	 * 获取当前用户信息
	 * @returns {Promise}
	 */
	getCurrentUser() {
		return request.get('/auth/me')
	},
	
	/**
	 * 修改密码
	 * @param {String} oldPassword - 旧密码
	 * @param {String} newPassword - 新密码
	 * @returns {Promise}
	 */
	changePassword(oldPassword, newPassword) {
		return request.post('/auth/change-password', null, {
			data: {
				old_password: oldPassword,
				new_password: newPassword
			}
		})
	},
	
	/**
	 * 获取测试账号信息
	 * @returns {Promise}
	 */
	getTestUsers() {
		return request.get('/test/test-users', { showLoading: false })
	}
}

// ==================== 任务相关接口 ====================
const tasks = {
	/**
	 * 获取任务列表
	 * @param {Object} params - 查询参数
	 * @param {String} params.status - 任务状态筛选
	 * @param {String} params.keyword - 关键词搜索
	 * @param {Number} params.page - 页码
	 * @param {Number} params.page_size - 每页数量
	 * @returns {Promise}
	 */
	getList(params = {}) {
		return request.get('/tasks', params)
	},
	
	/**
	 * 获取待执行任务（首页推送）
	 * @param {Object} params - 查询参数
	 * @returns {Promise}
	 */
	getPending(params = {}) {
		return request.get('/tasks/pending', params)
	},
	
	/**
	 * 获取任务详情
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	getDetail(taskId) {
		return request.get(`/tasks/${taskId}`)
	},
	
	/**
	 * 创建任务（管理员）
	 * @param {Object} data - 任务数据
	 * @returns {Promise}
	 */
	create(data) {
		return request.post('/tasks', data)
	},
	
	/**
	 * 更新任务（管理员）
	 * @param {Number} taskId - 任务ID
	 * @param {Object} data - 更新数据
	 * @returns {Promise}
	 */
	update(taskId, data) {
		return request.put(`/tasks/${taskId}`, data)
	},
	
	/**
	 * 接单
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	accept(taskId) {
		return request.post(`/tasks/${taskId}/accept`)
	},
	
	/**
	 * 开始生产
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	start(taskId) {
		return request.post(`/tasks/${taskId}/start`)
	},
	
	/**
	 * 完成任务
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	complete(taskId) {
		return request.post(`/tasks/${taskId}/complete`)
	},
	
	/**
	 * 删除任务（管理员）
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	delete(taskId) {
		return request.del(`/tasks/${taskId}`)
	}
}

// ==================== 配方相关接口 ====================
const formulas = {
	/**
	 * 获取配方列表
	 * @param {Object} params - 查询参数
	 * @returns {Promise}
	 */
	getList(params = {}) {
		return request.get('/formulas', params)
	},
	
	/**
	 * 快速检索配方
	 * @param {String} keyword - 搜索关键词
	 * @param {Object} params - 其他参数
	 * @returns {Promise}
	 */
	search(keyword, params = {}) {
		return request.get('/formulas/search', {
			keyword,
			...params
		})
	},
	
	/**
	 * 获取配方详情
	 * @param {Number} formulaId - 配方ID
	 * @returns {Promise}
	 */
	getDetail(formulaId) {
		return request.get(`/formulas/${formulaId}`)
	},
	
	/**
	 * 创建配方（管理员）
	 * @param {Object} data - 配方数据
	 * @returns {Promise}
	 */
	create(data) {
		return request.post('/formulas', data)
	},
	
	/**
	 * 更新配方（管理员）
	 * @param {Number} formulaId - 配方ID
	 * @param {Object} data - 更新数据
	 * @returns {Promise}
	 */
	update(formulaId, data) {
		return request.put(`/formulas/${formulaId}`, data)
	},
	
	/**
	 * 配方参数微调
	 * @param {Object} data - 调整数据
	 * @returns {Promise}
	 */
	adjust(data) {
		return request.post('/formulas/adjust', data)
	},
	
	/**
	 * 获取任务的配方调整历史
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	getAdjustments(taskId) {
		return request.get(`/formulas/adjustments/task/${taskId}`)
	},
	
	/**
	 * 删除配方（管理员）
	 * @param {Number} formulaId - 配方ID
	 * @returns {Promise}
	 */
	delete(formulaId) {
		return request.del(`/formulas/${formulaId}`)
	}
}

// ==================== 投料记录相关接口 ====================
const feeding = {
	/**
	 * 获取投料记录列表
	 * @param {Object} params - 查询参数
	 * @returns {Promise}
	 */
	getList(params = {}) {
		return request.get('/feeding', params)
	},
	
	/**
	 * 获取任务的所有投料记录
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	getByTask(taskId) {
		return request.get(`/feeding/task/${taskId}`)
	},
	
	/**
	 * 获取投料记录详情
	 * @param {Number} recordId - 记录ID
	 * @returns {Promise}
	 */
	getDetail(recordId) {
		return request.get(`/feeding/${recordId}`)
	},
	
	/**
	 * 创建投料记录（扫码/手动录入）
	 * @param {Object} data - 投料数据
	 * @returns {Promise}
	 */
	create(data) {
		return request.post('/feeding', data)
	},
	
	/**
	 * 删除投料记录
	 * @param {Number} recordId - 记录ID
	 * @returns {Promise}
	 */
	delete(recordId) {
		return request.del(`/feeding/${recordId}`)
	},
	
	/**
	 * 获取任务投料统计
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	getStats(taskId) {
		return request.get(`/feeding/stats/task/${taskId}`)
	}
}

// ==================== 搅拌记录相关接口 ====================
const mixing = {
	/**
	 * 获取搅拌记录列表
	 * @param {Object} params - 查询参数
	 * @returns {Promise}
	 */
	getList(params = {}) {
		return request.get('/mixing', params)
	},
	
	/**
	 * 获取任务的所有搅拌记录
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	getByTask(taskId) {
		return request.get(`/mixing/task/${taskId}`)
	},
	
	/**
	 * 获取搅拌记录详情
	 * @param {Number} recordId - 记录ID
	 * @returns {Promise}
	 */
	getDetail(recordId) {
		return request.get(`/mixing/${recordId}`)
	},
	
	/**
	 * 创建搅拌记录
	 * @param {Object} data - 搅拌数据
	 * @returns {Promise}
	 */
	create(data) {
		return request.post('/mixing', data)
	},
	
	/**
	 * 更新搅拌记录（补充异常说明）
	 * @param {Number} recordId - 记录ID
	 * @param {Object} data - 更新数据
	 * @returns {Promise}
	 */
	update(recordId, data) {
		return request.put(`/mixing/${recordId}`, null, {
			data
		})
	},
	
	/**
	 * 删除搅拌记录
	 * @param {Number} recordId - 记录ID
	 * @returns {Promise}
	 */
	delete(recordId) {
		return request.del(`/mixing/${recordId}`)
	},
	
	/**
	 * 获取任务搅拌统计
	 * @param {Number} taskId - 任务ID
	 * @returns {Promise}
	 */
	getStats(taskId) {
		return request.get(`/mixing/stats/task/${taskId}`)
	}
}

// ==================== 测试工具接口 ====================
const test = {
	/**
	 * 生成测试数据
	 * @returns {Promise}
	 */
	generateData() {
		return request.post('/test/generate-data')
	},
	
	/**
	 * 清空测试数据
	 * @returns {Promise}
	 */
	clearData() {
		return request.post('/test/clear-data')
	},
	
	/**
	 * 获取数据概览
	 * @returns {Promise}
	 */
	getSummary() {
		return request.get('/test/summary')
	}
}

export default {
	auth,
	tasks,
	formulas,
	feeding,
	mixing,
	test
}
