<template>
  <view class="material-container">
    <view class="search-section">
      <view class="search-input">
        <text class="search-icon">🔍</text>
        <input 
          placeholder="搜索原材料名称/编码" 
          v-model="searchKeyword"
          @confirm="handleSearch"
        />
      </view>
      <view class="add-btn" @click="showAddTip">
        <text class="add-text">+</text>
      </view>
    </view>
    
    <view class="filter-section">
      <view 
        class="filter-item" 
        :class="{ active: filterType === '' }"
        @click="filterType = ''"
      >
        <text>全部</text>
      </view>
      <view 
        class="filter-item" 
        :class="{ active: filterType === 'cement' }"
        @click="filterType = 'cement'"
      >
        <text>水泥</text>
      </view>
      <view 
        class="filter-item" 
        :class="{ active: filterType === 'aggregate' }"
        @click="filterType = 'aggregate'"
      >
        <text>骨料</text>
      </view>
      <view 
        class="filter-item" 
        :class="{ active: filterType === 'admixture' }"
        @click="filterType = 'admixture'"
      >
        <text>外加剂</text>
      </view>
    </view>
    
    <view class="material-list" v-if="materialList.length > 0">
      <view 
        class="material-card" 
        v-for="(item, index) in materialList" 
        :key="index"
        @click="showDetailTip"
      >
        <view class="card-header">
          <view class="material-icon" :class="item.material_type">
            <text class="icon-text">{{ getTypeIcon(item.material_type) }}</text>
          </view>
          <view class="material-info">
            <text class="material-name">{{ item.material_name }}</text>
            <text class="material-code">{{ item.material_code }}</text>
          </view>
          <view class="type-tag" :class="item.material_type">
            <text class="type-text">{{ getTypeText(item.material_type) }}</text>
          </view>
        </view>
        <view class="card-body">
          <view class="info-row">
            <text class="info-label">规格型号:</text>
            <text class="info-value">{{ item.specification || '-' }}</text>
          </view>
          <view class="info-row">
            <text class="info-label">供应商:</text>
            <text class="info-value">{{ item.supplier || '-' }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text class="empty-text">📦</text>
      </view>
      <text class="empty-title">暂无原材料数据</text>
      <text class="empty-desc">点击右上角按钮添加原材料</text>
    </view>
    
    <view class="load-more" v-if="materialList.length > 0 && hasMore">
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
      filterType: '',
      materialList: [],
      page: 1,
      pageSize: 10,
      loading: false,
      hasMore: true
    }
  },
  onShow() {
    this.page = 1
    this.materialList = []
    this.loadMaterials()
  },
  methods: {
    async loadMaterials() {
      if (this.loading) return
      
      this.loading = true
      
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        
        if (this.filterType) {
          params.material_type = this.filterType
        }
        
        const res = await request.get('/api/materials', params)
        
        if (res.code === 200) {
          const items = res.data.items || []
          
          if (this.page === 1) {
            this.materialList = items
          } else {
            this.materialList = [...this.materialList, ...items]
          }
          
          this.hasMore = items.length === this.pageSize
          if (items.length === this.pageSize) {
            this.page++
          }
        }
      } catch (err) {
        console.error('加载原材料失败:', err)
        this.materialList = [
          {
            id: 1,
            material_code: 'CEM001',
            material_name: 'P.O42.5普通硅酸盐水泥',
            material_type: 'cement',
            specification: 'P.O42.5',
            supplier: '海螺水泥'
          },
          {
            id: 2,
            material_code: 'AGG001',
            material_name: '粗骨料(碎石)',
            material_type: 'aggregate',
            specification: '5-25mm',
            supplier: '本地砂石场'
          },
          {
            id: 3,
            material_code: 'AGG002',
            material_name: '细骨料(河砂)',
            material_type: 'aggregate',
            specification: '中砂',
            supplier: '本地砂石场'
          },
          {
            id: 4,
            material_code: 'ADM001',
            material_name: '聚羧酸高效减水剂',
            material_type: 'admixture',
            specification: 'PCA-1',
            supplier: '江苏博特'
          }
        ]
      } finally {
        this.loading = false
      }
    },
    
    handleSearch() {
      this.page = 1
      this.materialList = []
      this.loadMaterials()
    },
    
    getTypeIcon(type) {
      const iconMap = {
        'cement': '🧱',
        'aggregate': '🪨',
        'admixture': '🧪'
      }
      return iconMap[type] || '📦'
    },
    
    getTypeText(type) {
      const textMap = {
        'cement': '水泥',
        'aggregate': '骨料',
        'admixture': '外加剂'
      }
      return textMap[type] || type
    },
    
    showAddTip() {
      uni.showToast({
        title: '添加功能开发中',
        icon: 'none'
      })
    },
    
    showDetailTip() {
      uni.showToast({
        title: '详情功能开发中',
        icon: 'none'
      })
    }
  }
}
</script>

<style scoped>
.material-container {
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

.add-btn {
  width: 72rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-text {
  font-size: 48rpx;
  color: #fff;
  font-weight: 300;
}

.filter-section {
  display: flex;
  padding: 16rpx 20rpx;
  background: #fff;
  border-bottom: 1rpx solid #f0f0f0;
}

.filter-item {
  padding: 12rpx 28rpx;
  margin-right: 16rpx;
  background: #f5f5f5;
  border-radius: 40rpx;
}

.filter-item.active {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
}

.filter-item text {
  font-size: 26rpx;
  color: #666;
}

.filter-item.active text {
  color: #fff;
}

.material-list {
  padding: 20rpx;
}

.material-card {
  background: #fff;
  border-radius: 16rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.material-icon {
  width: 64rpx;
  height: 64rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.material-icon.cement {
  background: #e3f2fd;
}

.material-icon.aggregate {
  background: #e8f5e9;
}

.material-icon.admixture {
  background: #f3e5f5;
}

.icon-text {
  font-size: 32rpx;
}

.material-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.material-name {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 4rpx;
}

.material-code {
  font-size: 22rpx;
  color: #999;
}

.type-tag {
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

.type-tag.cement {
  background: #e3f2fd;
}

.type-tag.aggregate {
  background: #e8f5e9;
}

.type-tag.admixture {
  background: #f3e5f5;
}

.type-text {
  font-size: 22rpx;
}

.cement .type-text {
  color: #1565c0;
}

.aggregate .type-text {
  color: #2e7d32;
}

.admixture .type-text {
  color: #7b1fa2;
}

.card-body {
  padding-top: 16rpx;
  border-top: 1rpx solid #f0f0f0;
}

.info-row {
  display: flex;
  margin-bottom: 8rpx;
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
