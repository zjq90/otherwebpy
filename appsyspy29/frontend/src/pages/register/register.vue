<template>
  <view class="register-container">
    <view class="header-section">
      <text class="title">注册账号</text>
      <text class="subtitle">创建您的健身管理账号</text>
    </view>
    
    <view class="form-section">
      <view class="form-item">
        <text class="form-label">用户名</text>
        <input 
          class="form-input" 
          type="text" 
          placeholder="请输入用户名（至少2个字符）" 
          v-model="formData.username"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">昵称</text>
        <input 
          class="form-input" 
          type="text" 
          placeholder="请输入昵称" 
          v-model="formData.nickname"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">密码</text>
        <input 
          class="form-input" 
          type="password" 
          placeholder="请输入密码（至少6个字符）" 
          v-model="formData.password"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">确认密码</text>
        <input 
          class="form-input" 
          type="password" 
          placeholder="请再次输入密码" 
          v-model="confirmPassword"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">手机号</text>
        <input 
          class="form-input" 
          type="number" 
          placeholder="请输入手机号（可选）" 
          v-model="formData.phone"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">邮箱</text>
        <input 
          class="form-input" 
          type="text" 
          placeholder="请输入邮箱（可选）" 
          v-model="formData.email"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">性别</text>
        <view class="gender-options">
          <view 
            class="gender-option" 
            :class="{ active: formData.gender === 'male' }"
            @click="selectGender('male')"
          >
            <text class="gender-icon">👨</text>
            <text class="gender-text">男</text>
          </view>
          <view 
            class="gender-option" 
            :class="{ active: formData.gender === 'female' }"
            @click="selectGender('female')"
          >
            <text class="gender-icon">👩</text>
            <text class="gender-text">女</text>
          </view>
        </view>
      </view>
      
      <view class="btn-section">
        <button 
          class="register-btn btn-primary" 
          :disabled="loading"
          @click="handleRegister"
        >
          {{ loading ? '注册中...' : '注 册' }}
        </button>
      </view>
      
      <view class="login-link">
        <text class="login-text" @click="goToLogin">
          已有账号？<text class="highlight">立即登录</text>
        </text>
      </view>
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
        nickname: '',
        password: '',
        phone: '',
        email: '',
        gender: ''
      },
      confirmPassword: '',
      loading: false
    }
  },
  methods: {
    selectGender(gender) {
      this.formData.gender = gender
    },
    
    async handleRegister() {
      // 表单验证
      if (!this.formData.username.trim()) {
        uni.showToast({
          title: '请输入用户名',
          icon: 'none'
        })
        return
      }
      
      if (this.formData.username.length < 2) {
        uni.showToast({
          title: '用户名至少2个字符',
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
      
      if (this.formData.password.length < 6) {
        uni.showToast({
          title: '密码至少6个字符',
          icon: 'none'
        })
        return
      }
      
      if (this.formData.password !== this.confirmPassword) {
        uni.showToast({
          title: '两次密码输入不一致',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        const res = await api.userApi.register(this.formData)
        
        uni.showToast({
          title: '注册成功',
          icon: 'success'
        })
        
        // 自动登录
        const loginRes = await api.userApi.login({
          username: this.formData.username,
          password: this.formData.password
        })
        
        uni.setStorageSync('token', loginRes.access_token)
        uni.setStorageSync('userInfo', loginRes.user)
        
        setTimeout(() => {
          uni.switchTab({
            url: '/pages/index/index'
          })
        }, 1000)
        
      } catch (error) {
        uni.showToast({
          title: error.message || '注册失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    goToLogin() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 40rpx;
}

.header-section {
  padding: 60rpx 40rpx 40rpx;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.title {
  font-size: 44rpx;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.form-section {
  background-color: #fff;
  margin: 30rpx;
  border-radius: 24rpx;
  padding: 40rpx 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  font-size: 28rpx;
  color: #606266;
  display: block;
  margin-bottom: 16rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.placeholder-text {
  color: #c0c4cc;
}

.gender-options {
  display: flex;
  gap: 30rpx;
}

.gender-option {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30rpx;
  background-color: #f5f7fa;
  border-radius: 16rpx;
  border: 2rpx solid transparent;
}

.gender-option.active {
  background-color: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.gender-icon {
  font-size: 48rpx;
  margin-bottom: 10rpx;
}

.gender-text {
  font-size: 26rpx;
  color: #606266;
}

.gender-option.active .gender-text {
  color: #409EFF;
  font-weight: 500;
}

.btn-section {
  margin-top: 40rpx;
}

.register-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.login-link {
  display: flex;
  justify-content: center;
  margin-top: 30rpx;
}

.login-text {
  font-size: 26rpx;
  color: #606266;
}

.highlight {
  color: #409EFF;
  font-weight: 500;
}
</style>
