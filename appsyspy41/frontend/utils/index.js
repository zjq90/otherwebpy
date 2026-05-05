/**
 * 工具函数
 */

/**
 * 获取设备类型名称
 * @param {String} type - 设备类型代码
 */
const getDeviceTypeName = (type) => {
	const typeMap = {
		'mixer': '搅拌主机',
		'belt_scale': '皮带秤',
		'compressor': '空压机'
	}
	return typeMap[type] || type
}

/**
 * 获取设备类型图标颜色
 * @param {String} type - 设备类型代码
 */
const getDeviceTypeColor = (type) => {
	const colorMap = {
		'mixer': '#1890ff',
		'belt_scale': '#52c41a',
		'compressor': '#faad14'
	}
	return colorMap[type] || '#999'
}

/**
 * 获取状态标签样式类
 * @param {String} status - 状态值
 */
const getStatusClass = (status) => {
	const classMap = {
		'normal': 'status-normal',
		'warning': 'status-warning',
		'fault': 'status-fault',
		'pending': 'status-pending',
		'processing': 'status-processing',
		'completed': 'status-completed',
		'overdue': 'status-overdue'
	}
	return classMap[status] || 'status-pending'
}

/**
 * 获取状态名称
 * @param {String} status - 状态值
 */
const getStatusName = (status) => {
	const nameMap = {
		'normal': '正常',
		'warning': '预警',
		'fault': '故障',
		'pending': '待处理',
		'processing': '处理中',
		'completed': '已完成',
		'overdue': '已超期'
	}
	return nameMap[status] || status
}

/**
 * 获取优先级样式类
 * @param {String} priority - 优先级
 */
const getPriorityClass = (priority) => {
	const classMap = {
		'high': 'priority-high',
		'medium': 'priority-medium',
		'low': 'priority-low'
	}
	return classMap[priority] || 'priority-medium'
}

/**
 * 获取优先级名称
 * @param {String} priority - 优先级
 */
const getPriorityName = (priority) => {
	const nameMap = {
		'high': '高',
		'medium': '中',
		'low': '低'
	}
	return nameMap[priority] || '中'
}

/**
 * 获取故障级别名称
 * @param {String} level - 故障级别
 */
const getFaultLevelName = (level) => {
	const nameMap = {
		'high': '高',
		'medium': '中',
		'low': '低'
	}
	return nameMap[level] || '中'
}

/**
 * 获取角色名称
 * @param {String} role - 角色代码
 */
const getRoleName = (role) => {
	const nameMap = {
		'admin': '系统管理员',
		'operator': '操作员',
		'repair': '维修人员'
	}
	return nameMap[role] || role
}

/**
 * 格式化日期时间
 * @param {String} dateStr - 日期字符串
 * @param {String} format - 格式
 */
const formatDateTime = (dateStr, format = 'YYYY-MM-DD HH:mm') => {
	if (!dateStr) return ''
	
	const date = new Date(dateStr)
	const year = date.getFullYear()
	const month = String(date.getMonth() + 1).padStart(2, '0')
	const day = String(date.getDate()).padStart(2, '0')
	const hour = String(date.getHours()).padStart(2, '0')
	const minute = String(date.getMinutes()).padStart(2, '0')
	const second = String(date.getSeconds()).padStart(2, '0')
	
	return format
		.replace('YYYY', year)
		.replace('MM', month)
		.replace('DD', day)
		.replace('HH', hour)
		.replace('mm', minute)
		.replace('ss', second)
}

/**
 * 格式化日期
 * @param {String} dateStr - 日期字符串
 */
const formatDate = (dateStr) => {
	return formatDateTime(dateStr, 'YYYY-MM-DD')
}

/**
 * 格式化时间
 * @param {String} dateStr - 日期字符串
 */
const formatTime = (dateStr) => {
	return formatDateTime(dateStr, 'HH:mm')
}

/**
 * 格式化数字（保留小数位）
 * @param {Number} num - 数字
 * @param {Number} decimals - 小数位数
 */
const formatNumber = (num, decimals = 2) => {
	if (num === null || num === undefined) return ''
	return Number(num).toFixed(decimals)
}

/**
 * 显示确认对话框
 * @param {String} content - 内容
 * @param {String} title - 标题
 */
const showConfirm = (content, title = '提示') => {
	return new Promise((resolve, reject) => {
		uni.showModal({
			title,
			content,
			success: (res) => {
				if (res.confirm) {
					resolve(true)
				} else {
					resolve(false)
				}
			},
			fail: (err) => {
				reject(err)
			}
		})
	})
}

/**
 * 显示加载提示
 * @param {String} title - 标题
 */
const showLoading = (title = '加载中...') => {
	uni.showLoading({
		title,
		mask: true
	})
}

/**
 * 隐藏加载提示
 */
const hideLoading = () => {
	uni.hideLoading()
}

/**
 * 显示成功提示
 * @param {String} title - 标题
 */
const showSuccess = (title = '操作成功') => {
	uni.showToast({
		title,
		icon: 'success',
		duration: 2000
	})
}

/**
 * 显示错误提示
 * @param {String} title - 标题
 */
const showError = (title = '操作失败') => {
	uni.showToast({
		title,
		icon: 'none',
		duration: 2000
	})
}

/**
 * 手机震动（用于故障报警提醒）
 * @param {Number} type - 震动类型: 1=短震动, 2=长震动
 */
const vibrate = (type = 1) => {
	if (type === 1) {
		// 短震动（400毫秒）
		uni.vibrateShort({
			success: () => {
				console.log('短震动成功')
			}
		})
	} else {
		// 长震动（400毫秒）
		uni.vibrateLong({
			success: () => {
				console.log('长震动成功')
			}
		})
	}
}

/**
 * 获取当前登录用户信息
 */
const getCurrentUser = () => {
	try {
		const userInfo = uni.getStorageSync('userInfo')
		return userInfo ? JSON.parse(userInfo) : null
	} catch (e) {
		return null
	}
}

/**
 * 设置当前登录用户信息
 * @param {Object} userInfo - 用户信息
 */
const setCurrentUser = (userInfo) => {
	uni.setStorageSync('userInfo', JSON.stringify(userInfo))
}

/**
 * 清除登录信息
 */
const clearLoginInfo = () => {
	uni.removeStorageSync('userInfo')
	uni.removeStorageSync('token')
}

/**
 * 检查是否有故障设备（用于首页报警提醒）
 * @param {Array} devices - 设备列表
 */
const checkFaultDevices = (devices) => {
	if (!devices || !devices.length) return false
	
	const faultDevices = devices.filter(d => 
		d.status === 'fault' || d.status === 'warning'
	)
	
	return faultDevices.length > 0
}

export default {
	getDeviceTypeName,
	getDeviceTypeColor,
	getStatusClass,
	getStatusName,
	getPriorityClass,
	getPriorityName,
	getFaultLevelName,
	getRoleName,
	formatDateTime,
	formatDate,
	formatTime,
	formatNumber,
	showConfirm,
	showLoading,
	hideLoading,
	showSuccess,
	showError,
	vibrate,
	getCurrentUser,
	setCurrentUser,
	clearLoginInfo,
	checkFaultDevices
}
