import config from './config.js'

class Request {
  constructor() {
    this.baseURL = config.baseURL
    this.apiPrefix = config.apiPrefix
    this.timeout = config.timeout
  }

  request(options) {
    return new Promise((resolve, reject) => {
      const url = this.baseURL + this.apiPrefix + options.url
      
      uni.request({
        url: url,
        method: options.method || 'GET',
        data: options.data || {},
        header: {
          'Content-Type': 'application/json',
          ...options.header
        },
        timeout: this.timeout,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(res.data)
          } else if (res.statusCode === 404) {
            reject(new Error('请求的资源不存在'))
          } else if (res.statusCode === 500) {
            reject(new Error('服务器内部错误'))
          } else {
            reject(new Error(res.data?.detail || `请求失败: ${res.statusCode}`))
          }
        },
        fail: (err) => {
          reject(new Error(`网络请求失败: ${err.errMsg}`))
        }
      })
    })
  }

  get(url, data = {}) {
    return this.request({
      url: url,
      method: 'GET',
      data: data
    })
  }

  post(url, data = {}) {
    return this.request({
      url: url,
      method: 'POST',
      data: data
    })
  }

  put(url, data = {}) {
    return this.request({
      url: url,
      method: 'PUT',
      data: data
    })
  }

  delete(url, data = {}) {
    return this.request({
      url: url,
      method: 'DELETE',
      data: data
    })
  }
}

const request = new Request()

export default request
