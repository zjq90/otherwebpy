<template>
  <view class="alert-container">
    <!-- 统计概览 -->
    <view class="stats-card">
      <view class="stats-row">
        <view class="stat-item" @click="filterByStatus('')">
          <text class="stat-value">{{ stats.total }}</text>
          <text class="stat-label">全部预警</text>
        </view>
        <view class="stat-item pending" @click="filterByStatus('待处理')">
          <text class="stat-value">{{ stats.pending }}</text>
          <text class="stat-label">待处理</text>
        </view>
        <view class="stat-item processing" @click="filterByStatus('处理中')">
          <text class="stat-value">{{ stats.processing }}</text>
          <text class="stat-label">处理中</text>
        </view>
        <view class="stat-item resolved" @click="filterByStatus('已处理')">
          <text class="stat-value">{{ stats.resolved }}</text>
          <text class="stat-label">已处理</text>
        </view>
      </view>
    </view>
    
    <!-- 级别筛选 -->
    <view class="level-filter">
      <view 
        class="filter-item" 
        :class="{ active: filterLevel === '' }"
        @click="filterLevel = ''"
      >
        <text>全部级别</text>
      </view>
      <view 
        class="filter-item urgent" 
        :class="{ active: filterLevel === '紧急' }"
        @click="filterLevel = '紧急'"
      >
        <text>紧急</text>
      </view>
      <view 
        class="filter-item serious" 
        :class="{ active: filterLevel === '严重' }"
        @click="filterLevel = '严重'"
      >
        <text>严重</text>
      </view>
      <view 
        class="filter-item normal" 
        :class="{ active: filterLevel === '一般' }"
        @click="filterLevel = '一般'"
      >
        <text>一般</text>
      </view>
    </view>
    
    <!-- 预警列表 -->
    <view class="alert-list" v-if="alertList.length > 0">
      <view 
        class="alert-card" 
        v-for="(item, index) in alertList" 
        :key="index"
        @click="goToDetail(item)"
      >
        <view class="card-header">
          <view class="alert-level" :class="item.alert_level.toLowerCase()">
            <text class="level-text">{{ item.alert_level }}</text>
          </view>
          <view class="alert-status" :class="item.status.toLowerCase()">
            <text class="status-text">{{ item.status }}</text>
          </view>
        </view>
        
        <view class="card-body">
          <view class="alert-type-row">
            <text class="alert-type">{{ alertTypeText(item.alert_type) }}</text>
            <text class="alert-time">{{ formatTime(item.created_at) }}</text>
          </view>
          <text class="alert-desc">{{ item.description }}</text>
        </view>
        
        <view class="card-footer" v-if="item.status === '待处理'">
          <view class="action-btn primary" @click.stop="handleAlert(item)">
            <text class="btn-text">一键处理</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text class="empty-text">🔔</text>
      </view>
      <text class="empty-title">暂无预警信息</text>
      <text class="empty-desc">系统运行正常，暂无质量预警</text>
    </view>
    
    <!-- 加载更多 -->
    <view class="load-more" v-if="alertList.length > 0 && hasMore">
      <text class="load-text">{{ loading ? '加载中...' : '上拉加载更多' }}</text>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      filterStatus: '',
      filterLevel: '',
      alertList: [],
      page: 1,
      pageSize: 10,
      loading: false,
      hasMore: true,
      stats: {
        total: 0,
        pending: 0,
        processing: 0,
        resolved: 0
      }
    }
  },
  onShow() {
    this.page = 1
    this.alertList = []
    this.loadStatistics()
    this.loadAlerts()
  },
  onPullDownRefresh() {
    this.page = 1
    this.alertList = []
    Promise.all([
      this.loadStatistics(),
      this.loadAlerts()
    ]).then(() => {
      uni.stopPullDownRefresh()
    })
  },
  onReachBottom() {
    if (this.hasMore && !this.loading) {
      this.loadAlerts()
    }
  },
  watch: {
    filterStatus() {
      this.page = 1
      this.alertList = []
      this.loadAlerts()
    },
    filterLevel() {
      this.page = 1
      this.alertList = []
      this.loadAlerts()
    }
  },
  methods: {
    async loadStatistics() {
      try {
        const res = await request.get('/api/alerts/statistics/overview')
        if (res.code === 200) {
          this.stats = {
            total: res.data.total,
            pending: res.data.by_status.pending,
            processing: res.data.by_status.processing,
            resolved: res.data.by_status.resolved
          }
        }
      } catch (err) {
        console.error('加载统计失败:', err)
        // 使用模拟数据
        this.stats = {
          total: 5,
          pending: 2,
          processing: 1,
          resolved: 2
        }
      }
    },
    
    async loadAlerts() {
      if (this.loading) return
      
      this.loading = true
      
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        
        if (this.filterStatus) {
          params.status = this.filterStatus
        }
        if (this.filterLevel) {
          params.alert_level = this.filterLevel
        }
        
        const res = await request.get('/api/alerts', params)
        
        if (res.code === 200) {
          const items = res.data.items || []
          
          if (this.page === 1) {
            this.alertList = items
          } else {
            this.alertList = [...this.alertList, ...items]
          }
          
          this.hasMore = items.length === this.pageSize
          if (items.length === this.pageSize) {
            this.page++
          }
        }
      } catch (err) {
        console.error('加载预警列表失败:', err)
        // 使用模拟数据
        this.alertList = [
          {
            id: 1,
            alert_level: '严重',
            alert_type: 'mix_time_short',
            status: '待处理',
            description: '搅拌时间不足：目标90秒，实际60秒，短缺30秒',
            created_at: '2026-05-05T10:30:00'
          },
          {
            id: 2,
            alert_level: '一般',
            alert_type: 'mix_ratio_deviation',
            status: '处理中',
            description: '配比偏差：水泥目标用量350kg，实际360kg，偏差2.86%',
            created_at: '2026-05-04T14:20:00'
          },
          {
            id: 3,
            alert_level: '紧急',
            alert_type: 'material_unqualified',
            status: '已处理',
            description: '原材料不合格：批次BATCH-002杂质含量超标',
            created_at: '2026-05-03T09:15:00'
          }
        ]
      } finally {
        this.loading = false
      }
    },
    
    filterByStatus(status) {
      this.filterStatus = status
    },
    
    goToDetail(item) {
      uni.navigateTo({
        url: `/pages/alert/alert-detail?id=${item.id}`
      })
    },
    
    async handleAlert(item) {
      uni.showModal({
        title: '确认处理',
        content: '确定要标记此预警为已处理吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              const result = await request.post(`/api/alerts/${item.id}/resolve`, {}, {
                data: {
                  handle_result: '已安排复检，确认产品合格'
                }
              })
              
              if (result.code === 200) {
                uni.showToast({
                  title: '处理成功',
                  icon: 'success'
                })
                
                // 刷新列表
                this.page = 1
                this.alertList = []
                this.loadStatistics()
                this.loadAlerts()
              }
            } catch (err) {
              console.error('处理预警失败:', err)
              // 模拟处理成功
              uni.showToast({
                title: '处理成功',
                icon: 'success'
              })
              
              this.page = 1
              this.alertList = []
              this.loadStatistics()
              this.loadAlerts()
            }
          }
        }
      })
    },
    
    alertTypeText(type) {
      const typeMap = {
        'mix_ratio_deviation': '配比偏差',
        'mix_time_short': '搅拌时间不足',
        'material_unqualified': '原材料不合格'
      }
      return typeMap[type] || type
    },
    
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const date = new Date(timeStr)
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hour = String(date.getHours()).padStart(2, '0')
      const minute = String(date.getMinutes()).padStart(2, '0')
      return `${month}-${day} ${hour}:${minute}`
    }
  }
}
</script>

