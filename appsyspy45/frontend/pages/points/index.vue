<template>
  <view class="page">
    <view class="header-section">
      <view class="user-info">
        <image :src="userInfo.avatar || '/static/images/default-avatar.png'" class="user-avatar"></image>
        <view class="user-texts">
          <text class="user-name">{{ userInfo.nickname || '用户' }}</text>
          <text class="user-phone">{{ maskPhone(userInfo.phone) }}</text>
        </view>
      </view>
      
      <view class="points-card">
        <view class="points-title">积分余额</view>
        <view class="points-value">{{ pointsBalance }}</view>
        <view class="points-unit">积分</view>
      </view>
    </view>
    
    <view class="stats-section">
      <view class="stats-grid">
        <view class="stat-item" @click="goHistory">
          <text class="stat-value">{{ stats.total_earned || 0 }}</text>
          <text class="stat-label">累计获得</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.total_spent || 0 }}</text>
          <text class="stat-label">已使用</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.order_count || 0 }}</text>
          <text class="stat-label">回收次数</text>
        </view>
        <view class="stat-item" @click="goInvite">
          <text class="stat-value">{{ stats.invite_count || 0 }}</text>
          <text class="stat-label">邀请好友</text>
        </view>
      </view>
    </view>
    
    <view class="menu-section">
      <view class="menu-header">
        <text class="menu-title">常用功能</text>
      </view>
      <view class="menu-list">
        <view class="menu-item" @click="goHistory">
          <view class="menu-icon">📊</view>
          <text class="menu-text">积分明细</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goMall">
          <view class="menu-icon">🛍️</view>
          <text class="menu-text">积分商城</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goExchangeOrders">
          <view class="menu-icon">📦</view>
          <text class="menu-text">兑换订单</text>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goInvite">
          <view class="menu-icon">🎉</view>
          <text class="menu-text">邀请好友</text>
          <text class="menu-arrow">›</text>
        </view>
      </view>
    </view>
    
    <view class="points-rules">
      <view class="rules-header">
        <text class="rules-title">积分获取规则</text>
      </view>
      <view class="rules-content">
        <view class="rule-item">
          <text class="rule-icon">👕</text>
          <view class="rule-info">
            <text class="rule-name">旧衣回收</text>
            <text class="rule-desc">根据衣物类型和数量获得积分</text>
          </view>
          <text class="rule-points">10-100积分/件</text>
        </view>
        <view class="rule-item">
          <text class="rule-icon">🎉</text>
          <view class="rule-info">
            <text class="rule-name">邀请好友</text>
            <text class="rule-desc">邀请好友注册并完成回收</text>
          </view>
          <text class="rule-points">+100积分</text>
        </view>
        <view class="rule-item">
          <text class="rule-icon">🎁</text>
          <view class="rule-info">
            <text class="rule-name">新用户奖励</text>
            <text class="rule-desc">新用户注册即送积分</text>
          </view>
          <text class="rule-points">+50积分</text>
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
      userInfo: {},
      pointsBalance: 0,
      stats: {}
    }
  },
  
  onShow() {
    this.loadData()
  },
  
  methods: {
    maskPhone(phone) {
      return utils.maskPhone(phone)
    },
    
    async loadData() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      await Promise.all([
        this.loadPointsBalance(),
        this.loadStats()
      ])
    },
    
    async loadPointsBalance() {
      try {
        const res = await api.get('/points/balance')
        if (res.code === 200) {
          this.pointsBalance = res.data.balance || 0
        }
      } catch (e) {
        console.error('加载积分余额失败:', e)
      }
    },
    
    async loadStats() {
      try {
        const res = await api.get('/points/statistics')
        if (res.code === 200) {
          this.stats = res.data
        }
      } catch (e) {
        console.error('加载积分统计失败:', e)
      }
    },
    
    goHistory() {
      uni.navigateTo({
        url: '/pages/points/history'
      })
    },
    
    goMall() {
      uni.switchTab({
        url: '/pages/mall/index'
      })
    },
    
    goExchangeOrders() {
      uni.navigateTo({
        url: '/pages/mall/orders'
      })
    },
    
    goInvite() {
      uni.navigateTo({
        url: '/pages/points/invite'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
}

.header-section {
  background: linear-gradient(135deg, $primary-color, #66BB6A);
  padding: 40rpx;
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.user-avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  border: 4rpx solid rgba($white, 0.3);
}

.user-texts {
  flex: 1;
}

.user-name {
  font-size: $font-size-lg;
  font-weight: bold;
  color: $white;
}

.user-phone {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-top: 6rpx;
  display: block;
}

.points-card {
  background-color: rgba($white, 0.2);
  border-radius: $border-radius-lg;
  padding: 30rpx;
  display: flex;
  align-items: baseline;
}

.points-title {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-right: 20rpx;
}

.points-value {
  font-size: 48rpx;
  font-weight: bold;
  color: $white;
}

.points-unit {
  font-size: $font-size-base;
  color: rgba($white, 0.8);
  margin-left: 10rpx;
}

.stats-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-lg;
  padding: 30rpx 0;
}

.stats-grid {
  display: flex;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1rpx solid $border-color;
  
  &:last-child {
    border-right: none;
  }
}

.stat-value {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $primary-color;
}

.stat-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 10rpx;
}

.menu-section,
.points-rules {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-lg;
  padding: 0 30rpx;
}

.menu-header,
.rules-header {
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
}

.menu-title,
.rules-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.menu-list {
  padding: 10rpx 0;
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

.rules-content {
  padding: 20rpx 0;
}

.rule-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.rule-icon {
  font-size: 48rpx;
  margin-right: 20rpx;
}

.rule-info {
  flex: 1;
}

.rule-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.rule-desc {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 6rpx;
  display: block;
}

.rule-points {
  font-size: $font-size-base;
  color: $primary-color;
  font-weight: bold;
}
</style>
