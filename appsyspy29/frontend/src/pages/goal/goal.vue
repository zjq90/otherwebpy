<template>
  <view class="goal-container">
    <view class="header-section">
      <text class="page-title">目标管理</text>
      <view class="filter-tabs">
        <view 
          class="filter-tab" 
          :class="{ active: filterStatus === 'all' }"
          @click="filterStatus = 'all'"
        >
          全部
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: filterStatus === 'active' }"
          @click="filterStatus = 'active'"
        >
          进行中
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: filterStatus === 'completed' }"
          @click="filterStatus = 'completed'"
        >
          已完成
        </view>
      </view>
    </view>
    
    <view class="stats-section" v-if="goalList.length > 0">
      <view class="stats-card">
        <view class="stats-item">
          <text class="stats-value">{{ stats.total }}</text>
          <text class="stats-label">总目标</text>
        </view>
        <view class="stats-divider"></view>
        <view class="stats-item">
          <text class="stats-value">{{ stats.active }}</text>
          <text class="stats-label">进行中</text>
        </view>
        <view class="stats-divider"></view>
        <view class="stats-item">
          <text class="stats-value">{{ stats.completed }}</text>
          <text class="stats-label">已完成</text>
        </view>
      </view>
    </view>
    
    <view class="list-section">
      <view class="goal-list" v-if="filteredGoals.length > 0">
        <view 
          class="goal-card" 
          v-for="(goal, index) in filteredGoals" 
          :key="index"
          @click="goToDetail(goal.id)"
        >
          <view class="goal-header">
            <view class="goal-type" :class="goal.goal_type">
              <text class="goal-type-icon">{{ getGoalTypeIcon(goal.goal_type) }}</text>
              <text class="goal-type-text">{{ getGoalTypeName(goal.goal_type) }}</text>
            </view>
            <view class="goal-status" :class="goal.status">
              {{ getStatusName(goal.status) }}
            </view>
          </view>
          
          <view class="goal-body">
            <text class="goal-name">{{ goal.goal_name }}</text>
            <view class="goal-desc" v-if="goal.description">
              <text class="goal-desc-text">{{ goal.description }}</text>
            </view>
          </view>
          
          <view class="goal-progress-section">
            <view class="goal-progress-info">
              <text class="goal-current">{{ goal.current_value || 0 }}</text>
              <text class="goal-slash">/</text>
              <text class="goal-target">{{ goal.target_value || 0 }}</text>
              <text class="goal-unit">{{ goal.unit || '' }}</text>
            </view>
            <view class="goal-progress-bar">
              <view class="progress-track">
                <view class="progress-fill" :style="{ width: goal.progress + '%' }"></view>
              </view>
              <text class="progress-text">{{ goal.progress || 0 }}%</text>
            </view>
          </view>
          
          <view class="goal-footer">
            <view class="goal-date-info">
              <text class="date-label">开始</text>
              <text class="date-value">{{ formatDate(goal.start_date) }}</text>
            </view>
            <view class="goal-date-info">
              <text class="date-label">截止</text>
              <text class="date-value" :class="{ overdue: isOverdue(goal) }">
                {{ formatDate(goal.end_date) }}
                {{ isOverdue(goal) ? ' (已过期)' : '' }}
              </text>
            </view>
          </view>
          
          <view class="recommendation-badge" v-if="goal.recommendations && goal.recommendations.length > 0">
            <text class="recommendation-icon">💡</text>
            <text class="recommendation-text">已有推荐方案</text>
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-else>
        <view class="empty-icon">🎯</view>
        <text class="empty-title">暂无目标</text>
        <text class="empty-subtitle">设定一个目标，开始您的健身之旅</text>
      </view>
    </view>
    
    <view class="add-btn" @click="goToAdd">
      <text class="add-icon">+</text>
      <text class="add-text">新建目标</text>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      userInfo: {},
      goalList: [],
      filterStatus: 'all'
    }
  },
  computed: {
    filteredGoals() {
      if (this.filterStatus === 'all') {
        return this.goalList
      }
      return this.goalList.filter(goal => goal.status === this.filterStatus)
    },
    
    stats() {
      const total = this.goalList.length
      const active = this.goalList.filter(g => g.status === 'active').length
      const completed = this.goalList.filter(g => g.status === 'completed').length
      return { total, active, completed }
    }
  },
  onShow() {
    this.loadData()
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    
    getGoalTypeIcon(type) {
      const iconMap = {
        'lose_weight': '🔥',
        'gain_muscle': '💪',
        'shape': '🏃',
        'endurance': '🧘'
      }
      return iconMap[type] || '🎯'
    },
    
    getGoalTypeName(type) {
      const typeMap = {
        'lose_weight': '减脂',
        'gain_muscle': '增肌',
        'shape': '塑形',
        'endurance': '耐力'
      }
      return typeMap[type] || type
    },
    
    getStatusName(status) {
      const statusMap = {
        'active': '进行中',
        'completed': '已完成',
        'paused': '已暂停',
        'cancelled': '已取消'
      }
      return statusMap[status] || status
    },
    
    isOverdue(goal) {
      if (!goal.end_date || goal.status === 'completed') return false
      const now = new Date()
      const endDate = new Date(goal.end_date)
      return now > endDate
    },
    
    async loadData() {
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      if (!this.userInfo.id) return
      
      await this.loadGoalList()
    },
    
    async loadGoalList() {
      try {
        this.goalList = await api.goalApi.getList(this.userInfo.id)
      } catch (error) {
        console.error('加载目标列表失败:', error)
      }
    },
    
    goToDetail(id) {
      uni.navigateTo({
        url: `/pages/goal-detail/goal-detail?id=${id}`
      })
    },
    
    goToAdd() {
      uni.navigateTo({
        url: '/pages/goal-add/goal-add'
      })
    }
  }
}
</script>

