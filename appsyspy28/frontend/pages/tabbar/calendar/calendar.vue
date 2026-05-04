<template>
  <view class="calendar-page">
    <view class="week-selector">
      <view class="header-row">
        <text class="prev-btn" @click="changeWeek(-1)">‹</text>
        <text class="week-title">{{ currentMonth }}</text>
        <text class="next-btn" @click="changeWeek(1)">›</text>
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
          <view class="dot" v-if="day.hasClass"></view>
        </view>
      </view>
    </view>

    <view class="view-toggle">
      <view 
        class="toggle-item" 
        :class="{ 'active': viewMode === 'day' }"
        @click="viewMode = 'day'"
      >
        日视图
      </view>
      <view 
        class="toggle-item" 
        :class="{ 'active': viewMode === 'week' }"
        @click="viewMode = 'week'"
      >
        周视图
      </view>
    </view>

    <view class="class-list" v-if="viewMode === 'day'">
      <scroll-view scroll-y class="scroll-content">
        <view v-if="loading" class="loading-container">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else-if="dayClasses.length === 0" class="empty-state">
          <text class="empty-icon">📅</text>
          <text class="empty-text">今日暂无课程</text>
        </view>

        <view v-else>
          <view 
            class="class-card" 
            v-for="classItem in dayClasses" 
            :key="classItem.id"
            @click="goToDetail(classItem)"
          >
            <view class="class-time">
              <text class="start-time">{{ formatTime(classItem.start_time) }}</text>
              <view class="time-line"></view>
              <text class="end-time">{{ formatTime(classItem.end_time) }}</text>
            </view>

            <view class="class-info">
              <view class="class-header">
                <text class="class-name">{{ classItem.name }}</text>
                <view 
                  class="capacity-tag" 
                  :class="{ 'full': classItem.booked_count >= classItem.capacity }"
                >
                  剩余 {{ classItem.capacity - classItem.booked_count }} 人
                </view>
              </view>

              <view class="class-meta">
                <view class="meta-item">
                  <text class="meta-icon">👨‍🏫</text>
                  <text class="meta-text">{{ classItem.coach?.name || '待分配' }}</text>
                </view>
                <view class="meta-item">
                  <text class="meta-icon">📍</text>
                  <text class="meta-text">{{ classItem.room?.name || '待确认' }}</text>
                </view>
              </view>

              <view class="class-tags">
                <view class="tag" v-if="classItem.category">
                  {{ classItem.category.name }}
                </view>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>

    <view class="week-view" v-else>
      <scroll-view scroll-y class="scroll-content">
        <view v-if="loading" class="loading-container">
          <text class="loading-text">加载中...</text>
        </view>

        <view v-else>
          <view class="day-section" v-for="day in weekDates" :key="day.dateStr">
            <view class="day-header" :class="{ 'today': day.isToday }">
              <text class="day-name">{{ day.weekDay }}</text>
              <text class="day-date">{{ day.day }}日</text>
            </view>

            <view class="day-classes">
              <view 
                class="week-class-card" 
                v-for="classItem in getClassesByDate(day.dateStr)" 
                :key="classItem.id"
                @click="goToDetail(classItem)"
              >
                <view class="week-class-time">
                  {{ formatTime(classItem.start_time) }}
                </view>
                <view class="week-class-info">
                  <text class="week-class-name">{{ classItem.name }}</text>
                  <text class="week-class-meta">
                    {{ classItem.coach?.name || '' }} · {{ classItem.room?.name || '' }}
                  </text>
                </view>
                <view 
                  class="week-class-status"
                  :class="{ 'full': classItem.booked_count >= classItem.capacity }"
                >
                  {{ classItem.capacity - classItem.booked_count > 0 ? '可约' : '满' }}
                </view>
              </view>

              <view class="empty-day" v-if="getClassesByDate(day.dateStr).length === 0">
                <text>暂无课程</text>
              </view>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
import { request, formatDate, formatTime, showToast } from '@/utils/utils'
import { useUserStore } from '@/store/user'

