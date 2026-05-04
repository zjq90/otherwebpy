<template>
  <view class="training-container">
    <view class="header-section">
      <view class="header-info">
        <text class="page-title">训练日志</text>
        <text class="page-subtitle">共 {{ trainingList.length }} 条记录</text>
      </view>
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ totalStats.sessions }}</text>
          <text class="stat-label">次数</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ totalStats.duration }}</text>
          <text class="stat-label">小时</text>
        </view>
        <view class="stat-divider"></view>
        <view class="stat-item">
          <text class="stat-value">{{ totalStats.calories }}</text>
          <text class="stat-label">卡路里</text>
        </view>
      </view>
    </view>
    
    <view class="filter-section">
      <view class="filter-tabs">
        <view 
          class="filter-tab" 
          :class="{ active: filterType === 'all' }"
          @click="filterType = 'all'"
        >
          全部
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: filterType === 'strength' }"
          @click="filterType = 'strength'"
        >
          力量训练
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: filterType === 'cardio' }"
          @click="filterType = 'cardio'"
        >
          有氧运动
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: filterType === 'flexibility' }"
          @click="filterType = 'flexibility'"
        >
          拉伸
        </view>
      </view>
    </view>
    
    <view class="list-section">
      <view class="training-group" v-for="(group, groupIndex) in groupedTrainings" :key="groupIndex">
        <view class="group-header">
          <text class="group-date">{{ formatGroupDate(group.date) }}</text>
          <text class="group-stats">{{ group.trainings.length }}次训练 · {{ group.totalDuration }}分钟 · {{ group.totalCalories }}卡</text>
        </view>
        
        <view class="group-list">
          <view 
            class="training-item" 
            v-for="(item, index) in group.trainings" 
            :key="index"
            @click="goToDetail(item.id)"
          >
            <view class="item-left">
              <view class="item-icon" :class="getTrainingTypeClass(item)">
                {{ getTrainingIcon(item) }}
              </view>
              <view class="item-info">
                <text class="item-date">{{ item.training_date }}</text>
                <view class="item-tags">
                  <view class="item-tag" v-if="item.duration">
                    ⏱️ {{ item.duration }}分钟
                  </view>
                  <view class="item-tag" v-if="item.total_calories">
                    🔥 {{ item.total_calories }}卡
                  </view>
                  <view class="item-tag" v-if="item.mood">
                    😊 {{ item.mood }}
                  </view>
                </view>
              </view>
            </view>
            <text class="item-arrow">›</text>
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-if="filteredTrainings.length === 0">
        <view class="empty-icon">🏋️</view>
        <text class="empty-title">暂无训练记录</text>
        <text class="empty-subtitle">开始记录您的第一次训练吧</text>
      </view>
    </view>
    
    <view class="add-btn" @click="goToAdd">
      <text class="add-icon">+</text>
      <text class="add-text">记录训练</text>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      userInfo: {},
      trainingList: [],
      filterType: 'all',
      totalStats: {
        sessions: 0,
        duration: 0,
        calories: 0
      }
    }
  },
  computed: {
    filteredTrainings() {
      if (this.filterType === 'all') {
        return this.trainingList
      }
      return this.trainingList.filter(item => {
        return item.training_type === this.filterType
      })
    },
    
    groupedTrainings() {
      const groups = {}
      
      this.filteredTrainings.forEach(item => {
        const dateKey = item.training_date
        if (!groups[dateKey]) {
          groups[dateKey] = {
            date: dateKey,
            trainings: [],
            totalDuration: 0,
            totalCalories: 0
          }
        }
        groups[dateKey].trainings.push(item)
        groups[dateKey].totalDuration += item.duration || 0
        groups[dateKey].totalCalories += item.total_calories || 0
      })
      
      return Object.values(groups).sort((a, b) => {
        return new Date(b.date) - new Date(a.date)
      })
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    formatGroupDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const now = new Date()
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
      const target = new Date(date.getFullYear(), date.getMonth(), date.getDate())
      const diffDays = Math.floor((today - target) / (1000 * 60 * 60 * 24))
      
      const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      
      if (diffDays === 0) {
        return '今天'
      } else if (diffDays === 1) {
        return '昨天'
      } else if (diffDays < 7) {
        return weekdays[date.getDay()]
      } else {
        return `${date.getMonth() + 1}月${date.getDate()}日`
      }
    },
    
    getTrainingTypeClass(item) {
      return item.training_type || 'default'
    },
    
    getTrainingIcon(item) {
      const iconMap = {
        'strength': '💪',
        'cardio': '🏃',
        'flexibility': '🧘',
        'crossfit': '🔥',
        'hiit': '⚡'
      }
      return iconMap[item.training_type] || '🏋️'
    },
    
    async loadData() {
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      if (!this.userInfo.id) return
      
      await this.loadTrainingList()
      this.calculateTotalStats()
    },
    
    async loadTrainingList() {
      try {
        this.trainingList = await api.trainingLogApi.getList(this.userInfo.id)
      } catch (error) {
        console.error('加载训练记录失败:', error)
      }
    },
    
    calculateTotalStats() {
      let sessions = 0
      let totalMinutes = 0
      let totalCalories = 0
      
      this.trainingList.forEach(item => {
        sessions++
        totalMinutes += item.duration || 0
        totalCalories += item.total_calories || 0
      })
      
      this.totalStats = {
        sessions,
        duration: (totalMinutes / 60).toFixed(1),
        calories: Math.round(totalCalories)
      }
    },
    
    goToDetail(id) {
      uni.navigateTo({
        url: `/pages/training-detail/training-detail?id=${id}`
      })
    },
    
    goToAdd() {
      uni.navigateTo({
        url: '/pages/training-add/training-add'
      })
    }
  }
}
</script>

