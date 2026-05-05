/**
 * 网络请求封装
 * 统一处理请求和响应
 */

// 基础URL，根据实际环境修改
const BASE_URL = 'http://localhost:8000'

/**
 * 统一请求方法
 * @param {Object} options - 请求配置
 * @param {String} options.url - 请求路径
 * @param {String} options.method - 请求方法
 * @param {Object} options.data - 请求数据
 * @param {Object} options.header - 请求头
 * @param {Boolean} options.showLoading - 是否显示加载提示
 */
const request = (options = {}) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    
    // 显示加载提示
    if (options.showLoading !== false) {
      uni.showLoading({
        title: '加载中...',
        mask: true
      })
    }
    
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.header
      },
      success: (res) => {
        uni.hideLoading()
        
        if (res.statusCode === 200) {
          const data = res.data
          if (data.code === 200) {
            resolve(data)
          } else {
            uni.showToast({
              title: data.message || '请求失败',
              icon: 'none'
            })
            reject(data)
          }
        } else if (res.statusCode === 401) {
          // 未授权，清除token并跳转登录
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none',
            success: () => {
              setTimeout(() => {
                uni.reLaunch({
                  url: '/pages/login/login'
                })
              }, 1500)
            }
          })
          reject(res)
        } else if (res.statusCode === 403) {
          uni.showToast({
            title: '无权限访问',
            icon: 'none'
          })
          reject(res)
        } else {
          uni.showToast({
            title: `请求失败: ${res.statusCode}`,
            icon: 'none'
          })
          reject(res)
        }
      },
      fail: (err) => {
        uni.hideLoading()
        console.error('请求失败:', err)
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

/**
 * 文件上传
 */
const uploadFile = (url, filePath, name = 'file', formData = {}) => {
  return new Promise((resolve, reject) => {
    const token = uni.getStorageSync('token')
    
    uni.showLoading({
      title: '上传中...',
      mask: true
    })
    
    uni.uploadFile({
      url: BASE_URL + url,
      filePath: filePath,
      name: name,
      formData: formData,
      header: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      success: (res) => {
        uni.hideLoading()
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data)
          if (data.code === 200) {
            resolve(data)
          } else {
            uni.showToast({
              title: data.message || '上传失败',
              icon: 'none'
            })
            reject(data)
          }
        } else {
          uni.showToast({
            title: `上传失败: ${res.statusCode}`,
            icon: 'none'
          })
          reject(res)
        }
      },
      fail: (err) => {
        uni.hideLoading()
        uni.showToast({
          title: '上传失败，请重试',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

export default {
  BASE_URL,
  request,
  get,
  post,
  put,
  del,
  uploadFile
}
