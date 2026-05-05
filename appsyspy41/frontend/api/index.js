/**
 * API接口封装
 * 统一管理所有API接口
 */

import request from './request'

// ==================== 用户认证接口 ====================
const authApi = {
	/**
	 * 用户登录
	 * @param {String} username - 用户名
	 * @param {String} password - 密码
	 */
	login(username, password) {
		return request.post('/api/auth/login', {
			username,
			password
		})
	},
	
	/**
	 * 用户注册
	 * @param {Object} userData - 用户数据
	 */
	register(userData) {
		return request.post('/api/auth/register', userData)
	},
	
	/**
	 * 获取用户列表
	 * @param {Object} params - 查询参数
	 */
	getUsers(params = {}) {
		return request.get('/api/auth/users', params)
	},
	
	/**
	 * 获取用户详情
	 * @param {Number} userId - 用户ID
	 */
	getUser(userId) {
		return request.get(`/api/auth/users/${userId}`)
	},
	
	/**
	 * 更新用户信息
	 * @param {Number} userId - 用户ID
	 * @param {Object} data - 更新数据
	 */
	updateUser(userId, data) {
		return request.put(`/api/auth/users/${userId}`, data)
	},
	
	/**
	 * 获取角色列表
	 */
	getRoles() {
		return request.get('/api/auth/roles')
	}
}

// ==================== 设备接口 ====================
const deviceApi = {
	/**
	 * 获取设备列表
	 * @param {Object} params - 查询参数
	 */
	getList(params = {}) {
		return request.get('/api/devices/', params)
	},
	
	/**
	 * 获取设备详情
	 * @param {Number} deviceId - 设备ID
	 */
	getDetail(deviceId) {
		return request.get(`/api/devices/${deviceId}`)
	},
	
	/**
	 * 创建设备
	 * @param {Object} data - 设备数据
	 */
	create(data) {
		return request.post('/api/devices/', data)
	},
	
	/**
	 * 更新设备
	 * @param {Number} deviceId - 设备ID
	 * @param {Object} data - 更新数据
	 */
	update(deviceId, data) {
		return request.put(`/api/devices/${deviceId}`, data)
	},
	
	/**
	 * 删除设备
	 * @param {Number} deviceId - 设备ID
	 */
	delete(deviceId) {
		return request.del(`/api/devices/${deviceId}`)
	},
	
	/**
	 * 获取设备状态历史
	 * @param {Number} deviceId - 设备ID
	 * @param {Object} params - 查询参数
	 */
	getStatusHistory(deviceId, params = {}) {
		return request.get(`/api/devices/${deviceId}/status-history`, params)
	},
	
	/**
	 * 上报设备状态
	 * @param {Number} deviceId - 设备ID
	 * @param {Object} status - 状态数据
	 */
	reportStatus(deviceId, status) {
		return request.post(`/api/devices/${deviceId}/status`, status)
	},
	
	/**
	 * 获取设备概览统计
	 */
	getOverview() {
		return request.get('/api/devices/overview/summary')
	}
}

// ==================== 保养任务接口 ====================
const maintenanceApi = {
	/**
	 * 获取保养任务列表
	 * @param {Object} params - 查询参数
	 */
	getTaskList(params = {}) {
		return request.get('/api/maintenance/tasks', params)
	},
	
	/**
	 * 获取保养任务详情
	 * @param {Number} taskId - 任务ID
	 */
	getTaskDetail(taskId) {
		return request.get(`/api/maintenance/tasks/${taskId}`)
	},
	
	/**
	 * 创建保养任务
	 * @param {Object} data - 任务数据
	 */
	createTask(data) {
		return request.post('/api/maintenance/tasks', data)
	},
	
	/**
	 * 更新保养任务
	 * @param {Number} taskId - 任务ID
	 * @param {Object} data - 更新数据
	 */
	updateTask(taskId, data) {
		return request.put(`/api/maintenance/tasks/${taskId}`, data)
	},
	
	/**
	 * 删除保养任务
	 * @param {Number} taskId - 任务ID
	 */
	deleteTask(taskId) {
		return request.del(`/api/maintenance/tasks/${taskId}`)
	},
	
	/**
	 * 自动生成保养任务
	 * @param {Number} deviceId - 设备ID（可选）
	 */
	generateTasks(deviceId) {
		const params = deviceId ? { device_id: deviceId } : {}
		return request.post('/api/maintenance/tasks/generate', params)
	},
	
	/**
	 * 获取保养记录列表
	 * @param {Object} params - 查询参数
	 */
	getRecordList(params = {}) {
		return request.get('/api/maintenance/records', params)
	},
	
	/**
	 * 获取保养记录详情
	 * @param {Number} recordId - 记录ID
	 */
	getRecordDetail(recordId) {
		return request.get(`/api/maintenance/records/${recordId}`)
	},
	
	/**
	 * 创建保养记录
	 * @param {Object} data - 记录数据
	 */
	createRecord(data) {
		return request.post('/api/maintenance/records', data)
	},
	
	/**
	 * 获取保养任务统计概览
	 */
	getOverview() {
		return request.get('/api/maintenance/overview/stats')
	}
}

