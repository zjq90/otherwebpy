const BASE_URL = 'http://localhost:8000/api'

interface RequestOptions {
  url: string
  method: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: any
  needAuth?: boolean
}

interface ResponseData<T = any> {
  code: number
  message: string
  data: T
}

const getToken = (): string | null => {
  return uni.getStorageSync('token')
}

const request = async <T>(options: RequestOptions): Promise<T> => {
  const { url, method, data, header = {}, needAuth = true } = options
  
  const headers: any = {
    'Content-Type': 'application/json',
    ...header
  }
  
  if (needAuth) {
    const token = getToken()
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
  }
  
  return new Promise((resolve, reject) => {
    uni.request({
      url: BASE_URL + url,
      method,
      data,
      header: headers,
      success: (res: any) => {
        if (res.statusCode === 200) {
          resolve(res.data as T)
        } else if (res.statusCode === 401) {
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.reLaunch({
            url: '/pages/login/login'
          })
          reject(new Error('登录已过期，请重新登录'))
        } else {
          const message = res.data?.detail || res.data?.message || '请求失败'
          uni.showToast({
            title: message,
            icon: 'none'
          })
          reject(new Error(message))
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

export const get = <T>(url: string, data?: any, needAuth: boolean = true): Promise<T> => {
  return request<T>({
    url,
    method: 'GET',
    data,
    needAuth
  })
}

export const post = <T>(url: string, data?: any, needAuth: boolean = true): Promise<T> => {
  return request<T>({
    url,
    method: 'POST',
    data,
    needAuth
  })
}

export const put = <T>(url: string, data?: any, needAuth: boolean = true): Promise<T> => {
  return request<T>({
    url,
    method: 'PUT',
    data,
    needAuth
  })
}

export const del = <T>(url: string, data?: any, needAuth: boolean = true): Promise<T> => {
  return request<T>({
    url,
    method: 'DELETE',
    data,
    needAuth
  })
}

export default {
  get,
  post,
  put,
  del,
  request
}