<style scoped>
.goal-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
}

.header-section {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  padding: 40rpx 30rpx;
}

.page-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: 24rpx;
}

.filter-tabs {
  display: flex;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
  padding: 6rpx;
}

.filter-tab {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
  border-radius: 12rpx;
}

.filter-tab.active {
  background-color: #fff;
  color: #409EFF;
  font-weight: 500;
}

.stats-section {
  margin: 20rpx;
}

.stats-card {
  display: flex;
  align-items: center;
  justify-content: space-around;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.stats-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stats-value {
  font-size: 40rpx;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8rpx;
}

.stats-label {
  font-size: 24rpx;
  color: #909399;
}

.stats-divider {
  width: 1rpx;
  height: 60rpx;
  background-color: #f0f0f0;
}

.list-section {
  margin: 20rpx;
}

.goal-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.goal-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  position: relative;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.goal-type {
  display: flex;
  align-items: center;
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
}

.goal-type.lose_weight {
  background-color: rgba(245, 108, 108, 0.1);
}

.goal-type.gain_muscle {
  background-color: rgba(103, 194, 58, 0.1);
}

.goal-type.shape {
  background-color: rgba(230, 162, 60, 0.1);
}

.goal-type.endurance {
  background-color: rgba(64, 158, 255, 0.1);
}

.goal-type-icon {
  font-size: 28rpx;
  margin-right: 8rpx;
}

.goal-type-text {
  font-size: 24rpx;
  color: #606266;
}

.goal-status {
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
}

.goal-status.active {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.goal-status.completed {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.goal-status.paused {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.goal-status.cancelled {
  background-color: rgba(144, 147, 153, 0.1);
  color: #909399;
}

.goal-body {
  margin-bottom: 20rpx;
}

.goal-name {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  display: block;
  margin-bottom: 12rpx;
}

.goal-desc {
  padding: 12rpx 16rpx;
  background-color: #f5f7fa;
  border-radius: 8rpx;
}

.goal-desc-text {
  font-size: 24rpx;
  color: #606266;
  line-height: 1.5;
}

.goal-progress-section {
  margin-bottom: 20rpx;
}

.goal-progress-info {
  display: flex;
  align-items: baseline;
  margin-bottom: 12rpx;
}

.goal-current {
  font-size: 36rpx;
  font-weight: 600;
  color: #409EFF;
}

.goal-slash {
  font-size: 28rpx;
  color: #c0c4cc;
  margin: 0 8rpx;
}

.goal-target {
  font-size: 28rpx;
  color: #606266;
}

.goal-unit {
  font-size: 24rpx;
  color: #909399;
  margin-left: 4rpx;
}

.goal-progress-bar {
  display: flex;
  align-items: center;
}

.progress-track {
  flex: 1;
  height: 16rpx;
  background-color: #ebeef5;
  border-radius: 8rpx;
  overflow: hidden;
  margin-right: 16rpx;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #66b1ff);
  border-radius: 8rpx;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 24rpx;
  font-weight: 500;
  color: #409EFF;
  min-width: 60rpx;
  text-align: right;
}

.goal-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.goal-date-info {
  display: flex;
  flex-direction: column;
}

.date-label {
  font-size: 22rpx;
  color: #909399;
  margin-bottom: 4rpx;
}

.date-value {
  font-size: 24rpx;
  color: #606266;
}

.date-value.overdue {
  color: #f56c6c;
}

.recommendation-badge {
  position: absolute;
  top: 16rpx;
  right: 16rpx;
  display: flex;
  align-items: center;
  padding: 8rpx 16rpx;
  background-color: rgba(230, 162, 60, 0.1);
  border-radius: 8rpx;
}

.recommendation-icon {
  font-size: 24rpx;
  margin-right: 6rpx;
}

.recommendation-text {
  font-size: 20rpx;
  color: #e6a23c;
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
