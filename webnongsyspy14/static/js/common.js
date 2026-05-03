const API_BASE = '';

function showToast(message, title = '提示', type = 'success') {
    const toast = $('#toast');
    const toastTitle = $('#toastTitle');
    const toastBody = $('#toastBody');
    
    toastTitle.text(title);
    toastBody.text(message);
    
    toast.addClass(type === 'success' ? 'bg-success text-white' : 'bg-danger text-white');
    toast.toast('show');
    
    setTimeout(() => {
        toast.removeClass('bg-success bg-danger text-white');
    }, 3500);
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
}

function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '-';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('zh-CN');
}

function formatMoney(amount) {
    if (amount === null || amount === undefined) return '-';
    return '¥' + parseFloat(amount).toFixed(2);
}

function getShippingStatusBadge(status) {
    const statusMap = {
        'pending': { text: '待发货', class: 'badge-warning' },
        'shipped': { text: '已发货', class: 'badge-info' },
        'delivered': { text: '已送达', class: 'badge-success' }
    };
    const s = statusMap[status] || { text: status, class: 'badge-secondary' };
    return `<span class="badge ${s.class}">${s.text}</span>`;
}

function getContractStatusBadge(status) {
    const statusMap = {
        'draft': { text: '草稿', class: 'badge-secondary' },
        'signed': { text: '已签署', class: 'badge-success' },
        'cancelled': { text: '已取消', class: 'badge-danger' }
    };
    const s = statusMap[status] || { text: status, class: 'badge-secondary' };
    return `<span class="badge ${s.class}">${s.text}</span>`;
}

function getFeedbackStatusBadge(status) {
    const statusMap = {
        'pending': { text: '待处理', class: 'badge-warning' },
        'processing': { text: '处理中', class: 'badge-info' },
        'resolved': { text: '已解决', class: 'badge-success' }
    };
    const s = statusMap[status] || { text: status, class: 'badge-secondary' };
    return `<span class="badge ${s.class}">${s.text}</span>`;
}

function getFeedbackTypeText(type) {
    const typeMap = {
        'suggestion': '建议',
        'complaint': '投诉',
        'praise': '表扬'
    };
    return typeMap[type] || type;
}

function confirmDelete(callback, message = '确定要删除吗？') {
    if (confirm(message)) {
        callback();
    }
}

function buildQueryString(params) {
    return Object.keys(params)
        .filter(key => params[key] !== null && params[key] !== undefined && params[key] !== '')
        .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
        .join('&');
}

async function apiGet(url, params = {}) {
    const queryString = buildQueryString(params);
    const fullUrl = queryString ? `${API_BASE}${url}?${queryString}` : `${API_BASE}${url}`;
    try {
        const response = await fetch(fullUrl);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        return await response.json();
    } catch (error) {
        console.error('API GET Error:', error);
        throw error;
    }
}

async function apiPost(url, data) {
    try {
        const response = await fetch(`${API_BASE}${url}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        return await response.json();
    } catch (error) {
        console.error('API POST Error:', error);
        throw error;
    }
}

async function apiPut(url, data) {
    try {
        const response = await fetch(`${API_BASE}${url}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        return await response.json();
    } catch (error) {
        console.error('API PUT Error:', error);
        throw error;
    }
}

async function apiDelete(url) {
    try {
        const response = await fetch(`${API_BASE}${url}`, {
            method: 'DELETE'
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || '请求失败');
        }
        return await response.json();
    } catch (error) {
        console.error('API DELETE Error:', error);
        throw error;
    }
}

$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip();
    
    if ($('.loading-spinner').length) {
        $('.loading-spinner').addClass('show');
    }
});
