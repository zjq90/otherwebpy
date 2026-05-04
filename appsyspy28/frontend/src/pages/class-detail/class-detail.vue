<template>
  <view class="class-detail-page">
    <view class="detail-header" v-if="classDetail">
      <view class="header-content">
        <text class="class-name">{{ classDetail.name }}</text>
        <view class="class-tags">
          <view class="tag" v-if="classDetail.category">
            {{ classDetail.category.name }}
          </view>
          <view 
            class="capacity-tag" 
            :class="{ 'full': isFull }"
          >
            {{ remaining }}人可约
          </view>
        </view>
      </view>
    </view>

    <view class="detail-body" v-if="classDetail">
      <view class="info-section">
        <view class="info-item">
          <view class="info-icon">📅</view>
          <view class="info-content">
            <text class="info-label">课程日期</text>
            <text class="info-value">{{ classDetail.class_date }}</text>
          </view>
        </view>

        <view class="info-item">
          <view class="info-icon">⏰</view>
          <view class="info-content">
            <text class="info-label">课程时间</text>
            <text class="info-value">
              {{ formatTime(classDetail.start_time) }} - {{ formatTime(classDetail.end_time) }}
            </text>
          </view>
        </view>

        <view class="info-item">
          <view class="info-icon">👨‍🏫</view>
          <view class="info-content">
            <text class="info-label">授课教练</text>
            <text class="info-value">{{ classDetail.coach?.name || '待分配' }}</text>
          </view>
        </view>

        <view class="info-item">
          <view class="info-icon">📍</view>
          <view class="info-content">
            <text class="info-label">上课地点</text>
            <text class="info-value">{{ classDetail.room?.name || '待确认' }}</text>
          </view>
        </view>
      </view>

      <view class="description-section" v-if="classDetail.description">
        <view class="section-title">课程介绍</view>
        <text class="description-text">{{ classDetail.description }}</text>
      </view>

      <view class="capacity-section">
        <view class="section-title">报名情况</view>
        <view class="capacity-bar">
          <view class="capacity-progress" :style="{ width: bookedPercent + '%' }"></view>
        </view>
        <view class="capacity-info">
          <text class="booked-text">已预约 {{ classDetail.booked_count }} 人</text>
          <text class="total-text">容量 {{ classDetail.capacity }} 人</text>
        </view>
      </view>

      <view class="alert-section" v-if="isPast">
        <view class="alert-icon">⚠️</view>
        <text class="alert-text">该课程已过期，无法预约</text>
      </view>

      <view class="alert-section" v-else-if="hasBooked">
        <view class="alert-icon success">✅</view>
        <text class="alert-text">您已预约该课程</text>
      </view>

      <view class="alert-section" v-else-if="isFull">
        <view class="alert-icon">😔</view>
        <text class="alert-text">该课程名额已满</text>
      </view>
    </view>

    <view class="bottom-bar" v-if="classDetail">
      <view class="price-info" v-if="!isPast && !hasBooked && !isFull">
        <text class="price-text">会员卡预约</text>
      </view>
      <button 
        class="book-btn"
        :class="{ 'disabled': isPast || hasBooked || isFull, 'loading': booking }"
        :disabled="isPast || hasBooked || isFull || booking"
        @click="handleBooking"
      >
        {{ getButtonText() }}
      </button>
    </view>

    <view class="loading-container" v-if="loading">
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script>
import { request, formatTime, showToast, showLoading, hideLoading, showModal } from '@/utils/utils'

