<template>
  <view class="index-container">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="user-info">
        <view class="avatar">
          <text class="avatar-text">{{ userInitial }}</text>
        </view>
        <view class="info-text">
          <text class="user-name">{{ userInfo.real_name || '用户' }}</text>
          <text class="user-role">{{ roleText }}</text>
        </view>
      </view>
      <view class="date-info">
        <text class="date-text">{{ currentDate }}</text>
      </view>
    </view>
    
    <!-- 快捷功能入口 -->
    <view class="quick-menu">
      <view class="menu-title">
        <text class="title-text">快捷功能</text>
      </view>
      <view class="menu-grid">
        <view class="menu-item" @click="navigateTo('/pages/inspection/inspection-form')">
          <view class="menu-icon inspection-icon">
            <text class="icon-text">检</text>
          </view>
          <text class="menu-text">检验录入</text>
        </view>
        <view class="menu-item" @click="navigateTo('/pages/trace/trace')">
          <view class="menu-icon trace-icon">
            <text class="icon-text">溯</text>
          </view>
          <text class="menu-text">扫码追溯</text>
        </view>
        <view class="menu-item" @click="navigateTo('/pages/production/production')">
          <view class="menu-icon production-icon">
            <text class="icon-text">产</text>
          </view>
          <text class="menu-text">生产记录</text>
        </view>
        <view class="menu-item" @click="navigateTo('/pages/alert/alert')">
          <view class="menu-icon alert-icon" :class="{ 'has-alert': alertCount > 0 }">
            <text class="icon-text">警</text>
            <text v-if="alertCount > 0" class="alert-badge">{{ alertCount > 99 ? '99+' : alertCount }}</text>
          </view>
          <text class="menu-text">质量预警</text>
        </view>
      </view>
    </view>
    
    <!-- 数据统计卡片 -->
    <view class="stats-section">
      <view class="section-title">
        <text class="title-text">今日统计</text>
      </view>
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value">{{ stats.inspectionCount }}</text>
          <text class="stat-label">检验记录</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.productionCount }}</text>
          <text class="stat-label">生产批次</text>
        </view>
        <view class="stat-item">
          <text class="stat-value success">{{ stats.qualifiedCount }}</text>
          <text class="stat-label">合格批次</text>
        </view>
        <view class="stat-item">
          <text class="stat-value danger">{{ stats.alertCount }}</text>
          <text class="stat-label">待处理预警</text>
        </view>
      </view>
    </view>
    
    <!-- 最近预警列表 -->
    <view class="recent-alerts" v-if="recentAlerts.length > 0">
      <view class="section-title">
        <text class="title-text">最近预警</text>
        <text class="more-text" @click="navigateTo('/pages/alert/alert')">查看全部</text>
      </view>
      <view class="alert-list">
        <view 
          class="alert-item" 
          v-for="(alert, index) in recentAlerts" 
          :key="index"
          @click="goToAlertDetail(alert)"
        >
          <view class="alert-level" :class="alert.alert_level.toLowerCase()">
            <text class="level-text">{{ alert.alert_level }}</text>
          </view>
          <view class="alert-content">
            <text class="alert-type">{{ alertTypeText(alert.alert_type) }}</text>
            <text class="alert-desc">{{ alert.description }}</text>
          </view>
          <view class="alert-status" :class="alert.status.toLowerCase()">
            <text class="status-text">{{ alert.status }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text class="empty-text">暂无预警</text>
      </view>
      <text class="empty-desc">系统运行正常，暂无质量预警</text>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      userInfo: {},
      alertCount: 0,
      stats: {
        inspectionCount: 0,
        productionCount: 0,
        qualifiedCount: 0,
        alertCount: 0
      },
      recentAlerts: [],
      currentDate: ''
    }
  },
  computed: {
    userInitial() {
      if (this.userInfo.real_name) {
        return this.userInfo.real_name.charAt(0)
      }
      return '用'
    },
    roleText() {
      const roleMap = {
        'admin': '管理员',
        'inspector': '检验员'
      }
      return roleMap[this.userInfo.role] || this.userInfo.role
    }
  },
  onShow() {
    this.loadUserInfo()
    this.loadStatistics()
    this.loadRecentAlerts()
    this.loadPendingAlertCount()
  },
  methods: {
    loadUserInfo() {
      const userInfo = uni.getStorageSync('userInfo')
      if (userInfo) {
        this.userInfo = userInfo
      }
      
      // 设置当前日期
      const now = new Date()
      const year = now.getFullYear()
      const month = String(now.getMonth() + 1).padStart(2, '0')
      const day = String(now.getDate()).padStart(2, '0')
      const weekDays = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
      const weekDay = weekDays[now.getDay()]
      this.currentDate = `${year}年${month}月${day}日 ${weekDay}`
    },
    
    async loadStatistics() {
      try {
        // 获取预警统计
        const alertRes = await request.get('/api/alerts/statistics/overview')
        if (alertRes.code === 200) {
          this.stats.alertCount = alertRes.data.by_status.pending
        }
        
        // 获取检验记录统计
        const inspectionRes = await request.get('/api/inspections', {
          page: 1,
          page_size: 1
        })
        if (inspectionRes.code === 200) {
          this.stats.inspectionCount = inspectionRes.total
        }
        
        // 获取生产记录统计
        const productionRes = await request.get('/api/productions/records', {
          page: 1,
          page_size: 1
        })
        if (productionRes.code === 200) {
          this.stats.productionCount = productionRes.total
        }
        
      } catch (err) {
        console.error('加载统计数据失败:', err)
        // 使用模拟数据
        this.stats = {
          inspectionCount: 15,
          productionCount: 8,
          qualifiedCount: 7,
          alertCount: 2
        }
      }
    },
    
    async loadRecentAlerts() {
      try {
        const res = await request.get('/api/alerts', {
          page: 1,
          page_size: 5,
          status: '待处理'
        })
        if (res.code === 200 && res.data.items) {
          this.recentAlerts = res.data.items
        }
      } catch (err) {
        console.error('加载最近预警失败:', err)
        // 使用模拟数据
        this.recentAlerts = [
          {
            id: 1,
            alert_level: '严重',
            alert_type: 'mix_time_short',
            description: '搅拌时间不足：目标90秒，实际60秒',
            status: '待处理'
          },
          {
            id: 2,
            alert_level: '一般',
            alert_type: 'mix_ratio_deviation',
            description: '配比偏差：水泥目标用量350kg，实际360kg',
            status: '待处理'
          }
        ]
      }
    },
    
    async loadPendingAlertCount() {
      try {
        const res = await request.get('/api/alerts/statistics/overview')
        if (res.code === 200) {
          this.alertCount = res.data.by_status.pending
        }
      } catch (err) {
        this.alertCount = 2
      }
    },
    
    navigateTo(url) {
      uni.navigateTo({
        url: url
      })
    },
    
    goToAlertDetail(alert) {
      uni.navigateTo({
        url: `/pages/alert/alert-detail?id=${alert.id}`
      })
    },
    
    alertTypeText(type) {
      const typeMap = {
        'mix_ratio_deviation': '配比偏差',
        'mix_time_short': '搅拌时间不足',
        'material_unqualified': '原材料不合格'
      }
      return typeMap[type] || type
    }
  }
}
</script>

