<template>
  <view class="login-container">
    <view class="logo-section">
      <view class="logo-icon">
        <text class="logo-text">砼</text>
      </view>
      <text class="app-title">混凝土质量追溯系统</text>
      <text class="app-subtitle">精准追溯 · 质量保障</text>
    </view>
    
    <view class="form-section">
      <view class="form-item">
        <text class="form-label">用户名</text>
        <input 
          class="form-input" 
          type="text" 
          placeholder="请输入用户名" 
          v-model="loginForm.username"
          placeholder-class="input-placeholder"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">密码</text>
        <input 
          class="form-input" 
          :type="showPassword ? 'text' : 'password'" 
          placeholder="请输入密码" 
          v-model="loginForm.password"
          placeholder-class="input-placeholder"
        />
        <text class="toggle-password" @click="showPassword = !showPassword">
          {{ showPassword ? '隐藏' : '显示' }}
        </text>
      </view>
      
      <view class="login-btn" @click="handleLogin">
        <text class="btn-text">登 录</text>
      </view>
      
      <view class="demo-info">
        <text class="demo-title">测试账号：</text>
        <view class="demo-account">
          <text class="account-item">管理员: admin / admin123</text>
          <text class="account-item">检验员: inspector / 123456</text>
        </view>
      </view>
    </view>
    
    <view class="footer-section">
      <text class="copyright">© 2026 混凝土质量追溯系统 v1.0.0</text>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      loginForm: {
        username: '',
        password: ''
      },
      showPassword: false
    }
  },
  methods: {
    async handleLogin() {
      // 表单验证
      if (!this.loginForm.username.trim()) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        })
        return
      }
      
      if (!this.loginForm.password) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        })
        return
      }
      
      try {
        // 调用登录API
        const res = await request.post('/api/auth/login', {}, {
          header: {
            'Content-Type': 'application/x-www-form-urlencoded'
          },
          data: {
            username: this.loginForm.username,
            password: this.loginForm.password
          }
        })
        
        // 保存token和用户信息
        uni.setStorageSync('token', res.data.access_token)
        uni.setStorageSync('userInfo', res.data.user)
        
        uni.showToast({
          title: '登录成功',
          icon: 'success',
          duration: 1500
        })
        
        // 延迟跳转
        setTimeout(() => {
          uni.switchTab({
            url: '/pages/index/index'
          })
        }, 1500)
        
      } catch (err) {
        console.error('登录失败:', err)
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #1E88E5 0%, #0D47A1 100%);
  display: flex;
  flex-direction: column;
  padding: 0 40rpx;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 120rpx;
  padding-bottom: 80rpx;
}

.logo-icon {
  width: 160rpx;
  height: 160rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32rpx;
}

.logo-text {
  font-size: 80rpx;
  font-weight: bold;
  color: #fff;
}

.app-title {
  font-size: 40rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 16rpx;
}

.app-subtitle {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.form-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 48rpx 32rpx;
  margin-bottom: 40rpx;
}

.form-item {
  margin-bottom: 32rpx;
  position: relative;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #666;
  margin-bottom: 16rpx;
}

.form-input {
  width: 100%;
  height: 96rpx;
  background: #f8f9fa;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 30rpx;
  color: #333;
  box-sizing: border-box;
}

.input-placeholder {
  color: #999;
}

.toggle-password {
  position: absolute;
  right: 24rpx;
  bottom: 32rpx;
  font-size: 26rpx;
  color: #1E88E5;
}

.login-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 24rpx;
}

.btn-text {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
}

.demo-info {
  margin-top: 40rpx;
  padding: 24rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
}

.demo-title {
  font-size: 26rpx;
  color: #666;
  margin-bottom: 12rpx;
}

.demo-account {
  display: flex;
  flex-direction: column;
}

.account-item {
  font-size: 24rpx;
  color: #999;
  line-height: 1.6;
}

.footer-section {
  margin-top: auto;
  padding-bottom: 40rpx;
  display: flex;
  justify-content: center;
}

.copyright {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.6);
}
</style>
