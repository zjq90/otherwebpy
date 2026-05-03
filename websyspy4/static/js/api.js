/**
 * API请求封装模块
 * 提供统一的HTTP请求处理，包含认证token的自动添加
 */

// API基础URL
const API_BASE_URL = '';

/**
 * API请求类
 * 封装了GET、POST、PUT、DELETE等HTTP方法
 */
const api = {
    /**
     * 发送GET请求
     * @param {string} url - 请求URL
     * @param {object} params - 查询参数
     * @returns {Promise} 返回响应数据
     */
    async get(url, params = {}) {
        const queryString = new URLSearchParams(params).toString();
        const fullUrl = queryString ? `${API_BASE_URL}${url}?${queryString}` : `${API_BASE_URL}${url}`;
        
        const response = await fetch(fullUrl, {
            method: 'GET',
            headers: this.getHeaders()
        });
        
        return this.handleResponse(response);
    },

    /**
     * 发送POST请求
     * @param {string} url - 请求URL
     * @param {object} data - 请求体数据
     * @returns {Promise} 返回响应数据
     */
    async post(url, data = {}) {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        
        return this.handleResponse(response);
    },

    /**
     * 发送PUT请求
     * @param {string} url - 请求URL
     * @param {object} data - 请求体数据
     * @returns {Promise} 返回响应数据
     */
    async put(url, data = {}) {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(data)
        });
        
        return this.handleResponse(response);
    },

    /**
     * 发送DELETE请求
     * @param {string} url - 请求URL
     * @returns {Promise} 返回响应数据
     */
    async delete(url) {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'DELETE',
            headers: this.getHeaders()
        });
        
        return this.handleResponse(response);
    },

    /**
     * 获取请求头
     * 自动添加Content-Type和Authorization（如果有token）
     * @returns {object} 请求头对象
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = localStorage.getItem('auth_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    },

    /**
     * 处理响应
     * 统一处理响应状态和错误
     * @param {Response} response - fetch响应对象
     * @returns {Promise} 返回解析后的响应数据，格式为 { data: ... }
     * @throws {Error} 当响应不是2xx状态码时抛出错误
     */
    async handleResponse(response) {
        const data = await response.json().catch(() => null);
        
        if (!response.ok) {
            const error = new Error(data?.detail || response.statusText || '请求失败');
            error.response = { data, status: response.status };
            throw error;
        }
        
        return { data: data };
    },

    /**
     * 文件上传
     * @param {string} url - 上传URL
     * @param {FormData} formData - 表单数据
     * @returns {Promise} 返回响应数据
     */
    async upload(url, formData) {
        const headers = {};
        const token = localStorage.getItem('auth_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'POST',
            headers: headers,
            body: formData
        });
        
        return this.handleResponse(response);
    },

    /**
     * 下载文件
     * @param {string} url - 下载URL
     * @param {string} filename - 下载的文件名
     */
    async download(url, filename) {
        const headers = {};
        const token = localStorage.getItem('auth_token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: 'GET',
            headers: headers
        });
        
        if (!response.ok) {
            throw new Error('下载失败');
        }
        
        const blob = await response.blob();
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);
    }
};