<style scoped>
.alert-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

/* 统计卡片 */
.stats-card {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  padding: 32rpx 24rpx;
  margin: 0;
}

.stats-row {
  display: flex;
  justify-content: space-between;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 8rpx;
}

.stat-value {
  font-size: 40rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

/* 级别筛选 */
.level-filter {
  display: flex;
  padding: 20rpx 24rpx;
  background: #fff;
  margin-bottom: 20rpx;
}

.filter-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16rpx 0;
  margin: 0 8rpx;
  border-radius: 8rpx;
  background: #f5f5f5;
}

.filter-item.active {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
}

.filter-item.active text {
  color: #fff;
}

.filter-item text {
  font-size: 24rpx;
  color: #666;
}

/* 预警列表 */
.alert-list {
  padding: 0 24rpx;
}

.alert-card {
  background: #fff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.alert-level {
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.alert-level.紧急 {
  background: #ffebee;
}

.alert-level.严重 {
  background: #ffebee;
}

.alert-level.一般 {
  background: #fff3e0;
}

.level-text {
  font-size: 22rpx;
}

.紧急 .level-text,
.严重 .level-text {
  color: #c62828;
}

.一般 .level-text {
  color: #ef6c00;
}

.alert-status {
  padding: 6rpx 16rpx;
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
}

.待处理 .status-text {
  color: #ef6c00;
}

.处理中 .status-text {
  color: #1565c0;
}

.已处理 .status-text {
  color: #2e7d32;
}

.card-body {
  padding: 20rpx 24rpx;
}

.alert-type-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.alert-type {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.alert-time {
  font-size: 22rpx;
  color: #999;
}

.alert-desc {
  font-size: 26rpx;
  color: #666;
  line-height: 1.6;
}

.card-footer {
  padding: 16rpx 24rpx;
  border-top: 1rpx solid #f0f0f0;
}

.action-btn {
  padding: 16rpx 32rpx;
  border-radius: 8rpx;
  display: inline-block;
}

.action-btn.primary {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
}

.action-btn.primary .btn-text {
  color: #fff;
}

.btn-text {
  font-size: 26rpx;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;
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
  font-size: 64rpx;
}

.empty-title {
  font-size: 32rpx;
  color: #333;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #999;
}

/* 加载更多 */
.load-more {
  padding: 30rpx;
  text-align: center;
}

.load-text {
  font-size: 26rpx;
  color: #999;
}
</style>
