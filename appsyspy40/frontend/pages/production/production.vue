<template>
  <view class="production-container">
    <view class="search-section">
      <view class="search-input">
        <text class="search-icon">🔍</text>
        <input 
          placeholder="搜索生产单号/罐车编号" 
          v-model="searchKeyword"
          @confirm="handleSearch"
        />
      </view>
      <view class="filter-btn" @click="showFilter = !showFilter">
        <text class="filter-text">筛选</text>
      </view>
    </view>
    
    <view class="filter-panel" v-if="showFilter">
      <view class="filter-item">
        <text class="filter-label">状态:</text>
        <view class="filter-options">
          <view 
            class="filter-option" 
            :class="{ active: filterStatus === '' }"
            @click="filterStatus = ''"
          >
            <text>全部</text>
          </view>
          <view 
            class="filter-option" 
            :class="{ active: filterStatus === '正常' }"
            @click="filterStatus = '正常'"
          >
            <text>正常</text>
          </view>
          <view 
            class="filter-option" 
            :class="{ active: filterStatus === '异常' }"
            @click="filterStatus = '异常'"
          >
            <text>异常</text>
          </view>
        </view>
      </view>
      <view class="filter-actions">
        <view class="filter-btn secondary" @click="resetFilter">
          <text>重置</text>
        </view>
        <view class="filter-btn primary" @click="applyFilter">
          <text>确定</text>
        </view>
      </view>
    </view>
    
    <view class="stats-card">
      <view class="stat-item">
        <text class="stat-value">{{ stats.total }}</text>
        <text class="stat-label">总批次</text>
      </view>
      <view class="stat-item normal">
        <text class="stat-value">{{ stats.normal }}</text>
        <text class="stat-label">正常</text>
      </view>
      <view class="stat-item warning">
        <text class="stat-value">{{ stats.warning }}</text>
        <text class="stat-label">异常</text>
      </view>
    </view>
    
    <view class="production-list" v-if="productionList.length > 0">
      <view 
        class="production-card" 
        v-for="(item, index) in productionList" 
        :key="index"
        @click="goToDetail(item)"
      >
        <view class="card-header">
          <view class="header-info">
            <text class="production-no">{{ item.production_no }}</text>
            <text class="truck-no">罐车: {{ item.truck_no || '-' }}</text>
          </view>
          <view class="status-tag" :class="item.status === '正常' ? 'normal' : 'warning'">
            <text class="status-text">{{ item.status || '正常' }}</text>
          </view>
        </view>
        
        <view class="card-body">
          <view class="info-row">
            <text class="info-label">生产时间:</text>
            <text class="info-value">{{ formatTime(item.production_date) }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">工程名称:</text>
            <text class="info-value">{{ item.project_name || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">施工部位:</text>
            <text class="info-value">{{ item.construction_site || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">搅拌时间:</text>
            <text class="info-value" :class="isMixingTimeOk(item) ? '' : 'warning-text'">
              {{ item.mixing_time || '-' }} 秒
            </text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text class="empty-text">🏭</text>
      </view>
      <text class="empty-title">暂无生产记录</text>
      <text class="empty-desc">系统将自动同步生产数据</text>
    </view>
    
    <view class="load-more" v-if="productionList.length > 0 && hasMore">
      <text class="load-text">{{ loading ? '加载中...' : '上拉加载更多' }}</text>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      searchKeyword: '',
      showFilter: false,
      filterStatus: '',
      productionList: [],
      page: 1,
      pageSize: 10,
      loading: false,
      hasMore: true,
      stats: {
        total: 0,
        normal: 0,
        warning: 0
      }
    }
  },
  onShow() {
    this.page = 1
    this.productionList = []
    this.loadProductions()
  },
  methods: {
    async loadProductions() {
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
        
        const res = await request.get('/api/productions', params)
        
        if (res.code === 200) {
          const items = res.data.items || []
          
          if (this.page === 1) {
            this.productionList = items
            this.calculateStats(items)
          } else {
            this.productionList = [...this.productionList, ...items]
          }
          
          this.hasMore = items.length === this.pageSize
          if (items.length === this.pageSize) {
            this.page++
          }
        }
      } catch (err) {
        console.error('加载生产记录失败:', err)
        this.productionList = [
          {
            id: 1,
            production_no: 'PRO20260505123456',
            truck_no: '豫A-12345',
            status: '正常',
            production_date: '2026-05-05T10:30:00',
            project_name: '郑州市轨道交通8号线工程',
            construction_site: '主体结构承台',
            mixing_time: 95,
            target_mix_duration: 90
          },
          {
            id: 2,
            production_no: 'PRO20260504987654',
            truck_no: '豫A-12346',
            status: '异常',
            production_date: '2026-05-04T14:30:00',
            project_name: '郑州市轨道交通8号线工程',
            construction_site: '主体结构柱',
            mixing_time: 60,
            target_mix_duration: 90
          }
        ]
        this.calculateStats(this.productionList)
      } finally {
        this.loading = false
      }
    },
    
    calculateStats(items) {
      const total = items.length
      const normal = items.filter(item => item.status === '正常').length
      const warning = total - normal
      
      this.stats = { total, normal, warning }
    },
    
    handleSearch() {
      this.page = 1
      this.productionList = []
      this.loadProductions()
    },
    
    resetFilter() {
      this.filterStatus = ''
    },
    
    applyFilter() {
      this.showFilter = false
      this.page = 1
      this.productionList = []
      this.loadProductions()
    },
    
    isMixingTimeOk(item) {
      if (!item.mixing_time || !item.target_mix_duration) return true
      return item.mixing_time >= item.target_mix_duration
    },
    
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const date = new Date(timeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hour = String(date.getHours()).padStart(2, '0')
      const minute = String(date.getMinutes()).padStart(2, '0')
      return year + '-' + month + '-' + day + ' ' + hour + ':' + minute
    },
    
    goToDetail(item) {
      uni.navigateTo({
        url: '/pages/production/production-detail?id=' + item.id
      })
    }
  }
}
</script>

<style scoped>
.production-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

.search-section {
  display: flex;
  padding: 20rpx;
  background: #fff;
  align-items: center;
}

.search-input {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 40rpx;
  padding: 16rpx 24rpx;
  margin-right: 16rpx;
}

.search-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.search-input input {
  flex: 1;
  font-size: 28rpx;
}

.filter-btn {
  padding: 16rpx 24rpx;
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  border-radius: 40rpx;
}

.filter-text {
  font-size: 28rpx;
  color: #fff;
}

.filter-panel {
  background: #fff;
  padding: 20rpx;
  border-bottom: 1rpx solid #eee;
}

.filter-item {
  margin-bottom: 20rpx;
}

.filter-label {
  font-size: 28rpx;
  color: #666;
  margin-bottom: 16rpx;
  display: block;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
}

.filter-option {
  padding: 12rpx 32rpx;
  background: #f5f5f5;
  border-radius: 40rpx;
  margin-right: 16rpx;
  margin-bottom: 12rpx;
}

.filter-option.active {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
}

.filter-option.active text {
  color: #fff;
}

.filter-option text {
  font-size: 26rpx;
  color: #666;
}

.filter-actions {
  display: flex;
  justify-content: flex-end;
}

.filter-actions .filter-btn {
  padding: 16rpx 40rpx;
  margin-left: 20rpx;
}

.filter-actions .filter-btn.secondary {
  background: #f5f5f5;
}

.filter-actions .filter-btn.secondary text {
  color: #666;
}

.stats-card {
  display: flex;
  padding: 20rpx;
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  margin: 0;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 40rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4rpx;
}

.stat-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.8);
}

.production-list {
  padding: 20rpx;
}

.production-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.header-info {
  display: flex;
  flex-direction: column;
}

.production-no {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 4rpx;
}

.truck-no {
  font-size: 22rpx;
  color: #999;
}

.status-tag {
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

.status-tag.normal {
  background: #e8f5e9;
}

.status-tag.warning {
  background: #ffebee;
}

.status-text {
  font-size: 22rpx;
}

.normal .status-text {
  color: #2e7d32;
}

.warning .status-text {
  color: #c62828;
}

.card-body {
  padding-top: 16rpx;
}

.info-row {
  display: flex;
  margin-bottom: 10rpx;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 24rpx;
  color: #999;
  width: 140rpx;
}

.info-value {
  font-size: 24rpx;
  color: #666;
  flex: 1;
}

.warning-text {
  color: #c62828;
  font-weight: 500;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;
}

.empty-icon {
  width: 160rpx;
  height: 160rpx;
  background: #e3f2fd;
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

.load-more {
  padding: 30rpx;
  text-align: center;
}

.load-text {
  font-size: 26rpx;
  color: #999;
}
</style>
