<template>
  <view class="page">
    <view class="header-desc">
      <text class="title">找回密码</text>
      <text class="subtitle">通过手机号验证重置密码</text>
    </view>
    
    <view class="form-section">
      <view class="input-group">
        <view class="input-item">
          <text class="label">手机号</text>
          <input 
            v-model="form.phone" 
            type="number" 
            placeholder="请输入手机号" 
            maxlength="11"
          />
        </view>
        <view class="input-item">
          <text class="label">验证码</text>
          <input 
            v-model="form.code" 
            type="number" 
            placeholder="请输入验证码" 
            maxlength="6"
          />
          <view 
            class="code-btn" 
            :class="{ disabled: isCounting }" 
            @click="sendCode"
          >
            {{ countDownText }}
          </view>
        </view>
        <view class="input-item">
          <text class="label">新密码</text>
          <input 
            v-model="form.newPassword" 
            :type="showPassword ? 'text' : 'password'" 
            placeholder="请输入6-20位新密码"
          />
          <text class="eye-icon" @click="showPassword = !showPassword">
            {{ showPassword ? '👁️' : '🙈' }}
          </text>
        </view>
        <view class="input-item">
          <text class="label">确认密码</text>
          <input 
            v-model="form.confirmPassword" 
            :type="showPassword ? 'text' : 'password'" 
            placeholder="请再次输入新密码"
          />
        </view>
      </view>
      
      <view class="btn-group">
        <view class="btn btn-primary" @click="handleReset">重置密码</view>
      </view>
      
      <view class="go-login">
        <text>想起密码了？</text>
        <text class="link" @click="goLogin">返回登录</text>
      </view>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

export default {
  data() {
    return {
      form: {
        phone: '',
        code: '',
        newPassword: '',
        confirmPassword: ''
      },
      showPassword: false,
      isCounting: false,
      countDown: 60,
      countDownTimer: null
    }
  },
  
  computed: {
    countDownText() {
      if (this.isCounting) {
        return `${this.countDown}s`
      }
      return '获取验证码'
    }
  },
  
  onUnload() {
    if (this.countDownTimer) {
      clearInterval(this.countDownTimer)
    }
  },
  
  methods: {
    async sendCode() {
      if (this.isCounting) return
      
      if (!this.form.phone) {
        utils.showToast('请输入手机号')
        return
      }
      
      if (!utils.validatePhone(this.form.phone)) {
        utils.showToast('请输入正确的手机号')
        return
      }
      
      try {
        const res = await api.post('/user/send-sms', {
          phone: this.form.phone,
          type: 'reset'
        })
        
        if (res.code === 200) {
          utils.showToast('验证码已发送')
          this.startCountDown()
        }
      } catch (e) {
        console.error('发送验证码失败:', e)
      }
    },
    
    startCountDown() {
      this.isCounting = true
      this.countDown = 60
      
      this.countDownTimer = setInterval(() => {
        this.countDown--
        if (this.countDown <= 0) {
          this.isCounting = false
          clearInterval(this.countDownTimer)
        }
      }, 1000)
    },
    
    async handleReset() {
      if (!this.form.phone) {
        utils.showToast('请输入手机号')
        return
      }
      
      if (!utils.validatePhone(this.form.phone)) {
        utils.showToast('请输入正确的手机号')
        return
      }
      
      if (!this.form.code) {
        utils.showToast('请输入验证码')
        return
      }
      
      if (!this.form.newPassword) {
        utils.showToast('请输入新密码')
        return
      }
      
      if (!utils.validatePassword(this.form.newPassword)) {
        utils.showToast('密码长度为6-20位')
        return
      }
      
      if (this.form.newPassword !== this.form.confirmPassword) {
        utils.showToast('两次密码输入不一致')
        return
      }
      
      utils.showLoading('重置中...')
      
      try {
        const res = await api.post('/user/reset-password', {
          phone: this.form.phone,
          sms_code: this.form.code,
          new_password: this.form.newPassword
        })
        
        utils.hideLoading()
        
        if (res.code === 200) {
          utils.showToast('密码重置成功')
          
          setTimeout(() => {
            uni.navigateTo({
              url: '/pages/login/login'
            })
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('重置密码失败:', e)
      }
    },
    
    goLogin() {
      uni.navigateBack()
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding: 40rpx;
}

.header-desc {
  padding: 40rpx 0;
}

.title {
  font-size: $font-size-xxl;
  font-weight: bold;
  color: $text-color;
}

.subtitle {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 16rpx;
  display: block;
}

.form-section {
  padding: 20rpx 0;
}

.btn-group {
  margin-bottom: 40rpx;
}

.go-login {
  text-align: center;
  font-size: $font-size-sm;
  color: $text-secondary;
}

.link {
  color: $primary-color;
}

.eye-icon {
  padding: 10rpx;
  font-size: $font-size-base;
}
</style>
