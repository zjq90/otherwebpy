/**
 * API请求工具类
 * 封装uni.request，添加拦截器和统一处理
 */
import { getToken, getBaseUrl, clearAuth, navigateToLogin } from './auth'

/**
 * 统一请求方法
 * @param {Object} options - 请求配置
 * @param {string} options.url - 接口地址
 * @param {string} options.method - 请求方法
 * @param {Object} options.data - 请求数据
 * @param {Object} options.header - 请求头
 * @param {boolean} options.showLoading - 是否显示加载中
 * @param {string} options.loadingText - 加载文字
 * @param {boolean} options.showError - 是否显示错误提示
 */
export function request(options) {
    const {
        url,
        method = 'GET',
        data = {},
        header = {},
        showLoading = false,
        loadingText = '加载中...',
        showError = true
    } = options

    // 获取Token
    const token = getToken()
    
    // 构建请求头
    const requestHeader = {
        'Content-Type': 'application/json',
        ...header
    }
    
    // 添加Token
    if (token) {
        requestHeader['Authorization'] = `Bearer ${token}`
    }

    // 显示加载
    if (showLoading) {
        uni.showLoading({
            title: loadingText,
            mask: true
        })
    }

    return new Promise((resolve, reject) => {
        uni.request({
            url: getBaseUrl() + '/api/v1' + url,
            method: method,
            data: data,
            header: requestHeader,
            success: (res) => {
                // 隐藏加载
                if (showLoading) {
                    uni.hideLoading()
                }

                const { statusCode, data: responseData } = res

                // 请求成功
                if (statusCode === 200 || statusCode === 201) {
                    resolve(responseData)
                } else if (statusCode === 401) {
                    // Token过期或无效
                    clearAuth()
                    if (showError) {
                        uni.showToast({
                            title: '登录已过期，请重新登录',
                            icon: 'none'
                        })
                    }
                    setTimeout(() => {
                        navigateToLogin()
                    }, 1500)
                    reject(new Error('登录已过期'))
                } else if (statusCode === 403) {
                    if (showError) {
                        uni.showToast({
                            title: responseData.detail || '没有权限',
                            icon: 'none'
                        })
                    }
                    reject(new Error(responseData.detail || '没有权限'))
                } else if (statusCode === 404) {
                    if (showError) {
                        uni.showToast({
                            title: responseData.detail || '资源不存在',
                            icon: 'none'
                        })
                    }
                    reject(new Error(responseData.detail || '资源不存在'))
                } else if (statusCode === 422) {
                    // 参数验证错误
                    const errorMsg = responseData.message || '参数验证失败'
                    if (showError) {
                        uni.showToast({
                            title: errorMsg,
                            icon: 'none'
                        })
                    }
                    reject(new Error(errorMsg))
                } else {
                    // 其他错误
                    const errorMsg = responseData.detail || responseData.message || '请求失败'
                    if (showError) {
                        uni.showToast({
                            title: errorMsg,
                            icon: 'none'
                        })
                    }
                    reject(new Error(errorMsg))
                }
            },
            fail: (err) => {
                // 隐藏加载
                if (showLoading) {
                    uni.hideLoading()
                }

                const errorMsg = err.errMsg || '网络请求失败'
                if (showError) {
                    uni.showToast({
                        title: '网络连接失败',
                        icon: 'none'
                    })
                }
                reject(new Error(errorMsg))
            }
        })
    })
}

/**
 * GET请求
 */
export function get(url, data = {}, options = {}) {
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
export function post(url, data = {}, options = {}) {
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
export function put(url, data = {}, options = {}) {
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
export function del(url, data = {}, options = {}) {
    return request({
        url,
        method: 'DELETE',
        data,
        ...options
    })
}

/**
 * 上传文件
 */
export function uploadFile(url, filePath, name = 'file', options = {}) {
    const token = getToken()
    const header = {}
    
    if (token) {
        header['Authorization'] = `Bearer ${token}`
    }

    return new Promise((resolve, reject) => {
        uni.uploadFile({
            url: getBaseUrl() + '/api/v1' + url,
            filePath: filePath,
            name: name,
            header: header,
            formData: options.formData || {},
            success: (res) => {
                try {
                    const data = JSON.parse(res.data)
                    resolve(data)
                } catch (e) {
                    reject(new Error('解析响应失败'))
                }
            },
            fail: (err) => {
                reject(new Error(err.errMsg || '上传失败'))
            }
        })
    })
}

export default request
