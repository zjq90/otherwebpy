<template>
  <view class="index-container">
    <view class="header-section">
      <view class="user-info">
        <view class="avatar">
          <text class="avatar-text">{{ userNickname.charAt(0) }}</text>
        </view>
        <view class="info">
          <text class="greeting">你好，{{ userNickname }} 👋</text>
          <text class="date">{{ currentDate }}</text>
        </view>
      </view>
      <view class="quick-actions">
        <view class="action-item" @click="goToMeasurementAdd">
          <text class="action-icon">📊</text>
          <text class="action-text">添加体测</text>
        </view>
        <view class="action-item" @click="goToTrainingAdd">
          <text class="action-icon">🏋️</text>
          <text class="action-text">记录训练</text>
        </view>
        <view class="action-item" @click="goToGoalAdd">
          <text class="action-icon">🎯</text>
          <text class="action-text">设定目标</text>
        </view>
      </view>
    </view>
    
    <view class="stats-section">
      <text class="section-title">今日概览</text>
      <view class="stats-grid">
        <view class="stats-item">
          <view class="stats-card">
            <text class="stats-value">{{ todayStats.sessions }}</text>
            <text class="stats-label">训练次数</text>
          </view>
        </view>
        <view class="stats-item">
          <view class="stats-card">
            <text class="stats-value">{{ todayStats.duration }}</text>
            <text class="stats-label">训练时长(分)</text>
          </view>
        </view>
        <view class="stats-item">
          <view class="stats-card">
            <text class="stats-value">{{ todayStats.calories }}</text>
            <text class="stats-label">消耗卡路里</text>
          </view>
        </view>
        <view class="stats-item">
          <view class="stats-card">
            <text class="stats-value">{{ todayStats.goals }}</text>
            <text class="stats-label">进行中目标</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="latest-measurement-section">
      <view class="section-header">
        <text class="section-title">最新体测</text>
        <text class="section-more" @click="goToMeasurement">查看全部</text>
      </view>
      <view class="measurement-card" v-if="latestMeasurement">
        <view class="measurement-row">
          <view class="measurement-item">
            <text class="measurement-value">{{ latestMeasurement.weight }}</text>
            <text class="measurement-unit">kg</text>
            <text class="measurement-label">体重</text>
          </view>
          <view class="measurement-item">
            <text class="measurement-value">{{ latestMeasurement.body_fat_rate }}</text>
            <text class="measurement-unit">%</text>
            <text class="measurement-label">体脂率</text>
          </view>
          <view class="measurement-item">
            <text class="measurement-value">{{ latestMeasurement.muscle_mass }}</text>
            <text class="measurement-unit">kg</text>
            <text class="measurement-label">肌肉量</text>
          </view>
          <view class="measurement-item">
            <text class="measurement-value">{{ latestMeasurement.bmi }}</text>
            <text class="measurement-unit"></text>
            <text class="measurement-label">BMI</text>
          </view>
        </view>
        <view class="measurement-footer">
          <text class="measurement-date">{{ formatDate(latestMeasurement.measurement_date) }}</text>
          <text class="measurement-source" :class="latestMeasurement.source">
            {{ latestMeasurement.source === 'gym_sync' ? '健身房同步' : '手动录入' }}
          </text>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-text">暂无体测记录</text>
        <text class="empty-hint" @click="goToMeasurementAdd">点击添加第一条记录</text>
      </view>
    </view>
    
    <view class="active-goal-section">
      <view class="section-header">
        <text class="section-title">当前目标</text>
        <text class="section-more" @click="goToGoal">查看全部</text>
      </view>
      <view class="goal-card" v-if="activeGoal" @click="goToGoalDetail(activeGoal.id)">
        <view class="goal-header">
          <view class="goal-type-tag" :class="activeGoal.goal_type">
            {{ getGoalTypeName(activeGoal.goal_type) }}
          </view>
          <text class="goal-status" :class="activeGoal.status">
            {{ activeGoal.status === 'active' ? '进行中' : '已完成' }}
          </text>
        </view>
        <text class="goal-name">{{ activeGoal.goal_name }}</text>
        <view class="goal-progress">
          <view class="progress-bar">
            <view class="progress-fill" :style="{ width: activeGoal.progress + '%' }"></view>
          </view>
          <text class="progress-text">{{ activeGoal.progress }}%</text>
        </view>
        <view class="goal-footer">
          <text class="goal-date">截止: {{ formatDate(activeGoal.end_date) }}</text>
          <text class="goal-values">
            {{ activeGoal.current_value || 0 }} / {{ activeGoal.target_value || 0 }}
          </text>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-text">暂无进行中的目标</text>
        <text class="empty-hint" @click="goToGoalAdd">点击设定目标</text>
      </view>
    </view>
    
    <view class="recent-training-section">
      <view class="section-header">
        <text class="section-title">最近训练</text>
        <text class="section-more" @click="goToTraining">查看全部</text>
      </view>
      <view class="training-list" v-if="recentTrainings.length > 0">
        <view 
          class="training-item" 
          v-for="(item, index) in recentTrainings" 
          :key="index"
          @click="goToTrainingDetail(item.id)"
        >
          <view class="training-icon">💪</view>
          <view class="training-info">
            <text class="training-date">{{ formatDate(item.training_date) }}</text>
            <view class="training-stats">
              <text class="stat-item">⏱️ {{ item.duration }}分钟</text>
              <text class="stat-item">🔥 {{ item.total_calories }}卡</text>
              <text class="stat-item" v-if="item.mood">😊 {{ item.mood }}</text>
            </view>
          </view>
          <text class="arrow">›</text>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-text">暂无训练记录</text>
        <text class="empty-hint" @click="goToTrainingAdd">点击记录第一次训练</text>
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
      todayStats: {
        sessions: 0,
        duration: 0,
        calories: 0,
        goals: 0
      },
      latestMeasurement: null,
      activeGoal: null,
      recentTrainings: [],
      currentDate: ''
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
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      return `${month}月${day}日`
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
    
    async loadData() {
      // 获取用户信息
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      // 设置当前日期
      const now = new Date()
      const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      this.currentDate = `${now.getMonth() + 1}月${now.getDate()}日 ${weekdays[now.getDay()]}`
      
      // 获取今日训练统计
      await this.loadTodayStats()
      
      // 获取最新体测记录
      await this.loadLatestMeasurement()
      
      // 获取当前进行中的目标
      await this.loadActiveGoal()
      
      // 获取最近训练记录
      await this.loadRecentTrainings()
    },
    
    async loadTodayStats() {
      if (!this.userInfo.id) return
      
      try {
        // 获取今日训练记录
        const todayLogs = await api.trainingLogApi.getToday(this.userInfo.id)
        this.todayStats.sessions = todayLogs.length || 0
        
        // 计算总时长和卡路里
        let totalDuration = 0
        let totalCalories = 0
        todayLogs.forEach(log => {
          totalDuration += log.duration || 0
          totalCalories += log.total_calories || 0
        })
        this.todayStats.duration = totalDuration
        this.todayStats.calories = Math.round(totalCalories)
        
        // 获取进行中目标数量
        const goals = await api.goalApi.getList(this.userInfo.id, { status: 'active' })
        this.todayStats.goals = goals.length || 0
        
      } catch (error) {
        console.error('加载今日统计失败:', error)
      }
    },
    
    async loadLatestMeasurement() {
      if (!this.userInfo.id) return
      
      try {
        this.latestMeasurement = await api.measurementApi.getLatest(this.userInfo.id)
      } catch (error) {
        console.error('加载最新体测失败:', error)
      }
    },
    
    async loadActiveGoal() {
      if (!this.userInfo.id) return
      
      try {
        this.activeGoal = await api.goalApi.getActive(this.userInfo.id)
      } catch (error) {
        console.error('加载当前目标失败:', error)
      }
    },
    
    async loadRecentTrainings() {
      if (!this.userInfo.id) return
      
      try {
        const logs = await api.trainingLogApi.getList(this.userInfo.id, { limit: 5 })
        this.recentTrainings = logs || []
      } catch (error) {
        console.error('加载最近训练失败:', error)
      }
    },
    
    goToMeasurementAdd() {
      uni.navigateTo({
        url: '/pages/measurement-add/measurement-add'
      })
    },
    
    goToTrainingAdd() {
      uni.navigateTo({
        url: '/pages/training-add/training-add'
      })
    },
    
    goToGoalAdd() {
      uni.navigateTo({
        url: '/pages/goal-add/goal-add'
      })
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
    
    goToTrainingDetail(id) {
      uni.navigateTo({
        url: `/pages/training-detail/training-detail?id=${id}`
      })
    },
    
    goToGoalDetail(id) {
      uni.navigateTo({
        url: `/pages/goal-detail/goal-detail?id=${id}`
      })
    }
  }
}
</script>

