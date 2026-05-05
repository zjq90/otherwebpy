/**
 * HTTP请求封装模块
 * 统一处理请求拦截、响应拦截、错误处理
 */

import config from './config.js'

/**
 * 统一请求封装
 * @param {Object} options - 请求配置
 * @param {String} options.url - 请求地址（不包含baseURL）
 * @param {String} options.method - 请求方法：GET/POST/PUT/DELETE
 * @param {Object} options.data - 请求参数
 * @param {Object} options.header - 自定义请求头
 * @param {Boolean} options.showLoading - 是否显示加载提示
 * @param {Boolean} options.showError - 是否显示错误提示
 * @returns {Promise}
 */
const request = (options = {}) => {
	return new Promise((resolve, reject) => {
		// 解构配置
		const {
			url,
			method = 'GET',
			data = {},
			header = {},
			showLoading = true,
			showError = true
		} = options

		// 显示加载提示
		if (showLoading) {
			uni.showLoading({
				title: '加载中...',
				mask: true
			})
		}

		// 获取Token
		const token = uni.getStorageSync('token')

		// 构建请求头
		const requestHeader = {
			'Content-Type': 'application/json',
			...header
		}

		// 添加Token
		if (token) {
			requestHeader['Authorization'] = `${config.tokenPrefix} ${token}`
		}

		// 发起请求
		uni.request({
			url: config.baseURL + url,
			method: method.toUpperCase(),
			data: data,
			header: requestHeader,
			timeout: config.timeout,
			success: (res) => {
				// 隐藏加载提示
				if (showLoading) {
					uni.hideLoading()
				}

				const { statusCode, data: responseData } = res

				// 处理HTTP状态码
				if (statusCode === 200) {
					// 请求成功
					resolve(responseData)
				} else if (statusCode === 401) {
					// 未授权，清除登录信息并跳转到登录页
					uni.removeStorageSync('token')
					uni.removeStorageSync('userInfo')
					
					uni.showToast({
						title: '登录已过期，请重新登录',
						icon: 'none'
					})
					
					setTimeout(() => {
						uni.redirectTo({
							url: '/pages/login/login'
						})
					}, 1500)
					
					reject(new Error('未授权'))
				} else if (statusCode === 403) {
					// 权限不足
					if (showError) {
						uni.showToast({
							title: responseData.detail || '权限不足',
							icon: 'none'
						})
					}
					reject(new Error(responseData.detail || '权限不足'))
				} else if (statusCode === 400) {
					// 请求错误
					if (showError) {
						uni.showToast({
							title: responseData.detail || '请求参数错误',
							icon: 'none'
						})
					}
					reject(new Error(responseData.detail || '请求参数错误'))
				} else if (statusCode === 404) {
					// 资源不存在
					if (showError) {
						uni.showToast({
							title: '请求的资源不存在',
							icon: 'none'
						})
					}
					reject(new Error('请求的资源不存在'))
				} else {
					// 其他错误
					if (showError) {
						uni.showToast({
							title: responseData.message || `请求失败 (${statusCode})`,
							icon: 'none'
						})
					}
					reject(new Error(responseData.message || `请求失败 (${statusCode})`))
				}
			},
			fail: (err) => {
				// 隐藏加载提示
				if (showLoading) {
					uni.hideLoading()
				}

				// 网络错误
				let errorMessage = '网络连接失败，请检查网络设置'
				
				if (err.errMsg && err.errMsg.includes('timeout')) {
					errorMessage = '请求超时，请稍后重试'
				}
				
				if (showError) {
					uni.showToast({
						title: errorMessage,
						icon: 'none'
					})
				}

				reject(new Error(errorMessage))
			}
		})
	})
}

/**
 * GET请求
 * @param {String} url - 请求地址
 * @param {Object} data - 请求参数
 * @param {Object} options - 其他配置
 * @returns {Promise}
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
 * @param {String} url - 请求地址
 * @param {Object} data - 请求参数
 * @param {Object} options - 其他配置
 * @returns {Promise}
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
 * @param {String} url - 请求地址
 * @param {Object} data - 请求参数
 * @param {Object} options - 其他配置
 * @returns {Promise}
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
 * @param {String} url - 请求地址
 * @param {Object} data - 请求参数
 * @param {Object} options - 其他配置
 * @returns {Promise}
 */
const del = (url, data = {}, options = {}) => {
	return request({
		url,
		method: 'DELETE',
		data,
		...options
	})
}

/**
 * 表单提交（multipart/form-data）
 * 用于文件上传等场景
 * @param {String} url - 请求地址
 * @param {Object} data - 表单数据
 * @param {Object} options - 其他配置
 * @returns {Promise}
 */
const formPost = (url, data = {}, options = {}) => {
	return request({
		url,
		method: 'POST',
		data,
		header: {
			'Content-Type': 'multipart/form-data'
		},
		...options
	})
}

export default {
	request,
	get,
	post,
	put,
	del,
	formPost
}
