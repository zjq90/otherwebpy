<template>
  <view class="login-container">
    <view class="login-header">
      <view class="logo">
        <text class="logo-icon">🏋️</text>
      </view>
      <text class="title">健身预约系统</text>
      <text class="subtitle">轻松预约，享受运动</text>
    </view>

    <view class="login-form">
      <view class="form-item">
        <text class="form-label">用户名/手机号</text>
        <input 
          class="form-input" 
          v-model="formData.username" 
          placeholder="请输入用户名或手机号"
          type="text"
        />
      </view>

      <view class="form-item">
        <text class="form-label">密码</text>
        <input 
          class="form-input" 
          v-model="formData.password" 
          placeholder="请输入密码"
          :password="!showPassword"
          @confirm="handleLogin"
        />
        <text class="toggle-password" @click="showPassword = !showPassword">
          {{ showPassword ? '🙈' : '👁️' }}
        </text>
      </view>

      <view class="test-accounts" v-if="showTestAccounts">
        <text class="test-title">测试账号：</text>
        <view class="account-item" v-for="(account, index) in testAccounts" :key="index">
          <text class="account-label">{{ account.role }}:</text>
          <text class="account-info" @click="fillAccount(account)">
            {{ account.username }} / {{ account.password }}
          </text>
        </view>
      </view>

      <view class="form-actions">
        <button 
          class="btn btn-primary btn-lg btn-block" 
          :loading="loading"
          @click="handleLogin"
        >
          登录
        </button>
      </view>

      <view class="register-link">
        <text>还没有账号？</text>
        <text class="link" @click="showRegister = true">立即注册</text>
      </view>
    </view>

    <view class="register-modal" v-if="showRegister" @click.self="showRegister = false">
      <view class="register-content">
        <view class="modal-header">
          <text class="modal-title">注册账号</text>
          <text class="modal-close" @click="showRegister = false">✕</text>
        </view>

        <view class="form-item">
          <text class="form-label">用户名</text>
          <input 
            class="form-input" 
            v-model="registerData.username" 
            placeholder="请输入用户名"
          />
        </view>

        <view class="form-item">
          <text class="form-label">真实姓名</text>
          <input 
            class="form-input" 
            v-model="registerData.name" 
            placeholder="请输入真实姓名"
          />
        </view>

        <view class="form-item">
          <text class="form-label">手机号</text>
          <input 
            class="form-input" 
            v-model="registerData.phone" 
            placeholder="请输入手机号"
            type="number"
          />
        </view>

        <view class="form-item">
          <text class="form-label">邮箱（选填）</text>
          <input 
            class="form-input" 
            v-model="registerData.email" 
            placeholder="请输入邮箱"
            type="text"
          />
        </view>

        <view class="form-item">
          <text class="form-label">密码</text>
          <input 
            class="form-input" 
            v-model="registerData.password" 
            placeholder="请输入密码（至少6位）"
            :password="!showRegisterPassword"
          />
        </view>

        <view class="form-actions">
          <button 
            class="btn btn-primary btn-lg btn-block" 
            :loading="registerLoading"
            @click="handleRegister"
          >
            注册
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { useUserStore } from '@/store/user'
import { showToast, showLoading, hideLoading } from '@/utils/utils'

export default {
  data() {
    return {
      formData: {
        username: '',
        password: ''
      },
      registerData: {
        username: '',
        name: '',
        phone: '',
        email: '',
        password: '',
        role: 'member'
      },
      showPassword: false,
      showRegisterPassword: false,
      loading: false,
      registerLoading: false,
      showRegister: false,
      showTestAccounts: true,
      testAccounts: [
        { role: '会员', username: 'member1', password: 'member123' },
        { role: '教练', username: 'coach1', password: 'coach123' },
        { role: '管理员', username: 'admin', password: 'admin123' }
      ]
    }
  },

  onLoad() {
    this.checkLoginStatus()
  },

  methods: {
    userStore() {
      return useUserStore()
    },

    async checkLoginStatus() {
      const token = uni.getStorageSync('token')
      if (token) {
        uni.switchTab({
          url: '/pages/tabbar/calendar/calendar'
        })
      }
    },

    fillAccount(account) {
      this.formData.username = account.username
      this.formData.password = account.password
    },

    async handleLogin() {
      if (!this.formData.username.trim()) {
        showToast('请输入用户名或手机号')
        return
      }
      if (!this.formData.password) {
        showToast('请输入密码')
        return
      }

      this.loading = true
      showLoading('登录中...')

      try {
        const result = await this.userStore().login(
          this.formData.username,
          this.formData.password
        )

        hideLoading()

        if (result.success) {
          showToast('登录成功', 'success')
          setTimeout(() => {
            uni.switchTab({
              url: '/pages/tabbar/calendar/calendar'
            })
          }, 1500)
        } else {
          showToast(result.message)
        }
      } catch (error) {
        hideLoading()
        console.error('登录失败:', error)
      } finally {
        this.loading = false
      }
    },

    async handleRegister() {
      if (!this.registerData.username.trim()) {
        showToast('请输入用户名')
        return
      }
      if (!this.registerData.name.trim()) {
        showToast('请输入真实姓名')
        return
      }
      if (!this.registerData.phone.trim()) {
        showToast('请输入手机号')
        return
      }
      if (!this.registerData.password || this.registerData.password.length < 6) {
        showToast('密码至少6位')
        return
      }

      this.registerLoading = true
      showLoading('注册中...')

      try {
        const result = await this.userStore().register(this.registerData)
        
        hideLoading()

        if (result.success) {
          showToast('注册成功', 'success')
          this.showRegister = false
          this.formData.username = this.registerData.username
        } else {
          showToast(result.message)
        }
      } catch (error) {
        hideLoading()
        console.error('注册失败:', error)
      } finally {
        this.registerLoading = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 40rpx;
}

.login-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 80rpx;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30rpx;
}

.logo-icon {
  font-size: 80rpx;
}

.title {
  font-size: 48rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 16rpx;
}

.subtitle {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.login-form {
  width: 100%;
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.form-item {
  position: relative;
  margin-bottom: 40rpx;
}

.form-label {
  display: block;
  font-size: 26rpx;
  color: #6b7280;
  margin-bottom: 16rpx;
}

.form-input {
  width: 100%;
  height: 96rpx;
  padding: 0 32rpx;
  background-color: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  font-size: 30rpx;
  color: #1f2937;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #2563eb;
  background-color: #ffffff;
}

.toggle-password {
  position: absolute;
  right: 32rpx;
  bottom: 28rpx;
  font-size: 40rpx;
}

.test-accounts {
  background-color: #f0f9ff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 40rpx;
}

.test-title {
  font-size: 24rpx;
  color: #1d4ed8;
  font-weight: 500;
  margin-bottom: 16rpx;
}

.account-item {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 10rpx;
}

.account-label {
  font-size: 24rpx;
  color: #6b7280;
  margin-right: 10rpx;
}

.account-info {
  font-size: 24rpx;
  color: #2563eb;
  text-decoration: underline;
}

.form-actions {
  margin-top: 20rpx;
}

.register-link {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 40rpx;
  font-size: 26rpx;
  color: #6b7280;
}

.link {
  color: #2563eb;
  margin-left: 10rpx;
}

.register-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 40rpx;
}

.register-content {
  width: 100%;
  max-width: 650rpx;
  background-color: #ffffff;
  border-radius: 24rpx;
  padding: 40rpx;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 40rpx;
}

.modal-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #1f2937;
}

.modal-close {
  font-size: 36rpx;
  color: #9ca3af;
}
</style>
