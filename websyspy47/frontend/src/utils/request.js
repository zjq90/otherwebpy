import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

function cleanParams(params) {
  if (!params) return params
  const cleaned = {}
  for (const [key, value] of Object.entries(params)) {
    if (value === '' || value === null || value === undefined) {
      continue
    }
    if (typeof value === 'string') {
      const trimmed = value.trim()
      if (trimmed !== '') {
        cleaned[key] = trimmed
      }
    } else {
      cleaned[key] = value
    }
  }
  return Object.keys(cleaned).length > 0 ? cleaned : undefined
}

request.interceptors.request.use(
  (config) => {
    if (config.params) {
      config.params = cleanParams(config.params)
    }
    if (config.data && typeof config.data === 'object') {
      config.data = cleanParams(config.data)
    }
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 200) {
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    console.error('Response error:', error)
    if (error.response) {
      if (error.response.status === 422) {
        const data = error.response.data
        let msg = '参数验证失败'
        if (data && data.data && Array.isArray(data.data)) {
          const errors = data.data.map(e => {
            const field = e.loc ? e.loc.join('.') : '参数'
            return `${field}: ${e.msg}`
          })
          msg = errors.join('\n')
        }
        ElMessage.error(msg)
      } else if (error.response.status === 500) {
        ElMessage.error('服务器内部错误，请稍后重试')
      } else {
        ElMessage.error(error.message || '网络错误')
      }
    } else {
      ElMessage.error(error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export default request
