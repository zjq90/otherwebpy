<template>
  <view class="page">
    <view class="tab-bar">
      <view 
        class="tab-item" 
        v-for="(tab, index) in tabs" 
        :key="index"
        :class="{ active: currentTab === tab.status }"
        @click="switchTab(tab.status)"
      >
        <text class="tab-text">{{ tab.label }}</text>
        <view class="tab-badge" v-if="tab.status === 1 && pendingCount > 0">{{ pendingCount }}</view>
      </view>
    </view>
    
    <scroll-view scroll-y class="scroll-content" @scrolltolower="loadMore">
      <view class="order-list" v-if="orders.length > 0">
        <view 
          class="order-card" 
          v-for="(order, index) in orders" 
          :key="index"
          @click="goDetail(order)"
        >
          <view class="order-header">
            <text class="order-no">订单号：{{ order.order_no }}</text>
            <view class="order-status" :class="getStatusClass(order.status)">
              {{ getStatusText(order.status) }}
            </view>
          </view>
          
          <view class="order-body">
            <view class="clothing-info">
              <view class="clothing-list">
                <view class="clothing-item" v-for="(item, idx) in order.items" :key="idx">
                  <image :src="item.clothing_type_icon" class="clothing-icon"></image>
                  <view class="clothing-detail">
                    <text class="clothing-name">{{ item.clothing_type_name }}</text>
                    <text class="clothing-quantity">x{{ item.quantity }}</text>
                  </view>
                </view>
              </view>
              <view class="order-summary">
                <text class="summary-text">共{{ order.total_quantity }}件</text>
                <text class="summary-points">预估{{ order.estimate_points }}积分</text>
              </view>
            </view>
            
            <view class="address-info">
              <text class="icon">📍</text>
              <text class="address-text">{{ order.address }}</text>
            </view>
            
            <view class="time-info">
              <text class="icon">🕐</text>
              <text class="time-text">预约时间：{{ order.schedule_date }} {{ order.schedule_time }}</text>
            </view>
          </view>
          
          <view class="order-footer" v-if="order.status === 1 || order.status === 2">
            <view class="btn-cancel" @click.stop="cancelOrder(order)">取消订单</view>
            <view class="btn-contact" v-if="order.collector_phone" @click.stop="callCollector(order)">联系回收员</view>
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-if="orders.length === 0 && !loading">
        <text class="empty-text">暂无订单</text>
        <view class="empty-btn" @click="goCreate">去预约回收</view>
      </view>
      
      <view class="loading-state" v-if="loading">
        <text>加载中...</text>
      </view>
      
      <view class="no-more" v-if="!hasMore && orders.length > 0">
        <text>没有更多了</text>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

const STATUS_MAP = {
  1: '待接单',
  2: '待上门',
  3: '回收中',
  4: '已完成',
  5: '已取消'
}

const STATUS_CLASS = {
  1: 'status-pending',
  2: 'status-progress',
  3: 'status-progress',
  4: 'status-completed',
  5: 'status-cancelled'
}

