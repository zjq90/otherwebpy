<template>
  <view class="page">
    <view class="status-header" v-if="order">
      <view class="status-main">
        <text class="status-icon">{{ getStatusIcon(order.status) }}</text>
        <view class="status-texts">
          <text class="status-title">{{ getStatusText(order.status) }}</text>
          <text class="status-subtitle">{{ getStatusSubtitle(order.status) }}</text>
        </view>
      </view>
    </view>
    
    <view class="map-section" v-if="order && order.status >= 2">
      <view class="map-placeholder">
        <text class="map-icon">🗺️</text>
        <text class="map-text">地图位置信息</text>
        <view class="location-info" v-if="order.collector_info">
          <view class="location-dot collector"></view>
          <text class="location-text">回收员位置</text>
        </view>
        <view class="location-info">
          <view class="location-dot user"></view>
          <text class="location-text">您的位置</text>
        </view>
      </view>
    </view>
    
    <scroll-view scroll-y class="scroll-content">
      <view class="collector-section" v-if="order && order.collector_info">
        <view class="section-header">
          <text class="section-title">回收员信息</text>
        </view>
        <view class="collector-card">
          <image :src="order.collector_info.avatar || '/static/images/default-avatar.png'" class="collector-avatar"></image>
          <view class="collector-info">
            <text class="collector-name">{{ order.collector_info.name }}</text>
            <view class="collector-rating">
              <text class="rating-text">评分：{{ order.collector_info.rating || '4.9' }}⭐</text>
              <text class="order-count">已完成 {{ order.collector_info.order_count || 0 }} 单</text>
            </view>
            <text class="collector-phone">{{ order.collector_info.phone }}</text>
          </view>
          <view class="collector-actions">
            <view class="action-btn" @click="callCollector">
              <text class="action-icon">📞</text>
            </view>
            <view class="action-btn" @click="sendMessage">
              <text class="action-icon">💬</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="progress-section" v-if="order && order.status_history">
        <view class="section-header">
          <text class="section-title">订单进度</text>
        </view>
        <view class="timeline">
          <view class="timeline-item" v-for="(item, index) in timelineList" :key="index">
            <view class="timeline-left">
              <view class="timeline-dot" :class="{ current: item.isCurrent, completed: item.isCompleted }">
                <text class="dot-icon" v-if="item.isCompleted">✓</text>
              </view>
              <view class="timeline-line" :class="{ completed: item.isCompleted }" v-if="index < timelineList.length - 1"></view>
            </view>
            <view class="timeline-right">
              <text class="timeline-title" :class="{ current: item.isCurrent }">{{ item.title }}</text>
              <text class="timeline-time" v-if="item.time">{{ item.time }}</text>
              <text class="timeline-desc" v-if="item.desc">{{ item.desc }}</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="order-section" v-if="order">
        <view class="section-header">
          <text class="section-title">订单信息</text>
        </view>
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">订单编号</text>
            <text class="info-value">{{ order.order_no }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">预约时间</text>
            <text class="info-value">{{ order.schedule_date }} {{ order.schedule_time }}</text>
          </view>
          <view class="info-item" v-if="order.items">
            <text class="info-label">回收衣物</text>
            <text class="info-value">共{{ order.total_quantity }}件</text>
          </view>
          <view class="info-item">
            <text class="info-label">预估积分</text>
            <text class="info-value highlight">{{ order.estimate_points }}积分</text>
          </view>
        </view>
      </view>
      
      <view class="address-section" v-if="order && order.address_info">
        <view class="section-header">
          <text class="section-title">回收地址</text>
        </view>
        <view class="address-card">
          <view class="address-header">
            <text class="name">{{ order.address_info.contact_name }}</text>
            <text class="phone">{{ order.address_info.contact_phone }}</text>
          </view>
          <text class="address-detail">
            {{ order.address_info.province }}{{ order.address_info.city }}{{ order.address_info.district }}{{ order.address_info.detail }}
          </text>
        </view>
      </view>
    </scroll-view>
    
    <view class="bottom-bar" v-if="order">
      <view class="bottom-actions" v-if="order.status === 2">
        <view class="action-btn contact" @click="callCollector">
          <text class="btn-icon">📞</text>
          <text class="btn-text">联系回收员</text>
        </view>
        <view class="action-btn primary" @click="sendMessage">
          <text class="btn-icon">💬</text>
          <text class="btn-text">发送消息</text>
        </view>
      </view>
      <view class="bottom-actions" v-else-if="order.status === 3">
        <view class="action-btn contact" @click="callCollector">
          <text class="btn-icon">📞</text>
          <text class="btn-text">联系回收员</text>
        </view>
        <view class="action-btn primary" @click="goMall">
          <text class="btn-text">去积分商城</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

const STATUS_MAP = {
  1: '待接单',
  2: '待上门',
  3: '回收中',
  4: '已完成',
  5: '已取消'
}

const STATUS_ICON_MAP = {
  1: '⏳',
  2: '🚚',
  3: '🔄',
  4: '✅',
  5: '❌'
}

export default {
  data() {
    return {
      orderId: null,
      order: null,
      loading: false,
      timelineList: []
    }
  },
  
  onLoad(options) {
    if (options.id) {
      this.orderId = parseInt(options.id)
      this.loadOrderDetail()
    }
  },
  
  onShow() {
    if (this.orderId) {
      this.loadOrderDetail()
    }
  },
  
  methods: {
    getStatusText(status) {
      return STATUS_MAP[status] || '未知'
    },
    
    getStatusIcon(status) {
      return STATUS_ICON_MAP[status] || '📋'
    },
    
    getStatusSubtitle(status) {
      const subtitles = {
        1: '等待回收员接单',
        2: '回收员已接单，正在前往',
        3: '回收员正在处理',
        4: '回收完成，积分已到账',
        5: '订单已取消'
      }
      return subtitles[status] || ''
    },
    
    async loadOrderDetail() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      this.loading = true
      
      try {
        const res = await api.get(`/order/${this.orderId}`)
        if (res.code === 200) {
          this.order = res.data
          this.buildTimeline()
        }
      } catch (e) {
        console.error('加载订单详情失败:', e)
      } finally {
        this.loading = false
      }
    },
    
    buildTimeline() {
      if (!this.order) return
      
      const baseSteps = [
        { status: 1, title: '提交预约', desc: '您的回收预约已提交' },
        { status: 2, title: '回收员接单', desc: '回收员已接单，正在前往' },
        { status: 3, title: '上门回收', desc: '回收员已到达，正在处理' },
        { status: 4, title: '回收完成', desc: '订单已完成，积分已到账' }
      ]
      
      const historyMap = {}
      if (this.order.status_history) {
        this.order.status_history.forEach(item => {
          historyMap[item.status] = item
        })
      }
      
      this.timelineList = baseSteps.map((step, index) => {
        const history = historyMap[step.status]
        const isCompleted = this.order.status >= step.status
        const isCurrent = this.order.status === step.status
        
        return {
          title: step.title,
          desc: history?.remark || step.desc,
          time: history ? utils.formatDateTime(history.created_at) : '',
          isCompleted,
          isCurrent
        }
      })
    },
    
    callCollector() {
      if (this.order && this.order.collector_info && this.order.collector_info.phone) {
        uni.makePhoneCall({
          phoneNumber: this.order.collector_info.phone
        })
      }
    },
    
    sendMessage() {
      if (this.order && this.order.collector_info) {
        uni.navigateTo({
          url: `/pages/chat/detail?collector_id=${this.order.collector_info.id}`
        })
      }
    },
    
    goMall() {
      uni.switchTab({
        url: '/pages/mall/index'
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

.status-header {
  background: linear-gradient(135deg, $primary-color, #66BB6A);
  padding: 40rpx;
  padding-top: calc(40rpx + env(safe-area-inset-top));
}

.status-main {
  display: flex;
  align-items: center;
}

.status-icon {
  font-size: 64rpx;
  margin-right: 30rpx;
}

.status-texts {
  flex: 1;
}

.status-title {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $white;
}

.status-subtitle {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-top: 10rpx;
  display: block;
}

.map-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-md;
  padding: 30rpx;
}

.map-placeholder {
  height: 300rpx;
  background-color: #E8F5E9;
  border-radius: $border-radius-md;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.map-icon {
  font-size: 64rpx;
  margin-bottom: 16rpx;
}

.map-text {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.location-info {
  position: absolute;
  display: flex;
  align-items: center;
}

.location-info:nth-child(3) {
  top: 40rpx;
  left: 40rpx;
}

.location-info:nth-child(4) {
  bottom: 40rpx;
  right: 40rpx;
}

.location-dot {
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  margin-right: 10rpx;
  
  &.collector {
    background-color: $info-color;
    box-shadow: 0 0 0 6rpx rgba($info-color, 0.3);
  }
  
  &.user {
    background-color: $primary-color;
    box-shadow: 0 0 0 6rpx rgba($primary-color, 0.3);
  }
}

.location-text {
  font-size: $font-size-xs;
  color: $text-secondary;
}

.scroll-content {
  height: calc(100vh - 340rpx);
}

.section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-md;
  padding: 0 30rpx;
}

.section-header {
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
}

.section-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.collector-section,
.progress-section,
.order-section,
.address-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-md;
  padding: 0 30rpx;
}

.collector-card {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
}

.collector-avatar {
  width: 100rpx;
  height: 100rpx;
  border-radius: 50%;
  margin-right: 20rpx;
}

.collector-info {
  flex: 1;
}

.collector-name {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.collector-rating {
  display: flex;
  align-items: center;
  gap: 20rpx;
  margin-top: 10rpx;
}

.rating-text,
.order-count {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.collector-phone {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 10rpx;
  display: block;
}

.collector-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  width: 80rpx;
  height: 80rpx;
  background-color: rgba($primary-color, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-icon {
  font-size: 36rpx;
}

.timeline {
  padding: 20rpx 0;
}

.timeline-item {
  display: flex;
}

.timeline-left {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 20rpx;
}

.timeline-dot {
  width: 32rpx;
  height: 32rpx;
  border-radius: 50%;
  background-color: $border-color;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.completed {
    background-color: $primary-color;
  }
  
  &.current {
    background-color: $primary-color;
    box-shadow: 0 0 0 8rpx rgba($primary-color, 0.2);
  }
}

.dot-icon {
  font-size: 20rpx;
  color: $white;
}

.timeline-line {
  width: 2rpx;
  height: 80rpx;
  background-color: $border-color;
  
  &.completed {
    background-color: $primary-color;
  }
}

.timeline-right {
  flex: 1;
  padding-bottom: 30rpx;
}

.timeline-title {
  font-size: $font-size-base;
  color: $text-secondary;
  
  &.current {
    color: $text-color;
    font-weight: bold;
  }
}

.timeline-time {
  font-size: $font-size-sm;
  color: $text-muted;
  margin-top: 6rpx;
  display: block;
}

.timeline-desc {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 6rpx;
  display: block;
}

.info-list {
  padding: 10rpx 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.info-label {
  font-size: $font-size-base;
  color: $text-secondary;
}

.info-value {
  font-size: $font-size-base;
  color: $text-color;
  
  &.highlight {
    color: $primary-color;
    font-weight: bold;
  }
}

.address-card {
  padding: 30rpx 0;
}

.address-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.name {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
  margin-right: 30rpx;
}

.phone {
  font-size: $font-size-base;
  color: $text-secondary;
}

.address-detail {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $white;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.bottom-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 44rpx;
  font-size: $font-size-base;
  
  &.contact {
    background-color: rgba($primary-color, 0.1);
    color: $primary-color;
  }
  
  &.primary {
    background-color: $primary-color;
    color: $white;
  }
}

.btn-icon {
  font-size: 32rpx;
  margin-right: 10rpx;
}
</style>
