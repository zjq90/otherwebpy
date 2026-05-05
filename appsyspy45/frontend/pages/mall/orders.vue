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
      <view class="order-list" v-if="orders.length > 0">
        <view class="order-card" v-for="(order, index) in orders" :key="index">
          <view class="order-header">
            <text class="order-no">订单号：{{ order.order_no }}</text>
            <view class="order-status" :class="getStatusClass(order.status)">
              {{ getStatusText(order.status) }}
            </view>
          </view>
          
          <view class="order-body" @click="goDetail(order)">
            <image :src="order.product_cover || '/static/images/default-product.png'" class="product-image"></image>
            <view class="product-info">
              <text class="product-name">{{ order.product_name }}</text>
              <view class="product-price">
                <text class="points">{{ order.points_used }}积分</text>
                <text class="cash" v-if="order.cash_used > 0">+¥{{ order.cash_used }}</text>
              </view>
              <text class="product-quantity">x{{ order.quantity }}</text>
            </view>
          </view>
          
          <view class="order-footer">
            <text class="order-time">下单时间：{{ formatTime(order.created_at) }}</text>
            <view class="order-actions" v-if="order.status === 1">
              <view class="action-btn cancel" @click.stop="cancelOrder(order)">取消订单</view>
            </view>
            <view class="order-actions" v-else-if="order.status === 3">
              <view class="action-btn confirm" @click.stop="confirmReceive(order)">确认收货</view>
            </view>
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-if="orders.length === 0 && !loading">
        <text class="empty-text">暂无兑换订单</text>
        <view class="empty-btn" @click="goMall">去逛逛</view>
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
  1: '待支付',
  2: '待发货',
  3: '待收货',
  4: '已完成',
  5: '已取消',
  6: '已退款'
}

const STATUS_CLASS_MAP = {
  1: 'status-pending',
  2: 'status-progress',
  3: 'status-progress',
  4: 'status-completed',
  5: 'status-cancelled',
  6: 'status-cancelled'
}

export default {
  data() {
    return {
      filters: [
        { label: '全部', value: null },
        { label: '待支付', value: 1 },
        { label: '待发货', value: 2 },
        { label: '待收货', value: 3 },
        { label: '已完成', value: 4 }
      ],
      currentFilter: null,
      orders: [],
      page: 1,
      pageSize: 10,
      hasMore: true,
      loading: false
    }
  },
  
  onLoad() {
    this.loadOrders()
  },
  
  onShow() {
    this.page = 1
    this.orders = []
    this.hasMore = true
    this.loadOrders()
  },
  
  methods: {
    formatTime(time) {
      return utils.formatDateTime(time)
    },
    
    getStatusText(status) {
      return STATUS_MAP[status] || '未知'
    },
    
    getStatusClass(status) {
      return STATUS_CLASS_MAP[status] || ''
    },
    
    switchFilter(value) {
      if (this.currentFilter === value) return
      
      this.currentFilter = value
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
        
        if (this.currentFilter !== null) {
          params.status = this.currentFilter
        }
        
        const res = await api.get('/points/exchange-orders', params)
        
        if (res.code === 200) {
          const list = res.data.list || []
          
          if (this.page === 1) {
            this.orders = list
          } else {
            this.orders = [...this.orders, ...list]
          }
          
          this.hasMore = list.length >= this.pageSize
          this.page++
        }
      } catch (e) {
        console.error('加载兑换订单失败:', e)
      } finally {
        this.loading = false
      }
    },
    
    loadMore() {
      if (this.hasMore && !this.loading) {
        this.loadOrders()
      }
    },
    
    goDetail(order) {
      uni.navigateTo({
        url: `/pages/mall/orders?id=${order.id}`
      })
    },
    
    async cancelOrder(order) {
      const confirmed = await utils.showModal('确定要取消该订单吗？')
      if (!confirmed) return
      
      utils.showLoading('取消中...')
      
      try {
        const res = await api.post(`/points/exchange-orders/${order.id}/cancel`)
        
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
    
    async confirmReceive(order) {
      const confirmed = await utils.showModal('确认已收到商品吗？')
      if (!confirmed) return
      
      utils.showLoading('确认中...')
      
      try {
        const res = await api.post(`/points/exchange-orders/${order.id}/confirm`)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          utils.showToast('确认成功')
          
          this.page = 1
          this.orders = []
          this.hasMore = true
          this.loadOrders()
        }
      } catch (e) {
        utils.hideLoading()
        console.error('确认收货失败:', e)
      }
    },
    
    goMall() {
      uni.switchTab({
        url: '/pages/mall/index'
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
  display: flex;
  padding: 30rpx;
}

.product-image {
  width: 160rpx;
  height: 160rpx;
  border-radius: $border-radius-md;
  margin-right: 20rpx;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-price {
  display: flex;
  align-items: baseline;
}

.points {
  font-size: $font-size-base;
  color: $primary-color;
  font-weight: bold;
}

.cash {
  font-size: $font-size-sm;
  color: $danger-color;
  margin-left: 10rpx;
}

.product-quantity {
  font-size: $font-size-sm;
  color: $text-secondary;
  text-align: right;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 30rpx;
  border-top: 1rpx solid $border-color;
}

.order-time {
  font-size: $font-size-sm;
  color: $text-muted;
}

.order-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  padding: 12rpx 30rpx;
  border-radius: 30rpx;
  font-size: $font-size-sm;
  
  &.cancel {
    background-color: $bg-color;
    color: $text-secondary;
  }
  
  &.confirm {
    background-color: $primary-color;
    color: $white;
  }
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
