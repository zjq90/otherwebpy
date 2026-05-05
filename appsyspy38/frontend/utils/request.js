/**
 * API请求封装
 * 处理统一的请求配置、错误处理、Token管理
 */

const BASE_URL = 'http://localhost:8000/api/v1'

/**
 * 发起请求
 * @param {Object} options 请求配置
 * @param {String} options.url 请求地址
 * @param {String} options.method 请求方法
 * @param {Object} options.data 请求数据
 * @param {Boolean} options.auth 是否需要认证
 * @param {Boolean} options.loading 是否显示加载提示
 */
const request = (options = {}) => {
    return new Promise((resolve, reject) => {
        const {
            url,
            method = 'GET',
            data = {},
            auth = false,
            loading = true
        } = options

        // 显示加载提示
        if (loading) {
            uni.showLoading({
                title: '加载中...',
                mask: true
            })
        }

        // 构建请求头
        const header = {
            'Content-Type': 'application/json'
        }

        // 添加认证Token
        if (auth) {
            const token = uni.getStorageSync('token')
            if (token) {
                header['Authorization'] = `Bearer ${token}`
            }
        }

        // 发起请求
        uni.request({
            url: BASE_URL + url,
            method: method,
            data: data,
            header: header,
            success: (res) => {
                // 隐藏加载提示
                if (loading) {
                    uni.hideLoading()
                }

                const { statusCode, data: responseData } = res

                // 处理响应
                if (statusCode === 200) {
                    // 请求成功
                    resolve(responseData)
                } else if (statusCode === 401) {
                    // 未授权，清除登录信息并跳转到登录页
                    uni.removeStorageSync('token')
                    uni.removeStorageSync('userInfo')
                    uni.removeStorageSync('permissions')
                    
                    uni.showToast({
                        title: '登录已过期，请重新登录',
                        icon: 'none',
                        duration: 2000
                    })

                    setTimeout(() => {
                        uni.redirectTo({
                            url: '/pages/login/login'
                        })
                    }, 1500)

                    reject(new Error('未授权'))
                } else if (statusCode === 403) {
                    // 权限不足
                    uni.showToast({
                        title: '权限不足',
                        icon: 'none',
                        duration: 2000
                    })
                    reject(new Error('权限不足'))
                } else {
                    // 其他错误
                    const errorMsg = responseData.detail || '请求失败'
                    uni.showToast({
                        title: errorMsg,
                        icon: 'none',
                        duration: 2000
                    })
                    reject(new Error(errorMsg))
                }
            },
            fail: (err) => {
                // 隐藏加载提示
                if (loading) {
                    uni.hideLoading()
                }

                console.error('请求失败:', err)
                uni.showToast({
                    title: '网络错误，请检查网络连接',
                    icon: 'none',
                    duration: 2000
                })
                reject(err)
            }
        })
    })
}

/**
 * GET请求
 * @param {String} url 请求地址
 * @param {Object} data 请求参数
 * @param {Object} options 其他配置
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
 * @param {String} url 请求地址
 * @param {Object} data 请求数据
 * @param {Object} options 其他配置
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
 * @param {String} url 请求地址
 * @param {Object} data 请求数据
 * @param {Object} options 其他配置
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
 * @param {String} url 请求地址
 * @param {Object} data 请求数据
 * @param {Object} options 其他配置
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
    del,
    BASE_URL
}
