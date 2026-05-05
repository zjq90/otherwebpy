/**
 * 应用配置文件
 * 包含API基础地址、超时时间等配置
 */

const config = {
    apiBaseUrl: 'http://localhost:8000/api/v1',
    timeout: 30000,
    tokenKey: 'token',
    userInfoKey: 'userInfo'
}

export default config
