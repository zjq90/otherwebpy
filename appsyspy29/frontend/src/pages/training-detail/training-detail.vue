<template>
  <view class="detail-container">
    <view class="header-section" v-if="trainingDetail">
      <view class="header-info">
        <view class="header-icon" :class="trainingDetail.training_type">
          {{ getTrainingIcon() }}
        </view>
        <view class="header-text">
          <text class="header-title">{{ getTrainingTypeName() }}</text>
          <text class="header-subtitle">{{ trainingDetail.training_date }}</text>
        </view>
      </view>
      
      <view class="header-stats">
        <view class="header-stat">
          <text class="stat-value">{{ trainingDetail.duration || 0 }}</text>
          <text class="stat-label">分钟</text>
        </view>
        <view class="header-stat">
          <text class="stat-value">{{ trainingDetail.total_calories || 0 }}</text>
          <text class="stat-label">卡路里</text>
        </view>
        <view class="header-stat" v-if="trainingDetail.mood">
          <text class="stat-value">{{ getMoodIcon() }}</text>
          <text class="stat-label">{{ trainingDetail.mood }}</text>
        </view>
      </view>
    </view>
    
    <view class="info-section" v-if="trainingDetail">
      <view class="info-item" v-if="trainingDetail.location">
        <text class="info-label">训练地点</text>
        <text class="info-value">{{ trainingDetail.location }}</text>
      </view>
      <view class="info-item" v-if="trainingDetail.notes">
        <text class="info-label">训练备注</text>
        <text class="info-value">{{ trainingDetail.notes }}</text>
      </view>
    </view>
    
    <view class="items-section" v-if="trainingItems.length > 0">
      <view class="section-header">
        <text class="section-title">训练项目</text>
        <text class="section-count">共 {{ trainingItems.length }} 个项目</text>
      </view>
      
      <view class="items-list">
        <view class="item-card" v-for="(item, index) in trainingItems" :key="index">
          <view class="item-header">
            <text class="item-order">{{ index + 1 }}</text>
            <text class="item-name">{{ getExerciseName(item.exercise_id) }}</text>
          </view>
          
          <view class="item-stats">
            <view class="item-stat" v-if="item.sets">
              <text class="item-stat-label">组数</text>
              <text class="item-stat-value">{{ item.sets }} 组</text>
            </view>
            <view class="item-stat" v-if="item.reps">
              <text class="item-stat-label">次数</text>
              <text class="item-stat-value">{{ item.reps }} 次</text>
            </view>
            <view class="item-stat" v-if="item.weight">
              <text class="item-stat-label">重量</text>
              <text class="item-stat-value">{{ item.weight }} kg</text>
            </view>
            <view class="item-stat" v-if="item.rest_time">
              <text class="item-stat-label">休息</text>
              <text class="item-stat-value">{{ item.rest_time }} 秒</text>
            </view>
          </view>
          
          <view class="item-notes" v-if="item.notes">
            <text class="item-notes-text">{{ item.notes }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="empty-section" v-if="!loading && !trainingDetail">
      <text class="empty-text">加载中...</text>
    </view>
    
    <view class="action-section">
      <button class="delete-btn" @click="handleDelete">删除记录</button>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      trainingId: null,
      trainingDetail: null,
      trainingItems: [],
      exercises: [],
      loading: true
    }
  },
  onLoad(options) {
    this.trainingId = options.id
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      
      try {
        await this.loadExercises()
        await this.loadTrainingDetail()
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async loadExercises() {
      try {
        this.exercises = await api.exerciseApi.getList()
      } catch (error) {
        console.error('加载训练项目失败:', error)
      }
    },
    
    async loadTrainingDetail() {
      if (!this.trainingId) return
      
      try {
        const detail = await api.trainingLogApi.getDetail(this.trainingId)
        this.trainingDetail = detail.log
        this.trainingItems = detail.items || []
      } catch (error) {
        console.error('加载训练详情失败:', error)
        uni.showToast({
          title: error.message || '加载失败',
          icon: 'none'
        })
      }
    },
    
    getTrainingIcon() {
      if (!this.trainingDetail) return '🏋️'
      const iconMap = {
        'strength': '💪',
        'cardio': '🏃',
        'flexibility': '🧘',
        'crossfit': '🔥',
        'hiit': '⚡'
      }
      return iconMap[this.trainingDetail.training_type] || '🏋️'
    },
    
    getTrainingTypeName() {
      if (!this.trainingDetail) return ''
      const typeMap = {
        'strength': '力量训练',
        'cardio': '有氧运动',
        'flexibility': '拉伸训练',
        'crossfit': 'CrossFit',
        'hiit': 'HIIT训练'
      }
      return typeMap[this.trainingDetail.training_type] || this.trainingDetail.training_type
    },
    
    getMoodIcon() {
      if (!this.trainingDetail || !this.trainingDetail.mood) return ''
      const moodMap = {
        'great': '😄',
        'good': '😊',
        'normal': '😐',
        'tired': '😫'
      }
      return moodMap[this.trainingDetail.mood] || '😊'
    },
    
    getExerciseName(exerciseId) {
      if (!exerciseId) return ''
      const exercise = this.exercises.find(e => e.id === exerciseId)
      return exercise ? exercise.name : '未知项目'
    },
    
    handleDelete() {
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这条训练记录吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await api.trainingLogApi.delete(this.trainingId)
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
  align-items: center;
  margin-bottom: 30rpx;
}

.header-icon {
  width: 80rpx;
  height: 80rpx;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 44rpx;
  margin-right: 20rpx;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.header-subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.header-stats {
  display: flex;
  justify-content: space-around;
  padding: 20rpx;
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 16rpx;
}

.header-stat {
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

.info-section {
  margin: 20rpx;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.info-item {
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 26rpx;
  color: #909399;
  display: block;
  margin-bottom: 10rpx;
}

.info-value {
  font-size: 28rpx;
  color: #333;
  line-height: 1.6;
}

.items-section {
  margin: 20rpx;
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
  color: #333;
}

.section-count {
  font-size: 24rpx;
  color: #909399;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.item-card {
  background-color: #fff;
  border-radius: 20rpx;
  padding: 24rpx;
}

.item-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.item-order {
  width: 48rpx;
  height: 48rpx;
  background-color: #409EFF;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  margin-right: 16rpx;
}

.item-name {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.item-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.item-stat {
  padding: 12rpx 20rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100rpx;
}

.item-stat-label {
  font-size: 20rpx;
  color: #909399;
  margin-bottom: 4rpx;
}

.item-stat-value {
  font-size: 24rpx;
  font-weight: 500;
  color: #333;
}

.item-notes {
  margin-top: 16rpx;
  padding: 16rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
}

.item-notes-text {
  font-size: 24rpx;
  color: #606266;
}

.empty-section {
  padding: 80rpx;
  text-align: center;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
}

.action-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx 30rpx;
  background-color: #fff;
  border-top: 1rpx solid #f0f0f0;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}

.delete-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  background-color: #fef0f0;
  color: #f56c6c;
  border-radius: 16rpx;
  font-size: 30rpx;
}
</style>
