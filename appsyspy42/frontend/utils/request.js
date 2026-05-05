/**
 * HTTP请求封装
 * 统一处理请求拦截、响应拦截、错误处理
 */
import config from './config.js'

const request = {
    /**
     * 通用请求方法
     * @param {Object} options 请求配置
     */
    async request(options) {
        const token = uni.getStorageSync(config.tokenKey)
        
        return new Promise((resolve, reject) => {
            uni.request({
                url: config.apiBaseUrl + options.url,
                method: options.method || 'GET',
                data: options.data || {},
                header: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : '',
                    ...options.header
                },
                timeout: config.timeout,
                success: (res) => {
                    if (res.statusCode === 200) {
                        resolve(res.data)
                    } else if (res.statusCode === 401) {
                        uni.removeStorageSync(config.tokenKey)
                        uni.removeStorageSync(config.userInfoKey)
                        uni.showToast({
                            title: '登录已过期，请重新登录',
                            icon: 'none'
                        })
                        setTimeout(() => {
                            uni.reLaunch({
                                url: '/pages/login/login'
                            })
                        }, 1500)
                        reject(res)
                    } else {
                        uni.showToast({
                            title: res.data?.detail || '请求失败',
                            icon: 'none'
                        })
                        reject(res)
                    }
                },
                fail: (err) => {
                    uni.showToast({
                        title: '网络错误，请检查网络连接',
                        icon: 'none'
                    })
                    reject(err)
                }
            })
        })
    },

    /**
     * GET请求
     * @param {String} url 请求地址
     * @param {Object} data 请求参数
     */
    get(url, data = {}) {
        return this.request({
            url,
            method: 'GET',
            data
        })
    },

    /**
     * POST请求
     * @param {String} url 请求地址
     * @param {Object} data 请求参数
     */
    post(url, data = {}) {
        return this.request({
            url,
            method: 'POST',
            data
        })
    },

    /**
     * PUT请求
     * @param {String} url 请求地址
     * @param {Object} data 请求参数
     */
    put(url, data = {}) {
        return this.request({
            url,
            method: 'PUT',
            data
        })
    },

    /**
     * DELETE请求
     * @param {String} url 请求地址
     * @param {Object} data 请求参数
     */
    delete(url, data = {}) {
        return this.request({
            url,
            method: 'DELETE',
            data
        })
    }
}

export default request
