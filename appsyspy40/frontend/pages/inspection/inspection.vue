<template>
  <view class="inspection-container">
    <!-- 搜索和筛选 -->
    <view class="search-section">
      <view class="search-input">
        <text class="search-icon">🔍</text>
        <input 
          placeholder="搜索检验单号/批次号" 
          v-model="searchKeyword"
          @confirm="handleSearch"
        />
      </view>
      <view class="filter-btn" @click="showFilter = !showFilter">
        <text class="filter-text">筛选</text>
      </view>
    </view>
    
    <!-- 筛选面板 -->
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
            :class="{ active: filterStatus === '合格' }"
            @click="filterStatus = '合格'"
          >
            <text>合格</text>
          </view>
          <view 
            class="filter-option" 
            :class="{ active: filterStatus === '禁用' }"
            @click="filterStatus = '禁用'"
          >
            <text>不合格</text>
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
    
    <!-- 检验记录列表 -->
    <view class="inspection-list" v-if="inspectionList.length > 0">
      <view 
        class="inspection-card" 
        v-for="(item, index) in inspectionList" 
        :key="index"
        @click="goToDetail(item)"
      >
        <view class="card-header">
          <view class="card-title">
            <text class="inspection-no">{{ item.inspection_no }}</text>
            <view class="status-tag" :class="item.status">
              <text>{{ item.status }}</text>
            </view>
          </view>
          <text class="batch-no">批次: {{ item.batch_no }}</text>
        </view>
        
        <view class="card-body">
          <view class="info-row">
            <text class="info-label">原材料:</text>
            <text class="info-value">{{ (item.material && item.material.material_name) || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">检验日期:</text>
            <text class="info-value">{{ formatDate(item.inspection_date) }}</text>
          </view>
          <view class="info-row" v-if="item.cement_strength_3d">
            <text class="info-label">3天强度:</text>
            <text class="info-value">{{ item.cement_strength_3d }} MPa</text>
          </view>
          <view class="info-row" v-if="item.cement_strength_28d">
            <text class="info-label">28天强度:</text>
            <text class="info-value">{{ item.cement_strength_28d }} MPa</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text class="empty-text">📋</text>
      </view>
      <text class="empty-title">暂无检验记录</text>
      <text class="empty-desc">点击下方按钮录入新的检验记录</text>
    </view>
    
    <!-- 录入按钮 -->
    <view class="add-btn" @click="goToForm">
      <text class="add-icon">+</text>
      <text class="add-text">录入检验</text>
    </view>
    
    <!-- 加载更多 -->
    <view class="load-more" v-if="inspectionList.length > 0 && hasMore">
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
      inspectionList: [],
      page: 1,
      pageSize: 10,
      loading: false,
      hasMore: true
    }
  },
  onShow() {
    this.page = 1
    this.inspectionList = []
    this.loadInspections()
  },
  onPullDownRefresh() {
    this.page = 1
    this.inspectionList = []
    this.loadInspections().then(() => {
      uni.stopPullDownRefresh()
    })
  },
  onReachBottom() {
    if (this.hasMore && !this.loading) {
      this.loadInspections()
    }
  },
  methods: {
    async loadInspections() {
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
        
        const res = await request.get('/api/inspections', params)
        
        if (res.code === 200) {
          const items = res.data.items || []
          
          if (this.page === 1) {
            this.inspectionList = items
          } else {
            this.inspectionList = [...this.inspectionList, ...items]
          }
          
          this.hasMore = items.length === this.pageSize
          if (items.length === this.pageSize) {
            this.page++
          }
        }
      } catch (err) {
        console.error('加载检验记录失败:', err)
        // 使用模拟数据
        this.inspectionList = [
          {
            id: 1,
            inspection_no: 'INS20260505123456',
            batch_no: 'BATCH-001',
            status: '合格',
            material: { material_name: 'P.O42.5普通硅酸盐水泥' },
            inspection_date: '2026-05-05T10:00:00',
            cement_strength_3d: 28.5,
            cement_strength_28d: 52.3
          },
          {
            id: 2,
            inspection_no: 'INS20260504987654',
            batch_no: 'BATCH-002',
            status: '禁用',
            material: { material_name: '粗骨料(碎石)' },
            inspection_date: '2026-05-04T14:30:00',
            impurity_content: 1.5
          }
        ]
      } finally {
        this.loading = false
      }
    },
    
    handleSearch() {
      this.page = 1
      this.inspectionList = []
      this.loadInspections()
    },
    
    resetFilter() {
      this.filterStatus = ''
    },
    
    applyFilter() {
      this.showFilter = false
      this.page = 1
      this.inspectionList = []
      this.loadInspections()
    },
    
    goToDetail(item) {
      uni.navigateTo({
        url: `/pages/inspection/inspection-detail?id=${item.id}`
      })
    },
    
    goToForm() {
      uni.navigateTo({
        url: '/pages/inspection/inspection-form'
      })
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
  }
}
</script>

<style scoped>
.inspection-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 140rpx;
}

/* 搜索区域 */
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

/* 筛选面板 */
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

/* 检验列表 */
.inspection-list {
  padding: 20rpx;
}

.inspection-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  margin-bottom: 20rpx;
}

.card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.inspection-no {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.status-tag {
  padding: 4rpx 16rpx;
  border-radius: 4rpx;
}

.status-tag.合格 {
  background: #e8f5e9;
}

.status-tag.禁用 {
  background: #ffebee;
}

.status-tag text {
  font-size: 22rpx;
}

.status-tag.合格 text {
  color: #2e7d32;
}

.status-tag.禁用 text {
  color: #c62828;
}

.batch-no {
  font-size: 24rpx;
  color: #999;
}

.card-body {
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.info-row {
  display: flex;
  margin-bottom: 12rpx;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  font-size: 26rpx;
  color: #999;
  width: 160rpx;
}

.info-value {
  font-size: 26rpx;
  color: #333;
  flex: 1;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 120rpx 0;
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

/* 添加按钮 */
.add-btn {
  position: fixed;
  bottom: 40rpx;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  padding: 20rpx 48rpx;
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  border-radius: 50rpx;
  box-shadow: 0 8rpx 24rpx rgba(30, 136, 229, 0.3);
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
