<template>
  <view class="history-page">
    <view class="tabs">
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'group' }"
        @click="activeTab = 'group'"
      >
        团课预约
      </view>
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'private' }"
        @click="activeTab = 'private'"
      >
        私教预约
      </view>
    </view>

    <scroll-view scroll-y class="scroll-content">
      <view v-if="loading" class="loading-container">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="filteredBookings.length === 0" class="empty-state">
        <text class="empty-icon">📋</text>
        <text class="empty-text">暂无预约记录</text>
      </view>

      <view v-else>
        <view 
          class="history-card" 
          v-for="booking in filteredBookings" 
          :key="booking.id"
        >
          <view class="card-header">
            <view class="class-info">
              <text class="class-name">{{ getClassName(booking) }}</text>
              <view 
                class="status-tag" 
                :class="getStatusClass(booking.status)"
              >
                {{ getStatusText(booking.status) }}
              </view>
            </view>
          </view>

          <view class="card-body">
            <view class="info-row">
              <view class="info-item">
                <text class="info-icon">👨‍🏫</text>
                <text class="info-text">{{ getCoachName(booking) }}</text>
              </view>
            </view>

            <view class="info-row">
              <view class="info-item">
                <text class="info-icon">📅</text>
                <text class="info-text">{{ getDateText(booking) }}</text>
              </view>
              <view class="info-item">
                <text class="info-icon">⏰</text>
                <text class="info-text">{{ getTimeText(booking) }}</text>
              </view>
            </view>

            <view class="info-row" v-if="booking.class_?.room?.name">
              <view class="info-item">
                <text class="info-icon">📍</text>
                <text class="info-text">{{ booking.class_.room.name }}</text>
              </view>
            </view>

            <view class="info-row" v-if="booking.cancel_reason">
              <view class="info-item">
                <text class="info-icon">💬</text>
                <text class="info-text cancel-reason">取消原因：{{ booking.cancel_reason }}</text>
              </view>
            </view>
          </view>

          <view class="card-footer" v-if="booking.status === 'completed'">
            <view class="checkin-info" v-if="booking.checkin">
              <text class="checkin-icon">✅</text>
              <text class="checkin-text">已签到</text>
              <text class="checkin-time">{{ formatCheckinTime(booking.checkin.checkin_time) }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { request, formatTime, showToast } from '@/utils/utils'

export default {
  data() {
    return {
      activeTab: 'group',
      groupBookings: [],
      privateBookings: [],
      loading: false
    }
  },

  computed: {
    filteredBookings() {
      return this.activeTab === 'group' ? this.groupBookings : this.privateBookings
    }
  },

  onShow() {
    this.loadBookings()
  },

  methods: {
    async loadBookings() {
      this.loading = true
      
      try {
        const [groupRes, privateRes] = await Promise.all([
          request.get('/bookings/my'),
          request.get('/private/my-bookings')
        ])
        
        this.groupBookings = groupRes.items || []
        this.privateBookings = privateRes || []
        
      } catch (error) {
        console.error('加载历史失败:', error)
        showToast('加载失败')
      } finally {
        this.loading = false
      }
    },

    getClassName(booking) {
      if (this.activeTab === 'group') {
        return booking.class_?.name || '未知课程'
      }
      return booking.class_name || '未知课程'
    },

    getCoachName(booking) {
      if (this.activeTab === 'group') {
        return booking.class_?.coach?.name || '待分配'
      }
      return booking.coach?.name || '待分配'
    },

    getDateText(booking) {
      if (this.activeTab === 'group') {
        return booking.class_?.class_date || ''
      }
      return booking.schedule?.schedule_date || ''
    },

    getTimeText(booking) {
      if (this.activeTab === 'group') {
        const start = booking.class_?.start_time
        const end = booking.class_?.end_time
        return `${formatTime(start)} - ${formatTime(end)}`
      }
      const start = booking.schedule?.start_time
      const end = booking.schedule?.end_time
      return `${formatTime(start)} - ${formatTime(end)}`
    },

    getStatusText(status) {
      const statusMap = {
        'pending': '待确认',
        'confirmed': '已预约',
        'cancelled': '已取消',
        'completed': '已完成'
      }
      return statusMap[status] || status
    },

    getStatusClass(status) {
      const classMap = {
        'pending': 'badge-warning',
        'confirmed': 'badge-success',
        'cancelled': 'badge-danger',
        'completed': 'badge-secondary'
      }
      return classMap[status] || 'badge-secondary'
    },

    formatCheckinTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    }
  }
}
</script>

<style scoped>
.history-page {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  flex-direction: column;
}

.tabs {
  display: flex;
  background-color: #ffffff;
  padding: 0 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.tab-item {
  flex: 1;
  text-align: center;
  padding: 30rpx 0;
  font-size: 30rpx;
  color: #6b7280;
  position: relative;
}

.tab-item.active {
  color: #2563eb;
  font-weight: 500;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 6rpx;
  background-color: #2563eb;
  border-radius: 3rpx;
}

.scroll-content {
  flex: 1;
  padding: 20rpx;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 100rpx;
}

.loading-text {
  color: #9ca3af;
  font-size: 28rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 40rpx;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #9ca3af;
}

.history-card {
  background-color: #ffffff;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  padding: 24rpx 30rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.class-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.class-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.status-tag {
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 500;
}

.badge-success {
  background-color: #d1fae5;
  color: #047857;
}

.badge-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-danger {
  background-color: #fee2e2;
  color: #b91c1c;
}

.badge-secondary {
  background-color: #f3f4f6;
  color: #4b5563;
}

.card-body {
  padding: 24rpx 30rpx;
}

.info-row {
  display: flex;
  margin-bottom: 16rpx;
  gap: 40rpx;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-item {
  display: flex;
  align-items: center;
  font-size: 26rpx;
}

.info-icon {
  margin-right: 10rpx;
  font-size: 28rpx;
}

.info-text {
  color: #374151;
}

.cancel-reason {
  color: #ef4444;
  font-style: italic;
}

.card-footer {
  padding: 20rpx 30rpx;
  border-top: 2rpx solid #f3f4f6;
  background-color: #f9fafb;
}

.checkin-info {
  display: flex;
  align-items: center;
}

.checkin-icon {
  font-size: 28rpx;
  margin-right: 10rpx;
}

.checkin-text {
  font-size: 24rpx;
  color: #047857;
  font-weight: 500;
  margin-right: 20rpx;
}

.checkin-time {
  font-size: 24rpx;
  color: #6b7280;
}
</style>
