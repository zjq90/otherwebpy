/**
 * API配置模块
 * 管理API基础配置和环境变量
 */

const config = {
	// API基础地址 - 根据实际环境修改
	baseURL: 'http://192.168.1.100:8000/api', // 局域网访问，替换为实际IP
	// baseURL: 'http://localhost:8000/api', // 本地调试
	
	// 超时时间（毫秒）
	timeout: 30000,
	
	// Token前缀
	tokenPrefix: 'Bearer'
}

// 根据运行环境动态配置
// #ifdef H5
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
	config.baseURL = 'http://localhost:8000/api'
}
// #endif

export default config
