<template>
  <view class="mine-page">
    <view class="user-header">
      <view class="user-info" v-if="userInfo">
        <view class="user-avatar">
          <text class="avatar-icon">{{ userInfo.name?.charAt(0) || '?' }}</text>
        </view>
        <view class="user-detail">
          <text class="user-name">{{ userInfo.name }}</text>
          <text class="user-role">{{ getRoleText(userInfo.role) }}</text>
          <text class="user-phone">{{ userInfo.phone }}</text>
        </view>
      </view>
    </view>

    <view class="stats-section" v-if="userInfo?.role === 'member'">
      <view class="stat-item" @click="goToBookings">
        <text class="stat-value">{{ stats.totalBookings }}</text>
        <text class="stat-label">已预约</text>
      </view>
      <view class="stat-item" @click="goToHistory">
        <text class="stat-value">{{ stats.completedBookings }}</text>
        <text class="stat-label">已完成</text>
      </view>
      <view class="stat-item" @click="goToCards">
        <text class="stat-value">{{ stats.validCards }}</text>
        <text class="stat-label">有效卡</text>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-item" @click="goToBookings">
        <view class="menu-icon booking-icon">
          <text>📅</text>
        </view>
        <view class="menu-info">
          <text class="menu-title">我的预约</text>
          <text class="menu-desc">查看已预约的课程</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @click="goToCards">
        <view class="menu-icon card-icon">
          <text>💳</text>
        </view>
        <view class="menu-info">
          <text class="menu-title">我的会员卡</text>
          <text class="menu-desc">查看和管理会员卡</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @click="goToHistory">
        <view class="menu-icon history-icon">
          <text>📋</text>
        </view>
        <view class="menu-info">
          <text class="menu-title">历史记录</text>
          <text class="menu-desc">查看预约历史</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <view class="menu-section">
      <view class="menu-item" @click="goToFeedback">
        <view class="menu-icon feedback-icon">
          <text>💬</text>
        </view>
        <view class="menu-info">
          <text class="menu-title">意见反馈</text>
          <text class="menu-desc">提交您的建议</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>

      <view class="menu-item" @click="goToAbout">
        <view class="menu-icon about-icon">
          <text>ℹ️</text>
        </view>
        <view class="menu-info">
          <text class="menu-title">关于我们</text>
          <text class="menu-desc">版本 1.0.0</text>
        </view>
        <text class="menu-arrow">›</text>
      </view>
    </view>

    <view class="logout-section">
      <button class="logout-btn" @click="handleLogout">
        退出登录
      </button>
    </view>

    <view class="cards-modal" v-if="showCardsModal" @click.self="showCardsModal = false">
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">我的会员卡</text>
          <text class="modal-close" @click="showCardsModal = false">✕</text>
        </view>

        <scroll-view scroll-y class="cards-list">
          <view v-if="loadingCards" class="loading-container">
            <text class="loading-text">加载中...</text>
          </view>

          <view v-else-if="myCards.length === 0" class="empty-state">
            <text class="empty-icon">💳</text>
            <text class="empty-text">暂无会员卡</text>
          </view>

          <view v-else>
            <view 
              class="card-item" 
              v-for="card in myCards" 
              :key="card.id"
              :class="{ 'inactive': !card.is_active }"
            >
              <view class="card-header">
                <text class="card-name">{{ card.card_name }}</text>
                <view class="card-type-tag" :class="getCardTypeClass(card.card_type)">
                  {{ getCardTypeText(card.card_type) }}
                </view>
              </view>

              <view class="card-body">
                <view class="card-times" v-if="card.total_times">
                  <text class="used">{{ card.used_times }}</text>
                  <text class="sep">/</text>
                  <text class="total">{{ card.total_times }}</text>
                  <text class="unit">次</text>
                </view>
                <view class="card-validity" v-else>
                  <text class="valid-text">有效期内</text>
                </view>
              </view>

              <view class="card-footer">
                <text class="date-text">{{ card.start_date }} 至 {{ card.end_date }}</text>
                <view class="status-dot" :class="card.is_active ? 'active' : 'inactive'"></view>
              </view>

              <view class="card-categories" v-if="card.categories?.length > 0">
                <text class="category-tag" v-for="cat in card.categories" :key="cat.id">
                  {{ cat.name }}
                </text>
              </view>
            </view>
          </view>
        </scroll-view>
      </view>
    </view>
  </view>
</template>

<script>
import { request, showToast, showModal } from '@/utils/utils'
import { useUserStore } from '@/store/user'

