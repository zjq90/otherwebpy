/**
 * Axios 请求封装
 */
import axios from 'axios'
import { Message, MessageBox } from 'element-ui'
import store from '@/store'
import { getToken } from '@/utils/auth'

// 创建 axios 实例
const service = axios.create({
  // API 基础地址
  baseURL: process.env.VUE_APP_API_BASE_URL,
  // 超时时间
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    if (store.getters.token) {
      // 让每个请求携带自定义 token
      config.headers['Authorization'] = `Bearer ${getToken()}`
    }
    return config
  },
  error => {
    // 对请求错误做些什么
    console.log(error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果自定义 code 不是 200，则判断为错误
    if (res.code !== 200) {
      Message({
        message: res.message || '请求失败',
        type: 'error',
        duration: 5 * 1000
      })
      
      // 401: 未授权或 Token 过期
      if (res.code === 401) {
        MessageBox.confirm('登录状态已过期，您可以继续留在该页面，或者重新登录', '系统提示', {
          confirmButtonText: '重新登录',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          store.dispatch('user/resetToken').then(() => {
            location.reload()
          })
        })
      }
      
      // 403: 权限不足
      if (res.code === 403) {
        Message({
          message: '权限不足',
          type: 'error',
          duration: 5 * 1000
        })
      }
      
      return Promise.reject(new Error(res.message || '请求失败'))
    } else {
      return res
    }
  },
  error => {
    console.log('err' + error)
    
    let message = error.message
    if (error.response) {
      switch (error.response.status) {
        case 400:
          message = '请求错误'
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
        case 408:
          message = '请求超时'
          break
        case 500:
          message = '服务器内部错误'
          break
        case 501:
          message = '服务未实现'
          break
        case 502:
          message = '网关错误'
          break
        case 503:
          message = '服务不可用'
          break
        case 504:
          message = '网关超时'
          break
        case 505:
          message = 'HTTP版本不受支持'
          break
        default:
          message = error.response.data?.message || '连接错误'
      }
    }
    
    Message({
      message: message,
      type: 'error',
      duration: 5 * 1000
    })
    
    return Promise.reject(error)
  }
)

export default service
