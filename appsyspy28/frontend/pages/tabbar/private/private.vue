<template>
  <view class="private-page">
    <view class="tabs">
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'coaches' }"
        @click="activeTab = 'coaches'"
      >
        约课
      </view>
      <view 
        class="tab-item" 
        :class="{ 'active': activeTab === 'bookings' }"
        @click="activeTab = 'bookings'"
      >
        我的预约
      </view>
    </view>

    <scroll-view scroll-y class="scroll-content" v-if="activeTab === 'coaches'">
      <view class="coach-list">
        <view class="section-title">选择教练</view>

        <view v-if="loadingCoaches" class="loading-container">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="coaches.length === 0" class="empty-state">
          <text class="empty-icon">👨‍🏫</text>
          <text class="empty-text">暂无可用教练</text>
        </view>

        <view v-else>
          <view 
            class="coach-card" 
            v-for="coach in coaches" 
            :key="coach.id"
            @click="selectCoach(coach)"
          >
            <view class="coach-avatar">
              <text class="avatar-icon">👤</text>
            </view>
            <view class="coach-info">
              <text class="coach-name">{{ coach.name }}</text>
              <text class="coach-role">私教教练</text>
            </view>
            <view class="coach-action">
              <text class="action-text">查看时段 ›</text>
            </view>
          </view>
        </view>
      </view>

      <view class="schedule-section" v-if="selectedCoach">
        <view class="section-header">
          <text class="section-title">{{ selectedCoach.name }}的可约时段</text>
          <view class="date-nav">
            <text class="nav-btn" @click="changeDate(-7)">‹</text>
            <text class="date-display">{{ currentWeekDisplay }}</text>
            <text class="nav-btn" @click="changeDate(7)">›</text>
          </view>
        </view>

        <view class="week-days">
          <view 
            class="day-item" 
            v-for="day in weekDates" 
            :key="day.dateStr"
            :class="{ 'active': selectedDate === day.dateStr, 'today': day.isToday }"
            @click="selectDate(day.dateStr)"
          >
            <text class="day-name">{{ day.weekDay }}</text>
            <text class="day-num">{{ day.day }}</text>
          </view>
        </view>

        <view class="time-slots">
          <view v-if="loadingSchedules" class="loading-container">
            <text class="loading-text">加载时段中...</text>
          </view>

          <view v-else-if="currentSchedules.length === 0" class="empty-state small">
            <text class="empty-text">该日期暂无可用时段</text>
          </view>

          <view v-else class="slot-grid">
            <view 
              class="slot-item" 
              v-for="slot in currentSchedules" 
              :key="slot.id"
              :class="{ 'booked': slot.is_booked, 'unavailable': !slot.is_available }"
              @click="selectSlot(slot)"
            >
              <text class="slot-time">{{ formatTime(slot.start_time) }}</text>
              <text class="slot-to">-</text>
              <text class="slot-time">{{ formatTime(slot.end_time) }}</text>
              <text class="slot-status" v-if="slot.is_booked">已约</text>
              <text class="slot-status unavailable" v-else-if="!slot.is_available">不可约</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <scroll-view scroll-y class="scroll-content" v-else>
      <view class="bookings-list">
        <view v-if="loadingBookings" class="loading-container">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="myBookings.length === 0" class="empty-state">
          <text class="empty-icon">📅</text>
          <text class="empty-text">暂无私教预约</text>
        </view>

        <view v-else>
          <view 
            class="booking-card" 
            v-for="booking in myBookings" 
            :key="booking.id"
          >
            <view class="booking-header">
              <text class="class-name">{{ booking.class_name }}</text>
              <view 
                class="status-tag" 
                :class="getStatusClass(booking.status)"
              >
                {{ getStatusText(booking.status) }}
              </view>
            </view>

            <view class="booking-body">
              <view class="info-row">
                <view class="info-item">
                  <text class="info-icon">👨‍🏫</text>
                  <text class="info-text">{{ booking.coach?.name || '教练' }}</text>
                </view>
              </view>

              <view class="info-row">
                <view class="info-item">
                  <text class="info-icon">📅</text>
                  <text class="info-text">
                    {{ booking.schedule?.schedule_date }} 
                    {{ formatTime(booking.schedule?.start_time) }}-{{ formatTime(booking.schedule?.end_time) }}
                  </text>
                </view>
              </view>

              <view class="info-row" v-if="booking.location">
                <view class="info-item">
                  <text class="info-icon">📍</text>
                  <text class="info-text">{{ booking.location }}</text>
                </view>
              </view>

              <view class="info-row" v-if="booking.member_notes">
                <view class="info-item">
                  <text class="info-icon">💬</text>
                  <text class="info-text">备注：{{ booking.member_notes }}</text>
                </view>
              </view>

              <view class="info-row" v-if="booking.coach_notes">
                <view class="info-item">
                  <text class="info-icon">📝</text>
                  <text class="info-text">教练备注：{{ booking.coach_notes }}</text>
                </view>
              </view>
            </view>

            <view class="booking-footer" v-if="booking.status === 'pending' || booking.status === 'confirmed'">
              <button 
                class="btn btn-danger btn-sm"
                v-if="booking.status === 'confirmed'"
                @click="cancelBooking(booking)"
              >
                取消预约
              </button>
              <button 
                class="btn btn-outline btn-sm"
                v-if="booking.status === 'pending'"
                @click="cancelBooking(booking)"
              >
                取消申请
              </button>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="booking-modal" v-if="showBookingModal" @click.self="showBookingModal = false">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">预约私教课</text>
          <text class="modal-close" @click="showBookingModal = false">✕</text>
        </view>

        <view class="modal-body">
          <view class="booking-summary">
            <view class="summary-row">
              <text class="summary-label">教练</text>
              <text class="summary-value">{{ selectedCoach?.name }}</text>
            </view>
            <view class="summary-row">
              <text class="summary-label">日期</text>
              <text class="summary-value">{{ selectedDate }}</text>
            </view>
            <view class="summary-row">
              <text class="summary-label">时间</text>
              <text class="summary-value">
                {{ formatTime(selectedSlot?.start_time) }} - {{ formatTime(selectedSlot?.end_time) }}
              </text>
            </view>
          </view>

          <view class="form-item">
            <text class="form-label">课程名称 *</text>
            <input 
              class="form-input" 
              v-model="bookingForm.class_name" 
              placeholder="请输入课程名称"
            />
          </view>

          <view class="form-item">
            <text class="form-label">课程描述</text>
            <textarea 
              class="form-textarea"
              v-model="bookingForm.class_description"
              placeholder="请描述您的训练需求"
              :maxlength="200"
            ></textarea>
          </view>

          <view class="form-item">
            <text class="form-label">地点</text>
            <input 
              class="form-input" 
              v-model="bookingForm.location" 
              placeholder="请输入训练地点（选填）"
            />
          </view>

          <view class="form-item">
            <text class="form-label">备注</text>
            <textarea 
              class="form-textarea"
              v-model="bookingForm.member_notes"
              placeholder="其他备注信息（选填）"
              :maxlength="100"
            ></textarea>
          </view>
        </view>

        <view class="modal-footer">
          <button 
            class="btn btn-primary btn-lg btn-block"
            :loading="submitting"
            @click="submitBooking"
          >
            确认预约
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { request, formatTime, formatDate, showToast, showLoading, hideLoading, showModal } from '@/utils/utils'

