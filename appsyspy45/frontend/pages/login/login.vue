<template>
  <view class="page">
    <view class="logo-section">
      <image class="logo" src="/static/images/logo.png"></image>
      <text class="app-name">旧衣回收</text>
      <text class="app-slogan">让旧衣焕发新生</text>
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
      </view>
      
      <view class="input-group">
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
      </view>
      
      <view class="tips">
        <text>登录即表示同意</text>
        <text class="link">《用户协议》</text>
        <text>和</text>
        <text class="link">《隐私政策》</text>
      </view>
      
      <view class="btn-group">
        <view class="btn btn-primary" @click="handleLogin">登录</view>
      </view>
      
      <view class="other-actions">
        <text class="action-item" @click="goRegister">注册账号</text>
        <text class="action-item" @click="goForgotPassword">忘记密码</text>
      </view>
      
      <view class="divider-line">
        <view class="line"></view>
        <text class="text">其他登录方式</text>
        <view class="line"></view>
      </view>
      
      <view class="third-party-login">
        <view class="third-item" @click="thirdPartyLogin('wechat')">
          <view class="third-icon wechat">微信</view>
          <text class="third-name">微信登录</text>
        </view>
        <view class="third-item" @click="thirdPartyLogin('alipay')">
          <view class="third-icon alipay">支付宝</view>
          <text class="third-name">支付宝登录</text>
        </view>
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
        password: ''
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
          type: 'login'
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
    
    async handleLogin() {
      if (!this.form.phone) {
        utils.showToast('请输入手机号')
        return
      }
      
      if (!utils.validatePhone(this.form.phone)) {
        utils.showToast('请输入正确的手机号')
        return
      }
      
      if (!this.form.code && !this.form.password) {
        utils.showToast('请输入验证码或密码')
        return
      }
      
      utils.showLoading('登录中...')
      
      try {
        let loginData
        if (this.form.code) {
          loginData = {
            phone: this.form.phone,
            sms_code: this.form.code,
            login_type: 'sms'
          }
        } else {
          loginData = {
            phone: this.form.phone,
            password: this.form.password,
            login_type: 'password'
          }
        }
        
        const res = await api.post('/user/login', loginData)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          const { access_token, user } = res.data
          
          const app = getApp()
          app.globalData.hasLogin = true
          app.globalData.userInfo = user
          
          uni.setStorageSync('token', access_token)
          uni.setStorageSync('userInfo', user)
          
          utils.showToast('登录成功')
          
          setTimeout(() => {
            uni.switchTab({
              url: '/pages/index/index'
            })
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('登录失败:', e)
      }
    },
    
    async thirdPartyLogin(platform) {
      utils.showLoading('登录中...')
      
      try {
        const res = await api.post('/user/third-party-login', {
          platform: platform,
          open_id: `mock_${platform}_${Date.now()}`,
          nickname: `${platform}用户`,
          avatar: ''
        })
        
        utils.hideLoading()
        
        if (res.code === 200) {
          const { access_token, user } = res.data
          
          const app = getApp()
          app.globalData.hasLogin = true
          app.globalData.userInfo = user
          
          uni.setStorageSync('token', access_token)
          uni.setStorageSync('userInfo', user)
          
          utils.showToast('登录成功')
          
          setTimeout(() => {
            uni.switchTab({
              url: '/pages/index/index'
            })
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('第三方登录失败:', e)
      }
    },
    
    goRegister() {
      uni.navigateTo({
        url: '/pages/register/register'
      })
    },
    
    goForgotPassword() {
      uni.navigateTo({
        url: '/pages/forgot-password/forgot-password'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background: linear-gradient(180deg, #E8F5E9 0%, $white 100%);
  padding: 60rpx 40rpx;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}

.logo {
  width: 160rpx;
  height: 160rpx;
  border-radius: 40rpx;
}

.app-name {
  font-size: $font-size-xxl;
  font-weight: bold;
  color: $primary-color;
  margin-top: 30rpx;
}

.app-slogan {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 10rpx;
}

.form-section {
  padding: 0 20rpx;
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

.other-actions {
  display: flex;
  justify-content: space-between;
  margin-bottom: 60rpx;
}

.action-item {
  font-size: $font-size-sm;
  color: $primary-color;
}

.divider-line {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.line {
  flex: 1;
  height: 1rpx;
  background-color: $border-color;
}

.text {
  padding: 0 30rpx;
  font-size: $font-size-sm;
  color: $text-muted;
}

.third-party-login {
  display: flex;
  justify-content: center;
  gap: 80rpx;
}

.third-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.third-icon {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-sm;
  color: $white;
  margin-bottom: 16rpx;
}

.wechat {
  background-color: #07C160;
}

.alipay {
  background-color: #1677FF;
}

.third-name {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.eye-icon {
  padding: 10rpx;
  font-size: $font-size-base;
}
</style>
