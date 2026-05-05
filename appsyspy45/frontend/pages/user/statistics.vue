<template>
  <view class="page">
    <view class="header-section">
      <view class="header-bg">
        <text class="header-title">我的回收统计</text>
      </view>
    </view>
    
    <view class="stats-overview">
      <view class="overview-card">
        <view class="overview-icon">👕</view>
        <view class="overview-info">
          <text class="overview-value">{{ stats.total_weight || 0 }}kg</text>
          <text class="overview-label">回收总重量</text>
        </view>
      </view>
      <view class="overview-card">
        <view class="overview-icon">🌱</view>
        <view class="overview-info">
          <text class="overview-value">{{ stats.carbon_saved || 0 }}kg</text>
          <text class="overview-label">减碳量</text>
        </view>
      </view>
    </view>
    
    <view class="stats-cards">
      <view class="stat-card">
        <view class="stat-header">
          <text class="stat-title">回收次数</text>
        </view>
        <view class="stat-body">
          <text class="stat-value">{{ stats.order_count || 0 }}</text>
          <text class="stat-unit">次</text>
        </view>
        <view class="stat-footer">
          <text class="stat-compare">较上月 +{{ stats.monthly_growth || 0 }}%</text>
        </view>
      </view>
      
      <view class="stat-card">
        <view class="stat-header">
          <text class="stat-title">获得积分</text>
        </view>
        <view class="stat-body">
          <text class="stat-value highlight">{{ stats.total_points || 0 }}</text>
          <text class="stat-unit">积分</text>
        </view>
        <view class="stat-footer">
          <text class="stat-compare">可兑换商品</text>
        </view>
      </view>
      
      <view class="stat-card">
        <view class="stat-header">
          <text class="stat-title">本月回收</text>
        </view>
        <view class="stat-body">
          <text class="stat-value">{{ stats.monthly_count || 0 }}</text>
          <text class="stat-unit">次</text>
        </view>
        <view class="stat-footer">
          <text class="stat-compare">本月重量 {{ stats.monthly_weight || 0 }}kg</text>
        </view>
      </view>
      
      <view class="stat-card">
        <view class="stat-header">
          <text class="stat-title">环保贡献</text>
        </view>
        <view class="stat-body">
          <text class="stat-value">{{ stats.tree_count || 0 }}</text>
          <text class="stat-unit">棵树</text>
        </view>
        <view class="stat-footer">
          <text class="stat-compare">相当于种植的树木</text>
        </view>
      </view>
    </view>
    
    <view class="chart-section">
      <view class="section-header">
        <text class="section-title">近6个月回收趋势</text>
      </view>
      <view class="chart-placeholder">
        <view class="chart-bars">
          <view class="chart-bar" v-for="(item, index) in chartData" :key="index">
            <view class="bar-fill" :style="{ height: item.height + '%' }"></view>
            <text class="bar-label">{{ item.month }}</text>
          </view>
        </view>
        <view class="chart-legend">
          <view class="legend-item">
            <view class="legend-color"></view>
            <text class="legend-text">回收重量(kg)</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="clothing-stats">
      <view class="section-header">
        <text class="section-title">衣物类型统计</text>
      </view>
      <view class="type-list">
        <view class="type-item" v-for="(item, index) in clothingStats" :key="index">
          <view class="type-left">
            <view class="type-icon">{{ item.icon }}</view>
            <view class="type-info">
              <text class="type-name">{{ item.name }}</text>
              <text class="type-count">{{ item.count }}件</text>
            </view>
          </view>
          <view class="type-right">
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: item.percent + '%' }"></view>
            </view>
            <text class="type-percent">{{ item.percent }}%</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="achievement-section">
      <view class="section-header">
        <text class="section-title">我的成就</text>
      </view>
      <view class="achievement-list">
        <view class="achievement-item" v-for="(item, index) in achievements" :key="index" :class="{ unlocked: item.unlocked }">
          <view class="achievement-icon">{{ item.icon }}</view>
          <text class="achievement-name">{{ item.name }}</text>
          <text class="achievement-desc">{{ item.desc }}</text>
          <view class="achievement-status" v-if="!item.unlocked">
            <text class="status-text">{{ item.progress }}%</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

