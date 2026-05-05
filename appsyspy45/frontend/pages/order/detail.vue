<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-content">
      <view class="status-section" v-if="order">
        <view class="status-icon">
          <text class="icon">{{ getStatusIcon(order.status) }}</text>
        </view>
        <view class="status-info">
          <text class="status-text">{{ getStatusText(order.status) }}</text>
          <text class="status-desc">{{ getStatusDesc(order.status) }}</text>
        </view>
      </view>
      
      <view class="section" v-if="order">
        <view class="section-header">
          <text class="section-title">订单信息</text>
        </view>
        <view class="info-item">
          <text class="label">订单编号</text>
          <text class="value">{{ order.order_no }}</text>
        </view>
        <view class="info-item">
          <text class="label">预约时间</text>
          <text class="value">{{ order.schedule_date }} {{ order.schedule_time }}</text>
        </view>
        <view class="info-item">
          <text class="label">创建时间</text>
          <text class="value">{{ formatTime(order.created_at) }}</text>
        </view>
        <view class="info-item" v-if="order.remark">
          <text class="label">备注</text>
          <text class="value">{{ order.remark }}</text>
        </view>
      </view>
      
      <view class="section" v-if="order && order.items">
        <view class="section-header">
          <text class="section-title">回收衣物</text>
        </view>
        <view class="clothing-list">
          <view class="clothing-item" v-for="(item, index) in order.items" :key="index">
            <image :src="item.clothing_type_icon" class="clothing-icon"></image>
            <view class="clothing-info">
              <text class="clothing-name">{{ item.clothing_type_name }}</text>
              <view class="clothing-detail">
                <text class="quantity">数量：{{ item.quantity }}件</text>
                <text class="quality">品质：{{ getQualityText(item.quality) }}</text>
              </view>
            </view>
            <view class="clothing-points">
              <text class="points">{{ item.estimate_points }}积分</text>
            </view>
          </view>
        </view>
        <view class="summary-row">
          <text class="label">共{{ order.total_quantity }}件</text>
          <text class="value">预估积分：{{ order.estimate_points }}积分</text>
        </view>
        <view class="summary-row" v-if="order.actual_points">
          <text class="label">实际获得</text>
          <text class="value highlight">实际积分：{{ order.actual_points }}积分</text>
        </view>
      </view>
      
      <view class="section" v-if="order && order.address_info">
        <view class="section-header">
          <text class="section-title">回收地址</text>
        </view>
        <view class="address-card">
          <view class="address-header">
            <text class="name">{{ order.address_info.contact_name }}</text>
            <text class="phone">{{ order.address_info.contact_phone }}</text>
          </view>
          <text class="address">
            {{ order.address_info.province }}{{ order.address_info.city }}{{ order.address_info.district }}{{ order.address_info.detail }}
          </text>
        </view>
      </view>
      
      <view class="section" v-if="order && order.collector_info">
        <view class="section-header">
          <text class="section-title">回收员信息</text>
        </view>
        <view class="collector-card">
          <image :src="order.collector_info.avatar || '/static/images/default-avatar.png'" class="collector-avatar"></image>
          <view class="collector-info">
            <text class="collector-name">{{ order.collector_info.name }}</text>
            <text class="collector-phone">{{ order.collector_info.phone }}</text>
          </view>
          <view class="collector-actions">
            <view class="action-btn" @click="callCollector">
              <text class="action-icon">📞</text>
              <text class="action-text">联系</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="section" v-if="order && order.status_history && order.status_history.length > 0">
        <view class="section-header">
          <text class="section-title">订单进度</text>
        </view>
        <view class="timeline">
          <view class="timeline-item" v-for="(item, index) in order.status_history" :key="index">
            <view class="timeline-left">
              <view class="timeline-dot" :class="{ active: index === 0 }"></view>
              <view class="timeline-line" v-if="index < order.status_history.length - 1"></view>
            </view>
            <view class="timeline-content">
              <text class="timeline-title">{{ getStatusText(item.status) }}</text>
              <text class="timeline-time">{{ formatTime(item.created_at) }}</text>
              <text class="timeline-remark" v-if="item.remark">{{ item.remark }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
    
    <view class="bottom-bar" v-if="order">
      <view class="bottom-actions" v-if="order.status === 1 || order.status === 2">
        <view class="action-item" @click="cancelOrder">取消订单</view>
        <view class="action-item" @click="goTrack">订单跟踪</view>
        <view class="action-item primary" @click="reschedule">调整时间</view>
      </view>
      <view class="bottom-actions" v-else-if="order.status === 3">
        <view class="action-item" @click="goTrack">订单跟踪</view>
      </view>
      <view class="bottom-actions" v-else-if="order.status === 4">
        <view class="action-item" @click="goMall">去积分商城</view>
        <view class="action-item primary" @click="createAgain">再预约一次</view>
      </view>
    </view>
    
    <view class="reschedule-modal" v-if="showReschedule">
      <view class="modal-mask" @click="showReschedule = false"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">调整预约时间</text>
          <text class="modal-close" @click="showReschedule = false">×</text>
        </view>
        <view class="modal-body">
          <view class="picker-section">
            <text class="picker-label">选择日期</text>
            <picker :value="dateIndex" :range="dates" range-key="date" @change="onDateChange">
              <view class="picker-value">
                <text>{{ selectedDate || '请选择' }}</text>
                <text class="picker-arrow">›</text>
              </view>
            </picker>
          </view>
          <view class="picker-section">
            <text class="picker-label">选择时间</text>
            <picker :value="timeIndex" :range="timeSlots" range-key="slot" @change="onTimeSlotChange">
              <view class="picker-value">
                <text>{{ selectedTimeSlot || '请选择' }}</text>
                <text class="picker-arrow">›</text>
              </view>
            </picker>
          </view>
        </view>
        <view class="modal-footer">
          <view class="modal-btn cancel" @click="showReschedule = false">取消</view>
          <view class="modal-btn confirm" @click="confirmReschedule">确认</view>
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

const QUALITY_MAP = {
  'good': '良好',
  'normal': '一般',
  'poor': '较差'
}

export default {
  data() {
    return {
      orderId: null,
      order: null,
      loading: false,
      showReschedule: false,
      dates: [],
      timeSlots: [],
      dateIndex: 0,
      timeIndex: 0,
      selectedDate: '',
      selectedTimeSlot: ''
    }
  },
  
  onLoad(options) {
    if (options.id) {
      this.orderId = parseInt(options.id)
      this.loadOrderDetail()
    }
  },
  
  methods: {
    formatTime(time) {
      return utils.formatDateTime(time)
    },
    
    getStatusText(status) {
      return STATUS_MAP[status] || '未知'
    },
    
    getStatusIcon(status) {
      return STATUS_ICON_MAP[status] || '📋'
    },
    
    getStatusDesc(status) {
      const desc = {
        1: '等待回收员接单',
        2: '回收员已接单，等待上门',
        3: '回收员正在上门回收',
        4: '订单已完成，积分已到账',
        5: '订单已取消'
      }
      return desc[status] || ''
    },
    
    getQualityText(quality) {
      return QUALITY_MAP[quality] || quality
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
        }
      } catch (e) {
        console.error('加载订单详情失败:', e)
      } finally {
        this.loading = false
      }
    },
    
    async cancelOrder() {
      const confirmed = await utils.showModal('确定要取消该订单吗？')
      if (!confirmed) return
      
      utils.showLoading('取消中...')
      
      try {
        const res = await api.post(`/order/${this.orderId}/cancel`)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          utils.showToast('订单已取消')
          this.loadOrderDetail()
        }
      } catch (e) {
        utils.hideLoading()
        console.error('取消订单失败:', e)
      }
    },
    
    goTrack() {
      uni.navigateTo({
        url: `/pages/order/track?id=${this.orderId}`
      })
    },
    
    callCollector() {
      if (this.order && this.order.collector_info && this.order.collector_info.phone) {
        uni.makePhoneCall({
          phoneNumber: this.order.collector_info.phone
        })
      }
    },
    
    async reschedule() {
      this.showReschedule = true
      await this.loadAvailableTimes()
    },
    
    async loadAvailableTimes() {
      try {
        const res = await api.get('/order/available-times')
        if (res.code === 200) {
          this.dates = res.data.dates || []
          this.timeSlots = res.data.time_slots || []
          
          if (this.dates.length > 0) {
            this.selectedDate = this.dates[0].date
          }
          if (this.timeSlots.length > 0) {
            this.selectedTimeSlot = this.timeSlots[0].slot
          }
        }
      } catch (e) {
        console.error('加载可预约时间失败:', e)
      }
    },
    
    onDateChange(e) {
      this.dateIndex = e.detail.value
      this.selectedDate = this.dates[this.dateIndex].date
    },
    
    onTimeSlotChange(e) {
      this.timeIndex = e.detail.value
      this.selectedTimeSlot = this.timeSlots[this.timeIndex].slot
    },
    
    async confirmReschedule() {
      if (!this.selectedDate || !this.selectedTimeSlot) {
        utils.showToast('请选择日期和时间')
        return
      }
      
      utils.showLoading('提交中...')
      
      try {
        const res = await api.post(`/order/${this.orderId}/reschedule`, {
          schedule_date: this.selectedDate,
          schedule_time: this.selectedTimeSlot
        })
        
        utils.hideLoading()
        
        if (res.code === 200) {
          this.showReschedule = false
          utils.showToast('调整成功')
          this.loadOrderDetail()
        }
      } catch (e) {
        utils.hideLoading()
        console.error('调整时间失败:', e)
      }
    },
    
    goMall() {
      uni.switchTab({
        url: '/pages/mall/index'
      })
    },
    
    createAgain() {
      uni.switchTab({
        url: '/pages/order/create'
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

.scroll-content {
  height: calc(100vh - 120rpx);
}

.status-section {
  background: linear-gradient(135deg, $primary-color, #66BB6A);
  padding: 40rpx;
  display: flex;
  align-items: center;
}

.status-icon {
  width: 100rpx;
  height: 100rpx;
  background-color: rgba($white, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 30rpx;
}

.status-icon .icon {
  font-size: 48rpx;
}

.status-info {
  flex: 1;
}

.status-text {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $white;
}

.status-desc {
  font-size: $font-size-sm;
  color: rgba($white, 0.8);
  margin-top: 10rpx;
  display: block;
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

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.info-item .label {
  font-size: $font-size-base;
  color: $text-secondary;
}

.info-item .value {
  font-size: $font-size-base;
  color: $text-color;
}

.clothing-list {
  padding: 20rpx 0;
}

.clothing-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.clothing-icon {
  width: 80rpx;
  height: 80rpx;
  margin-right: 20rpx;
}

.clothing-info {
  flex: 1;
}

.clothing-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.clothing-detail {
  display: flex;
  gap: 30rpx;
  margin-top: 10rpx;
}

.quantity,
.quality {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.clothing-points {
  text-align: right;
}

.points {
  font-size: $font-size-base;
  color: $primary-color;
  font-weight: bold;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-top: 1rpx solid $border-color;
}

.summary-row .label {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.summary-row .value {
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

.address {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
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

.collector-phone {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 10rpx;
  display: block;
}

.collector-actions {
  margin-left: 20rpx;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.action-icon {
  font-size: 40rpx;
}

.action-text {
  font-size: $font-size-xs;
  color: $primary-color;
  margin-top: 6rpx;
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
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  background-color: $border-color;
  
  &.active {
    background-color: $primary-color;
    box-shadow: 0 0 0 6rpx rgba($primary-color, 0.2);
  }
}

.timeline-line {
  width: 2rpx;
  height: 80rpx;
  background-color: $border-color;
}

.timeline-content {
  flex: 1;
  padding-bottom: 30rpx;
}

.timeline-title {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.timeline-time {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 6rpx;
  display: block;
}

.timeline-remark {
  font-size: $font-size-sm;
  color: $text-muted;
  margin-top: 6rpx;
  display: block;
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

.action-item {
  flex: 1;
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  border-radius: 44rpx;
  font-size: $font-size-base;
  color: $text-secondary;
  background-color: $bg-color;
  
  &.primary {
    background-color: $primary-color;
    color: $white;
  }
}

.reschedule-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
}

.modal-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $white;
  border-radius: 24rpx 24rpx 0 0;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid $border-color;
}

.modal-title {
  font-size: $font-size-lg;
  font-weight: bold;
  color: $text-color;
}

.modal-close {
  font-size: 48rpx;
  color: $text-muted;
}

.modal-body {
  padding: 30rpx;
}

.picker-section {
  margin-bottom: 30rpx;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.picker-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-bottom: 16rpx;
  display: block;
}

.picker-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  background-color: $bg-color;
  border-radius: $border-radius-md;
}

.picker-arrow {
  color: $text-muted;
}

.modal-footer {
  display: flex;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  gap: 20rpx;
}

.modal-btn {
  flex: 1;
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  border-radius: 44rpx;
  font-size: $font-size-base;
  
  &.cancel {
    background-color: $bg-color;
    color: $text-secondary;
  }
  
  &.confirm {
    background-color: $primary-color;
    color: $white;
  }
}
</style>
