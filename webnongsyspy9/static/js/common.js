/**
 * 通用JavaScript工具函数
 * 为所有页面提供通用功能
 */

// API基础URL
const API_BASE = '/api';

/**
 * 通用API请求函数
 * @param {string} url - API端点
 * @param {Object} options - fetch选项
 * @returns {Promise} 返回数据或错误
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };
    
    try {
        const response = await fetch(url, defaultOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `请求失败: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API请求错误:', error);
        throw error;
    }
}

/**
 * 显示成功消息
 * @param {string} message - 消息内容
 */
function showSuccess(message) {
    // 创建消息元素
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <strong>成功!</strong> ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 3秒后自动关闭
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

/**
 * 显示错误消息
 * @param {string} message - 消息内容
 */
function showError(message) {
    // 创建消息元素
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <strong>错误!</strong> ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // 5秒后自动关闭
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * 显示确认对话框
 * @param {string} message - 确认消息
 * @returns {Promise<boolean>} 用户选择
 */
function showConfirm(message) {
    return new Promise((resolve) => {
        const result = confirm(message);
        resolve(result);
    });
}

/**
 * 格式化日期时间
 * @param {string} dateString - 日期字符串
 * @returns {string} 格式化后的日期
 */
function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * 格式化日期（仅日期）
 * @param {string} dateString - 日期字符串
 * @returns {string} 格式化后的日期
 */
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

/**
 * 初始化模态框
 * @param {string} modalId - 模态框ID
 * @param {Function} onShow - 显示时的回调
 * @param {Function} onHide - 隐藏时的回调
 */
function initModal(modalId, onShow = null, onHide = null) {
    const modal = document.getElementById(modalId);
    
    if (modal) {
        modal.addEventListener('show.bs.modal', () => {
            if (onShow) onShow();
        });
        
        modal.addEventListener('hide.bs.modal', () => {
            if (onHide) onHide();
            // 重置表单
            const form = modal.querySelector('form');
            if (form) form.reset();
        });
    }
}

/**
 * 加载选择框选项
 * @param {string} selectId - 选择框ID
 * @param {Array} options - 选项数组 [{value, text}]
 * @param {string} defaultText - 默认选项文本
 */
function loadSelectOptions(selectId, options, defaultText = '请选择') {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    // 清空现有选项
    select.innerHTML = '';
    
    // 添加默认选项
    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = defaultText;
    defaultOption.disabled = true;
    defaultOption.selected = true;
    select.appendChild(defaultOption);
    
    // 添加数据选项
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option.value;
        opt.textContent = option.text;
        select.appendChild(opt);
    });
}

/**
 * 设置页面加载状态
 * @param {boolean} loading - 是否加载中
 * @param {string} containerId - 容器ID
 */
function setLoading(loading, containerId = null) {
    const container = containerId ? document.getElementById(containerId) : document.body;
    if (!container) return;
    
    if (loading) {
        container.style.opacity = '0.5';
        container.style.pointerEvents = 'none';
    } else {
        container.style.opacity = '1';
        container.style.pointerEvents = 'auto';
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('页面加载完成');
    
    // 可以在这里添加全局初始化逻辑
});
