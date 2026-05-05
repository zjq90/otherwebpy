<template>
  <view class="login-container">
    <!-- 顶部背景 -->
    <view class="login-bg">
      <view class="bg-circle bg-circle-1"></view>
      <view class="bg-circle bg-circle-2"></view>
    </view>
    
    <!-- Logo和标题 -->
    <view class="login-header">
      <view class="logo">
        <text class="logo-text">运</text>
      </view>
      <text class="app-title">运输管理系统</text>
      <text class="app-subtitle">Transport Management System</text>
    </view>
    
    <!-- 登录表单 -->
    <view class="login-form">
      <view class="form-item">
        <view class="input-wrapper">
          <text class="input-icon">👤</text>
          <input 
            class="input-field" 
            v-model="username" 
            placeholder="请输入用户名" 
            placeholder-class="placeholder"
            :disabled="loading"
          />
        </view>
      </view>
      
      <view class="form-item">
        <view class="input-wrapper">
          <text class="input-icon">🔒</text>
          <input 
            class="input-field" 
            v-model="password" 
            type="password" 
            placeholder="请输入密码" 
            placeholder-class="placeholder"
            :disabled="loading"
            @confirm="handleLogin"
          />
          <view class="password-toggle" @click="showPassword = !showPassword">
            <text>{{ showPassword ? '🙈' : '👁️' }}</text>
          </view>
        </view>
      </view>
      
      <!-- 登录按钮 -->
      <view class="form-item">
        <button 
          class="login-btn" 
          :class="{ 'btn-disabled': loading }"
          @click="handleLogin"
          :loading="loading"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </view>
      
      <!-- 快速登录提示 -->
      <view class="quick-login">
        <text class="quick-title">测试账号：</text>
        <view class="quick-list">
          <view class="quick-item" @click="quickLogin('admin', '123456')">
            <text class="quick-role">管理员</text>
            <text class="quick-account">admin/123456</text>
          </view>
          <view class="quick-item" @click="quickLogin('dispatcher1', '123456')">
            <text class="quick-role">调度员</text>
            <text class="quick-account">dispatcher1/123456</text>
          </view>
          <view class="quick-item" @click="quickLogin('driver1', '123456')">
            <text class="quick-role">司机</text>
            <text class="quick-account">driver1/123456</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 底部版权 -->
    <view class="login-footer">
      <text class="copyright">Version 1.0.0</text>
    </view>
  </view>
</template>

<script>
import config from '@/utils/config.js'
import { http } from '@/utils/http.js'

export default {
  data() {
    return {
      username: '',
      password: '',
      showPassword: false,
      loading: false
    }
  },
  
  onLoad() {
    // 页面加载时检查是否已登录
    const token = uni.getStorageSync(config.tokenKey)
    const userInfo = uni.getStorageSync(config.userInfoKey)
    
    if (token && userInfo) {
      uni.switchTab({
        url: '/pages/index/index'
      })
    }
  },
  
  methods: {
    // 快速登录
    quickLogin(username, password) {
      this.username = username
      this.password = password
    },
    
    // 处理登录
    async handleLogin() {
      // 表单验证
      if (!this.username.trim()) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        })
        return
      }
      
      if (!this.password.trim()) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        // 构建form-data格式的请求体
        // OAuth2密码模式需要使用application/x-www-form-urlencoded格式
        const formData = `username=${encodeURIComponent(this.username)}&password=${encodeURIComponent(this.password)}`
        
        // 调用登录接口
        const res = await uni.request({
          url: config.baseUrl + '/api/auth/login',
          method: 'POST',
          header: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          data: formData
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          // 保存Token
          uni.setStorageSync(config.tokenKey, res[1].data.data.access_token)
          
          // 获取用户信息
          const userRes = await uni.request({
            url: config.baseUrl + '/api/auth/me',
            method: 'GET',
            header: {
              'Authorization': `Bearer ${res[1].data.data.access_token}`
            }
          })
          
          if (userRes[1].statusCode === 200 && userRes[1].data.code === 200) {
            uni.setStorageSync(config.userInfoKey, userRes[1].data.data)
            
            uni.showToast({
              title: '登录成功',
              icon: 'success'
            })
            
            // 延迟跳转
            setTimeout(() => {
              uni.switchTab({
                url: '/pages/index/index'
              })
            }, 1000)
          }
        } else {
          uni.showToast({
            title: res[1].data?.message || '登录失败',
            icon: 'none'
          })
        }
      } catch (error) {
        console.error('登录失败:', error)
        uni.showToast({
          title: '网络错误，请稍后重试',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #409EFF 0%, #66b1ff 100%);
  position: relative;
  overflow: hidden;
  padding: 40rpx;
  display: flex;
  flex-direction: column;
}

/* 背景装饰 */
.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  z-index: 0;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.bg-circle-1 {
  width: 600rpx;
  height: 600rpx;
  top: -200rpx;
  right: -100rpx;
}

.bg-circle-2 {
  width: 400rpx;
  height: 400rpx;
  bottom: -100rpx;
  left: -100rpx;
}

/* 头部 */
.login-header {
  position: relative;
  z-index: 1;
  text-align: center;
  padding-top: 100rpx;
  padding-bottom: 80rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  background: #FFFFFF;
  border-radius: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 30rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.2);
}

.logo-text {
  font-size: 80rpx;
  font-weight: bold;
  color: #409EFF;
}

.app-title {
  font-size: 48rpx;
  font-weight: bold;
  color: #FFFFFF;
  display: block;
  margin-bottom: 10rpx;
}

.app-subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

/* 登录表单 */
.login-form {
  position: relative;
  z-index: 1;
  background: #FFFFFF;
  border-radius: 24rpx;
  padding: 50rpx 40rpx;
  box-shadow: 0 10rpx 40rpx rgba(0, 0, 0, 0.15);
}

.form-item {
  margin-bottom: 30rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background: #F5F7FA;
  border-radius: 12rpx;
  padding: 0 30rpx;
  height: 96rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: #409EFF;
  background: #FFFFFF;
}

.input-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
}

.input-field {
  flex: 1;
  height: 100%;
  font-size: 32rpx;
  color: #303133;
}

.placeholder {
  color: #909399;
}

.password-toggle {
  padding: 10rpx;
  font-size: 36rpx;
}

/* 登录按钮 */
.login-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(90deg, #409EFF 0%, #66b1ff 100%);
  border: none;
  border-radius: 12rpx;
  color: #FFFFFF;
  font-size: 36rpx;
  font-weight: bold;
  box-shadow: 0 6rpx 20rpx rgba(64, 158, 255, 0.4);
}

.login-btn::after {
  border: none;
}

.btn-disabled {
  opacity: 0.7;
}

/* 快速登录 */
.quick-login {
  margin-top: 40rpx;
  padding-top: 30rpx;
  border-top: 1rpx solid #EBEEF5;
}

.quick-title {
  font-size: 26rpx;
  color: #909399;
  display: block;
  margin-bottom: 20rpx;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.quick-item {
  flex: 1;
  min-width: 200rpx;
  background: #F5F7FA;
  border-radius: 12rpx;
  padding: 20rpx;
  text-align: center;
}

.quick-role {
  display: block;
  font-size: 28rpx;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8rpx;
}

.quick-account {
  font-size: 22rpx;
  color: #909399;
}

/* 底部版权 */
.login-footer {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 40rpx 0;
  margin-top: auto;
}

.copyright {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.6);
}
</style>