export default {
  data() {
    return {
      activeTab: 'coaches',
      currentDate: new Date(),
      selectedDate: formatDate(new Date(), 'YYYY-MM-DD'),
      weekDates: [],
      currentWeekDisplay: '',
      coaches: [],
      schedules: [],
      myBookings: [],
      selectedCoach: null,
      selectedSlot: null,
      loadingCoaches: false,
      loadingSchedules: false,
      loadingBookings: false,
      showBookingModal: false,
      submitting: false,
      bookingForm: {
        class_name: '',
        class_description: '',
        location: '',
        member_notes: ''
      }
    }
  },

  computed: {
    currentSchedules() {
      return this.schedules.filter(s => s.schedule_date === this.selectedDate)
    }
  },

  onShow() {
    this.initWeekDates()
    this.loadCoaches()
    this.loadMyBookings()
  },

  methods: {
    initWeekDates() {
      const dates = this.getWeekDates(this.currentDate)
      this.weekDates = dates.map(d => ({
        ...d,
        isToday: formatDate(d.date, 'YYYY-MM-DD') === formatDate(new Date(), 'YYYY-MM-DD')
      }))
      this.updateWeekDisplay()
    },

    getWeekDates(baseDate) {
      const currentDay = baseDate.getDay()
      const dates = []
      const weekDays = ['日', '一', '二', '三', '四', '五', '六']

      for (let i = 0; i < 7; i++) {
        const diff = i - currentDay
        const date = new Date(baseDate)
        date.setDate(baseDate.getDate() + diff)
        dates.push({
          date,
          dateStr: formatDate(date, 'YYYY-MM-DD'),
          day: date.getDate(),
          weekDay: weekDays[i]
        })
      }
      return dates
    },

    updateWeekDisplay() {
      const firstDay = this.weekDates[0].date
      const lastDay = this.weekDates[6].date
      this.currentWeekDisplay = `${firstDay.getMonth() + 1}/${firstDay.getDate()} - ${lastDay.getMonth() + 1}/${lastDay.getDate()}`
    },

    changeDate(direction) {
      const newDate = new Date(this.currentDate)
      newDate.setDate(newDate.getDate() + direction)
      this.currentDate = newDate
      this.initWeekDates()
      this.selectedDate = this.weekDates[Math.min(6, Math.max(0, this.weekDates.findIndex(d => d.dateStr === this.selectedDate)))]?.dateStr || this.weekDates[0].dateStr
      
      if (this.selectedCoach) {
        this.loadSchedules()
      }
    },

    selectDate(dateStr) {
      this.selectedDate = dateStr
    },

    async loadCoaches() {
      this.loadingCoaches = true
      
      try {
        const res = await request.get('/private/coaches')
        this.coaches = res || []
      } catch (error) {
        console.error('加载教练失败:', error)
      } finally {
        this.loadingCoaches = false
      }
    },

    selectCoach(coach) {
      this.selectedCoach = coach
      this.loadSchedules()
    },

    async loadSchedules() {
      if (!this.selectedCoach) return
      
      this.loadingSchedules = true
      
      try {
        const startDate = this.weekDates[0].dateStr
        
        const res = await request.get(`/private/schedules/${this.selectedCoach.id}`, {
          start_date: startDate
        })
        
        this.schedules = res || []
      } catch (error) {
        console.error('加载时段失败:', error)
      } finally {
        this.loadingSchedules = false
      }
    },

    selectSlot(slot) {
      if (slot.is_booked || !slot.is_available) {
        showToast('该时段不可约')
        return
      }
      
      this.selectedSlot = slot
      this.showBookingModal = true
    },

    async loadMyBookings() {
      this.loadingBookings = true
      
      try {
        const res = await request.get('/private/my-bookings')
        this.myBookings = res || []
      } catch (error) {
        console.error('加载预约失败:', error)
      } finally {
        this.loadingBookings = false
      }
    },

    async submitBooking() {
      if (!this.bookingForm.class_name.trim()) {
        showToast('请输入课程名称')
        return
      }
      
      this.submitting = true
      showLoading('预约中...')
      
      try {
        const bookingData = {
          coach_id: this.selectedCoach.id,
          schedule_id: this.selectedSlot.id,
          class_name: this.bookingForm.class_name,
          class_description: this.bookingForm.class_description,
          location: this.bookingForm.location,
          member_notes: this.bookingForm.member_notes
        }
        
        const res = await request.post('/private/book', bookingData)
        
        hideLoading()
        
        showToast('预约成功，等待教练确认', 'success')
        this.showBookingModal = false
        this.bookingForm = {
          class_name: '',
          class_description: '',
          location: '',
          member_notes: ''
        }
        this.activeTab = 'bookings'
        this.loadMyBookings()
        this.loadSchedules()
        
      } catch (error) {
        hideLoading()
        console.error('预约失败:', error)
      } finally {
        this.submitting = false
      }
    },

    async cancelBooking(booking) {
      const confirmed = await showModal('确认取消', '确定要取消这个预约吗？', true)
      
      if (!confirmed) return
      
      showLoading('取消中...')
      
      try {
        const res = await request.delete(`/private/${booking.id}`, {
          cancel_reason: '会员主动取消'
        })
        
        hideLoading()
        
        if (res.success) {
          showToast('取消成功', 'success')
          this.loadMyBookings()
        } else {
          showToast(res.message || '取消失败')
        }
      } catch (error) {
        hideLoading()
        console.error('取消失败:', error)
      }
    },

    getStatusText(status) {
      const statusMap = {
        'pending': '待确认',
        'confirmed': '已确认',
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
    }
  }
}
</script>

<style scoped>
.private-page {
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

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 20rpx;
  padding: 0 10rpx;
}

.coach-list,
.bookings-list {
  background-color: #ffffff;
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
  padding: 80rpx 40rpx;
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

.coach-card {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background-color: #f9fafb;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
}

.coach-avatar {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 24rpx;
}

.avatar-icon {
  font-size: 50rpx;
}

.coach-info {
  flex: 1;
}

.coach-name {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.coach-role {
  font-size: 24rpx;
  color: #9ca3af;
}

.action-text {
  font-size: 26rpx;
  color: #2563eb;
}

.schedule-section {
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-top: 20rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.date-nav {
  display: flex;
  align-items: center;
}

.nav-btn {
  font-size: 32rpx;
  color: #2563eb;
  padding: 10rpx 20rpx;
}

.date-display {
  font-size: 26rpx;
  color: #6b7280;
  margin: 0 10rpx;
}

.week-days {
  display: flex;
  justify-content: space-around;
  background-color: #f9fafb;
  border-radius: 16rpx;
  padding: 16rpx 10rpx;
  margin-bottom: 24rpx;
}

.day-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12rpx 16rpx;
  border-radius: 12rpx;
}

.day-item.active {
  background-color: #2563eb;
}

.day-item.today {
  background-color: #dbeafe;
}

.day-item.active.today {
  background-color: #2563eb;
}

.day-name {
  font-size: 20rpx;
  color: #6b7280;
  margin-bottom: 6rpx;
}

.day-item.active .day-name,
.day-item.today .day-name {
  color: #ffffff;
}

.day-num {
  font-size: 28rpx;
  font-weight: 600;
  color: #1f2937;
}

.day-item.active .day-num,
.day-item.today .day-num {
  color: #ffffff;
}

.slot-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.slot-item {
  width: calc(33.333% - 12rpx);
  padding: 20rpx 10rpx;
  background-color: #f9fafb;
  border-radius: 12rpx;
  text-align: center;
  border: 2rpx solid #e5e7eb;
}

.slot-item.booked,
.slot-item.unavailable {
  opacity: 0.5;
  pointer-events: none;
}

.slot-time {
  font-size: 24rpx;
  font-weight: 500;
  color: #1f2937;
}

.slot-to {
  font-size: 20rpx;
  color: #9ca3af;
  margin: 0 4rpx;
}

.slot-status {
  display: block;
  font-size: 20rpx;
  color: #ef4444;
  margin-top: 6rpx;
}

.slot-status.unavailable {
  color: #9ca3af;
}

.booking-card {
  background-color: #f9fafb;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx;
  border-bottom: 2rpx solid #e5e7eb;
}

.class-name {
  font-size: 30rpx;
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
  padding: 24rpx;
}

.info-row {
  margin-bottom: 16rpx;
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

.booking-footer {
  padding: 20rpx 24rpx;
  border-top: 2rpx solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
}

.booking-modal {
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
  max-width: 650rpx;
  max-height: 80vh;
  background-color: #ffffff;
  border-radius: 24rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 40rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.modal-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.modal-close {
  font-size: 36rpx;
  color: #9ca3af;
}

.modal-body {
  flex: 1;
  padding: 30rpx 40rpx;
  overflow-y: auto;
}

.booking-summary {
  background-color: #f9fafb;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 30rpx;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.summary-row:last-child {
  margin-bottom: 0;
}

.summary-label {
  font-size: 26rpx;
  color: #6b7280;
}

.summary-value {
  font-size: 26rpx;
  color: #1f2937;
  font-weight: 500;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 12rpx;
  font-weight: 500;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background-color: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  height: 160rpx;
  padding: 20rpx 24rpx;
  background-color: #f9fafb;
  border: 2rpx solid #e5e7eb;
  border-radius: 12rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.modal-footer {
  padding: 30rpx 40rpx;
  border-top: 2rpx solid #f3f4f6;
}
</style>
