<template>
  <view class="page">
    <view class="filter-bar">
      <view 
        class="filter-item" 
        v-for="(filter, index) in filters" 
        :key="index"
        :class="{ active: currentFilter === filter.value }"
        @click="switchFilter(filter.value)"
      >
        {{ filter.label }}
      </view>
    </view>
    
    <scroll-view scroll-y class="scroll-content" @scrolltolower="loadMore">
      <view class="history-list" v-if="historyList.length > 0">
        <view class="history-item" v-for="(item, index) in historyList" :key="index">
          <view class="history-header">
            <view class="history-type">
              <text class="type-icon">{{ getTypeIcon(item.type) }}</text>
              <text class="type-name">{{ getTypeName(item.type) }}</text>
            </view>
            <view class="history-points" :class="{ income: item.points > 0 }">
              {{ item.points > 0 ? '+' : '' }}{{ item.points }}
            </view>
          </view>
          <view class="history-body">
            <text class="history-desc">{{ item.description }}</text>
            <text class="history-time">{{ formatTime(item.created_at) }}</text>
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-if="historyList.length === 0 && !loading">
        <text class="empty-text">暂无积分记录</text>
      </view>
      
      <view class="loading-state" v-if="loading">
        <text>加载中...</text>
      </view>
      
      <view class="no-more" v-if="!hasMore && historyList.length > 0">
        <text>没有更多了</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

const TYPE_MAP = {
  'recycle': { name: '旧衣回收', icon: '👕' },
  'invite': { name: '邀请奖励', icon: '🎉' },
  'exchange': { name: '商品兑换', icon: '🛍️' },
  'register': { name: '新用户奖励', icon: '🎁' },
  'activity': { name: '活动奖励', icon: '🎊' },
  'other': { name: '其他', icon: '📋' }
}

export default {
  data() {
    return {
      filters: [
        { label: '全部', value: null },
        { label: '收入', value: 'income' },
        { label: '支出', value: 'expense' }
      ],
      currentFilter: null,
      historyList: [],
      page: 1,
      pageSize: 10,
      hasMore: true,
      loading: false
    }
  },
  
  onLoad() {
    this.loadHistory()
  },
  
  methods: {
    formatTime(time) {
      return utils.formatDateTime(time)
    },
    
    getTypeName(type) {
      return TYPE_MAP[type]?.name || type
    },
    
    getTypeIcon(type) {
      return TYPE_MAP[type]?.icon || '📋'
    },
    
    switchFilter(value) {
      if (this.currentFilter === value) return
      
      this.currentFilter = value
      this.page = 1
      this.historyList = []
      this.hasMore = true
      this.loadHistory()
    },
    
    async loadHistory() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      if (this.loading) return
      
      this.loading = true
      
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        
        if (this.currentFilter) {
          params.type = this.currentFilter
        }
        
        const res = await api.get('/points/transactions', params)
        
        if (res.code === 200) {
          const list = res.data.list || []
          
          if (this.page === 1) {
            this.historyList = list
          } else {
            this.historyList = [...this.historyList, ...list]
          }
          
          this.hasMore = list.length >= this.pageSize
          this.page++
        }
      } catch (e) {
        console.error('加载积分明细失败:', e)
      } finally {
        this.loading = false
      }
    },
    
    loadMore() {
      if (this.hasMore && !this.loading) {
        this.loadHistory()
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
}

.filter-bar {
  display: flex;
  background-color: $white;
  padding: 20rpx;
}

.filter-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: $font-size-base;
  color: $text-secondary;
  border-radius: $border-radius-md;
  margin: 0 10rpx;
  
  &.active {
    background-color: rgba($primary-color, 0.1);
    color: $primary-color;
    font-weight: bold;
  }
}

.scroll-content {
  height: calc(100vh - 100rpx);
}

.history-list {
  padding: 20rpx;
}

.history-item {
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.history-type {
  display: flex;
  align-items: center;
}

.type-icon {
  font-size: 36rpx;
  margin-right: 16rpx;
}

.type-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.history-points {
  font-size: $font-size-lg;
  font-weight: bold;
  color: $danger-color;
  
  &.income {
    color: $success-color;
  }
}

.history-body {
  display: flex;
  flex-direction: column;
}

.history-desc {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.history-time {
  font-size: $font-size-xs;
  color: $text-muted;
  margin-top: 10rpx;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 0;
}

.empty-text {
  font-size: $font-size-base;
  color: $text-secondary;
}

.loading-state,
.no-more {
  text-align: center;
  padding: 30rpx;
  font-size: $font-size-sm;
  color: $text-muted;
}
</style>
