import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 创建axios实例
const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    const res = response.data
    
    // 业务状态码判断
    if (res.code && res.code !== 200 && res.code !== 201) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    
    return res
  },
  error => {
    let message = error.message
    
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = '请求参数错误'
          break
        case 401:
          message = '未授权，请登录'
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求地址不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = `连接出错(${error.response.status})`
      }
    } else if (error.code === 'ECONNABORTED') {
      message = '请求超时，请重试'
    }
    
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

// GET请求
export function get(url, params = {}) {
  return http({
    method: 'get',
    url,
    params
  })
}

// POST请求
export function post(url, data = {}) {
  return http({
    method: 'post',
    url,
    data
  })
}

// PUT请求
export function put(url, data = {}) {
  return http({
    method: 'put',
    url,
    data
  })
}

// DELETE请求
export function del(url, params = {}) {
  return http({
    method: 'delete',
    url,
    params
  })
}

export default http
