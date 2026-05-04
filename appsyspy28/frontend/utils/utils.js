const weekDays = ['日', '一', '二', '三', '四', '五', '六']

function formatDate(date, format = 'YYYY-MM-DD') {
  if (!(date instanceof Date)) {
    date = new Date(date)
  }
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hour = String(date.getHours()).padStart(2, '0')
  const minute = String(date.getMinutes()).padStart(2, '0')
  const second = String(date.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hour)
    .replace('mm', minute)
    .replace('ss', second)
}

function parseTime(timeStr) {
  if (!timeStr) return null
  
  if (typeof timeStr === 'string') {
    const [hours, minutes, seconds = 0] = timeStr.split(':').map(Number)
    return { hours, minutes, seconds }
  }
  
  return timeStr
}

function formatTime(timeStr, format = 'HH:mm') {
  const time = parseTime(timeStr)
  if (!time) return ''
  
  const hour = String(time.hours).padStart(2, '0')
  const minute = String(time.minutes).padStart(2, '0')
  
  return format
    .replace('HH', hour)
    .replace('mm', minute)
}

function getWeekDates(baseDate) {
  if (!(baseDate instanceof Date)) {
    baseDate = new Date(baseDate)
  }
  
  const currentDay = baseDate.getDay()
  const dates = []
  
  for (let i = 0; i < 7; i++) {
    const diff = i - currentDay
    const date = new Date(baseDate)
    date.setDate(baseDate.getDate() + diff)
    dates.push({
      date,
      dateStr: formatDate(date, 'YYYY-MM-DD'),
      day: date.getDate(),
      weekDay: weekDays[i]
    })
  }
  
  return dates
}

function isToday(dateStr) {
  const today = formatDate(new Date(), 'YYYY-MM-DD')
  return today === dateStr
}

function getBookingStatusText(status) {
  const statusMap = {
    'pending': '待确认',
    'confirmed': '已预约',
    'cancelled': '已取消',
    'completed': '已完成'
  }
  return statusMap[status] || status
}

function getBookingStatusType(status) {
  const typeMap = {
    'pending': 'warning',
    'confirmed': 'success',
    'cancelled': 'danger',
    'completed': 'secondary'
  }
  return typeMap[status] || 'secondary'
}

function getCheckinMethodText(method) {
  const methodMap = {
    'qrcode': '扫码签到',
    'face': '人脸识别'
  }
  return methodMap[method] || method
}

function getCardTypeText(type) {
  const typeMap = {
    'monthly': '月卡',
    'yearly': '年卡',
    'times': '次卡',
    'group': '团课卡',
    'private': '私教课卡'
  }
  return typeMap[type] || type
}

function showToast(title, icon = 'none', duration = 2000) {
  uni.showToast({
    title,
    icon,
    duration
  })
}

function showLoading(title = '加载中...') {
  uni.showLoading({
    title,
    mask: true
  })
}

function hideLoading() {
  uni.hideLoading()
}

function showModal(title, content, showCancel = true) {
  return new Promise((resolve) => {
    uni.showModal({
      title,
      content,
      showCancel,
      success: (res) => {
        resolve(res.confirm)
      }
    })
  })
}

export {
  weekDays,
  formatDate,
  parseTime,
  formatTime,
  getWeekDates,
  isToday,
  getBookingStatusText,
  getBookingStatusType,
  getCheckinMethodText,
  getCardTypeText,
  showToast,
  showLoading,
  hideLoading,
  showModal
}
