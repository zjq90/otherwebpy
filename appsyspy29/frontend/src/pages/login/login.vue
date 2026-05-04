<template>
  <view class="login-container">
    <view class="logo-section">
      <view class="logo">🏋️</view>
      <text class="app-name">健身管理</text>
      <text class="app-slogan">记录每一次进步</text>
    </view>
    
    <view class="form-section">
      <view class="form-item">
        <input 
          class="form-input" 
          type="text" 
          placeholder="请输入用户名" 
          v-model="formData.username"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <input 
          class="form-input" 
          type="password" 
          placeholder="请输入密码" 
          v-model="formData.password"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="btn-section">
        <button 
          class="login-btn btn-primary" 
          :disabled="loading"
          @click="handleLogin"
        >
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </view>
      
      <view class="register-link">
        <text class="register-text" @click="goToRegister">
          还没有账号？<text class="highlight">立即注册</text>
        </text>
      </view>
    </view>
    
    <view class="test-account">
      <text class="test-title">测试账号：</text>
      <text class="test-info">用户名: testuser1 / 密码: 123456</text>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      formData: {
        username: '',
        password: ''
      },
      loading: false
    }
  },
  methods: {
    async handleLogin() {
      // 表单验证
      if (!this.formData.username.trim()) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.password.trim()) {
        uni.showToast({
          title: '请输入密码',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        const res = await api.userApi.login(this.formData)
        
        // 保存登录信息
        uni.setStorageSync('token', res.access_token)
        uni.setStorageSync('userInfo', res.user)
        
        uni.showToast({
          title: '登录成功',
          icon: 'success'
        })
        
        // 跳转到首页
        setTimeout(() => {
          uni.switchTab({
            url: '/pages/index/index'
          })
        }, 1000)
        
      } catch (error) {
        uni.showToast({
          title: error.message || '登录失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    goToRegister() {
      uni.navigateTo({
        url: '/pages/register/register'
      })
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #409EFF 0%, #66b1ff 50%, #f5f5f5 50%);
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

.logo {
  font-size: 120rpx;
  margin-bottom: 30rpx;
}

.app-name {
  font-size: 48rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 16rpx;
}

.app-slogan {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.form-section {
  background-color: #fff;
  border-radius: 24rpx;
  padding: 50rpx 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.form-item {
  margin-bottom: 30rpx;
}

.form-input {
  width: 100%;
  height: 96rpx;
  padding: 0 30rpx;
  background-color: #f5f7fa;
  border-radius: 16rpx;
  font-size: 30rpx;
  color: #333;
  box-sizing: border-box;
}

.placeholder-text {
  color: #909399;
}

.btn-section {
  margin-top: 40rpx;
}

.login-btn {
  width: 100%;
  height: 96rpx;
  line-height: 96rpx;
  border-radius: 16rpx;
  font-size: 32rpx;
  font-weight: 500;
}

.register-link {
  display: flex;
  justify-content: center;
  margin-top: 40rpx;
}

.register-text {
  font-size: 28rpx;
  color: #606266;
}

.highlight {
  color: #409EFF;
  font-weight: 500;
}

.test-account {
  margin-top: 60rpx;
  padding: 20rpx;
  background-color: rgba(64, 158, 255, 0.1);
  border-radius: 16rpx;
}

.test-title {
  font-size: 26rpx;
  color: #409EFF;
  font-weight: 500;
  display: block;
  margin-bottom: 10rpx;
}

.test-info {
  font-size: 24rpx;
  color: #606266;
}
</style>