<style scoped>
.index-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 30rpx;
}

.header-section {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  padding: 40rpx 30rpx 50rpx;
  border-bottom-left-radius: 40rpx;
  border-bottom-right-radius: 40rpx;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.avatar-text {
  font-size: 44rpx;
  color: #fff;
  font-weight: 600;
}

.info {
  display: flex;
  flex-direction: column;
}

.greeting {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.date {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.quick-actions {
  display: flex;
  justify-content: space-around;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.action-icon {
  font-size: 48rpx;
  margin-bottom: 12rpx;
}

.action-text {
  font-size: 24rpx;
  color: #606266;
}

.stats-section {
  padding: 30rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
  display: block;
}

.stats-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10rpx;
}

.stats-item {
  width: 50%;
  padding: 0 10rpx;
  margin-bottom: 20rpx;
  box-sizing: border-box;
}

.stats-card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 30rpx 20rpx;
  text-align: center;
}

.stats-value {
  font-size: 40rpx;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8rpx;
  display: block;
}

.stats-label {
  font-size: 22rpx;
  color: #909399;
}

.latest-measurement-section,
.active-goal-section,
.recent-training-section {
  padding: 0 30rpx;
  margin-bottom: 20rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-more {
  font-size: 26rpx;
  color: #409EFF;
}

.measurement-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.measurement-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 24rpx;
}

.measurement-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.measurement-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.measurement-unit {
  font-size: 22rpx;
  color: #909399;
  margin-left: 4rpx;
}

.measurement-label {
  font-size: 22rpx;
  color: #909399;
  margin-top: 8rpx;
}

.measurement-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.measurement-date {
  font-size: 24rpx;
  color: #909399;
}

.measurement-source {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
}

.measurement-source.gym_sync {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.measurement-source.manual {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.goal-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.goal-type-tag {
  font-size: 24rpx;
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}

.goal-type-tag.lose_weight {
  background-color: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.goal-type-tag.gain_muscle {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.goal-type-tag.shape {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.goal-type-tag.endurance {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.goal-status {
  font-size: 24rpx;
}

.goal-status.active {
  color: #409EFF;
}

.goal-status.completed {
  color: #67c23a;
}

.goal-name {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.goal-progress {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.progress-bar {
  flex: 1;
  height: 16rpx;
  background-color: #ebeef5;
  border-radius: 8rpx;
  overflow: hidden;
  margin-right: 20rpx;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #66b1ff);
  border-radius: 8rpx;
}

.progress-text {
  font-size: 26rpx;
  font-weight: 600;
  color: #409EFF;
}

.goal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16rpx;
  border-top: 1rpx solid #f0f0f0;
}

.goal-date {
  font-size: 24rpx;
  color: #909399;
}

.goal-values {
  font-size: 26rpx;
  color: #606266;
}

.empty-state {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 60rpx 30rpx;
  text-align: center;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
  display: block;
  margin-bottom: 16rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: #409EFF;
}

.training-list {
  background-color: #fff;
  border-radius: 20rpx;
  overflow: hidden;
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

.training-icon {
  font-size: 44rpx;
  margin-right: 20rpx;
}

.training-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.training-date {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
  margin-bottom: 10rpx;
}

.training-stats {
  display: flex;
}

.stat-item {
  font-size: 24rpx;
  color: #909399;
  margin-right: 24rpx;
}

.arrow {
  font-size: 36rpx;
  color: #c0c4cc;
}
</style>
