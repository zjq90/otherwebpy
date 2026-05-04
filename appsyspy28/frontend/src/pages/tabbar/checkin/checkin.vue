<template>
  <view class="checkin-page">
    <view class="checkin-header">
      <view class="qrcode-placeholder" @click="scanQRCode">
        <text class="qrcode-icon">📷</text>
        <text class="qrcode-text">点击扫描教室二维码</text>
        <text class="qrcode-hint">提前30分钟可开始签到</text>
      </view>
    </view>

    <view class="checkin-methods">
      <view class="method-title">签到方式</view>
      
      <view class="method-list">
        <view class="method-item" @click="scanQRCode">
          <view class="method-icon qrcode-icon-bg">
            <text class="icon">📱</text>
          </view>
          <view class="method-info">
            <text class="method-name">扫码签到</text>
            <text class="method-desc">扫描教室二维码完成签到</text>
          </view>
          <text class="method-arrow">›</text>
        </view>

        <view class="method-item" @click="showFaceCheckin">
          <view class="method-icon face-icon-bg">
            <text class="icon">😊</text>
          </view>
          <view class="method-info">
            <text class="method-name">人脸识别签到</text>
            <text class="method-desc">人脸识别验证，不可代签</text>
          </view>
          <text class="method-arrow">›</text>
        </view>
      </view>
    </view>

    <view class="recent-bookings">
      <view class="section-header">
        <text class="section-title">今日可签到课程</text>
      </view>

      <view v-if="loading" class="loading-container">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="todayBookings.length === 0" class="empty-state">
        <text class="empty-icon">📝</text>
        <text class="empty-text">今日暂无预约课程</text>
      </view>

      <view v-else>
        <view 
          class="booking-item" 
          v-for="booking in todayBookings" 
          :key="booking.id"
        >
          <view class="booking-info">
            <view class="booking-time">
              <text class="start-time">{{ formatTime(booking.class_?.start_time) }}</text>
              <text class="time-sep">-</text>
              <text class="end-time">{{ formatTime(booking.class_?.end_time) }}</text>
            </view>
            <view class="booking-detail">
              <text class="class-name">{{ booking.class_?.name || '未知课程' }}</text>
              <text class="class-meta">
                {{ booking.class_?.coach?.name || '' }} · {{ booking.class_?.room?.name || '' }}
              </text>
            </view>
          </view>

          <view class="booking-action">
            <button 
              class="btn" 
              :class="isCheckinAvailable(booking) ? 'btn-primary' : 'btn-disabled'"
              :disabled="!isCheckinAvailable(booking) || booking.checkin"
              @click="quickCheckin(booking)"
            >
              {{ getCheckinButtonText(booking) }}
            </button>
          </view>
        </view>
      </view>
    </view>

    <view class="checkin-history">
      <view class="section-header">
        <text class="section-title">签到记录</text>
        <text class="section-more" @click="goToHistory">查看全部 ›</text>
      </view>

      <view v-if="recentCheckins.length === 0" class="empty-state small">
        <text class="empty-text">暂无签到记录</text>
      </view>

      <view v-else>
        <view 
          class="history-item" 
          v-for="checkin in recentCheckins.slice(0, 5)" 
          :key="checkin.id"
        >
          <view class="history-info">
            <text class="history-class">课程名称</text>
            <text class="history-time">{{ formatCheckinTime(checkin.checkin_time) }}</text>
          </view>
          <view class="history-method">
            <text class="method-badge" :class="checkin.checkin_method === 'face' ? 'face-badge' : 'qrcode-badge'">
              {{ getCheckinMethodText(checkin.checkin_method) }}
            </text>
          </view>
        </view>
      </view>
    </view>

    <view class="face-modal" v-if="showFaceModal" @click.self="showFaceModal = false">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">人脸识别签到</text>
          <text class="modal-close" @click="showFaceModal = false">✕</text>
        </view>

        <view class="modal-body">
          <view class="face-preview">
            <text class="face-icon">😊</text>
            <text class="face-hint">请将面部对准框内</text>
          </view>

          <view class="face-actions">
            <button class="btn btn-primary" @click="takePhoto">
              拍照
            </button>
            <button class="btn btn-secondary" @click="selectFromAlbum">
              从相册选择
            </button>
          </view>

          <view class="simulate-section" v-if="simulateFaceData">
            <view class="face-result">
              <text class="result-icon">✅</text>
              <text class="result-text">人脸识别成功</text>
            </view>
            <text class="simulate-hint">（演示模式：模拟人脸识别成功）</text>
          </view>
        </view>

        <view class="modal-footer" v-if="selectedBooking">
          <button 
            class="btn btn-primary btn-lg btn-block"
            :loading="checkingIn"
            :disabled="!simulateFaceData"
            @click="confirmFaceCheckin"
          >
            确认签到
          </button>
        </view>
      </view>
    </view>

    <view class="booking-select-modal" v-if="showBookingSelect" @click.self="showBookingSelect = false">
      <view class="select-content">
        <view class="select-header">
          <text class="select-title">选择预约课程</text>
          <text class="select-close" @click="showBookingSelect = false">✕</text>
        </view>
        
        <view class="select-list">
          <view 
            class="select-item" 
            v-for="booking in todayBookings" 
            :key="booking.id"
            :class="{ 'selected': selectedBooking?.id === booking.id }"
            @click="selectBooking(booking)"
          >
            <view class="select-info">
              <text class="select-name">{{ booking.class_?.name }}</text>
              <text class="select-meta">
                {{ formatTime(booking.class_?.start_time) }}-{{ formatTime(booking.class_?.end_time) }}
              </text>
            </view>
            <view class="select-check" v-if="selectedBooking?.id === booking.id">✓</view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { request, formatTime, formatDate, showToast, showLoading, hideLoading } from '@/utils/utils'

