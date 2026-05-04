/**
 * API请求封装
 * 统一处理请求、响应、错误处理
 */

// API基础地址
const BASE_URL = 'http://localhost:8000'

/**
 * 通用请求方法
 * @param {Object} options - 请求配置
 * @param {string} options.url - 请求路径
 * @param {string} options.method - 请求方法
 * @param {Object} options.data - 请求数据
 * @param {Object} options.header - 请求头
 * @returns {Promise} - 请求结果
 */
const request = (options) => {
  return new Promise((resolve, reject) => {
    // 获取token
    const token = uni.getStorageSync('token')
    
    // 构建请求头
    const header = {
      'Content-Type': 'application/json',
      ...options.header
    }
    
    // 如果有token，添加到请求头
    if (token) {
      header['Authorization'] = `Bearer ${token}`
    }
    
    uni.request({
      url: BASE_URL + options.url,
      method: options.method || 'GET',
      data: options.data || {},
      header: header,
      success: (res) => {
        if (res.statusCode === 200 || res.statusCode === 201) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // 未授权，清除登录信息并跳转到登录页
          uni.removeStorageSync('token')
          uni.removeStorageSync('userInfo')
          uni.showToast({
            title: '登录已过期，请重新登录',
            icon: 'none'
          })
          setTimeout(() => {
            uni.redirectTo({
              url: '/pages/login/login'
            })
          }, 1500)
          reject(new Error('未授权'))
        } else if (res.statusCode === 404) {
          reject(new Error('资源不存在'))
        } else if (res.statusCode === 400) {
          reject(new Error(res.data.detail || '请求参数错误'))
        } else {
          reject(new Error(res.data.detail || '请求失败'))
        }
      },
      fail: (err) => {
        uni.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * 用户相关API
 */
const userApi = {
  /**
   * 用户登录
   * @param {Object} data - 登录数据
   * @param {string} data.username - 用户名
   * @param {string} data.password - 密码
   */
  login(data) {
    return request({
      url: '/api/users/login',
      method: 'POST',
      data: data
    })
  },
  
  /**
   * 用户注册
   * @param {Object} data - 注册数据
   */
  register(data) {
    return request({
      url: '/api/users/register',
      method: 'POST',
      data: data
    })
  },
  
  /**
   * 获取用户信息
   * @param {number} userId - 用户ID
   */
  getInfo(userId) {
    return request({
      url: `/api/users/${userId}`,
      method: 'GET'
    })
  },
  
  /**
   * 更新用户信息
   * @param {number} userId - 用户ID
   * @param {Object} data - 更新数据
   */
  update(userId, data) {
    return request({
      url: `/api/users/${userId}`,
      method: 'PUT',
      data: data
    })
  }
}

/**
 * 体测记录相关API
 */
const measurementApi = {
  /**
   * 获取用户体测记录列表
   * @param {number} userId - 用户ID
   * @param {Object} params - 查询参数
   */
  getList(userId, params = {}) {
    return request({
      url: `/api/measurements/user/${userId}`,
      method: 'GET',
      data: params
    })
  },
  
  /**
   * 获取体测记录详情
   * @param {number} id - 记录ID
   */
  getDetail(id) {
    return request({
      url: `/api/measurements/${id}`,
      method: 'GET'
    })
  },
  
  /**
   * 添加体测记录
   * @param {number} userId - 用户ID
   * @param {Object} data - 体测数据
   */
  add(userId, data) {
    return request({
      url: `/api/measurements/user/${userId}`,
      method: 'POST',
      data: data
    })
  },
  
  /**
   * 更新体测记录
   * @param {number} id - 记录ID
   * @param {Object} data - 更新数据
   */
  update(id, data) {
    return request({
      url: `/api/measurements/${id}`,
      method: 'PUT',
      data: data
    })
  },
  
  /**
   * 删除体测记录
   * @param {number} id - 记录ID
   */
  delete(id) {
    return request({
      url: `/api/measurements/${id}`,
      method: 'DELETE'
    })
  },
  
  /**
   * 获取体测统计数据（用于折线图）
   * @param {number} userId - 用户ID
   * @param {Object} params - 查询参数
   */
  getStats(userId, params = {}) {
    return request({
      url: `/api/measurements/stats/user/${userId}`,
      method: 'GET',
      data: params
    })
  },
  
  /**
   * 获取最新体测记录
   * @param {number} userId - 用户ID
   */
  getLatest(userId) {
    return request({
      url: `/api/measurements/latest/user/${userId}`,
      method: 'GET'
    })
  },
  
  /**
   * 同步健身房体测数据
   * @param {number} userId - 用户ID
   * @param {Array} data - 体测数据列表
   */
  syncGymData(userId, data) {
    return request({
      url: `/api/measurements/sync/user/${userId}`,
      method: 'POST',
      data: data
    })
  }
}

/**
 * 训练项目相关API
 */
const exerciseApi = {
  /**
   * 获取所有训练项目列表
   * @param {Object} params - 查询参数
   */
  getList(params = {}) {
    return request({
      url: '/api/exercises/',
      method: 'GET',
      data: params
    })
  },
  
  /**
   * 获取训练项目详情
   * @param {number} id - 项目ID
   */
  getDetail(id) {
    return request({
      url: `/api/exercises/${id}`,
      method: 'GET'
    })
  },
  
  /**
   * 按分类获取训练项目
   * @param {string} category - 分类名称
   */
  getByCategory(category) {
    return request({
      url: `/api/exercises/category/${category}`,
      method: 'GET'
    })
  },
  
  /**
   * 获取所有分类
   */
  getCategories() {
    return request({
      url: '/api/exercises/categories/list',
      method: 'GET'
    })
  },
  
  /**
   * 添加训练项目
   * @param {Object} data - 项目数据
   */
  add(data) {
    return request({
      url: '/api/exercises/',
      method: 'POST',
      data: data
    })
  },
  
  /**
   * 更新训练项目
   * @param {number} id - 项目ID
   * @param {Object} data - 更新数据
   */
  update(id, data) {
    return request({
      url: `/api/exercises/${id}`,
      method: 'PUT',
      data: data
    })
  },
  
  /**
   * 删除训练项目
   * @param {number} id - 项目ID
   */
  delete(id) {
    return request({
      url: `/api/exercises/${id}`,
      method: 'DELETE'
    })
  }
}

/**
 * 训练日志相关API
 */
const trainingLogApi = {
  /**
   * 获取用户训练日志列表
   * @param {number} userId - 用户ID
   * @param {Object} params - 查询参数
   */
  getList(userId, params = {}) {
    return request({
      url: `/api/training-logs/user/${userId}`,
      method: 'GET',
      data: params
    })
  },
  
  /**
   * 获取训练日志详情
   * @param {number} id - 日志ID
   */
  getDetail(id) {
    return request({
      url: `/api/training-logs/${id}`,
      method: 'GET'
    })
  },
  
  /**
   * 添加训练日志
   * @param {number} userId - 用户ID
   * @param {Object} data - 日志数据
   */
  add(userId, data) {
    return request({
      url: `/api/training-logs/user/${userId}`,
      method: 'POST',
      data: data
    })
  },
  
  /**
   * 更新训练日志
   * @param {number} id - 日志ID
   * @param {Object} data - 更新数据
   */
  update(id, data) {
    return request({
      url: `/api/training-logs/${id}`,
      method: 'PUT',
      data: data
    })
  },
  
  /**
   * 删除训练日志
   * @param {number} id - 日志ID
   */
  delete(id) {
    return request({
      url: `/api/training-logs/${id}`,
      method: 'DELETE'
    })
  },
  
  /**
   * 获取月度训练统计
   * @param {number} userId - 用户ID
   * @param {Object} params - 查询参数
   */
  getMonthlyStats(userId, params = {}) {
    return request({
      url: `/api/training-logs/stats/user/${userId}/monthly`,
      method: 'GET',
      data: params
    })
  },
  
  /**
   * 获取今日训练日志
   * @param {number} userId - 用户ID
   */
  getToday(userId) {
    return request({
      url: `/api/training-logs/today/user/${userId}`,
      method: 'GET'
    })
  }
}

/**
 * 目标设定相关API
 */
const goalApi = {
  /**
   * 获取用户目标列表
   * @param {number} userId - 用户ID
   * @param {Object} params - 查询参数
   */
  getList(userId, params = {}) {
    return request({
      url: `/api/goals/user/${userId}`,
      method: 'GET',
      data: params
    })
  },
  
  /**
   * 获取目标详情
   * @param {number} id - 目标ID
   */
  getDetail(id) {
    return request({
      url: `/api/goals/${id}`,
      method: 'GET'
    })
  },
  
  /**
   * 添加目标
   * @param {number} userId - 用户ID
   * @param {Object} data - 目标数据
   */
  add(userId, data) {
    return request({
      url: `/api/goals/user/${userId}`,
      method: 'POST',
      data: data
    })
  },
  
  /**
   * 更新目标
   * @param {number} id - 目标ID
   * @param {Object} data - 更新数据
   */
  update(id, data) {
    return request({
      url: `/api/goals/${id}`,
      method: 'PUT',
      data: data
    })
  },
  
  /**
   * 删除目标
   * @param {number} id - 目标ID
   */
  delete(id) {
    return request({
      url: `/api/goals/${id}`,
      method: 'DELETE'
    })
  },
  
  /**
   * 获取当前进行中的目标
   * @param {number} userId - 用户ID
   */
  getActive(userId) {
    return request({
      url: `/api/goals/active/user/${userId}`,
      method: 'GET'
    })
  },
  
  /**
   * 添加目标进度记录
   * @param {number} goalId - 目标ID
   * @param {Object} data - 进度数据
   */
  addProgress(goalId, data) {
    return request({
      url: `/api/goals/${goalId}/progress`,
      method: 'POST',
      data: data
    })
  },
  
  /**
   * 获取目标进度记录列表
   * @param {number} goalId - 目标ID
   * @param {Object} params - 查询参数
   */
  getProgressList(goalId, params = {}) {
    return request({
      url: `/api/goals/${goalId}/progress`,
      method: 'GET',
      data: params
    })
  },
  
  /**
   * 获取目标统计
   * @param {number} userId - 用户ID
   */
  getStats(userId) {
    return request({
      url: `/api/goals/stats/user/${userId}`,
      method: 'GET'
    })
  },
  
  /**
   * 标记目标完成
   * @param {number} id - 目标ID
   */
  complete(id) {
    return request({
      url: `/api/goals/${id}/complete`,
      method: 'POST'
    })
  },
  
  /**
   * 标记目标失败
   * @param {number} id - 目标ID
   */
  fail(id) {
    return request({
      url: `/api/goals/${id}/fail`,
      method: 'POST'
    })
  }
}

/**
 * 健康检查API
 */
const healthApi = {
  /**
   * 健康检查
   */
  check() {
    return request({
      url: '/health',
      method: 'GET'
    })
  }
}

// 导出所有API
export default {
  request,
  userApi,
  measurementApi,
  exerciseApi,
  trainingLogApi,
  goalApi,
  healthApi,
  BASE_URL
}
