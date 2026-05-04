const BASE_URL = 'http://localhost:8000/api'

class Request {
  constructor() {
    this.baseUrl = BASE_URL
  }

  getToken() {
    return uni.getStorageSync('token') || ''
  }

  request(options) {
    const { url, method = 'GET', data = {}, header = {} } = options
    const token = this.getToken()

    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }
    header['Content-Type'] = 'application/json'

    return new Promise((resolve, reject) => {
      uni.request({
        url: this.baseUrl + url,
        method,
        data,
        header,
        success: (res) => {
          if (res.statusCode === 401) {
            uni.removeStorageSync('token')
            uni.removeStorageSync('userInfo')
            uni.reLaunch({
              url: '/pages/login/login'
            })
            reject(new Error('登录已过期，请重新登录'))
            return
          }
          
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(res.data)
          } else {
            const errMsg = res.data?.detail || res.data?.message || '请求失败'
            uni.showToast({
              title: errMsg,
              icon: 'none'
            })
            reject(new Error(errMsg))
          }
        },
        fail: (err) => {
          console.error('请求失败:', err)
          uni.showToast({
            title: '网络连接失败',
            icon: 'none'
          })
          reject(err)
        }
      })
    })
  }

  get(url, data = {}) {
    return this.request({
      url,
      method: 'GET',
      data
    })
  }

  post(url, data = {}) {
    return this.request({
      url,
      method: 'POST',
      data
    })
  }

  put(url, data = {}) {
    return this.request({
      url,
      method: 'PUT',
      data
    })
  }

  delete(url, data = {}) {
    return this.request({
      url,
      method: 'DELETE',
      data
    })
  }

  upload(url, filePath, formData = {}) {
    const token = this.getToken()
    const header = {}
    
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }

    return new Promise((resolve, reject) => {
      uni.uploadFile({
        url: this.baseUrl + url,
        filePath,
        name: 'file',
        formData,
        header,
        success: (res) => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(res.data))
          } else {
            reject(new Error('上传失败'))
          }
        },
        fail: (err) => {
          reject(err)
        }
      })
    })
  }
}

const request = new Request()
export default request