<style scoped>
.training-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
}

.header-section {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  padding: 40rpx 30rpx;
}

.header-info {
  margin-bottom: 30rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: 8rpx;
}

.page-subtitle {
  font-size: 24rpx;
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

.filter-section {
  background-color: #fff;
  padding: 20rpx 30rpx;
}

.filter-tabs {
  display: flex;
  overflow-x: auto;
  white-space: nowrap;
}

.filter-tab {
  flex-shrink: 0;
  padding: 16rpx 28rpx;
  font-size: 26rpx;
  color: #606266;
  border-radius: 30rpx;
  margin-right: 16rpx;
}

.filter-tab.active {
  background-color: #409EFF;
  color: #fff;
}

.list-section {
  margin: 20rpx;
}

.training-group {
  margin-bottom: 20rpx;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
  background-color: #fff;
  border-top-left-radius: 20rpx;
  border-top-right-radius: 20rpx;
}

.group-date {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.group-stats {
  font-size: 24rpx;
  color: #909399;
}

.group-list {
  background-color: #fff;
  border-bottom-left-radius: 20rpx;
  border-bottom-right-radius: 20rpx;
}

.training-item {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.training-item:last-child {
  border-bottom: none;
}

.item-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.item-icon {
  width: 80rpx;
  height: 80rpx;
  background-color: #f5f7fa;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40rpx;
  margin-right: 20rpx;
}

.item-icon.strength {
  background-color: rgba(245, 108, 108, 0.1);
}

.item-icon.cardio {
  background-color: rgba(103, 194, 58, 0.1);
}

.item-icon.flexibility {
  background-color: rgba(230, 162, 60, 0.1);
}

.item-icon.crossfit {
  background-color: rgba(156, 39, 176, 0.1);
}

.item-icon.hiit {
  background-color: rgba(64, 158, 255, 0.1);
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.item-date {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 10rpx;
}

.item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12rpx;
}

.item-tag {
  font-size: 22rpx;
  color: #909399;
  background-color: #f5f7fa;
  padding: 6rpx 12rpx;
  border-radius: 6rpx;
}

.item-arrow {
  font-size: 36rpx;
  color: #c0c4cc;
}

.empty-state {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 80rpx 30rpx;
  text-align: center;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-title {
  font-size: 30rpx;
  color: #606266;
  display: block;
  margin-bottom: 12rpx;
}

.empty-subtitle {
  font-size: 26rpx;
  color: #909399;
}

.add-btn {
  position: fixed;
  bottom: 40rpx;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  padding: 24rpx 48rpx;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  border-radius: 50rpx;
  box-shadow: 0 8rpx 24rpx rgba(64, 158, 255, 0.3);
}

.add-icon {
  font-size: 40rpx;
  color: #fff;
  margin-right: 12rpx;
  font-weight: 300;
}

.add-text {
  font-size: 30rpx;
  color: #fff;
  font-weight: 500;
}
</style>