export default {
  data() {
    return {
      loading: false,
      todayBookings: [],
      recentCheckins: [],
      showFaceModal: false,
      showBookingSelect: false,
      selectedBooking: null,
      checkingIn: false,
      simulateFaceData: null,
      scannedQRCode: ''
    }
  },

  onShow() {
    this.loadData()
  },

  methods: {
    async loadData() {
      this.loading = true
      
      try {
        const [bookingRes, checkinRes] = await Promise.all([
          request.get('/bookings/my'),
          request.get('/checkin/my')
        ])
        
        const today = formatDate(new Date(), 'YYYY-MM-DD')
        this.todayBookings = (bookingRes.items || []).filter(b => {
          return b.status === 'confirmed' && b.class_?.class_date === today
        })
        
        this.recentCheckins = checkinRes || []
        
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },

    scanQRCode() {
      if (this.todayBookings.length === 0) {
        showToast('今日暂无预约课程')
        return
      }

      if (this.todayBookings.length === 1) {
        this.selectedBooking = this.todayBookings[0]
        this.performQRCodeScan()
      } else {
        this.showBookingSelect = true
      }
    },

    performQRCodeScan() {
      uni.scanCode({
        success: async (res) => {
          this.scannedQRCode = res.result
          await this.doQRCodeCheckin(this.scannedQRCode)
        },
        fail: (err) => {
          console.log('扫码失败:', err)
          this.simulateScan()
        }
      })
    },

    async simulateScan() {
      showLoading('模拟扫码中...')
      
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      hideLoading()
      
      const mockQRCode = 'ROOM_YOGA_A_001'
      await this.doQRCodeCheckin(mockQRCode)
    },

    async doQRCodeCheckin(qrCode) {
      if (!this.selectedBooking) return
      
      showLoading('签到中...')
      
      try {
        const res = await request.post('/checkin/qrcode', {
          qr_code: qrCode,
          booking_id: this.selectedBooking.id
        })
        
        hideLoading()
        showToast('签到成功', 'success')
        this.loadData()
        
      } catch (error) {
        hideLoading()
        console.error('签到失败:', error)
      }
    },

    showFaceCheckin() {
      if (this.todayBookings.length === 0) {
        showToast('今日暂无预约课程')
        return
      }

      if (this.todayBookings.length === 1) {
        this.selectedBooking = this.todayBookings[0]
        this.showFaceModal = true
      } else {
        this.showBookingSelect = true
      }
    },

    selectBooking(booking) {
      this.selectedBooking = booking
      this.showBookingSelect = false
      this.showFaceModal = true
    },

    takePhoto() {
      uni.chooseImage({
        count: 1,
        sourceType: ['camera'],
        success: (res) => {
          console.log('拍照成功:', res.tempFilePaths[0])
          this.simulateFaceData = 'face_image_data'
        }
      })
    },

    selectFromAlbum() {
      uni.chooseImage({
        count: 1,
        sourceType: ['album'],
        success: (res) => {
          console.log('选择图片成功:', res.tempFilePaths[0])
          this.simulateFaceData = 'face_image_data'
        }
      })
    },

    async confirmFaceCheckin() {
      if (!this.selectedBooking || !this.simulateFaceData) return
      
      this.checkingIn = true
      showLoading('签到中...')
      
      try {
        const res = await request.post('/checkin/face', {
          booking_id: this.selectedBooking.id,
          face_image: this.simulateFaceData
        })
        
        hideLoading()
        this.checkingIn = false
        this.showFaceModal = false
        this.simulateFaceData = null
        
        showToast('签到成功', 'success')
        this.loadData()
        
      } catch (error) {
        hideLoading()
        this.checkingIn = false
        console.error('签到失败:', error)
      }
    },

    quickCheckin(booking) {
      if (!this.isCheckinAvailable(booking)) return
      if (booking.checkin) return
      
      this.selectedBooking = booking
      this.scanQRCode()
    },

    isCheckinAvailable(booking) {
      if (!booking.class_) return false
      
      const classDate = booking.class_.class_date
      const startTime = booking.class_.start_time
      const today = formatDate(new Date(), 'YYYY-MM-DD')
      
      if (classDate !== today) return false
      
      const now = new Date()
      const [hours, minutes] = startTime.split(':').map(Number)
      const classStart = new Date(now.getFullYear(), now.getMonth(), now.getDate(), hours, minutes)
      
      const diffMinutes = (classStart - now) / (1000 * 60)
      
      return diffMinutes <= 30 && diffMinutes >= -15
    },

    getCheckinButtonText(booking) {
      if (booking.checkin) return '已签到'
      if (!this.isCheckinAvailable(booking)) return '签到未开始'
      return '签到'
    },

    getCheckinMethodText(method) {
      const methodMap = {
        'qrcode': '扫码签到',
        'face': '人脸识别'
      }
      return methodMap[method] || method
    },

    formatCheckinTime(timeStr) {
      if (!timeStr) return ''
      const date = new Date(timeStr)
      return `${date.getMonth() + 1}/${date.getDate()} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
    },

    goToHistory() {
      uni.navigateTo({
        url: '/pages/booking-history/booking-history'
      })
    }
  }
}
</script>

<style scoped>
.checkin-page {
  min-height: 100vh;
  background-color: #f3f4f6;
  padding-bottom: 40rpx;
}

.checkin-header {
  padding: 40rpx 30rpx;
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
}

.qrcode-placeholder {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qrcode-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.qrcode-text {
  font-size: 32rpx;
  color: #ffffff;
  font-weight: 500;
  margin-bottom: 10rpx;
}

.qrcode-hint {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.checkin-methods {
  background-color: #ffffff;
  margin: 20rpx;
  border-radius: 20rpx;
  padding: 30rpx;
}

.method-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 30rpx;
}

.method-list {
  display: flex;
  flex-direction: column;
  gap: 30rpx;
}

.method-item {
  display: flex;
  align-items: center;
  padding: 20rpx;
  border-radius: 16rpx;
  background-color: #f9fafb;
}

.method-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 24rpx;
}

.qrcode-icon-bg {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
}

.face-icon-bg {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.method-icon .icon {
  font-size: 40rpx;
}

.method-info {
  flex: 1;
}

.method-name {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 6rpx;
}

.method-desc {
  display: block;
  font-size: 24rpx;
  color: #9ca3af;
}

.method-arrow {
  font-size: 36rpx;
  color: #9ca3af;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
}

.section-more {
  font-size: 26rpx;
  color: #2563eb;
}

.recent-bookings,
.checkin-history {
  background-color: #ffffff;
  margin: 20rpx;
  border-radius: 20rpx;
  padding: 30rpx;
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60rpx;
}

.loading-text {
  color: #9ca3af;
  font-size: 28rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 40rpx;
}

.empty-state.small {
  padding: 40rpx;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 26rpx;
  color: #9ca3af;
}

.booking-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.booking-item:last-child {
  border-bottom: none;
}

.booking-info {
  flex: 1;
  margin-right: 20rpx;
}

.booking-time {
  margin-bottom: 8rpx;
}

.booking-time .start-time,
.booking-time .end-time {
  font-size: 28rpx;
  font-weight: 600;
  color: #2563eb;
}

.booking-time .time-sep {
  font-size: 24rpx;
  color: #9ca3af;
  margin: 0 8rpx;
}

.class-name {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 6rpx;
}

.class-meta {
  font-size: 24rpx;
  color: #9ca3af;
}

.btn-disabled {
  background-color: #e5e7eb;
  color: #9ca3af;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 2rpx solid #f3f4f6;
}

.history-item:last-child {
  border-bottom: none;
}

.history-class {
  font-size: 28rpx;
  color: #1f2937;
  margin-bottom: 6rpx;
}

.history-time {
  font-size: 24rpx;
  color: #9ca3af;
}

.method-badge {
  padding: 8rpx 16rpx;
  border-radius: 20rpx;
  font-size: 22rpx;
}

.qrcode-badge {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.face-badge {
  background-color: #d1fae5;
  color: #047857;
}

.face-modal,
.booking-select-modal {
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

.modal-content,
.select-content {
  width: 100%;
  max-width: 650rpx;
  background-color: #ffffff;
  border-radius: 24rpx;
  overflow: hidden;
  max-height: 80vh;
}

.modal-header,
.select-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.modal-title,
.select-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.modal-close,
.select-close {
  font-size: 36rpx;
  color: #9ca3af;
}

.modal-body {
  padding: 40rpx;
}

.face-preview {
  width: 300rpx;
  height: 300rpx;
  margin: 0 auto 40rpx;
  background-color: #f3f4f6;
  border-radius: 20rpx;
  border: 4rpx dashed #9ca3af;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.face-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.face-hint {
  font-size: 26rpx;
  color: #9ca3af;
}

.face-actions {
  display: flex;
  gap: 20rpx;
  margin-bottom: 30rpx;
}

.face-actions .btn {
  flex: 1;
}

.simulate-section {
  background-color: #d1fae5;
  border-radius: 16rpx;
  padding: 30rpx;
}

.face-result {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10rpx;
}

.result-icon {
  font-size: 40rpx;
  margin-right: 16rpx;
}

.result-text {
  font-size: 28rpx;
  color: #047857;
  font-weight: 500;
}

.simulate-hint {
  display: block;
  text-align: center;
  font-size: 22rpx;
  color: #6b7280;
}

.modal-footer {
  padding: 30rpx 40rpx;
  border-top: 2rpx solid #f3f4f6;
}

.select-list {
  max-height: 500rpx;
  overflow-y: auto;
  padding: 20rpx;
}

.select-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 16rpx;
  border: 2rpx solid #e5e7eb;
}

.select-item.selected {
  border-color: #2563eb;
  background-color: #eff6ff;
}

.select-info {
  flex: 1;
}

.select-name {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.select-meta {
  font-size: 24rpx;
  color: #9ca3af;
}

.select-check {
  width: 40rpx;
  height: 40rpx;
  background-color: #2563eb;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #ffffff;
  font-size: 24rpx;
}
</style>
