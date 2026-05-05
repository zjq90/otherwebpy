<template>
  <view class="page">
    <view class="header-desc">
      <text class="title">注册账号</text>
      <text class="subtitle">注册成为会员，享受积分奖励</text>
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
          <text class="label">昵称</text>
          <input 
            v-model="form.nickname" 
            type="text" 
            placeholder="请输入昵称（选填）"
            maxlength="20"
          />
        </view>
        <view class="input-item">
          <text class="label">密码</text>
          <input 
            v-model="form.password" 
            :type="showPassword ? 'text' : 'password'" 
            placeholder="请输入6-20位密码"
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
            placeholder="请再次输入密码"
          />
        </view>
        <view class="input-item">
          <text class="label">邀请码</text>
          <input 
            v-model="form.inviteCode" 
            type="text" 
            placeholder="有邀请码？请输入（选填）"
            maxlength="20"
          />
        </view>
      </view>
      
      <view class="tips">
        <text>注册即表示同意</text>
        <text class="link">《用户协议》</text>
        <text>和</text>
        <text class="link">《隐私政策》</text>
      </view>
      
      <view class="btn-group">
        <view class="btn btn-primary" @click="handleRegister">注册</view>
      </view>
      
      <view class="go-login">
        <text>已有账号？</text>
        <text class="link" @click="goLogin">立即登录</text>
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
        nickname: '',
        password: '',
        confirmPassword: '',
        inviteCode: ''
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
          type: 'register'
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
    
    async handleRegister() {
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
      
      if (!this.form.password) {
        utils.showToast('请输入密码')
        return
      }
      
      if (!utils.validatePassword(this.form.password)) {
        utils.showToast('密码长度为6-20位')
        return
      }
      
      if (this.form.password !== this.form.confirmPassword) {
        utils.showToast('两次密码输入不一致')
        return
      }
      
      utils.showLoading('注册中...')
      
      try {
        const registerData = {
          phone: this.form.phone,
          sms_code: this.form.code,
          password: this.form.password
        }
        
        if (this.form.nickname) {
          registerData.nickname = this.form.nickname
        }
        
        if (this.form.inviteCode) {
          registerData.invite_code = this.form.inviteCode
        }
        
        const res = await api.post('/user/register', registerData)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          const { access_token, user } = res.data
          
          const app = getApp()
          app.globalData.hasLogin = true
          app.globalData.userInfo = user
          
          uni.setStorageSync('token', access_token)
          uni.setStorageSync('userInfo', user)
          
          utils.showToast('注册成功')
          
          setTimeout(() => {
            uni.switchTab({
              url: '/pages/index/index'
            })
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('注册失败:', e)
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

.tips {
  font-size: $font-size-xs;
  color: $text-secondary;
  text-align: center;
  margin-bottom: 40rpx;
}

.link {
  color: $primary-color;
}

.btn-group {
  margin-bottom: 40rpx;
}

.go-login {
  text-align: center;
  font-size: $font-size-sm;
  color: $text-secondary;
}

.eye-icon {
  padding: 10rpx;
  font-size: $font-size-base;
}
</style>