export default {
  data() {
    return {
      userInfo: null,
      stats: {
        totalBookings: 0,
        completedBookings: 0,
        validCards: 0
      },
      myCards: [],
      loadingCards: false,
      showCardsModal: false
    }
  },

  onShow() {
    this.loadUserInfo()
    this.loadStats()
  },

  methods: {
    userStore() {
      return useUserStore()
    },

    async loadUserInfo() {
      const storedUser = uni.getStorageSync('userInfo')
      if (storedUser) {
        this.userInfo = storedUser
      }
      
      try {
        const res = await request.get('/auth/me')
        this.userInfo = res
        uni.setStorageSync('userInfo', res)
      } catch (error) {
        console.error('加载用户信息失败:', error)
      }
    },

    async loadStats() {
      try {
        const [bookingsRes, cardsRes] = await Promise.all([
          request.get('/bookings/my'),
          request.get('/cards/my-valid')
        ])
        
        const bookings = bookingsRes.items || []
        this.stats.totalBookings = bookings.filter(b => b.status === 'confirmed').length
        this.stats.completedBookings = bookings.filter(b => b.status === 'completed').length
        this.stats.validCards = (cardsRes || []).length
        
      } catch (error) {
        console.error('加载统计失败:', error)
      }
    },

    getRoleText(role) {
      const roleMap = {
        'member': '会员',
        'coach': '教练',
        'admin': '管理员'
      }
      return roleMap[role] || role
    },

    getCardTypeText(type) {
      const typeMap = {
        'monthly': '月卡',
        'yearly': '年卡',
        'times': '次卡',
        'group': '团课卡',
        'private': '私教课卡'
      }
      return typeMap[type] || type
    },

    getCardTypeClass(type) {
      const classMap = {
        'monthly': 'type-monthly',
        'yearly': 'type-yearly',
        'times': 'type-times',
        'group': 'type-group',
        'private': 'type-private'
      }
      return classMap[type] || 'type-default'
    },

    goToBookings() {
      uni.switchTab({
        url: '/pages/tabbar/booking/booking'
      })
    },

    goToHistory() {
      uni.navigateTo({
        url: '/pages/booking-history/booking-history'
      })
    },

    async goToCards() {
      this.showCardsModal = true
      await this.loadMyCards()
    },

    async loadMyCards() {
      this.loadingCards = true
      
      try {
        const res = await request.get('/cards/my')
        this.myCards = res || []
      } catch (error) {
        console.error('加载会员卡失败:', error)
      } finally {
        this.loadingCards = false
      }
    },

    goToFeedback() {
      showToast('功能开发中')
    },

    goToAbout() {
      showToast('健身预约系统 v1.0.0')
    },

    async handleLogout() {
      const confirmed = await showModal('退出登录', '确定要退出登录吗？', true)
      
      if (confirmed) {
        this.userStore().logout()
      }
    }
  }
}
</script>

<style scoped>
.mine-page {
  min-height: 100vh;
  background-color: #f3f4f6;
  padding-bottom: 40rpx;
}

.user-header {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  padding: 60rpx 40rpx;
}

.user-info {
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 140rpx;
  height: 140rpx;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 30rpx;
}

.avatar-icon {
  font-size: 60rpx;
  color: #ffffff;
  font-weight: bold;
}

.user-detail {
  flex: 1;
}

.user-name {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #ffffff;
  margin-bottom: 10rpx;
}

.user-role {
  display: inline-block;
  padding: 6rpx 16rpx;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #ffffff;
  margin-bottom: 10rpx;
}

.user-phone {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.stats-section {
  display: flex;
  background-color: #ffffff;
  margin: -30rpx 30rpx 30rpx;
  border-radius: 20rpx;
  padding: 30rpx 0;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.08);
  position: relative;
  z-index: 10;
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #2563eb;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 24rpx;
  color: #6b7280;
}

.menu-section {
  background-color: #ffffff;
  margin: 20rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 24rpx;
}

.booking-icon {
  background-color: #dbeafe;
}

.card-icon {
  background-color: #d1fae5;
}

.history-icon {
  background-color: #fef3c7;
}

.feedback-icon {
  background-color: #ede9fe;
}

.about-icon {
  background-color: #f3f4f6;
}

.menu-icon text {
  font-size: 36rpx;
}

.menu-info {
  flex: 1;
}

.menu-title {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 6rpx;
}

.menu-desc {
  font-size: 24rpx;
  color: #9ca3af;
}

.menu-arrow {
  font-size: 32rpx;
  color: #d1d5db;
}

.logout-section {
  padding: 40rpx;
  margin-top: 20rpx;
}

.logout-btn {
  width: 100%;
  height: 96rpx;
  background-color: #ffffff;
  color: #ef4444;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 500;
  border: none;
}

.cards-modal {
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

.cards-list {
  flex: 1;
  padding: 20rpx;
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

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 26rpx;
  color: #9ca3af;
}

.card-item {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  position: relative;
  overflow: hidden;
}

.card-item.inactive {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  opacity: 0.7;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30rpx;
}

.card-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #ffffff;
}

.card-type-tag {
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
  background-color: rgba(255, 255, 255, 0.3);
  color: #ffffff;
}

.card-body {
  margin-bottom: 20rpx;
}

.card-times {
  display: flex;
  align-items: baseline;
}

.card-times .used {
  font-size: 56rpx;
  font-weight: bold;
  color: #ffffff;
}

.card-times .sep {
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 8rpx;
}

.card-times .total {
  font-size: 36rpx;
  color: rgba(255, 255, 255, 0.8);
}

.card-times .unit {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 8rpx;
}

.card-validity {
  display: flex;
  align-items: center;
}

.valid-text {
  font-size: 28rpx;
  color: #ffffff;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 2rpx solid rgba(255, 255, 255, 0.2);
}

.date-text {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

.status-dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
}

.status-dot.active {
  background-color: #10b981;
}

.status-dot.inactive {
  background-color: #ef4444;
}

.card-categories {
  display: flex;
  flex-wrap: wrap;
  margin-top: 16rpx;
  gap: 10rpx;
}

.category-tag {
  padding: 4rpx 12rpx;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 8rpx;
  font-size: 20rpx;
  color: #ffffff;
}
</style>
