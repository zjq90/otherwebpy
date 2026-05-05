<template>
  <view class="page">
    <view class="header-section" v-if="hasLogin">
      <view class="user-info" @click="goProfile">
        <image :src="userInfo.avatar || '/static/images/default-avatar.png'" class="user-avatar"></image>
        <view class="user-texts">
          <text class="user-name">{{ userInfo.nickname || '用户' }}</text>
          <text class="user-phone">{{ maskPhone(userInfo.phone) }}</text>
        </view>
        <text class="user-arrow">›</text>
      </view>
      
      <view class="stats-row">
        <view class="stat-item" @click="goOrders">
          <text class="stat-value">{{ stats.order_count || 0 }}</text>
          <text class="stat-label">回收订单</text>
        </view>
        <view class="stat-item" @click="goPoints">
          <text class="stat-value">{{ stats.points_balance || 0 }}</text>
          <text class="stat-label">积分余额</text>
        </view>
        <view class="stat-item" @click="goStatistics">
          <text class="stat-value">{{ stats.carbon_saved || 0 }}kg</text>
          <text class="stat-label">减碳量</text>
        </view>
      </view>
    </view>
    
    <view class="header-section" v-else @click="goLogin">
      <view class="user-info">
        <view class="guest-avatar">
          <text class="guest-icon">👤</text>
        </view>
        <view class="user-texts">
          <text class="user-name">点击登录</text>
          <text class="guest-tip">登录后享受更多功能</text>
        </view>
      </view>
    </view>
    
    <view class="menu-section">
      <view class="menu-group">
        <view class="menu-item" @click="goOrders">
          <view class="menu-icon">📋</view>
          <text class="menu-text">我的订单</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goPoints">
          <view class="menu-icon">💰</view>
          <text class="menu-text">积分中心</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goExchangeOrders">
          <view class="menu-icon">📦</view>
          <text class="menu-text">兑换订单</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goAddress">
          <view class="menu-icon">📍</view>
          <text class="menu-text">收货地址</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
      
      <view class="menu-group">
        <view class="menu-item" @click="goArticles">
          <view class="menu-icon">📰</view>
          <text class="menu-text">环保资讯</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goChat">
          <view class="menu-icon">💬</view>
          <text class="menu-text">客服咨询</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goInvite">
          <view class="menu-icon">🎉</view>
          <text class="menu-text">邀请好友</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
      
      <view class="menu-group">
        <view class="menu-item" @click="goProfile">
          <view class="menu-icon">⚙️</view>
          <text class="menu-text">个人设置</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="showAbout">
          <view class="menu-icon">ℹ️</view>
          <text class="menu-text">关于我们</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>
    
    <view class="logout-section" v-if="hasLogin">
      <view class="logout-btn" @click="handleLogout">退出登录</view>
    </view>
    
    <view class="version-info">
      <text class="version-text">版本 1.0.0</text>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

export default {
  data() {
    return {
      hasLogin: false,
      userInfo: {},
      stats: {}
    }
  },
  
  onShow() {
    this.checkLogin()
    if (this.hasLogin) {
      this.loadUserInfo()
      this.loadUserStats()
    }
  },
  
  methods: {
    maskPhone(phone) {
      return utils.maskPhone(phone)
    },
    
    checkLogin() {
      const token = uni.getStorageSync('token')
      this.hasLogin = !!token
      
      const app = getApp()
      this.hasLogin = app.globalData.hasLogin
    },
    
    async loadUserInfo() {
      try {
        const res = await api.get('/user/profile')
        if (res.code === 200) {
          this.userInfo = res.data
          
          uni.setStorageSync('userInfo', res.data)
          const app = getApp()
          app.globalData.userInfo = res.data
        }
      } catch (e) {
        console.error('加载用户信息失败:', e)
      }
    },
    
    async loadUserStats() {
      try {
        const res = await api.get('/user/statistics')
        if (res.code === 200) {
          this.stats = res.data
        }
      } catch (e) {
        console.error('加载用户统计失败:', e)
      }
    },
    
    goLogin() {
      uni.navigateTo({
        url: '/pages/login/login'
      })
    },
    
    goProfile() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/user/profile'
      })
    },
    
    goOrders() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/order/list'
      })
    },
    
    goPoints() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/points/index'
      })
    },
    
    goExchangeOrders() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/mall/orders'
      })
    },
    
    goAddress() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/user/address'
      })
    },
    
    goStatistics() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/user/statistics'
      })
    },
    
    goArticles() {
      uni.switchTab({
        url: '/pages/article/list'
      })
    },
    
    goChat() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/chat/list'
      })
    },
    
    goInvite() {
      if (!this.checkLoginAndRedirect()) return
      
      uni.navigateTo({
        url: '/pages/points/invite'
      })
    },
    
    checkLoginAndRedirect() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return false
      }
      return true
    },
    
    showAbout() {
      utils.showModal(
        '旧衣回收App v1.0.0\n\n让旧衣焕发新生，为环保贡献力量。\n\n旧衣回收是一款专注于衣物回收的环保应用，通过上门回收、积分奖励等方式，鼓励用户积极参与环保行动。',
        '关于我们',
        false
      )
    },
    
    async handleLogout() {
      const confirmed = await utils.showModal('确定要退出登录吗？')
      if (!confirmed) return
      
      const app = getApp()
      app.globalData.hasLogin = false
      app.globalData.userInfo = null
      
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
      
      this.hasLogin = false
      this.userInfo = {}
      
      utils.showToast('已退出登录')
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding-bottom: 40rpx;
}

.header-section {
  background: linear-gradient(135deg, $primary-color, #66BB6A);
  padding: 40rpx;
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.user-avatar,
.guest-avatar {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  margin-right: 24rpx;
  border: 4rpx solid rgba($white, 0.3);
}

.guest-avatar {
  background-color: rgba($white, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.guest-icon {
  font-size: 48rpx;
}

.user-texts {
  flex: 1;
}

.user-name {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $white;
}

.user-phone {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-top: 10rpx;
  display: block;
}

.guest-tip {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-top: 10rpx;
  display: block;
}

.user-arrow {
  font-size: $font-size-lg;
  color: rgba($white, 0.6);
}

.stats-row {
  display: flex;
  background-color: rgba($white, 0.15);
  border-radius: $border-radius-lg;
  padding: 30rpx 0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1rpx solid rgba($white, 0.2);
  
  &:last-child {
    border-right: none;
  }
}

.stat-value {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $white;
}

.stat-label {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-top: 10rpx;
}

.menu-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-lg;
  overflow: hidden;
}

.menu-group {
  padding: 0 30rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.menu-icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.menu-text {
  flex: 1;
  font-size: $font-size-base;
  color: $text-color;
}

.menu-arrow {
  font-size: $font-size-lg;
  color: $text-muted;
}

.logout-section {
  padding: 40rpx 30rpx;
}

.logout-btn {
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  background-color: $white;
  color: $danger-color;
  font-size: $font-size-base;
  border-radius: $border-radius-lg;
}

.version-info {
  text-align: center;
  padding: 20rpx 0;
}

.version-text {
  font-size: $font-size-xs;
  color: $text-muted;
}
</style>
