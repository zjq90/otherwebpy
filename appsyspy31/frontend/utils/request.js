const BASE_URL = 'http://localhost:8000/api/v1'

const request = (options = {}) => {
    const { url, method = 'GET', data = {}, header = {} } = options
    
    const token = uni.getStorageSync('token')
    if (token) {
        header['Authorization'] = `Bearer ${token}`
    }
    header['Content-Type'] = 'application/json'
    
    return new Promise((resolve, reject) => {
        uni.request({
            url: BASE_URL + url,
            method: method,
            data: data,
            header: header,
            success: (res) => {
                if (res.statusCode === 200) {
                    if (res.data.code === 200) {
                        resolve(res.data)
                    } else {
                        uni.showToast({
                            title: res.data.message || '请求失败',
                            icon: 'none'
                        })
                        reject(res.data)
                    }
                } else if (res.statusCode === 401) {
                    uni.removeStorageSync('token')
                    uni.removeStorageSync('userInfo')
                    uni.showToast({
                        title: '登录已过期，请重新登录',
                        icon: 'none'
                    })
                    setTimeout(() => {
                        uni.navigateTo({
                            url: '/pages/login/login'
                        })
                    }, 1500)
                    reject(res.data)
                } else if (res.statusCode === 403) {
                    uni.showToast({
                        title: '权限不足',
                        icon: 'none'
                    })
                    reject(res.data)
                } else if (res.statusCode === 404) {
                    uni.showToast({
                        title: '资源不存在',
                        icon: 'none'
                    })
                    reject(res.data)
                } else {
                    uni.showToast({
                        title: res.data?.message || '服务器错误',
                        icon: 'none'
                    })
                    reject(res.data)
                }
            },
            fail: (err) => {
                uni.showToast({
                    title: '网络请求失败',
                    icon: 'none'
                })
                reject(err)
            }
        })
    })
}

export const get = (url, data = {}) => {
    return request({
        url: url,
        method: 'GET',
        data: data
    })
}

export const post = (url, data = {}) => {
    return request({
        url: url,
        method: 'POST',
        data: data
    })
}

export const put = (url, data = {}) => {
    return request({
        url: url,
        method: 'PUT',
        data: data
    })
}

export const del = (url, data = {}) => {
    return request({
        url: url,
        method: 'DELETE',
        data: data
    })
}

export default {
    get,
    post,
    put,
    del
}
