/**
 * 应用全局配置
 * 管理API地址、环境配置等全局变量
 */

// 环境配置
const ENV = {
  DEVELOPMENT: 'development',
  PRODUCTION: 'production',
  TEST: 'test'
}

// 当前环境
const currentEnv = ENV.DEVELOPMENT

// API基础地址配置
const API_BASE_URL = {
  [ENV.DEVELOPMENT]: 'http://localhost:8000',
  [ENV.PRODUCTION]: 'https://your-api-domain.com',
  [ENV.TEST]: 'http://test-api-domain.com'
}

// 获取API基础地址
const getBaseUrl = () => {
  return API_BASE_URL[currentEnv] || API_BASE_URL[ENV.DEVELOPMENT]
}

// 应用配置
const config = {
  // 环境
  env: currentEnv,
  // API基础地址
  baseUrl: getBaseUrl(),
  // 请求超时时间（毫秒）
  timeout: 30000,
  // Token存储键名
  tokenKey: 'token',
  // 用户信息存储键名
  userInfoKey: 'userInfo',
  // 应用名称
  appName: '运输管理系统',
  // 应用版本
  appVersion: '1.0.0',
  
  // 用户角色
  roles: {
    ADMIN: 'admin',
    DISPATCHER: 'dispatcher',
    DRIVER: 'driver'
  },
  
  // 任务状态
  taskStatus: {
    PENDING: 'pending',
    ASSIGNED: 'assigned',
    CONFIRMED: 'confirmed',
    DEPARTED: 'departed',
    ARRIVED: 'arrived',
    UNLOADING: 'unloading',
    COMPLETED: 'completed',
    CANCELLED: 'cancelled'
  },
  
  // 任务状态文本
  taskStatusText: {
    pending: '待分配',
    assigned: '已分配',
    confirmed: '已确认',
    departed: '已出发',
    arrived: '已到达',
    unloading: '卸料中',
    completed: '已完成',
    cancelled: '已取消'
  },
  
  // 车辆状态
  vehicleStatus: {
    IDLE: 'idle',
    IN_TRANSIT: 'in_transit',
    MAINTENANCE: 'maintenance',
    DISABLED: 'disabled'
  },
  
  // 车辆状态文本
  vehicleStatusText: {
    idle: '空闲',
    in_transit: '运输中',
    maintenance: '维护中',
    disabled: '停用'
  }
}

// 将配置挂载到全局
uni.$config = config

export default config
