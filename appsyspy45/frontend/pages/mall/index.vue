<template>
  <view class="page">
    <view class="search-bar" @click="goSearch">
      <text class="search-icon">🔍</text>
      <text class="search-placeholder">搜索商品</text>
    </view>
    
    <view class="category-section">
      <view class="category-list">
        <view 
          class="category-item" 
          v-for="(cat, index) in categories" 
          :key="index"
          :class="{ active: currentCategory === cat.id }"
          @click="switchCategory(cat.id)"
        >
          <text class="category-name">{{ cat.name }}</text>
        </view>
      </view>
    </view>
    
    <scroll-view scroll-y class="scroll-content" @scrolltolower="loadMore">
      <view class="product-grid" v-if="products.length > 0">
        <view class="product-item" v-for="(item, index) in products" :key="index" @click="goDetail(item)">
          <image :src="item.cover_image || '/static/images/default-product.png'" class="product-image"></image>
          <view class="product-info">
            <text class="product-name">{{ item.name }}</text>
            <view class="product-price">
              <text class="points">{{ item.points_required }}积分</text>
              <text class="price" v-if="item.cash_required > 0">+{{ item.cash_required }}元</text>
            </view>
            <view class="product-stock">
              <text class="stock-text">库存：{{ item.stock }}件</text>
              <text class="sales-text">已兑{{ item.sales_count }}件</text>
            </view>
          </view>
          <view class="exchange-btn" :class="{ disabled: item.stock <= 0 }">
            立即兑换
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-if="products.length === 0 && !loading">
        <text class="empty-text">暂无商品</text>
      </view>
      
      <view class="loading-state" v-if="loading">
        <text>加载中...</text>
      </view>
      
      <view class="no-more" v-if="!hasMore && products.length > 0">
        <text>没有更多了</text>
      </view>
      
      <view class="bottom-spacer"></view>
    </scroll-view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

export default {
  data() {
    return {
      categories: [],
      currentCategory: null,
      products: [],
      page: 1,
      pageSize: 10,
      hasMore: true,
      loading: false
    }
  },
  
  onShow() {
    this.loadData()
  },
  
  methods: {
    async loadData() {
      await Promise.all([
        this.loadCategories(),
        this.loadProducts()
      ])
    },
    
    async loadCategories() {
      try {
        const res = await api.get('/points/product-categories')
        if (res.code === 200) {
          this.categories = [{ id: null, name: '全部' }, ...(res.data.list || [])]
        }
      } catch (e) {
        console.error('加载商品分类失败:', e)
      }
    },
    
    async loadProducts() {
      if (this.loading) return
      
      this.loading = true
      
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        
        if (this.currentCategory) {
          params.category_id = this.currentCategory
        }
        
        const res = await api.get('/points/products', params)
        
        if (res.code === 200) {
          const list = res.data.list || []
          
          if (this.page === 1) {
            this.products = list
          } else {
            this.products = [...this.products, ...list]
          }
          
          this.hasMore = list.length >= this.pageSize
          this.page++
        }
      } catch (e) {
        console.error('加载商品列表失败:', e)
      } finally {
        this.loading = false
      }
    },
    
    switchCategory(categoryId) {
      if (this.currentCategory === categoryId) return
      
      this.currentCategory = categoryId
      this.page = 1
      this.products = []
      this.hasMore = true
      this.loadProducts()
    },
    
    loadMore() {
      if (this.hasMore && !this.loading) {
        this.loadProducts()
      }
    },
    
    goSearch() {
      utils.showToast('搜索功能开发中')
    },
    
    goDetail(product) {
      uni.navigateTo({
        url: `/pages/mall/product?id=${product.id}`
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

.search-bar {
  display: flex;
  align-items: center;
  background-color: $white;
  margin: 20rpx;
  padding: 20rpx 30rpx;
  border-radius: 40rpx;
}

.search-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
}

.search-placeholder {
  font-size: $font-size-sm;
  color: $text-muted;
}

.category-section {
  background-color: $white;
  margin-bottom: 20rpx;
}

.category-list {
  display: flex;
  overflow-x: auto;
  white-space: nowrap;
  padding: 20rpx;
  
  &::-webkit-scrollbar {
    display: none;
  }
}

.category-item {
  flex-shrink: 0;
  padding: 16rpx 40rpx;
  margin-right: 20rpx;
  font-size: $font-size-sm;
  color: $text-secondary;
  border-radius: 30rpx;
  background-color: $bg-color;
  
  &.active {
    background-color: $primary-color;
    color: $white;
  }
}

.category-name {
  font-size: $font-size-base;
}

.scroll-content {
  height: calc(100vh - 200rpx);
}

.product-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 0 20rpx;
  gap: 20rpx;
}

.product-item {
  width: calc(50% - 10rpx);
  background-color: $white;
  border-radius: $border-radius-md;
  overflow: hidden;
  position: relative;
}

.product-image {
  width: 100%;
  height: 280rpx;
}

.product-info {
  padding: 20rpx;
}

.product-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.product-price {
  display: flex;
  align-items: baseline;
  margin-bottom: 16rpx;
}

.points {
  font-size: $font-size-lg;
  color: $primary-color;
  font-weight: bold;
}

.price {
  font-size: $font-size-sm;
  color: $danger-color;
  margin-left: 10rpx;
}

.product-stock {
  display: flex;
  justify-content: space-between;
}

.stock-text,
.sales-text {
  font-size: $font-size-xs;
  color: $text-muted;
}

.exchange-btn {
  position: absolute;
  right: 20rpx;
  bottom: 80rpx;
  padding: 10rpx 24rpx;
  background-color: $primary-color;
  color: $white;
  font-size: $font-size-xs;
  border-radius: 20rpx;
  
  &.disabled {
    background-color: $text-muted;
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
}

.loading-state,
.no-more {
  text-align: center;
  padding: 30rpx;
  font-size: $font-size-sm;
  color: $text-muted;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
