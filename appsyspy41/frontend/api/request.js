/**
 * HTTP请求封装
 * 统一处理请求和响应
 */

const BASE_URL = 'http://localhost:8000'

/**
 * 发起请求
 * @param {Object} options - 请求配置
 * @param {String} options.url - 请求路径
 * @param {String} options.method - 请求方法
 * @param {Object} options.data - 请求数据
 * @param {Object} options.header - 请求头
 */
const request = (options) => {
	return new Promise((resolve, reject) => {
		// 从本地存储获取token（如果需要）
		const token = uni.getStorageSync('token')
		
		// 构建请求头
		const header = {
			'Content-Type': 'application/json',
			...options.header
		}
		
		// 如果有token，添加到请求头
		if (token) {
			header['Authorization'] = `Bearer ${token}`
		}
		
		// 显示加载提示
		if (options.showLoading !== false) {
			uni.showLoading({
				title: options.loadingText || '加载中...',
				mask: true
			})
		}
		
		uni.request({
			url: BASE_URL + options.url,
			method: options.method || 'GET',
			data: options.data || {},
			header: header,
			success: (res) => {
				// 隐藏加载提示
				if (options.showLoading !== false) {
					uni.hideLoading()
				}
				
				// 处理响应
				if (res.statusCode === 200) {
					const data = res.data
					// 检查业务状态码
					if (data.code === 200) {
						resolve(data)
					} else {
						// 业务错误
						uni.showToast({
							title: data.message || '请求失败',
							icon: 'none'
						})
						reject(data)
					}
				} else if (res.statusCode === 401) {
					// 未授权，清除登录信息并跳转登录页
					uni.removeStorageSync('userInfo')
					uni.removeStorageSync('token')
					uni.reLaunch({
						url: '/pages/login/login'
					})
					reject(res)
				} else {
					// 其他错误
					uni.showToast({
						title: `请求失败: ${res.statusCode}`,
						icon: 'none'
					})
					reject(res)
				}
			},
			fail: (err) => {
				// 隐藏加载提示
				if (options.showLoading !== false) {
					uni.hideLoading()
				}
				
				// 网络错误
				uni.showToast({
					title: '网络请求失败，请检查网络',
					icon: 'none'
				})
				reject(err)
			}
		})
	})
}

/**
 * GET请求
 */
const get = (url, data = {}, options = {}) => {
	return request({
		url,
		method: 'GET',
		data,
		...options
	})
}

/**
 * POST请求
 */
const post = (url, data = {}, options = {}) => {
	return request({
		url,
		method: 'POST',
		data,
		...options
	})
}

/**
 * PUT请求
 */
const put = (url, data = {}, options = {}) => {
	return request({
		url,
		method: 'PUT',
		data,
		...options
	})
}

/**
 * DELETE请求
 */
const del = (url, data = {}, options = {}) => {
	return request({
		url,
		method: 'DELETE',
		data,
		...options
	})
}

export default {
	request,
	get,
	post,
	put,
	del
}
