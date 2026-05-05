<template>
  <view class="login-container">
    <view class="login-header">
      <view class="logo">
        <text class="logo-text">衣回收</text>
      </view>
      <text class="slogan">旧衣物回收 · 环保先行</text>
    </view>
    
    <view class="login-form">
      <view class="form-item">
        <text class="form-label">用户名</text>
        <input 
          class="form-input" 
          v-model="formData.username" 
          placeholder="请输入用户名"
          placeholder-class="input-placeholder"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">密码</text>
        <input 
          class="form-input" 
          v-model="formData.password" 
          type="password"
          placeholder="请输入密码"
          placeholder-class="input-placeholder"
        />
      </view>
      
      <button 
        class="login-btn" 
        :loading="loading"
        @click="handleLogin"
      >
        {{ loading ? '登录中...' : '登录' }}
      </button>
      
      <view class="register-link">
        <text class="link-text" @click="goToRegister">还没有账号？立即注册</text>
      </view>
    </view>
    
    <view class="test-hint">
      <text class="hint-text">测试账号：collector1 / 123456</text>
    </view>
  </view>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue'
import { login, saveLoginInfo } from '@/api/auth'

export default defineComponent({
  setup() {
    const loading = ref(false)
    
    const formData = reactive({
      username: 'collector1',
      password: '123456'
    })
    
    const handleLogin = async () => {
      if (!formData.username.trim()) {
        uni.showToast({ title: '请输入用户名', icon: 'none' })
        return
      }
      if (!formData.password.trim()) {
        uni.showToast({ title: '请输入密码', icon: 'none' })
        return
      }
      
      loading.value = true
      try {
        const result = await login({
          username: formData.username,
          password: formData.password
        })
        saveLoginInfo(result)
        uni.showToast({ title: '登录成功', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/orders/orders' })
        }, 1000)
      } catch (error) {
        console.error('登录失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const goToRegister = () => {
      uni.navigateTo({ url: '/pages/register/register' })
    }
    
    return {
      loading,
      formData,
      handleLogin,
      goToRegister
    }
  }
})
</script>

<style lang="scss" scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #2979ff 0%, #e3f2fd 100%);
  padding: 0 40rpx;
  display: flex;
  flex-direction: column;
}

.login-header {
  padding-top: 160rpx;
  text-align: center;
  margin-bottom: 80rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  background: #ffffff;
  border-radius: 50%;
  margin: 0 auto 30rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(41, 121, 255, 0.3);
}

.logo-text {
  font-size: 40rpx;
  font-weight: bold;
  color: #2979ff;
}

.slogan {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.85);
}

.login-form {
  background: #ffffff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.08);
}

.form-item {
  margin-bottom: 40rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #303133;
  margin-bottom: 16rpx;
  font-weight: 500;
}

.form-input {
  width: 100%;
  height: 88rpx;
  background: #f5f7fa;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
  color: #303133;
}

.input-placeholder {
  color: #c0c4cc;
}

.login-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(90deg, #2979ff 0%, #1976d2 100%);
  border-radius: 44rpx;
  color: #ffffff;
  font-size: 32rpx;
  font-weight: 500;
  border: none;
  margin-top: 20rpx;
}

.register-link {
  text-align: center;
  margin-top: 40rpx;
}

.link-text {
  font-size: 26rpx;
  color: #2979ff;
}

.test-hint {
  text-align: center;
  margin-top: 60rpx;
}

.hint-text {
  font-size: 24rpx;
  color: rgba(0, 0, 0, 0.5);
}
</style>
