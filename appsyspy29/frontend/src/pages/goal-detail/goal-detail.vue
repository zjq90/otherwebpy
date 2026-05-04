<template>
  <view class="detail-container">
    <view class="header-section" v-if="goalDetail">
      <view class="header-info">
        <view class="goal-type-badge" :class="goalDetail.goal_type">
          <text class="type-icon">{{ getGoalTypeIcon() }}</text>
          <text class="type-text">{{ getGoalTypeName() }}</text>
        </view>
        <view class="goal-status" :class="goalDetail.status">
          {{ getStatusName() }}
        </view>
      </view>
      <text class="goal-name">{{ goalDetail.goal_name }}</text>
      <text class="goal-desc" v-if="goalDetail.description">{{ goalDetail.description }}</text>
    </view>
    
    <view class="progress-section" v-if="goalDetail">
      <view class="progress-info">
        <view class="progress-values">
          <text class="current-value">{{ goalDetail.current_value || 0 }}</text>
          <text class="value-slash">/</text>
          <text class="target-value">{{ goalDetail.target_value || 0 }}</text>
          <text class="value-unit">{{ goalDetail.unit || '' }}</text>
        </view>
        <text class="progress-percent">{{ goalDetail.progress || 0 }}%</text>
      </view>
      <view class="progress-bar-container">
        <view class="progress-track">
          <view class="progress-fill" :style="{ width: (goalDetail.progress || 0) + '%' }"></view>
        </view>
      </view>
    </view>
    
    <view class="info-section" v-if="goalDetail">
      <view class="info-card">
        <view class="info-item">
          <text class="info-label">开始日期</text>
          <text class="info-value">{{ formatDate(goalDetail.start_date) }}</text>
        </view>
        <view class="info-divider"></view>
        <view class="info-item">
          <text class="info-label">结束日期</text>
          <text class="info-value" :class="{ overdue: isOverdue }">
            {{ formatDate(goalDetail.end_date) }}
            {{ isOverdue ? ' (已过期)' : '' }}
          </text>
        </view>
      </view>
      
      <view class="update-card">
        <view class="update-header">
          <text class="update-title">更新进度</text>
        </view>
        <view class="update-form">
          <input 
            class="update-input" 
            type="digit" 
            placeholder="输入当前值" 
            v-model="updateValue"
          />
          <button class="update-btn" @click="handleUpdateProgress">更新</button>
        </view>
      </view>
    </view>
    
    <view class="recommend-section" v-if="goalDetail && (recommendations.length > 0 || trainingPlan || dietAdvice)">
      <view class="section-header">
        <text class="section-title">推荐方案</text>
      </view>
      
      <view class="plan-card" v-if="trainingPlan">
        <view class="plan-header">
          <text class="plan-icon">💪</text>
          <text class="plan-title">训练计划</text>
        </view>
        <text class="plan-content">{{ trainingPlan }}</text>
      </view>
      
      <view class="plan-card" v-if="dietAdvice">
        <view class="plan-header">
          <text class="plan-icon">🍎</text>
          <text class="plan-title">饮食建议</text>
        </view>
        <text class="plan-content">{{ dietAdvice }}</text>
      </view>
      
      <view class="progress-list" v-if="progressList.length > 0">
        <view class="progress-item" v-for="(item, index) in progressList" :key="index">
          <view class="progress-date">{{ formatDate(item.record_date) }}</view>
          <view class="progress-info">
            <text class="progress-current">{{ item.current_value }}</text>
            <text class="progress-unit">{{ goalDetail.unit }}</text>
          </view>
          <view class="progress-change" :class="item.value_change >= 0 ? 'up' : 'down'">
            {{ item.value_change >= 0 ? '+' : '' }}{{ item.value_change }}
          </view>
        </view>
      </view>
    </view>
    
    <view class="action-section" v-if="goalDetail">
      <button 
        class="action-btn" 
        :class="goalDetail.status === 'active' ? 'pause-btn' : 'active-btn'"
        @click="toggleStatus"
      >
        {{ goalDetail.status === 'active' ? '暂停目标' : '继续目标' }}
      </button>
      <button class="action-btn delete-btn" @click="handleDelete">删除目标</button>
    </view>
    
    <view class="loading-section" v-if="loading">
      <text class="loading-text">加载中...</text>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      goalId: null,
      goalDetail: null,
      recommendations: [],
      trainingPlan: '',
      dietAdvice: '',
      progressList: [],
      updateValue: '',
      loading: true
    }
  },
  computed: {
    isOverdue() {
      if (!this.goalDetail || !this.goalDetail.end_date) return false
      if (this.goalDetail.status === 'completed') return false
      const now = new Date()
      const endDate = new Date(this.goalDetail.end_date)
      return now > endDate
    }
  },
  onLoad(options) {
    this.goalId = options.id
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
    
    getGoalTypeIcon() {
      if (!this.goalDetail) return '🎯'
      const iconMap = {
        'lose_weight': '🔥',
        'gain_muscle': '💪',
        'shape': '🏃',
        'endurance': '🧘'
      }
      return iconMap[this.goalDetail.goal_type] || '🎯'
    },
    
    getGoalTypeName() {
      if (!this.goalDetail) return ''
      const typeMap = {
        'lose_weight': '减脂',
        'gain_muscle': '增肌',
        'shape': '塑形',
        'endurance': '耐力'
      }
      return typeMap[this.goalDetail.goal_type] || this.goalDetail.goal_type
    },
    
    getStatusName() {
      if (!this.goalDetail) return ''
      const statusMap = {
        'active': '进行中',
        'paused': '已暂停',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statusMap[this.goalDetail.status] || this.goalDetail.status
    },
    
    async loadData() {
      this.loading = true
      
      try {
        const detail = await api.goalApi.getDetail(this.goalId)
        this.goalDetail = detail.goal
        
        if (detail.recommendations && detail.recommendations.length > 0) {
          this.recommendations = detail.recommendations
          
          const plan = detail.recommendations.find(r => r.recommendation_type === 'training_plan')
          const diet = detail.recommendations.find(r => r.recommendation_type === 'diet_advice')
          
          if (plan) {
            this.trainingPlan = plan.content
          }
          if (diet) {
            this.dietAdvice = diet.content
          }
        }
        
        if (detail.progress_records) {
          this.progressList = detail.progress_records
        }
        
      } catch (error) {
        console.error('加载目标详情失败:', error)
        uni.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    },
    
    async handleUpdateProgress() {
      if (!this.updateValue) {
        uni.showToast({
          title: '请输入当前值',
          icon: 'none'
        })
        return
      }
      
      try {
        await api.goalApi.updateProgress(this.goalId, {
          current_value: parseFloat(this.updateValue)
        })
        
        uni.showToast({
          title: '更新成功',
          icon: 'success'
        })
        
        this.updateValue = ''
        this.loadData()
        
      } catch (error) {
        uni.showToast({
          title: error.message || '更新失败',
          icon: 'none'
        })
      }
    },
    
    async toggleStatus() {
      if (!this.goalDetail) return
      
      const newStatus = this.goalDetail.status === 'active' ? 'paused' : 'active'
      
      try {
        await api.goalApi.updateStatus(this.goalId, {
          status: newStatus
        })
        
        uni.showToast({
          title: newStatus === 'active' ? '已继续' : '已暂停',
          icon: 'success'
        })
        
        this.loadData()
        
      } catch (error) {
        uni.showToast({
          title: error.message || '操作失败',
          icon: 'none'
        })
      }
    },
    
    async handleDelete() {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这个目标吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await api.goalApi.delete(this.goalId)
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
              setTimeout(() => {
                uni.navigateBack()
              }, 1000)
            } catch (error) {
              uni.showToast({
                title: error.message || '删除失败',
                icon: 'none'
              })
            }
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
}

.header-section {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  padding: 40rpx 30rpx;
  border-bottom-left-radius: 40rpx;
  border-bottom-right-radius: 40rpx;
}

.header-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.goal-type-badge {
  display: flex;
  align-items: center;
  padding: 10rpx 20rpx;
  border-radius: 30rpx;
}

.goal-type-badge.lose_weight {
  background-color: rgba(245, 108, 108, 0.3);
}

.goal-type-badge.gain_muscle {
  background-color: rgba(103, 194, 58, 0.3);
}

.goal-type-badge.shape {
  background-color: rgba(230, 162, 60, 0.3);
}

.goal-type-badge.endurance {
  background-color: rgba(64, 158, 255, 0.3);
}

.type-icon {
  font-size: 32rpx;
  margin-right: 8rpx;
}

.type-text {
  font-size: 24rpx;
  color: #fff;
}

.goal-status {
  font-size: 24rpx;
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  background-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.goal-status.active {
  background-color: rgba(255, 255, 255, 0.3);
}

.goal-status.paused {
  background-color: rgba(230, 162, 60, 0.4);
}

.goal-status.completed {
  background-color: rgba(103, 194, 58, 0.4);
}

.goal-status.cancelled {
  background-color: rgba(144, 147, 153, 0.4);
}

.goal-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  display: block;
  margin-bottom: 12rpx;
}

.goal-desc {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.progress-section {
  margin: -40rpx 30rpx 20rpx;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
  position: relative;
  z-index: 10;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 20rpx;
}

.progress-values {
  display: flex;
  align-items: baseline;
}

.current-value {
  font-size: 48rpx;
  font-weight: 600;
  color: #409EFF;
}

.value-slash {
  font-size: 32rpx;
  color: #c0c4cc;
  margin: 0 8rpx;
}

.target-value {
  font-size: 36rpx;
  color: #606266;
}

.value-unit {
  font-size: 24rpx;
  color: #909399;
  margin-left: 4rpx;
}

.progress-percent {
  font-size: 32rpx;
  font-weight: 600;
  color: #409EFF;
}

.progress-bar-container {
  padding-top: 10rpx;
}

.progress-track {
  height: 16rpx;
  background-color: #ebeef5;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #66b1ff);
  border-radius: 8rpx;
  transition: width 0.3s ease;
}

.info-section {
  margin: 20rpx;
}

.info-card {
  display: flex;
  align-items: center;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.info-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.info-label {
  font-size: 24rpx;
  color: #909399;
  margin-bottom: 8rpx;
}

.info-value {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.info-value.overdue {
  color: #f56c6c;
}

.info-divider {
  width: 1rpx;
  height: 60rpx;
  background-color: #f0f0f0;
}

.update-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.update-header {
  margin-bottom: 20rpx;
}

.update-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.update-form {
  display: flex;
  gap: 20rpx;
}

.update-input {
  flex: 1;
  height: 80rpx;
  padding: 0 24rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  font-size: 28rpx;
  text-align: center;
}

.update-btn {
  height: 80rpx;
  padding: 0 30rpx;
  line-height: 80rpx;
  background-color: #409EFF;
  color: #fff;
  border-radius: 12rpx;
  font-size: 28rpx;
  margin: 0;
}

.recommend-section {
  margin: 20rpx;
}

.section-header {
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.plan-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 16rpx;
}

.plan-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.plan-icon {
  font-size: 36rpx;
  margin-right: 12rpx;
}

.plan-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.plan-content {
  font-size: 26rpx;
  color: #606266;
  line-height: 1.8;
}

.progress-list {
  margin-top: 20rpx;
}

.progress-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx;
  background-color: #fff;
  border-radius: 12rpx;
  margin-bottom: 10rpx;
}

.progress-date {
  font-size: 24rpx;
  color: #909399;
}

.progress-info {
  display: flex;
  align-items: baseline;
}

.progress-current {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.progress-unit {
  font-size: 22rpx;
  color: #909399;
  margin-left: 4rpx;
}

.progress-change {
  font-size: 24rpx;
  font-weight: 500;
  padding: 6rpx 12rpx;
  border-radius: 8rpx;
}

.progress-change.up {
  background-color: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

.progress-change.down {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.action-section {
  display: flex;
  gap: 20rpx;
  margin: 20rpx;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  margin: 0;
}

.pause-btn {
  background-color: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.active-btn {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.delete-btn {
  background-color: #fef0f0;
  color: #f56c6c;
}

.loading-section {
  padding: 100rpx;
  text-align: center;
}

.loading-text {
  font-size: 28rpx;
  color: #909399;
}
</style>