export default {
  data() {
    return {
      currentDate: new Date(),
      selectedDate: formatDate(new Date(), 'YYYY-MM-DD'),
      viewMode: 'day',
      weekDates: [],
      dayClasses: [],
      weekClasses: [],
      loading: false,
      currentMonth: ''
    }
  },

  onLoad() {
    this.initWeekDates()
  },

  onShow() {
    this.checkLogin()
    this.loadClasses()
  },

  methods: {
    checkLogin() {
      const token = uni.getStorageSync('token')
      if (!token) {
        uni.reLaunch({
          url: '/pages/login/login'
        })
      }
    },

    initWeekDates() {
      const dates = this.getWeekDates(this.currentDate)
      this.weekDates = dates.map(d => ({
        ...d,
        isToday: formatDate(d.date, 'YYYY-MM-DD') === formatDate(new Date(), 'YYYY-MM-DD'),
        hasClass: false
      }))
      this.updateMonthDisplay()
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

    updateMonthDisplay() {
      const firstDay = this.weekDates[0].date
      const lastDay = this.weekDates[6].date
      
      const firstMonth = firstDay.getMonth() + 1
      const lastMonth = lastDay.getMonth() + 1
      
      if (firstMonth === lastMonth) {
        this.currentMonth = `${firstDay.getFullYear()}年${firstMonth}月`
      } else {
        this.currentMonth = `${firstDay.getFullYear()}年${firstMonth}月 - ${lastMonth}月`
      }
    },

    changeWeek(direction) {
      const newDate = new Date(this.currentDate)
      newDate.setDate(newDate.getDate() + direction * 7)
      this.currentDate = newDate
      this.initWeekDates()
      this.loadClasses()
    },

    selectDate(dateStr) {
      this.selectedDate = dateStr
      this.viewMode = 'day'
    },

    async loadClasses() {
      this.loading = true
      
      try {
        const startDate = this.weekDates[0].dateStr
        const endDate = this.weekDates[6].dateStr

        const res = await request.get('/classes/calendar/range', {
          start_date: startDate,
          end_date: endDate
        })

        this.weekClasses = res.items || []
        
        this.weekDates.forEach(day => {
          day.hasClass = this.weekClasses.some(c => c.class_date === day.dateStr)
        })

        this.dayClasses = this.weekClasses.filter(c => c.class_date === this.selectedDate)

      } catch (error) {
        console.error('加载课程失败:', error)
        showToast('加载课程失败')
      } finally {
        this.loading = false
      }
    },

    getClassesByDate(dateStr) {
      return this.weekClasses.filter(c => c.class_date === dateStr)
    },

    goToDetail(classItem) {
      uni.navigateTo({
        url: `/pages/class-detail/class-detail?id=${classItem.id}`
      })
    }
  }
}
</script>

<style scoped>
.calendar-page {
  min-height: 100vh;
  background-color: #f3f4f6;
  display: flex;
  flex-direction: column;
}

.week-selector {
  background-color: #ffffff;
  padding: 20rpx 0;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 30rpx;
  margin-bottom: 20rpx;
}

.prev-btn, .next-btn {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40rpx;
  color: #2563eb;
  font-weight: bold;
}

.week-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.week-days {
  display: flex;
  justify-content: space-around;
  padding: 0 10rpx;
}

.day-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 20rpx;
  border-radius: 16rpx;
  position: relative;
  transition: all 0.3s ease;
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
  font-size: 22rpx;
  color: #6b7280;
  margin-bottom: 8rpx;
}

.day-item.active .day-name,
.day-item.today .day-name {
  color: #ffffff;
}

.day-num {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.day-item.active .day-num,
.day-item.today .day-num {
  color: #ffffff;
}

.dot {
  width: 8rpx;
  height: 8rpx;
  background-color: #ef4444;
  border-radius: 50%;
  margin-top: 8rpx;
}

.day-item.active .dot,
.day-item.today .dot {
  background-color: #ffffff;
}

.view-toggle {
  display: flex;
  background-color: #f3f4f6;
  padding: 20rpx;
  gap: 20rpx;
}

.toggle-item {
  flex: 1;
  text-align: center;
  padding: 20rpx;
  background-color: #ffffff;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #6b7280;
  transition: all 0.3s ease;
}

.toggle-item.active {
  background-color: #2563eb;
  color: #ffffff;
  font-weight: 500;
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

.class-card {
  display: flex;
  background-color: #ffffff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.class-time {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 120rpx;
  padding-right: 30rpx;
  border-right: 2rpx solid #e5e7eb;
}

.start-time {
  font-size: 32rpx;
  font-weight: 600;
  color: #2563eb;
}

.time-line {
  width: 4rpx;
  height: 40rpx;
  background-color: #dbeafe;
  margin: 10rpx 0;
}

.end-time {
  font-size: 24rpx;
  color: #9ca3af;
}

.class-info {
  flex: 1;
  padding-left: 30rpx;
}

.class-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16rpx;
}

.class-name {
  font-size: 34rpx;
  font-weight: 600;
  color: #1f2937;
  flex: 1;
}

.capacity-tag {
  padding: 6rpx 16rpx;
  background-color: #d1fae5;
  color: #047857;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 500;
}

.capacity-tag.full {
  background-color: #fee2e2;
  color: #b91c1c;
}

.class-meta {
  display: flex;
  gap: 30rpx;
  margin-bottom: 16rpx;
}

.meta-item {
  display: flex;
  align-items: center;
  font-size: 26rpx;
  color: #6b7280;
}

.meta-icon {
  margin-right: 8rpx;
}

.class-tags {
  display: flex;
  flex-wrap: wrap;
}

.tag {
  padding: 6rpx 16rpx;
  background-color: #dbeafe;
  color: #1d4ed8;
  border-radius: 8rpx;
  font-size: 22rpx;
}

.day-section {
  margin-bottom: 30rpx;
}

.day-header {
  display: flex;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: #ffffff;
  border-radius: 16rpx 16rpx 0 0;
  margin-bottom: 2rpx;
}

.day-header.today {
  background-color: #dbeafe;
}

.day-header .day-name {
  font-size: 28rpx;
  font-weight: 500;
  color: #6b7280;
  margin-right: 16rpx;
}

.day-header.today .day-name {
  color: #1d4ed8;
}

.day-header .day-date {
  font-size: 28rpx;
  font-weight: 600;
  color: #1f2937;
}

.day-classes {
  background-color: #ffffff;
  border-radius: 0 0 16rpx 16rpx;
}

.week-class-card {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.week-class-card:last-child {
  border-bottom: none;
}

.week-class-time {
  width: 120rpx;
  font-size: 26rpx;
  font-weight: 500;
  color: #2563eb;
}

.week-class-info {
  flex: 1;
}

.week-class-name {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.week-class-meta {
  font-size: 24rpx;
  color: #9ca3af;
}

.week-class-status {
  padding: 8rpx 20rpx;
  background-color: #d1fae5;
  color: #047857;
  border-radius: 20rpx;
  font-size: 22rpx;
  font-weight: 500;
}

.week-class-status.full {
  background-color: #fee2e2;
  color: #b91c1c;
}

.empty-day {
  padding: 40rpx;
  text-align: center;
  font-size: 26rpx;
  color: #9ca3af;
}
</style>
