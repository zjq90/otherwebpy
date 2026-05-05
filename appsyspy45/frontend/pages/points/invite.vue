<template>
  <view class="page">
    <view class="header-section">
      <view class="header-bg">
        <view class="invite-title">邀请好友</view>
        <view class="invite-subtitle">分享邀请码，双方都得积分奖励</view>
      </view>
    </view>
    
    <view class="card-section">
      <view class="invite-card">
        <view class="card-header">
          <text class="card-title">我的邀请码</text>
        </view>
        <view class="card-body">
          <text class="invite-code">{{ inviteCode || '暂无' }}</text>
          <view class="copy-btn" @click="copyCode">复制邀请码</view>
        </view>
      </view>
      
      <view class="share-card">
        <view class="card-header">
          <text class="card-title">分享方式</text>
        </view>
        <view class="share-options">
          <view class="share-item" @click="shareToWechat">
            <view class="share-icon wechat">微信</view>
            <text class="share-name">微信好友</text>
          </view>
          <view class="share-item" @click="shareToMoments">
            <view class="share-icon moments">朋友圈</view>
            <text class="share-name">朋友圈</text>
          </view>
          <view class="share-item" @click="generatePoster">
            <view class="share-icon poster">海报</view>
            <text class="share-name">生成海报</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="rules-section">
      <view class="section-header">
        <text class="section-title">邀请奖励规则</text>
      </view>
      <view class="rules-list">
        <view class="rule-item">
          <view class="rule-number">1</view>
          <text class="rule-text">邀请好友注册成功，邀请者和被邀请者均可获得50积分奖励</text>
        </view>
        <view class="rule-item">
          <view class="rule-number">2</view>
          <text class="rule-text">被邀请者完成第一笔旧衣回收订单，邀请者再获得50积分奖励</text>
        </view>
        <view class="rule-item">
          <view class="rule-number">3</view>
          <text class="rule-text">邀请奖励不限次数，邀请越多，奖励越多</text>
        </view>
        <view class="rule-item">
          <view class="rule-number">4</view>
          <text class="rule-text">积分可在积分商城兑换商品或参与公益捐赠</text>
        </view>
      </view>
    </view>
    
    <view class="records-section" v-if="inviteRecords.length > 0">
      <view class="section-header">
        <text class="section-title">邀请记录</text>
      </view>
      <view class="records-list">
        <view class="record-item" v-for="(item, index) in inviteRecords" :key="index">
          <image :src="item.avatar || '/static/images/default-avatar.png'" class="record-avatar"></image>
          <view class="record-info">
            <text class="record-name">{{ item.nickname || '用户' }}</text>
            <text class="record-time">{{ formatTime(item.created_at) }}</text>
          </view>
          <view class="record-status" :class="{ completed: item.has_order }">
            {{ item.has_order ? '已下单' : '已注册' }}
          </view>
        </view>
      </view>
    </view>
    
    <view class="stats-section">
      <view class="stats-header">
        <text class="stats-title">邀请统计</text>
      </view>
      <view class="stats-grid">
        <view class="stats-item">
          <text class="stats-value">{{ inviteStats.total_invited || 0 }}</text>
          <text class="stats-label">已邀请</text>
        </view>
        <view class="stats-item">
          <text class="stats-value">{{ inviteStats.total_orders || 0 }}</text>
          <text class="stats-label">已下单</text>
        </view>
        <view class="stats-item">
          <text class="stats-value">{{ inviteStats.total_points || 0 }}</text>
          <text class="stats-label">获得积分</text>
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
      inviteCode: '',
      inviteRecords: [],
      inviteStats: {}
    }
  },
  
  onShow() {
    this.loadData()
  },
  
  methods: {
    formatTime(time) {
      return utils.formatDate(time)
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
      
      await Promise.all([
        this.loadInviteInfo(),
        this.loadInviteRecords(),
        this.loadInviteStats()
      ])
    },
    
    async loadInviteInfo() {
      try {
        const res = await api.get('/points/invite-info')
        if (res.code === 200) {
          this.inviteCode = res.data.invite_code || ''
        }
      } catch (e) {
        console.error('加载邀请信息失败:', e)
      }
    },
    
    async loadInviteRecords() {
      try {
        const res = await api.get('/points/invite-records', { page: 1, page_size: 10 })
        if (res.code === 200) {
          this.inviteRecords = res.data.list || []
        }
      } catch (e) {
        console.error('加载邀请记录失败:', e)
      }
    },
    
    async loadInviteStats() {
      try {
        const res = await api.get('/points/statistics')
        if (res.code === 200) {
          this.inviteStats = {
            total_invited: res.data.invite_count || 0,
            total_orders: res.data.invite_order_count || 0,
            total_points: res.data.invite_points || 0
          }
        }
      } catch (e) {
        console.error('加载邀请统计失败:', e)
      }
    },
    
    copyCode() {
      if (!this.inviteCode) {
        utils.showToast('暂无邀请码')
        return
      }
      
      uni.setClipboardData({
        data: this.inviteCode,
        success: () => {
          utils.showToast('复制成功')
        }
      })
    },
    
    shareToWechat() {
      utils.showToast('请点击右上角分享')
    },
    
    shareToMoments() {
      utils.showToast('请点击右上角分享')
    },
    
    generatePoster() {
      utils.showToast('功能开发中')
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
  padding: 0;
  position: relative;
}

.header-bg {
  padding: 60rpx 40rpx;
  padding-top: calc(60rpx + env(safe-area-inset-top));
  text-align: center;
}

.invite-title {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $white;
  margin-bottom: 16rpx;
}

.invite-subtitle {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
}

.card-section {
  padding: 0 20rpx;
  margin-top: -30rpx;
  position: relative;
  z-index: 10;
}

.invite-card,
.share-card {
  background-color: $white;
  border-radius: $border-radius-lg;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.card-header {
  margin-bottom: 20rpx;
}

.card-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.card-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.invite-code {
  font-size: 48rpx;
  font-weight: bold;
  color: $primary-color;
  letter-spacing: 8rpx;
}

.copy-btn {
  padding: 16rpx 40rpx;
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
  font-size: $font-size-sm;
  border-radius: 30rpx;
}

.share-options {
  display: flex;
  justify-content: center;
  gap: 60rpx;
}

.share-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.share-icon {
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

.moments {
  background-color: #2DBB57;
}

.poster {
  background-color: #FF9800;
}

.share-name {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.rules-section,
.records-section,
.stats-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-lg;
  padding: 0 30rpx;
}

.section-header,
.stats-header {
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
}

.section-title,
.stats-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.rules-list {
  padding: 20rpx 0;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  padding: 20rpx 0;
}

.rule-number {
  width: 40rpx;
  height: 40rpx;
  background-color: $primary-color;
  color: $white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-sm;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.rule-text {
  flex: 1;
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.8;
}

.records-list {
  padding: 10rpx 0;
}

.record-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.record-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: 20rpx;
}

.record-info {
  flex: 1;
}

.record-name {
  font-size: $font-size-base;
  color: $text-color;
}

.record-time {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 6rpx;
  display: block;
}

.record-status {
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
  font-size: $font-size-sm;
  background-color: $bg-color;
  color: $text-secondary;
  
  &.completed {
    background-color: rgba($success-color, 0.1);
    color: $success-color;
  }
}

.stats-grid {
  display: flex;
  padding: 30rpx 0;
}

.stats-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stats-value {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $primary-color;
}

.stats-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 10rpx;
}
</style>
