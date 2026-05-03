/**
 * 认证工具模块
 * 提供用户认证相关的工具函数，包括token管理、用户信息存储、登录状态检查等
 */

/**
 * 设置认证token
 * @param {string} token - JWT令牌
 */
function setAuthToken(token) {
    localStorage.setItem('auth_token', token);
}

/**
 * 获取认证token
 * @returns {string|null} 返回存储的token，如果不存在则返回null
 */
function getAuthToken() {
    return localStorage.getItem('auth_token');
}

/**
 * 移除认证token
 */
function removeAuthToken() {
    localStorage.removeItem('auth_token');
}

/**
 * 设置当前用户信息
 * @param {object} user - 用户信息对象
 */
function setCurrentUser(user) {
    localStorage.setItem('current_user', JSON.stringify(user));
}

/**
 * 获取当前用户信息
 * @returns {object|null} 返回用户信息对象，如果不存在则返回null
 */
function getCurrentUser() {
    const userStr = localStorage.getItem('current_user');
    if (userStr) {
        try {
            return JSON.parse(userStr);
        } catch (e) {
            return null;
        }
    }
    return null;
}

/**
 * 移除当前用户信息
 */
function removeCurrentUser() {
    localStorage.removeItem('current_user');
}

/**
 * 检查是否已登录
 * @returns {boolean} 返回是否已登录
 */
function isLoggedIn() {
    const token = getAuthToken();
    const user = getCurrentUser();
    return !!(token && user);
}

/**
 * 检查是否为管理员
 * @returns {boolean} 返回是否为管理员
 */
function isAdmin() {
    const user = getCurrentUser();
    return user && user.role === 'admin';
}

/**
 * 退出登录
 * 清除本地存储的token和用户信息，并重定向到登录页面
 */
function logout() {
    removeAuthToken();
    removeCurrentUser();
    
    if (confirm('确定要退出登录吗？')) {
        window.location.href = '/login';
    }
}

/**
 * 解析JWT token
 * @param {string} token - JWT令牌
 * @returns {object|null} 返回解析后的payload，如果解析失败则返回null
 */
function parseJwt(token) {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    } catch (e) {
        return null;
    }
}

/**
 * 检查token是否过期
 * @returns {boolean} 返回token是否过期
 */
function isTokenExpired() {
    const token = getAuthToken();
    if (!token) {
        return true;
    }
    
    const payload = parseJwt(token);
    if (!payload || !payload.exp) {
        return true;
    }
    
    const now = Date.now() / 1000;
    return payload.exp < now;
}

/**
 * 获取剩余过期时间（秒）
 * @returns {number} 返回剩余秒数，如果没有token或已过期则返回0
 */
function getTokenExpiresIn() {
    const token = getAuthToken();
    if (!token) {
        return 0;
    }
    
    const payload = parseJwt(token);
    if (!payload || !payload.exp) {
        return 0;
    }
    
    const now = Date.now() / 1000;
    const remaining = payload.exp - now;
    
    return remaining > 0 ? Math.floor(remaining) : 0;
}

/**
 * 检查并刷新token（如果即将过期）
 * 当token剩余时间小于5分钟时，提示用户重新登录
 */
function checkTokenExpiration() {
    const expiresIn = getTokenExpiresIn();
    
    if (expiresIn > 0 && expiresIn < 300) {
        console.warn(`Token将在${expiresIn}秒后过期，请重新登录`);
    }
    
    if (expiresIn === 0 && isLoggedIn()) {
        removeAuthToken();
        removeCurrentUser();
        alert('登录已过期，请重新登录');
        window.location.href = '/login';
    }
}

/**
 * 格式化日期
 * @param {string|Date} date - 日期字符串或Date对象
 * @param {string} format - 格式化方式，默认为'YYYY-MM-DD'
 * @returns {string} 返回格式化后的日期字符串
 */
function formatDate(date, format = 'YYYY-MM-DD') {
    if (!date) return '-';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '-';
    
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    const hours = String(d.getHours()).padStart(2, '0');
    const minutes = String(d.getMinutes()).padStart(2, '0');
    const seconds = String(d.getSeconds()).padStart(2, '0');
    
    let result = format;
    result = result.replace('YYYY', year);
    result = result.replace('MM', month);
    result = result.replace('DD', day);
    result = result.replace('HH', hours);
    result = result.replace('mm', minutes);
    result = result.replace('ss', seconds);
    
    return result;
}

/**
 * 获取状态文本
 * @param {string} status - 状态值
 * @returns {string} 返回状态文本
 */
function getStatusText(status) {
    const statusMap = {
        'pending': '待确认',
        'confirmed': '已确认',
        'paid': '已支付押金',
        'picked_up': '已领取',
        'returned': '已归还',
        'completed': '已完成',
        'cancelled': '已取消'
    };
    return statusMap[status] || status;
}

/**
 * 获取状态徽章HTML
 * @param {string} status - 状态值
 * @returns {string} 返回状态徽章的HTML字符串
 */
function getStatusBadge(status) {
    const badgeClassMap = {
        'pending': 'bg-warning',
        'confirmed': 'bg-info',
        'paid': 'bg-primary',
        'picked_up': 'bg-secondary',
        'returned': 'bg-secondary',
        'completed': 'bg-success',
        'cancelled': 'bg-danger'
    };
    
    const badgeClass = badgeClassMap[status] || 'bg-secondary';
    const statusText = getStatusText(status);
    
    return `<span class="badge ${badgeClass}">${statusText}</span>`;
}

/**
 * 显示消息提示
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型：success, error, warning, info
 */
function showMessage(message, type = 'info') {
    const toastEl = document.getElementById('toast');
    if (!toastEl) {
        alert(message);
        return;
    }
    
    const toast = new bootstrap.Toast(toastEl);
    const toastTitle = document.getElementById('toastTitle');
    const toastBody = document.getElementById('toastBody');
    
    const typeMap = {
        'success': { title: '成功', class: 'text-success' },
        'error': { title: '错误', class: 'text-danger' },
        'warning': { title: '警告', class: 'text-warning' },
        'info': { title: '提示', class: 'text-primary' }
    };
    
    const config = typeMap[type] || typeMap['info'];
    
    toastTitle.textContent = config.title;
    toastTitle.className = `me-auto ${config.class}`;
    toastBody.textContent = message;
    
    toast.show();
}

/**
 * 显示加载状态
 * @param {HTMLElement} element - 要显示加载状态的元素
 * @param {string} text - 加载提示文本
 */
function showLoading(element, text = '加载中...') {
    if (element) {
        const originalContent = element.innerHTML;
        element.dataset.originalContent = originalContent;
        element.innerHTML = `
            <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
            ${text}
        `;
        element.disabled = true;
    }
}

/**
 * 隐藏加载状态，恢复原始内容
 * @param {HTMLElement} element - 要隐藏加载状态的元素
 */
function hideLoading(element) {
    if (element && element.dataset.originalContent) {
        element.innerHTML = element.dataset.originalContent;
        element.disabled = false;
    }
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @returns {Function} 返回防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 时间限制（毫秒）
 * @returns {Function} 返回节流后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 页面加载完成后的自动检查
 * 检查token是否过期
 */
document.addEventListener('DOMContentLoaded', function() {
    if (isLoggedIn()) {
        checkTokenExpiration();
    }
});

/**
 * 定时检查token过期状态
 * 每分钟检查一次
 */
setInterval(function() {
    if (isLoggedIn()) {
        checkTokenExpiration();
    }
}, 60000);
