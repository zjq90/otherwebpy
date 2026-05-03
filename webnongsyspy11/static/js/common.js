/**
 * 农资管理系统通用JavaScript工具
 */

const API_BASE = '';

function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast ${type} show`;
    toast.innerHTML = `
        <div class="toast-body d-flex align-items-center">
            <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-exclamation-triangle'} mr-2"></i>
            ${message}
        </div>
    `;
    
    document.getElementById('toastContainer').appendChild(toast);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

async function apiRequest(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(API_BASE + url, options);
        
        if (response.ok) {
            const result = await response.json();
            return { success: true, data: result };
        } else {
            const error = await response.json().catch(() => ({ detail: '请求失败' }));
            return { success: false, error: error.detail || '请求失败' };
        }
    } catch (error) {
        return { success: false, error: error.message };
    }
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN');
}

function formatDateTime(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('zh-CN');
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined) return '-';
    return '¥' + parseFloat(amount).toFixed(2);
}

function serializeForm(form) {
    const formData = new FormData(form);
    const data = {};
    for (const [key, value] of formData.entries()) {
        if (value !== '') {
            if (['quantity', 'unit_price', 'area', 'growth_cycle', 'warning_threshold'].includes(key)) {
                data[key] = parseFloat(value);
            } else {
                data[key] = value;
            }
        }
    }
    return data;
}

function confirmDelete(message = '确定要删除吗？') {
    return new Promise((resolve) => {
        const result = confirm(message);
        resolve(result);
    });
}

function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
}

function getTomorrowDate() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
}

function generateBatchNo(prefix = 'B') {
    const now = new Date();
    const dateStr = now.getFullYear().toString() + 
                   (now.getMonth() + 1).toString().padStart(2, '0') +
                   now.getDate().toString().padStart(2, '0');
    const random = Math.floor(Math.random() * 10000).toString().padStart(4, '0');
    return prefix + dateStr + random;
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        $(modal).modal('show');
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        $(modal).modal('hide');
    }
}

function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
    }
}

function fillForm(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    for (const [key, value] of Object.entries(data)) {
        const input = form.querySelector(`[name="${key}"]`);
        if (input) {
            if (input.type === 'date' && value) {
                input.value = value.split('T')[0];
            } else if (input.type === 'checkbox') {
                input.checked = value;
            } else {
                input.value = value;
            }
        }
    }
}

function populateSelect(selectId, options, valueKey = 'id', textKey = 'name') {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    const currentValue = select.value;
    select.innerHTML = '<option value="">请选择</option>';
    
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option[valueKey];
        opt.textContent = option[textKey];
        select.appendChild(opt);
    });
    
    if (currentValue) {
        select.value = currentValue;
    }
}

async function loadDataAndPopulateSelect(url, selectId, valueKey = 'id', textKey = 'name') {
    const result = await apiRequest(url);
    if (result.success) {
        populateSelect(selectId, result.data, valueKey, textKey);
    }
}

function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return parseFloat(num).toFixed(decimals);
}

function getStatusBadge(quantity, threshold) {
    if (quantity <= 0) {
        return '<span class="badge badge-danger">已售罄</span>';
    } else if (quantity <= threshold) {
        return '<span class="badge badge-warning">库存不足</span>';
    }
    return '<span class="badge badge-success">正常</span>';
}

function showLoading(buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) {
        const originalText = btn.innerHTML;
        btn.dataset.originalText = originalText;
        btn.innerHTML = '<span class="loading-spinner mr-2"></span>处理中...';
        btn.disabled = true;
    }
}

function hideLoading(buttonId) {
    const btn = document.getElementById(buttonId);
    if (btn) {
        btn.innerHTML = btn.dataset.originalText || btn.innerHTML;
        btn.disabled = false;
    }
}

const Validators = {
    required: function(value, message = '此字段为必填项') {
        if (value === null || value === undefined || value === '' || (Array.isArray(value) && value.length === 0)) {
            return message;
        }
        return null;
    },

    minLength: function(value, min, message) {
        if (value && value.length < min) {
            return message || `最少需要 ${min} 个字符`;
        }
        return null;
    },

    maxLength: function(value, max, message) {
        if (value && value.length > max) {
            return message || `最多允许 ${max} 个字符`;
        }
        return null;
    },

    minValue: function(value, min, message) {
        const num = parseFloat(value);
        if (!isNaN(num) && num < min) {
            return message || `值不能小于 ${min}`;
        }
        return null;
    },

    maxValue: function(value, max, message) {
        const num = parseFloat(value);
        if (!isNaN(num) && num > max) {
            return message || `值不能大于 ${max}`;
        }
        return null;
    },

    positive: function(value, message = '值必须大于0') {
        const num = parseFloat(value);
        if (!isNaN(num) && num <= 0) {
            return message;
        }
        return null;
    },

    phone: function(value, message = '请输入有效的手机号码或固定电话号码') {
        if (value && !/^1[3-9]\d{9}$|^0\d{2,3}-?\d{7,8}$/.test(value)) {
            return message;
        }
        return null;
    },

    dateNotAfterToday: function(value, message = '日期不能晚于今天') {
        if (value) {
            const inputDate = new Date(value);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            if (inputDate > today) {
                return message;
            }
        }
        return null;
    },

    dateAfter: function(value, compareDate, message) {
        if (value && compareDate) {
            const inputDate = new Date(value);
            const compare = new Date(compareDate);
            if (inputDate < compare) {
                return message || `日期必须晚于 ${compareDate}`;
            }
        }
        return null;
    }
};

function validateField(validators, value) {
    for (const validator of validators) {
        const error = validator(value);
        if (error) {
            return error;
        }
    }
    return null;
}

function showFieldError(input, message) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.classList.add('has-error');
        let helpBlock = formGroup.querySelector('.help-block, .text-danger');
        if (!helpBlock) {
            helpBlock = document.createElement('small');
            helpBlock.className = 'form-text text-danger';
            input.parentNode.appendChild(helpBlock);
        }
        helpBlock.textContent = message;
        input.classList.add('is-invalid');
    }
}

function clearFieldError(input) {
    const formGroup = input.closest('.form-group');
    if (formGroup) {
        formGroup.classList.remove('has-error');
        const helpBlock = formGroup.querySelector('.help-block, .text-danger');
        if (helpBlock && helpBlock !== input) {
            helpBlock.textContent = '';
        }
        input.classList.remove('is-invalid');
    }
}

function validateForm(formId, rules) {
    const form = document.getElementById(formId);
    if (!form) return { valid: true, errors: {} };

    let valid = true;
    const errors = {};

    for (const [fieldName, fieldRules] of Object.entries(rules)) {
        const input = form.querySelector(`[name="${fieldName}"]`);
        if (!input) continue;

        clearFieldError(input);

        const value = input.type === 'checkbox' ? input.checked : input.value;
        const error = validateField(fieldRules, value);
        
        if (error) {
            valid = false;
            errors[fieldName] = error;
            showFieldError(input, error);
        }
    }

    return { valid, errors };
}

function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const result = {};
    for (const [key, value] of params.entries()) {
        result[key] = value;
    }
    return result;
}

function buildUrlWithParams(baseUrl, params) {
    const url = new URL(baseUrl, window.location.origin);
    for (const [key, value] of Object.entries(params)) {
        if (value !== null && value !== undefined && value !== '') {
            url.searchParams.set(key, value);
        }
    }
    return url.toString();
}

function renderPagination(containerId, pagination, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container || !pagination || pagination.total_pages <= 1) {
        if (container) container.innerHTML = '';
        return;
    }

    const { page, total_pages, has_prev, has_next, start_index, end_index, total } = pagination;
    
    let html = `
        <div class="row align-items-center">
            <div class="col-md-6">
                <span class="text-muted">
                    显示 <strong>${start_index}</strong> - <strong>${end_index}</strong> 条，共 <strong>${total}</strong> 条记录
                </span>
            </div>
            <div class="col-md-6 text-right">
                <nav>
                    <ul class="pagination justify-content-end mb-0">
    `;

    if (has_prev) {
        html += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="${page - 1}" aria-label="上一页">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
        `;
    } else {
        html += `
            <li class="page-item disabled">
                <span class="page-link" aria-label="上一页">
                    <span aria-hidden="true">&laquo;</span>
                </span>
            </li>
        `;
    }

    const startPage = Math.max(1, page - 2);
    const endPage = Math.min(total_pages, page + 2);

    if (startPage > 1) {
        html += `<li class="page-item"><a class="page-link" href="#" data-page="1">1</a></li>`;
        if (startPage > 2) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        if (i === page) {
            html += `<li class="page-item active"><span class="page-link">${i}</span></li>`;
        } else {
            html += `<li class="page-item"><a class="page-link" href="#" data-page="${i}">${i}</a></li>`;
        }
    }

    if (endPage < total_pages) {
        if (endPage < total_pages - 1) {
            html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
        }
        html += `<li class="page-item"><a class="page-link" href="#" data-page="${total_pages}">${total_pages}</a></li>`;
    }

    if (has_next) {
        html += `
            <li class="page-item">
                <a class="page-link" href="#" data-page="${page + 1}" aria-label="下一页">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
        `;
    } else {
        html += `
            <li class="page-item disabled">
                <span class="page-link" aria-label="下一页">
                    <span aria-hidden="true">&raquo;</span>
                </span>
            </li>
        `;
    }

    html += `
                    </ul>
                </nav>
            </div>
        </div>
    `;

    container.innerHTML = html;

    container.querySelectorAll('.page-link[data-page]').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const pageNum = parseInt(this.dataset.page);
            if (onPageChange && pageNum >= 1) {
                onPageChange(pageNum);
            }
        });
    });
}

function goToPage(page, extraParams = {}) {
    const params = getUrlParams();
    params.page = page;
    Object.assign(params, extraParams);
    window.location.search = new URLSearchParams(params).toString();
}

function initPagination(containerId, pagination) {
    renderPagination(containerId, pagination, (page) => {
        goToPage(page);
    });
}
