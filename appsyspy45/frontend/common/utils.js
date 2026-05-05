const formatTime = (date, format = 'YYYY-MM-DD HH:mm:ss') => {
  if (!date) return ''
  
  let d = date
  if (typeof date === 'string' || typeof date === 'number') {
    d = new Date(date)
  }
  
  const year = d.getFullYear()
  const month = d.getMonth() + 1
  const day = d.getDate()
  const hour = d.getHours()
  const minute = d.getMinutes()
  const second = d.getSeconds()
  
  const formatMap = {
    'YYYY': year,
    'MM': padZero(month),
    'DD': padZero(day),
    'HH': padZero(hour),
    'mm': padZero(minute),
    'ss': padZero(second)
  }
  
  let result = format
  for (const key in formatMap) {
    result = result.replace(key, formatMap[key])
  }
  
  return result
}

const padZero = (num) => {
  return num < 10 ? '0' + num : num
}

const formatDate = (date) => {
  return formatTime(date, 'YYYY-MM-DD')
}

const formatDateTime = (date) => {
  return formatTime(date, 'YYYY-MM-DD HH:mm')
}

const relativeTime = (date) => {
  if (!date) return ''
  
  const now = new Date()
  let d = date
  if (typeof date === 'string' || typeof date === 'number') {
    d = new Date(date)
  }
  
  const diff = now.getTime() - d.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)
  
  if (seconds < 60) {
    return '刚刚'
  } else if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else if (days < 7) {
    return `${days}天前`
  } else {
    return formatDate(d)
  }
}

const formatNumber = (num) => {
  if (!num && num !== 0) return '0'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toString()
}

const formatPrice = (price) => {
  if (!price && price !== 0) return '0.00'
  return parseFloat(price).toFixed(2)
}

const maskPhone = (phone) => {
  if (!phone) return ''
  if (phone.length !== 11) return phone
  return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
}

const validatePhone = (phone) => {
  const reg = /^1[3-9]\d{9}$/
  return reg.test(phone)
}

const validatePassword = (password) => {
  if (!password) return false
  if (password.length < 6 || password.length > 20) return false
  return true
}

const showToast = (title, icon = 'none', duration = 2000) => {
  uni.showToast({
    title,
    icon,
    duration
  })
}

const showLoading = (title = '加载中...') => {
  uni.showLoading({
    title,
    mask: true
  })
}

const hideLoading = () => {
  uni.hideLoading()
}

const showModal = (content, title = '提示', showCancel = true) => {
  return new Promise((resolve, reject) => {
    uni.showModal({
      title,
      content,
      showCancel,
      success: (res) => {
        if (res.confirm) {
          resolve(true)
        } else {
          resolve(false)
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

const navigateTo = (url) => {
  uni.navigateTo({
    url
  })
}

const redirectTo = (url) => {
  uni.redirectTo({
    url
  })
}

const switchTab = (url) => {
  uni.switchTab({
    url
  })
}

const navigateBack = (delta = 1) => {
  uni.navigateBack({
    delta
  })
}

const getStorageSync = (key) => {
  try {
    return uni.getStorageSync(key)
  } catch (e) {
    console.error('获取缓存失败:', e)
    return null
  }
}

const setStorageSync = (key, value) => {
  try {
    uni.setStorageSync(key, value)
  } catch (e) {
    console.error('设置缓存失败:', e)
  }
}

const removeStorageSync = (key) => {
  try {
    uni.removeStorageSync(key)
  } catch (e) {
    console.error('清除缓存失败:', e)
  }
}

const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item))
  }
  
  const cloned = {}
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key])
    }
  }
  
  return cloned
}

const debounce = (fn, delay = 300) => {
  let timer = null
  return function(...args) {
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

const throttle = (fn, delay = 300) => {
  let lastTime = 0
  return function(...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      lastTime = now
      fn.apply(this, args)
    }
  }
}

export default {
  formatTime,
  formatDate,
  formatDateTime,
  relativeTime,
  formatNumber,
  formatPrice,
  maskPhone,
  validatePhone,
  validatePassword,
  showToast,
  showLoading,
  hideLoading,
  showModal,
  navigateTo,
  redirectTo,
  switchTab,
  navigateBack,
  getStorageSync,
  setStorageSync,
  removeStorageSync,
  deepClone,
  debounce,
  throttle
}
