<template>
  <view class="profile-container">
    <view class="header-section">
      <view class="user-info">
        <view class="avatar">
          <text class="avatar-text">{{ userNickname.charAt(0) }}</text>
        </view>
        <view class="info">
          <text class="nickname">{{ userNickname }}</text>
          <text class="username">@{{ userInfo.username }}</text>
        </view>
      </view>
      
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ stats.sessions }}</text>
          <text class="stat-label">训练次数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.hours }}</text>
          <text class="stat-label">训练时长</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.calories }}</text>
          <text class="stat-label">消耗卡</text>
        </view>
      </view>
    </view>
    
    <view class="menu-section">
      <view class="menu-group">
        <text class="group-title">我的数据</text>
        <view class="menu-item" @click="goToMeasurement">
          <view class="menu-left">
            <text class="menu-icon">📊</text>
            <text class="menu-text">体测记录</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToTraining">
          <view class="menu-left">
            <text class="menu-icon">🏋️</text>
            <text class="menu-text">训练日志</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="goToGoal">
          <view class="menu-left">
            <text class="menu-icon">🎯</text>
            <text class="menu-text">目标管理</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
      </view>
      
      <view class="menu-group">
        <text class="group-title">账户设置</text>
        <view class="menu-item" @click="showEditProfile">
          <view class="menu-left">
            <text class="menu-icon">⚙️</text>
            <text class="menu-text">个人资料</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
        <view class="menu-item" @click="showAbout">
          <view class="menu-left">
            <text class="menu-icon">ℹ️</text>
            <text class="menu-text">关于我们</text>
          </view>
          <text class="menu-arrow">›</text>
        </view>
      </view>
      
      <view class="menu-group">
        <view class="menu-item logout-item" @click="handleLogout">
          <view class="menu-left">
            <text class="menu-icon">🚪</text>
            <text class="menu-text logout-text">退出登录</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="version-section">
      <text class="version-text">健身管理 v1.0.0</text>
    </view>
    
    <view class="about-popup" v-if="showAboutPopup">
      <view class="popup-mask" @click="hideAbout"></view>
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">关于我们</text>
          <text class="popup-close" @click="hideAbout">×</text>
        </view>
        <view class="popup-body">
          <view class="about-logo">🏋️</view>
          <text class="about-name">健身管理</text>
          <text class="about-version">版本 1.0.0</text>
          <view class="about-desc">
            <text class="desc-text">健身管理是一款帮助您记录健身数据、追踪训练进度、设定健身目标的专业健身助手应用。</text>
            <text class="desc-text">支持体测记录、训练日志、目标设定等功能，让健身更科学、更高效。</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      userInfo: {},
      stats: {
        sessions: 0,
        hours: '0',
        calories: 0
      },
      showAboutPopup: false
    }
  },
  computed: {
    userNickname() {
      return this.userInfo.nickname || this.userInfo.username || '用户'
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      if (!this.userInfo.id) {
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      await this.loadStats()
    },
    
    async loadStats() {
      try {
        const logs = await api.trainingLogApi.getList(this.userInfo.id)
        
        let sessions = 0
        let totalMinutes = 0
        let totalCalories = 0
        
        logs.forEach(log => {
          sessions++
          totalMinutes += log.duration || 0
          totalCalories += log.total_calories || 0
        })
        
        this.stats = {
          sessions,
          hours: (totalMinutes / 60).toFixed(1),
          calories: Math.round(totalCalories)
        }
        
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    
    goToMeasurement() {
      uni.switchTab({
        url: '/pages/measurement/measurement'
      })
    },
    
    goToTraining() {
      uni.switchTab({
        url: '/pages/training/training'
      })
    },
    
    goToGoal() {
      uni.switchTab({
        url: '/pages/goal/goal'
      })
    },
    
    showEditProfile() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },
    
    showAbout() {
      this.showAboutPopup = true
    },
    
    hideAbout() {
      this.showAboutPopup = false
    },
    
    handleLogout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            uni.removeStorageSync('token')
            uni.removeStorageSync('userInfo')
            
            uni.showToast({
              title: '已退出登录',
              icon: 'success'
            })
            
            setTimeout(() => {
              uni.reLaunch({
                url: '/pages/login/login'
              })
            }, 1000)
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.header-section {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  padding: 40rpx 30rpx;
  border-bottom-left-radius: 40rpx;
  border-bottom-right-radius: 40rpx;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 30rpx;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.avatar-text {
  font-size: 52rpx;
  color: #fff;
  font-weight: 600;
}

.info {
  display: flex;
  flex-direction: column;
}

.nickname {
  font-size: 40rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.username {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
  padding: 24rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6rpx;
}

.stat-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

.stat-divider {
  width: 1rpx;
  height: 60rpx;
  background-color: rgba(255, 255, 255, 0.3);
}

.menu-section {
  margin: 20rpx;
}

.menu-group {
  background-color: #fff;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.group-title {
  font-size: 26rpx;
  color: #909399;
  padding: 20rpx 30rpx 10rpx;
  display: block;
}

.menu-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-left {
  display: flex;
  align-items: center;
}

.menu-icon {
  font-size: 36rpx;
  margin-right: 16rpx;
}

.menu-text {
  font-size: 30rpx;
  color: #333;
}

.menu-arrow {
  font-size: 36rpx;
  color: #c0c4cc;
}

.logout-item {
  justify-content: center;
  padding: 30rpx;
}

.logout-text {
  color: #f56c6c;
}

.version-section {
  padding: 40rpx;
  text-align: center;
}

.version-text {
  font-size: 24rpx;
  color: #c0c4cc;
}

.about-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
}

.popup-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.popup-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 600rpx;
  background-color: #fff;
  border-radius: 20rpx;
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.popup-close {
  font-size: 48rpx;
  color: #909399;
  line-height: 1;
}

.popup-body {
  padding: 40rpx 30rpx;
  text-align: center;
}

.about-logo {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.about-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.about-version {
  font-size: 26rpx;
  color: #909399;
  display: block;
  margin-bottom: 30rpx;
}

.about-desc {
  text-align: left;
}

.desc-text {
  font-size: 26rpx;
  color: #606266;
  line-height: 1.8;
  display: block;
  margin-bottom: 16rpx;
}

.desc-text:last-child {
  margin-bottom: 0;
}
</style>