export default {
  data() {
    return {
      classId: null,
      classDetail: null,
      loading: true,
      booking: false,
      hasBooked: false,
      isPast: false
    }
  },

  computed: {
    remaining() {
      if (!this.classDetail) return 0
      return this.classDetail.capacity - this.classDetail.booked_count
    },
    isFull() {
      return this.remaining <= 0
    },
    bookedPercent() {
      if (!this.classDetail || this.classDetail.capacity === 0) return 0
      return Math.min(100, (this.classDetail.booked_count / this.classDetail.capacity) * 100)
    }
  },

  onLoad(options) {
    if (options.id) {
      this.classId = parseInt(options.id)
      this.loadClassDetail()
    }
  },

  methods: {
    async loadClassDetail() {
      if (!this.classId) return
      
      this.loading = true
      
      try {
        const [classRes, bookingsRes] = await Promise.all([
          request.get(`/classes/${this.classId}`),
          request.get('/bookings/my')
        ])
        
        this.classDetail = classRes
        
        const bookings = bookingsRes.items || []
        this.hasBooked = bookings.some(b => 
          b.class_id === this.classId && 
          ['pending', 'confirmed'].includes(b.status)
        )
        
        const classDate = this.classDetail.class_date
        const startTime = this.classDetail.start_time
        const now = new Date()
        const [hours, minutes] = startTime.split(':').map(Number)
        const classDateTime = new Date(classDate)
        classDateTime.setHours(hours, minutes, 0, 0)
        
        this.isPast = classDateTime < now
        
      } catch (error) {
        console.error('加载课程详情失败:', error)
        showToast('加载失败')
      } finally {
        this.loading = false
      }
    },

    getButtonText() {
      if (this.booking) return '预约中...'
      if (this.isPast) return '课程已过期'
      if (this.hasBooked) return '已预约'
      if (this.isFull) return '名额已满'
      return '立即预约'
    },

    async handleBooking() {
      if (this.isPast || this.hasBooked || this.isFull) return
      
      const confirmed = await showModal(
        '确认预约',
        `确定要预约「${this.classDetail.name}」吗？`
      )
      
      if (!confirmed) return
      
      this.booking = true
      showLoading('预约中...')
      
      try {
        const res = await request.post('/bookings/', {
          class_id: this.classId
        })
        
        hideLoading()
        
        showToast('预约成功', 'success')
        this.hasBooked = true
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
        
      } catch (error) {
        hideLoading()
        console.error('预约失败:', error)
      } finally {
        this.booking = false
      }
    }
  }
}
</script>

<style scoped>
.class-detail-page {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  flex-direction: column;
}

.detail-header {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  padding: 40rpx 30rpx;
}

.header-content {
  color: #ffffff;
}

.class-name {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  margin-bottom: 20rpx;
}

.class-tags {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.tag {
  padding: 8rpx 20rpx;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 20rpx;
  font-size: 24rpx;
}

.capacity-tag {
  padding: 8rpx 20rpx;
  background-color: #d1fae5;
  color: #047857;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 500;
}

.capacity-tag.full {
  background-color: #fee2e2;
  color: #b91c1c;
}

.detail-body {
  flex: 1;
  padding: 20rpx;
  padding-bottom: 150rpx;
}

.info-section {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 10rpx 0;
  margin-bottom: 20rpx;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.info-item:last-child {
  border-bottom: none;
}

.info-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
  width: 60rpx;
  text-align: center;
}

.info-content {
  flex: 1;
}

.info-label {
  display: block;
  font-size: 24rpx;
  color: #9ca3af;
  margin-bottom: 6rpx;
}

.info-value {
  font-size: 28rpx;
  color: #1f2937;
  font-weight: 500;
}

.description-section,
.capacity-section {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20rpx;
}

.description-text {
  font-size: 28rpx;
  color: #6b7280;
  line-height: 1.8;
}

.capacity-bar {
  height: 16rpx;
  background-color: #f3f4f6;
  border-radius: 8rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.capacity-progress {
  height: 100%;
  background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
  border-radius: 8rpx;
  transition: width 0.3s ease;
}

.capacity-info {
  display: flex;
  justify-content: space-between;
}

.booked-text {
  font-size: 24rpx;
  color: #2563eb;
  font-weight: 500;
}

.total-text {
  font-size: 24rpx;
  color: #9ca3af;
}

.alert-section {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #fef3c7;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.alert-section.success {
  background-color: #d1fae5;
}

.alert-icon {
  font-size: 40rpx;
  margin-right: 16rpx;
}

.alert-text {
  font-size: 28rpx;
  color: #92400e;
  font-weight: 500;
}

.alert-section.success .alert-text {
  color: #047857;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #ffffff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  box-shadow: 0 -4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.price-info {
  margin-right: 20rpx;
}

.price-text {
  font-size: 28rpx;
  color: #6b7280;
}

.book-btn {
  flex: 1;
  height: 96rpx;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  color: #ffffff;
  border-radius: 48rpx;
  font-size: 30rpx;
  font-weight: 600;
  border: none;
}

.book-btn.disabled {
  background: #e5e7eb;
  color: #9ca3af;
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
</style>