// ==================== 故障报修接口 ====================
const faultApi = {
	/**
	 * 获取故障报修列表
	 * @param {Object} params - 查询参数
	 */
	getReportList(params = {}) {
		return request.get('/api/fault/reports', params)
	},
	
	/**
	 * 获取故障报修详情
	 * @param {Number} reportId - 报修ID
	 */
	getReportDetail(reportId) {
		return request.get(`/api/fault/reports/${reportId}`)
	},
	
	/**
	 * 提交故障报修
	 * @param {Object} data - 报修数据
	 * @param {Number} reporterId - 上报人ID
	 */
	createReport(data, reporterId) {
		return request.post('/api/fault/reports', data, {
			data: { ...data, reporter_id: reporterId }
		})
	},
	
	/**
	 * 更新故障报修
	 * @param {Number} reportId - 报修ID
	 * @param {Object} data - 更新数据
	 */
	updateReport(reportId, data) {
		return request.put(`/api/fault/reports/${reportId}`, data)
	},
	
	/**
	 * 分配故障报修
	 * @param {Number} reportId - 报修ID
	 * @param {Number} repairUserId - 维修人员ID
	 */
	assignReport(reportId, repairUserId) {
		return request.post(`/api/fault/reports/${reportId}/assign`, {}, {
			data: { repair_user_id: repairUserId }
		})
	},
	
	/**
	 * 完成故障报修
	 * @param {Number} reportId - 报修ID
	 * @param {Number} operatorId - 操作员ID
	 */
	completeReport(reportId, operatorId) {
		return request.post(`/api/fault/reports/${reportId}/complete`, {}, {
			data: { operator_id: operatorId }
		})
	},
	
	/**
	 * 删除故障报修
	 * @param {Number} reportId - 报修ID
	 */
	deleteReport(reportId) {
		return request.del(`/api/fault/reports/${reportId}`)
	},
	
	/**
	 * 获取维修记录列表
	 * @param {Object} params - 查询参数
	 */
	getRecordList(params = {}) {
		return request.get('/api/fault/records', params)
	},
	
	/**
	 * 创建维修记录
	 * @param {Object} data - 记录数据
	 */
	createRecord(data) {
		return request.post('/api/fault/records', data)
	},
	
	/**
	 * 获取故障报修统计概览
	 */
	getOverview() {
		return request.get('/api/fault/overview/stats')
	}
}

// ==================== 测试辅助接口 ====================
const testApi = {
	/**
	 * 重置数据库
	 */
	resetDatabase() {
		return request.post('/api/test/reset-database')
	},
	
	/**
	 * 生成设备状态测试数据
	 * @param {Number} deviceId - 设备ID（可选）
	 * @param {Number} count - 数据条数
	 */
	generateDeviceStatus(deviceId, count = 24) {
		const params = { count }
		if (deviceId) {
			params.device_id = deviceId
		}
		return request.post('/api/test/generate-device-status', params)
	},
	
	/**
	 * 模拟设备故障报警
	 * @param {Number} deviceId - 设备ID
	 * @param {String} faultType - 故障类型
	 */
	generateFaultAlarm(deviceId, faultType = 'temperature') {
		return request.post('/api/test/generate-fault-alarm', {
			device_id: deviceId,
			fault_type: faultType
		})
	},
	
	/**
	 * 获取首页仪表盘数据
	 */
	getDashboardOverview() {
		return request.get('/api/test/dashboard-overview')
	},
	
	/**
	 * 获取快速统计数据
	 */
	getQuickStats() {
		return request.get('/api/test/quick-stats')
	},
	
	/**
	 * 清除测试数据
	 */
	clearTestData() {
		return request.post('/api/test/clear-test-data')
	}
}

export default {
	auth: authApi,
	device: deviceApi,
	maintenance: maintenanceApi,
	fault: faultApi,
	test: testApi
}
