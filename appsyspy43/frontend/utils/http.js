/**
 * HTTP请求封装
 * 统一处理请求拦截、响应拦截、错误处理等
 */

import config from './config.js'

/**
 * 通用请求方法
 * @param {Object} options - 请求配置
 * @param {String} options.url - 请求地址
 * @param {String} options.method - 请求方法 GET/POST/PUT/DELETE
 * @param {Object} options.data - 请求参数
 * @param {Object} options.header - 请求头
 * @param {Boolean} options.showLoading - 是否显示加载提示
 * @param {Boolean} options.showError - 是否显示错误提示
 */
const request = (options) => {
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
  const token = uni.getStorageSync(config.tokenKey)
  
  // 构建请求头
  const requestHeader = {
    'Content-Type': 'application/json',
    ...header
  }
  
  // 添加Authorization头
  if (token) {
    requestHeader['Authorization'] = `Bearer ${token}`
  }
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: config.baseUrl + url,
      method: method,
      data: data,
      header: requestHeader,
      timeout: config.timeout,
      
      success: (res) => {
        // 隐藏加载提示
        if (showLoading) {
          uni.hideLoading()
        }
        
        const { statusCode, data: responseData } = res
        
        // HTTP状态码处理
        if (statusCode === 200 || statusCode === 201) {
          // 请求成功
          if (responseData.code === 200 || responseData.code === 0) {
            resolve(responseData)
          } else {
            // 业务错误
            if (showError) {
              uni.showToast({
                title: responseData.message || '请求失败',
                icon: 'none',
                duration: 2000
              })
            }
            reject(responseData)
          }
        } else if (statusCode === 401) {
          // 未授权，需要重新登录
          uni.removeStorageSync(config.tokenKey)
          uni.removeStorageSync(config.userInfoKey)
          
          uni.showModal({
            title: '提示',
            content: '登录已过期，请重新登录',
            showCancel: false,
            success: () => {
              uni.redirectTo({
                url: '/pages/login/login'
              })
            }
          })
          reject({ message: '未授权' })
        } else if (statusCode === 403) {
          // 无权限
          if (showError) {
            uni.showToast({
              title: '无权限访问',
              icon: 'none',
              duration: 2000
            })
          }
          reject({ message: '无权限', statusCode })
        } else if (statusCode === 404) {
          if (showError) {
            uni.showToast({
              title: '请求地址不存在',
              icon: 'none',
              duration: 2000
            })
          }
          reject({ message: '请求地址不存在', statusCode })
        } else if (statusCode === 500) {
          if (showError) {
            uni.showToast({
              title: '服务器内部错误',
              icon: 'none',
              duration: 2000
            })
          }
          reject({ message: '服务器内部错误', statusCode })
        } else {
          if (showError) {
            uni.showToast({
              title: `请求失败: ${statusCode}`,
              icon: 'none',
              duration: 2000
            })
          }
          reject({ message: `请求失败: ${statusCode}`, statusCode })
        }
      },
      
      fail: (err) => {
        // 隐藏加载提示
        if (showLoading) {
          uni.hideLoading()
        }
        
        // 网络错误
        let errorMessage = '网络错误，请检查网络连接'
        
        if (err.errMsg) {
          if (err.errMsg.includes('timeout')) {
            errorMessage = '请求超时，请稍后重试'
          } else if (err.errMsg.includes('fail')) {
            errorMessage = '网络连接失败'
          }
        }
        
        if (showError) {
          uni.showToast({
            title: errorMessage,
            icon: 'none',
            duration: 2000
          })
        }
        
        reject({ message: errorMessage, err: err })
      },
      
      complete: () => {
        // 完成时的处理
      }
    })
  })
}

/**
 * 上传文件方法
 * @param {Object} options - 上传配置
 * @param {String} options.url - 上传地址
 * @param {String} options.filePath - 文件路径
 * @param {String} options.name - 文件参数名
 * @param {Object} options.formData - 额外表单数据
 * @param {Boolean} options.showLoading - 是否显示加载提示
 */
const upload = (options) => {
  const {
    url,
    filePath,
    name = 'file',
    formData = {},
    showLoading = true
  } = options
  
  if (showLoading) {
    uni.showLoading({
      title: '上传中...',
      mask: true
    })
  }
  
  const token = uni.getStorageSync(config.tokenKey)
  
  const header = {}
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }
  
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: config.baseUrl + url,
      filePath: filePath,
      name: name,
      formData: formData,
      header: header,
      
      success: (res) => {
        if (showLoading) {
          uni.hideLoading()
        }
        
        if (res.statusCode === 200) {
          const data = JSON.parse(res.data)
          if (data.code === 200 || data.code === 0) {
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
            title: '上传失败',
            icon: 'none'
          })
          reject(res)
        }
      },
      
      fail: (err) => {
        if (showLoading) {
          uni.hideLoading()
        }
        uni.showToast({
          title: '上传失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

// 导出HTTP方法
const http = {
  // GET请求
  get: (url, data = {}, options = {}) => {
    return request({
      url,
      method: 'GET',
      data,
      ...options
    })
  },
  
  // POST请求
  post: (url, data = {}, options = {}) => {
    return request({
      url,
      method: 'POST',
      data,
      ...options
    })
  },
  
  // PUT请求
  put: (url, data = {}, options = {}) => {
    return request({
      url,
      method: 'PUT',
      data,
      ...options
    })
  },
  
  // DELETE请求
  delete: (url, data = {}, options = {}) => {
    return request({
      url,
      method: 'DELETE',
      data,
      ...options
    })
  },
  
  // 上传文件
  upload: upload
}

// 挂载到全局
uni.$http = http

export { http, request, upload }