export default {
  data() {
    return {
      stats: {
        total_weight: 0,
        carbon_saved: 0,
        order_count: 0,
        total_points: 0,
        monthly_count: 0,
        monthly_weight: 0,
        monthly_growth: 0,
        tree_count: 0
      },
      chartData: [],
      clothingStats: [],
      achievements: []
    }
  },
  
  onShow() {
    this.loadData()
  },
  
  methods: {
    async loadData() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      utils.showLoading('加载中...')
      
      try {
        const res = await api.get('/user/statistics')
        if (res.code === 200) {
          this.stats = {
            total_weight: res.data.total_weight || 0,
            carbon_saved: res.data.carbon_saved || 0,
            order_count: res.data.order_count || 0,
            total_points: res.data.points_earned || 0,
            monthly_count: res.data.monthly_order_count || 0,
            monthly_weight: res.data.monthly_weight || 0,
            monthly_growth: res.data.monthly_growth || 0,
            tree_count: Math.floor((res.data.carbon_saved || 0) / 20)
          }
        }
      } catch (e) {
        console.error('加载统计数据失败:', e)
      }
      
      this.loadMockData()
      
      utils.hideLoading()
    },
    
    loadMockData() {
      const now = new Date()
      this.chartData = []
      for (let i = 5; i >= 0; i--) {
        const date = new Date(now.getFullYear(), now.getMonth() - i, 1)
        this.chartData.push({
          month: (date.getMonth() + 1) + '月',
          height: Math.floor(Math.random() * 60) + 20
        })
      }
      
      this.clothingStats = [
        { icon: '👕', name: 'T恤', count: 12, percent: 25 },
        { icon: '🧥', name: '外套', count: 8, percent: 17 },
        { icon: '👖', name: '裤子', count: 10, percent: 21 },
        { icon: '🧶', name: '毛衣', count: 6, percent: 12 },
        { icon: '🛏️', name: '家纺', count: 5, percent: 10 },
        { icon: '👔', name: '其他', count: 7, percent: 15 }
      ]
      
      this.achievements = [
        { icon: '🌱', name: '环保新手', desc: '完成首次回收', unlocked: true, progress: 100 },
        { icon: '🌿', name: '环保达人', desc: '完成10次回收', unlocked: true, progress: 100 },
        { icon: '🌳', name: '环保先锋', desc: '完成50次回收', unlocked: false, progress: 40 },
        { icon: '🏆', name: '环保大师', desc: '回收重量超过100kg', unlocked: false, progress: 30 }
      ]
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding-bottom: 40rpx;
}

.header-section {
  background: linear-gradient(135deg, $primary-color, #66BB6A);
  padding: 40rpx;
  padding-top: calc(40rpx + env(safe-area-inset-top));
  margin-bottom: -40rpx;
  position: relative;
  z-index: 1;
}

.header-title {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $white;
}

.stats-overview {
  display: flex;
  padding: 0 20rpx;
  position: relative;
  z-index: 10;
  margin-bottom: 20rpx;
}

.overview-card {
  flex: 1;
  background-color: $white;
  border-radius: $border-radius-lg;
  padding: 30rpx;
  margin: 0 10rpx;
  display: flex;
  align-items: center;
}

.overview-icon {
  font-size: 48rpx;
  margin-right: 20rpx;
}

.overview-info {
  flex: 1;
}

.overview-value {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $text-color;
}

.overview-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 6rpx;
  display: block;
}

.stats-cards {
  display: flex;
  flex-wrap: wrap;
  padding: 0 20rpx;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.stat-card {
  width: calc(50% - 10rpx);
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 30rpx;
}

.stat-header {
  margin-bottom: 20rpx;
}

.stat-title {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.stat-body {
  display: flex;
  align-items: baseline;
  margin-bottom: 16rpx;
}

.stat-value {
  font-size: 40rpx;
  font-weight: bold;
  color: $text-color;
  
  &.highlight {
    color: $primary-color;
  }
}

.stat-unit {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-left: 6rpx;
}

.stat-footer {
  padding-top: 16rpx;
  border-top: 1rpx solid $border-color;
}

.stat-compare {
  font-size: $font-size-xs;
  color: $text-muted;
}

.chart-section,
.clothing-stats,
.achievement-section {
  background-color: $white;
  margin: 0 20rpx;
  margin-bottom: 20rpx;
  border-radius: $border-radius-md;
  padding: 0 30rpx;
}

.section-header {
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
}

.section-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.chart-placeholder {
  padding: 30rpx 0;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 300rpx;
  margin-bottom: 30rpx;
}

.chart-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 60rpx;
}

.bar-fill {
  width: 40rpx;
  background: linear-gradient(180deg, $primary-color 0%, #81C784 100%);
  border-radius: 8rpx 8rpx 0 0;
  margin-bottom: 16rpx;
  transition: height 0.5s;
}

.bar-label {
  font-size: $font-size-xs;
  color: $text-muted;
}

.chart-legend {
  display: flex;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
}

.legend-color {
  width: 24rpx;
  height: 24rpx;
  background-color: $primary-color;
  border-radius: 4rpx;
  margin-right: 10rpx;
}

.legend-text {
  font-size: $font-size-xs;
  color: $text-muted;
}

.type-list {
  padding: 20rpx 0;
}

.type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.type-left {
  display: flex;
  align-items: center;
}

.type-icon {
  font-size: 40rpx;
  margin-right: 20rpx;
}

.type-info {
  display: flex;
  flex-direction: column;
}

.type-name {
  font-size: $font-size-base;
  color: $text-color;
}

.type-count {
  font-size: $font-size-xs;
  color: $text-muted;
  margin-top: 6rpx;
}

.type-right {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.progress-bar {
  width: 160rpx;
  height: 12rpx;
  background-color: $bg-color;
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: $primary-color;
  border-radius: 6rpx;
}

.type-percent {
  font-size: $font-size-sm;
  color: $primary-color;
  font-weight: 500;
}

.achievement-list {
  display: flex;
  flex-wrap: wrap;
  padding: 20rpx 0;
  gap: 20rpx;
}

.achievement-item {
  width: calc(50% - 10rpx);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 30rpx 20rpx;
  background-color: $bg-color;
  border-radius: $border-radius-md;
  opacity: 0.6;
  
  &.unlocked {
    opacity: 1;
    background-color: rgba($primary-color, 0.05);
  }
}

.achievement-icon {
  font-size: 48rpx;
  margin-bottom: 16rpx;
}

.achievement-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.achievement-desc {
  font-size: $font-size-xs;
  color: $text-muted;
  margin-top: 6rpx;
}

.achievement-status {
  margin-top: 16rpx;
  padding: 6rpx 20rpx;
  background-color: rgba($warning-color, 0.1);
  border-radius: 20rpx;
}

.status-text {
  font-size: $font-size-xs;
  color: $warning-color;
}
</style>
