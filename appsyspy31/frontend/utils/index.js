export * from './request'
export * from './api'

export const formatDate = (date, format = 'YYYY-MM-DD') => {
    if (!date) return ''
    const d = new Date(date)
    const year = d.getFullYear()
    const month = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const hour = String(d.getHours()).padStart(2, '0')
    const minute = String(d.getMinutes()).padStart(2, '0')
    const second = String(d.getSeconds()).padStart(2, '0')
    
    return format
        .replace('YYYY', year)
        .replace('MM', month)
        .replace('DD', day)
        .replace('HH', hour)
        .replace('mm', minute)
        .replace('ss', second)
}

export const formatTime = (date) => {
    return formatDate(date, 'HH:mm')
}

export const formatDateTime = (date) => {
    return formatDate(date, 'YYYY-MM-DD HH:mm:ss')
}

export const showLoading = (title = '加载中...') => {
    uni.showLoading({
        title: title,
        mask: true
    })
}

export const hideLoading = () => {
    uni.hideLoading()
}

export const showToast = (title, icon = 'none', duration = 2000) => {
    uni.showToast({
        title: title,
        icon: icon,
        duration: duration
    })
}

export const showConfirm = (title, content) => {
    return new Promise((resolve, reject) => {
        uni.showModal({
            title: title,
            content: content,
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

export const debounce = (fn, delay = 300) => {
    let timer = null
    return function (...args) {
        if (timer) clearTimeout(timer)
        timer = setTimeout(() => {
            fn.apply(this, args)
        }, delay)
    }
}

export const throttle = (fn, delay = 300) => {
    let last = 0
    return function (...args) {
        const now = Date.now()
        if (now - last >= delay) {
            last = now
            fn.apply(this, args)
        }
    }
}

export const getStatusBadge = (status) => {
    const statusMap = {
        'pending': { text: '待确认', color: '#ffa502' },
        'confirmed': { text: '已确认', color: '#2ed573' },
        'completed': { text: '已完成', color: '#667eea' },
        'cancelled': { text: '已取消', color: '#ff4757' },
        'no_show': { text: '未出席', color: '#999999' }
    }
    return statusMap[status] || { text: status, color: '#999999' }
}

export const getDifficultyLabel = (level) => {
    const labels = {
        1: '初级',
        2: '初级-中级',
        3: '中级',
        4: '中级-高级',
        5: '高级'
    }
    return labels[level] || '未知'
}

export const getRatingStars = (rating) => {
    const fullStars = Math.floor(rating)
    const hasHalfStar = rating - fullStars >= 0.5
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0)
    
    return {
        full: fullStars,
        half: hasHalfStar ? 1 : 0,
        empty: emptyStars
    }
}
