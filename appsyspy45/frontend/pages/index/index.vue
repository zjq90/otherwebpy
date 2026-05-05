<template>
  <view class="page">
    <view class="header">
      <view class="location">
        <text class="iconfont">📍</text>
        <text class="location-text">{{ location || '请选择地址' }}</text>
      </view>
      <view class="search-bar" @click="goSearch">
        <text class="iconfont">🔍</text>
        <text class="placeholder">搜索回收服务</text>
      </view>
    </view>
    
    <scroll-view scroll-y class="scroll-content">
      <view class="banner">
        <swiper class="banner-swiper" indicator-dots autoplay circular>
          <swiper-item v-for="(item, index) in banners" :key="index">
            <image :src="item.image" class="banner-image" mode="aspectFill"></image>
          </swiper-item>
        </swiper>
      </view>
      
      <view class="menu-grid">
        <view class="menu-item" v-for="(item, index) in menuList" :key="index" @click="handleMenuClick(item)">
          <image :src="item.icon" class="menu-icon"></image>
          <text class="menu-text">{{ item.name }}</text>
        </view>
      </view>
      
      <view class="quick-recycle">
        <view class="section-header">
          <text class="section-title">快速回收</text>
          <text class="section-more" @click="goCreateOrder">更多 ></text>
        </view>
        <view class="clothing-types">
          <view 
            class="type-item" 
            v-for="(item, index) in clothingTypes" 
            :key="index"
            @click="selectType(item)"
          >
            <image :src="item.icon" class="type-icon"></image>
            <text class="type-name">{{ item.name }}</text>
            <text class="type-points">{{ item.points }}积分/件</text>
          </view>
        </view>
      </view>
      
      <view class="eco-stats">
        <view class="section-header">
          <text class="section-title">环保贡献</text>
        </view>
        <view class="stats-grid">
          <view class="stat-item">
            <text class="stat-value">{{ stats.totalWeight }}kg</text>
            <text class="stat-label">回收重量</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.orderCount }}次</text>
            <text class="stat-label">回收次数</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.carbonSaved }}kg</text>
            <text class="stat-label">减碳量</text>
          </view>
          <view class="stat-item">
            <text class="stat-value">{{ stats.pointsBalance }}</text>
            <text class="stat-label">积分余额</text>
          </view>
        </view>
      </view>
      
      <view class="hot-articles">
        <view class="section-header">
          <text class="section-title">环保资讯</text>
          <text class="section-more" @click="goArticles">更多 ></text>
        </view>
        <view class="article-list">
          <view class="article-item" v-for="(item, index) in hotArticles" :key="index" @click="goArticleDetail(item)">
            <image :src="item.cover_image" class="article-cover"></image>
            <view class="article-info">
              <text class="article-title">{{ item.title }}</text>
              <text class="article-summary">{{ item.summary }}</text>
              <view class="article-meta">
                <text class="article-time">{{ formatTime(item.created_at) }}</text>
                <text class="article-views">{{ item.view_count }}阅读</text>
              </view>
            </view>
          </view>
        </view>
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
      location: '北京市朝阳区',
      banners: [
        { image: '/static/images/banner1.jpg', link: '' },
        { image: '/static/images/banner2.jpg', link: '' },
        { image: '/static/images/banner3.jpg', link: '' }
      ],
      menuList: [
        { name: '预约回收', icon: '/static/icons/recycle.png', path: '/pages/order/create' },
        { name: '我的订单', icon: '/static/icons/order.png', path: '/pages/order/list' },
        { name: '积分商城', icon: '/static/icons/mall.png', path: '/pages/mall/index' },
        { name: '邀请好友', icon: '/static/icons/invite.png', path: '/pages/points/invite' },
        { name: '环保资讯', icon: '/static/icons/article.png', path: '/pages/article/list' },
        { name: '客服中心', icon: '/static/icons/service.png', path: '/pages/chat/list' },
        { name: '回收流程', icon: '/static/icons/process.png', path: '' },
        { name: '更多服务', icon: '/static/icons/more.png', path: '' }
      ],
      clothingTypes: [],
      hotArticles: [],
      stats: {
        totalWeight: 0,
        orderCount: 0,
        carbonSaved: 0,
        pointsBalance: 0
      }
    }
  },
  
  onShow() {
    this.loadData()
  },
  
  methods: {
    formatTime(time) {
      return utils.formatDate(time)
    },
    
    async loadData() {
      await Promise.all([
        this.loadClothingTypes(),
        this.loadHotArticles(),
        this.loadUserStats()
      ])
    },
    
    async loadClothingTypes() {
      try {
        const res = await api.get('/order/clothing-types')
        if (res.code === 200) {
          this.clothingTypes = res.data.list || []
        }
      } catch (e) {
        console.error('加载衣物类型失败:', e)
      }
    },
    
    async loadHotArticles() {
      try {
        const res = await api.get('/article/hot', { limit: 3 })
        if (res.code === 200) {
          this.hotArticles = res.data.list || []
        }
      } catch (e) {
        console.error('加载热门资讯失败:', e)
      }
    },
    
    async loadUserStats() {
      const token = uni.getStorageSync('token')
      if (!token) return
      
      try {
        const res = await api.get('/user/statistics')
        if (res.code === 200) {
          this.stats = {
            totalWeight: res.data.total_weight || 0,
            orderCount: res.data.order_count || 0,
            carbonSaved: res.data.carbon_saved || 0,
            pointsBalance: res.data.points_balance || 0
          }
        }
      } catch (e) {
        console.error('加载用户统计失败:', e)
      }
    },
    
    handleMenuClick(item) {
      if (item.path) {
        if (item.path.startsWith('/pages/mall') || item.path.startsWith('/pages/article') || item.path.startsWith('/pages/user')) {
          uni.switchTab({
            url: item.path
          })
        } else {
          uni.navigateTo({
            url: item.path
          })
        }
      } else {
        utils.showToast('功能开发中')
      }
    },
    
    selectType(item) {
      uni.setStorageSync('selectedClothingType', item)
      uni.navigateTo({
        url: '/pages/order/create'
      })
    },
    
    goSearch() {
      utils.showToast('搜索功能开发中')
    },
    
    goCreateOrder() {
      uni.navigateTo({
        url: '/pages/order/create'
      })
    },
    
    goArticles() {
      uni.switchTab({
        url: '/pages/article/list'
      })
    },
    
    goArticleDetail(item) {
      uni.navigateTo({
        url: `/pages/article/detail?id=${item.id}`
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

.header {
  background: linear-gradient(135deg, $primary-color, #66BB6A);
  padding: 30rpx;
  padding-top: calc(30rpx + env(safe-area-inset-top));
}

.location {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  color: $white;
  font-size: $font-size-base;
}

.location-text {
  margin-left: 10rpx;
}

.search-bar {
  display: flex;
  align-items: center;
  background-color: rgba($white, 0.2);
  border-radius: 40rpx;
  padding: 16rpx 30rpx;
  color: $white;
}

.placeholder {
  margin-left: 16rpx;
  font-size: $font-size-sm;
  opacity: 0.8;
}

.scroll-content {
  height: calc(100vh - 200rpx);
}

.banner {
  padding: 20rpx;
}

.banner-swiper {
  height: 300rpx;
  border-radius: $border-radius-lg;
  overflow: hidden;
}

.banner-image {
  width: 100%;
  height: 100%;
}

.menu-grid {
  display: flex;
  flex-wrap: wrap;
  background-color: $white;
  padding: 20rpx 0;
  margin: 0 20rpx;
  border-radius: $border-radius-lg;
}

.menu-item {
  width: 25%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 0;
}

.menu-icon {
  width: 80rpx;
  height: 80rpx;
  margin-bottom: 10rpx;
}

.menu-text {
  font-size: $font-size-sm;
  color: $text-color;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 0;
}

.section-title {
  font-size: $font-size-lg;
  font-weight: bold;
  color: $text-color;
}

.section-more {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.quick-recycle,
.eco-stats,
.hot-articles {
  background-color: $white;
  margin: 20rpx;
  padding: 0 30rpx;
  border-radius: $border-radius-lg;
}

.clothing-types {
  display: flex;
  flex-wrap: wrap;
  padding-bottom: 30rpx;
}

.type-item {
  width: 50%;
  display: flex;
  align-items: center;
  padding: 20rpx;
  box-sizing: border-box;
  border: 2rpx solid $border-color;
  border-radius: $border-radius-md;
  margin-bottom: 20rpx;
  
  &:nth-child(odd) {
    margin-right: 10rpx;
  }
  
  &:nth-child(even) {
    margin-left: 10rpx;
  }
}

.type-icon {
  width: 80rpx;
  height: 80rpx;
  margin-right: 20rpx;
}

.type-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.type-points {
  font-size: $font-size-sm;
  color: $primary-color;
  margin-top: 6rpx;
}

.stats-grid {
  display: flex;
  padding-bottom: 30rpx;
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $primary-color;
}

.stat-label {
  font-size: $font-size-sm;
  color: $text-secondary;
  margin-top: 10rpx;
}

.article-list {
  padding-bottom: 30rpx;
}

.article-item {
  display: flex;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.article-cover {
  width: 200rpx;
  height: 140rpx;
  border-radius: $border-radius-md;
  margin-right: 20rpx;
}

.article-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.article-title {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-summary {
  font-size: $font-size-sm;
  color: $text-secondary;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-top: 10rpx;
}

.article-meta {
  display: flex;
  justify-content: space-between;
  margin-top: 10rpx;
}

.article-time,
.article-views {
  font-size: $font-size-xs;
  color: $text-muted;
}

.bottom-spacer {
  height: 200rpx;
}
</style>