export default {
  data() {
    return {
      tabs: [
        { label: '全部', status: null },
        { label: '待接单', status: 1 },
        { label: '待上门', status: 2 },
        { label: '回收中', status: 3 },
        { label: '已完成', status: 4 }
      ],
      currentTab: null,
      orders: [],
      page: 1,
      pageSize: 10,
      hasMore: true,
      loading: false,
      pendingCount: 0
    }
  },
  
  onLoad(options) {
    if (options.status) {
      this.currentTab = parseInt(options.status)
    }
  },
  
  onShow() {
    this.page = 1
    this.orders = []
    this.hasMore = true
    this.loadOrders()
  },
  
  methods: {
    getStatusText(status) {
      return STATUS_MAP[status] || '未知'
    },
    
    getStatusClass(status) {
      return STATUS_CLASS[status] || ''
    },
    
    switchTab(status) {
      if (this.currentTab === status) return
      
      this.currentTab = status
      this.page = 1
      this.orders = []
      this.hasMore = true
      this.loadOrders()
    },
    
    async loadOrders() {
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
        
        if (this.currentTab !== null) {
          params.status = this.currentTab
        }
        
        const res = await api.get('/order/list', params)
        
        if (res.code === 200) {
          const list = res.data.list || []
          
          if (this.page === 1) {
            this.orders = list
          } else {
            this.orders = [...this.orders, ...list]
          }
          
          this.hasMore = list.length >= this.pageSize
          this.page++
          
          if (this.currentTab === null) {
            await this.loadPendingCount()
          }
        }
      } catch (e) {
        console.error('加载订单失败:', e)
      } finally {
        this.loading = false
      }
    },
    
    async loadPendingCount() {
      try {
        const res = await api.get('/order/list', { status: 1, page: 1, page_size: 1 })
        if (res.code === 200) {
          this.pendingCount = res.data.total || 0
        }
      } catch (e) {
        console.error('加载待处理订单数量失败:', e)
      }
    },
    
    loadMore() {
      if (this.hasMore && !this.loading) {
        this.loadOrders()
      }
    },
    
    goDetail(order) {
      uni.navigateTo({
        url: `/pages/order/detail?id=${order.id}`
      })
    },
    
    async cancelOrder(order) {
      const confirmed = await utils.showModal('确定要取消该订单吗？')
      if (!confirmed) return
      
      utils.showLoading('取消中...')
      
      try {
        const res = await api.post(`/order/${order.id}/cancel`)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          utils.showToast('订单已取消')
          
          this.page = 1
          this.orders = []
          this.hasMore = true
          this.loadOrders()
        }
      } catch (e) {
        utils.hideLoading()
        console.error('取消订单失败:', e)
      }
    },
    
    callCollector(order) {
      uni.makePhoneCall({
        phoneNumber: order.collector_phone
      })
    },
    
    goCreate() {
      uni.switchTab({
        url: '/pages/order/create'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
}

.tab-bar {
  display: flex;
  background-color: $white;
  padding: 0 20rpx;
  position: sticky;
  top: 0;
  z-index: 10;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 30rpx 0;
  position: relative;
}

.tab-text {
  font-size: $font-size-base;
  color: $text-secondary;
  
  .active & {
    color: $primary-color;
    font-weight: bold;
  }
}

.tab-badge {
  position: absolute;
  top: 20rpx;
  right: 30rpx;
  min-width: 32rpx;
  height: 32rpx;
  line-height: 32rpx;
  padding: 0 8rpx;
  background-color: $danger-color;
  color: $white;
  font-size: $font-size-xs;
  border-radius: 16rpx;
  text-align: center;
}

.scroll-content {
  height: calc(100vh - 100rpx);
}

.order-list {
  padding: 20rpx;
}

.order-card {
  background-color: $white;
  border-radius: $border-radius-md;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid $border-color;
}

.order-no {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.order-status {
  display: inline-block;
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
  font-size: $font-size-sm;
  
  &.status-pending {
    background-color: #FFF3E0;
    color: $warning-color;
  }
  
  &.status-progress {
    background-color: #E3F2FD;
    color: $info-color;
  }
  
  &.status-completed {
    background-color: #E8F5E9;
    color: $success-color;
  }
  
  &.status-cancelled {
    background-color: #F5F5F5;
    color: $text-secondary;
  }
}

.order-body {
  padding: 30rpx;
}

.clothing-info {
  margin-bottom: 20rpx;
}

.clothing-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 20rpx;
}

.clothing-item {
  display: flex;
  align-items: center;
  padding: 16rpx 20rpx;
  background-color: $bg-color;
  border-radius: $border-radius-sm;
}

.clothing-icon {
  width: 48rpx;
  height: 48rpx;
  margin-right: 16rpx;
}

.clothing-detail {
  display: flex;
  flex-direction: column;
}

.clothing-name {
  font-size: $font-size-sm;
  color: $text-color;
}

.clothing-quantity {
  font-size: $font-size-xs;
  color: $text-secondary;
}

.order-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-top: 1rpx solid $border-color;
}

.summary-text {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.summary-points {
  font-size: $font-size-base;
  color: $primary-color;
  font-weight: bold;
}

.address-info,
.time-info {
  display: flex;
  align-items: flex-start;
  margin-top: 16rpx;
}

.icon {
  margin-right: 16rpx;
  font-size: $font-size-base;
}

.address-text,
.time-text {
  flex: 1;
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
}

.order-footer {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  padding: 20rpx 30rpx;
  border-top: 1rpx solid $border-color;
  gap: 20rpx;
}

.btn-cancel,
.btn-contact {
  padding: 12rpx 30rpx;
  border-radius: 30rpx;
  font-size: $font-size-sm;
}

.btn-cancel {
  background-color: $bg-color;
  color: $text-secondary;
}

.btn-contact {
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
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
  margin-bottom: 30rpx;
}

.empty-btn {
  padding: 20rpx 60rpx;
  background-color: $primary-color;
  color: $white;
  font-size: $font-size-base;
  border-radius: 40rpx;
}

.loading-state,
.no-more {
  text-align: center;
  padding: 30rpx;
  font-size: $font-size-sm;
  color: $text-muted;
}
</style>
