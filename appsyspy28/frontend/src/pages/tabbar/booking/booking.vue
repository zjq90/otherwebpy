<template>
  <view class="booking-page">
    <view class="tabs">
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'confirmed' }"
        @click="activeTab = 'confirmed'"
      >
        已预约
        <view class="tab-badge" v-if="confirmedCount > 0">{{ confirmedCount }}</view>
      </view>
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'history' }"
        @click="activeTab = 'history'"
      >
        历史记录
      </view>
    </view>

    <scroll-view scroll-y class="scroll-content">
      <view v-if="loading" class="loading-container">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="filteredBookings.length === 0" class="empty-state">
        <text class="empty-icon">📋</text>
        <text class="empty-text">
          {{ activeTab === 'confirmed' ? '暂无预约课程' : '暂无历史记录' }}
        </text>
      </view>

      <view v-else>
        <view 
          class="booking-card" 
          v-for="booking in filteredBookings" 
          :key="booking.id"
        >
          <view class="booking-header">
            <view class="class-title">
              <text class="class-name">{{ booking.class_?.name || '未知课程' }}</text>
              <view 
                class="status-tag" 
                :class="getStatusClass(booking.status)"
              >
                {{ getStatusText(booking.status) }}
              </view>
            </view>
          </view>

          <view class="booking-body">
            <view class="info-row">
              <view class="info-item">
                <text class="info-icon">📅</text>
                <text class="info-text">
                  {{ booking.class_?.class_date }} 
                  {{ formatTime(booking.class_?.start_time) }}-{{ formatTime(booking.class_?.end_time) }}
                </text>
              </view>
            </view>

            <view class="info-row">
              <view class="info-item">
                <text class="info-icon">👨‍🏫</text>
                <text class="info-text">{{ booking.class_?.coach?.name || '待分配' }}</text>
              </view>
              <view class="info-item">
                <text class="info-icon">📍</text>
                <text class="info-text">{{ booking.class_?.room?.name || '待确认' }}</text>
              </view>
            </view>

            <view class="info-row" v-if="booking.status === 'cancelled' && booking.cancel_reason">
              <view class="info-item">
                <text class="info-icon">💬</text>
                <text class="info-text cancel-reason">取消原因：{{ booking.cancel_reason }}</text>
              </view>
            </view>
          </view>

          <view class="booking-footer" v-if="booking.status === 'confirmed'">
            <button 
              class="btn btn-outline btn-sm"
              @click="showCancelModal(booking)"
            >
              取消预约
            </button>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="cancel-modal" v-if="showModal" @click.self="showModal = false">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">取消预约</text>
        </view>
        
        <view class="modal-body">
          <text class="modal-text">确定要取消预约吗？</text>
          <text class="modal-hint">{{ cancelLimitMessage }}</text>
        </view>

        <view class="form-item">
          <textarea 
            class="form-textarea"
            v-model="cancelReason"
            placeholder="请输入取消原因（选填）"
            :maxlength="100"
          ></textarea>
          <text class="char-count">{{ cancelReason.length }}/100</text>
        </view>

        <view class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">
            再想想
          </button>
          <button 
            class="btn btn-danger" 
            :loading="canceling"
            @click="confirmCancel"
          >
            确认取消
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { request, formatTime, showToast, showLoading, hideLoading, showModal } from '@/utils/utils'

export default {
  data() {
    return {
      activeTab: 'confirmed',
      bookings: [],
      loading: false,
      showModal: false,
      currentBooking: null,
      cancelReason: '',
      canceling: false,
      cancelLimitMessage: ''
    }
  },

  computed: {
    confirmedCount() {
      return this.bookings.filter(b => b.status === 'confirmed').length
    },
    filteredBookings() {
      if (this.activeTab === 'confirmed') {
        return this.bookings.filter(b => b.status === 'confirmed')
      } else {
        return this.bookings.filter(b => b.status !== 'confirmed')
      }
    }
  },

  onShow() {
    this.loadBookings()
  },

  methods: {
    async loadBookings() {
      this.loading = true
      
      try {
        const res = await request.get('/bookings/my')
        this.bookings = res.items || []
      } catch (error) {
        console.error('加载预约失败:', error)
        showToast('加载失败')
      } finally {
        this.loading = false
      }
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

    async showCancelModal(booking) {
      this.currentBooking = booking
      this.cancelReason = ''
      
      try {
        const res = await request.get('/bookings/check/cancel-limit')
        this.cancelLimitMessage = res.message
      } catch (error) {
        this.cancelLimitMessage = '72小时内取消次数限制为3次'
      }
      
      this.showModal = true
    },

    async confirmCancel() {
      if (!this.currentBooking) return
      
      this.canceling = true
      showLoading('取消中...')
      
      try {
        const res = await request.delete('/bookings/' + this.currentBooking.id, {
          reason: this.cancelReason
        })
        
        hideLoading()
        
        if (res.success) {
          showToast('取消成功', 'success')
          this.showModal = false
          this.loadBookings()
        } else {
          showToast(res.message || '取消失败')
        }
      } catch (error) {
        hideLoading()
        console.error('取消失败:', error)
      } finally {
        this.canceling = false
      }
    }
  }
}
</script>

<style scoped>
.booking-page {
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

.tab-badge {
  position: absolute;
  top: 20rpx;
  right: 30rpx;
  min-width: 36rpx;
  height: 36rpx;
  padding: 0 10rpx;
  background-color: #ef4444;
  color: #ffffff;
  border-radius: 18rpx;
  font-size: 20rpx;
  display: flex;
  justify-content: center;
  align-items: center;
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

.booking-card {
  background-color: #ffffff;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.booking-header {
  padding: 30rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.class-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.class-name {
  font-size: 34rpx;
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

.booking-body {
  padding: 30rpx;
}

.info-row {
  display: flex;
  margin-bottom: 20rpx;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-item {
  display: flex;
  align-items: center;
  flex: 1;
  font-size: 26rpx;
  color: #6b7280;
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

.booking-footer {
  padding: 20rpx 30rpx;
  border-top: 2rpx solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
}

.cancel-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 40rpx;
}

.modal-content {
  width: 100%;
  max-width: 600rpx;
  background-color: #ffffff;
  border-radius: 24rpx;
  overflow: hidden;
}

.modal-header {
  padding: 40rpx;
  border-bottom: 2rpx solid #f3f4f6;
  text-align: center;
}

.modal-title {
  font-size: 34rpx;
  font-weight: 600;
  color: #1f2937;
}

.modal-body {
  padding: 40rpx;
  text-align: center;
}

.modal-text {
  display: block;
  font-size: 30rpx;
  color: #1f2937;
  margin-bottom: 20rpx;
}

.modal-hint {
  display: block;
  font-size: 24rpx;
  color: #9ca3af;
}

.form-item {
  padding: 0 40rpx 40rpx;
}

.form-textarea {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background-color: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 16rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.char-count {
  display: block;
  text-align: right;
  font-size: 22rpx;
  color: #9ca3af;
  margin-top: 10rpx;
}

.modal-footer {
  display: flex;
  border-top: 2rpx solid #f3f4f6;
}

.modal-footer .btn {
  flex: 1;
  margin: 0;
  border-radius: 0;
  height: 100rpx;
  line-height: 100rpx;
}
</style>