<style scoped>
.index-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

/* 用户信息卡片 */
.user-card {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  padding: 40rpx 32rpx;
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 24rpx;
}

.avatar {
  width: 100rpx;
  height: 100rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.avatar-text {
  font-size: 44rpx;
  font-weight: 600;
  color: #fff;
}

.info-text {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.user-role {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.2);
  padding: 4rpx 16rpx;
  border-radius: 4rpx;
  align-self: flex-start;
}

.date-info {
  padding-left: 124rpx;
}

.date-text {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.7);
}

/* 快捷功能入口 */
.quick-menu {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
}

.menu-title {
  margin-bottom: 24rpx;
}

.title-text {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.menu-grid {
  display: flex;
  justify-content: space-between;
}

.menu-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 23%;
}

.menu-icon {
  width: 112rpx;
  height: 112rpx;
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
  position: relative;
}

.icon-text {
  font-size: 40rpx;
  font-weight: 600;
  color: #fff;
}

.inspection-icon {
  background: linear-gradient(135deg, #4CAF50 0%, #388E3C 100%);
}

.trace-icon {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
}

.production-icon {
  background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
}

.alert-icon {
  background: linear-gradient(135deg, #F44336 0%, #D32F2F 100%);
}

.has-alert {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(244, 67, 54, 0.4);
  }
  50% {
    box-shadow: 0 0 0 12rpx rgba(244, 67, 54, 0);
  }
}

.alert-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  background: #ff4757;
  color: #fff;
  font-size: 20rpx;
  min-width: 36rpx;
  height: 36rpx;
  border-radius: 18rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8rpx;
}

.menu-text {
  font-size: 24rpx;
  color: #666;
}

/* 统计卡片 */
.stats-section {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.more-text {
  font-size: 24rpx;
  color: #1E88E5;
}

.stats-grid {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 25%;
}

.stat-value {
  font-size: 44rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 8rpx;
}

.stat-value.success {
  color: #4CAF50;
}

.stat-value.danger {
  color: #F44336;
}

.stat-label {
  font-size: 22rpx;
  color: #999;
}

/* 最近预警 */
.recent-alerts {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
}

.alert-list {
  margin-top: 16rpx;
}

.alert-item {
  display: flex;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-level {
  padding: 8rpx 16rpx;
  border-radius: 8rpx;
  margin-right: 16rpx;
}

.alert-level.严重 {
  background: #ffebee;
}

.alert-level.一般 {
  background: #fff3e0;
}

.alert-level.紧急 {
  background: #ffebee;
}

.level-text {
  font-size: 22rpx;
  color: #c62828;
}

.一般 .level-text {
  color: #ef6c00;
}

.alert-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.alert-type {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.alert-desc {
  font-size: 22rpx;
  color: #999;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 360rpx;
}

.alert-status {
  padding: 6rpx 12rpx;
  border-radius: 4rpx;
}

.alert-status.待处理 {
  background: #fff3e0;
}

.alert-status.处理中 {
  background: #e3f2fd;
}

.alert-status.已处理 {
  background: #e8f5e9;
}

.status-text {
  font-size: 22rpx;
  color: #ef6c00;
}

.处理中 .status-text {
  color: #1565c0;
}

.已处理 .status-text {
  color: #2e7d32;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}

.empty-icon {
  width: 160rpx;
  height: 160rpx;
  background: #e8f5e9;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 48rpx;
  color: #4CAF50;
}

.empty-desc {
  font-size: 26rpx;
  color: #999;
}
</style>
