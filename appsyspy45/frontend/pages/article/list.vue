<template>
  <view class="page">
    <view class="category-section">
      <scroll-view scroll-x class="category-scroll">
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
      </scroll-view>
    </view>
    
    <scroll-view scroll-y class="scroll-content" @scrolltolower="loadMore">
      <view class="hot-section" v-if="currentCategory === null">
        <view class="section-header">
          <text class="section-title">🔥 热门推荐</text>
        </view>
        <view class="hot-articles">
          <view class="hot-item" v-for="(item, index) in hotArticles" :key="index" @click="goDetail(item)">
            <image :src="item.cover_image || '/static/images/default-article.png'" class="hot-image"></image>
            <view class="hot-info">
              <text class="hot-title">{{ item.title }}</text>
              <view class="hot-meta">
                <text class="hot-views">{{ item.view_count }}阅读</text>
                <text class="hot-time">{{ formatTime(item.created_at) }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <view class="article-section">
        <view class="section-header" v-if="currentCategory !== null">
          <text class="section-title">最新文章</text>
        </view>
        <view class="article-list">
          <view class="article-item" v-for="(item, index) in articles" :key="index" @click="goDetail(item)">
            <image :src="item.cover_image || '/static/images/default-article.png'" class="article-cover"></image>
            <view class="article-info">
              <text class="article-title">{{ item.title }}</text>
              <text class="article-summary">{{ item.summary }}</text>
              <view class="article-meta">
                <text class="article-category">{{ item.category_name }}</text>
                <text class="article-time">{{ formatTime(item.created_at) }}</text>
                <text class="article-views">{{ item.view_count }}阅读</text>
              </view>
            </view>
          </view>
        </view>
      </view>
      
      <view class="empty-state" v-if="articles.length === 0 && !loading && !isLoadingMore">
        <text class="empty-text">暂无文章</text>
      </view>
      
      <view class="loading-state" v-if="loading || isLoadingMore">
        <text>加载中...</text>
      </view>
      
      <view class="no-more" v-if="!hasMore && articles.length > 0">
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
      hotArticles: [],
      articles: [],
      page: 1,
      pageSize: 10,
      hasMore: true,
      loading: false,
      isLoadingMore: false
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
      this.loading = true
      
      await Promise.all([
        this.loadCategories(),
        this.loadHotArticles()
      ])
      
      this.page = 1
      this.articles = []
      this.hasMore = true
      await this.loadArticles()
      
      this.loading = false
    },
    
    async loadCategories() {
      try {
        const res = await api.get('/article/categories')
        if (res.code === 200) {
          this.categories = [{ id: null, name: '推荐' }, ...(res.data.list || [])]
        }
      } catch (e) {
        console.error('加载分类失败:', e)
      }
    },
    
    async loadHotArticles() {
      try {
        const res = await api.get('/article/hot', { limit: 5 })
        if (res.code === 200) {
          this.hotArticles = res.data.list || []
        }
      } catch (e) {
        console.error('加载热门文章失败:', e)
      }
    },
    
    async loadArticles() {
      if (this.isLoadingMore) return
      
      this.isLoadingMore = true
      
      try {
        const params = {
          page: this.page,
          page_size: this.pageSize
        }
        
        if (this.currentCategory) {
          params.category_id = this.currentCategory
        }
        
        const res = await api.get('/article/list', params)
        
        if (res.code === 200) {
          const list = res.data.list || []
          
          if (this.page === 1) {
            this.articles = list
          } else {
            this.articles = [...this.articles, ...list]
          }
          
          this.hasMore = list.length >= this.pageSize
          this.page++
        }
      } catch (e) {
        console.error('加载文章列表失败:', e)
      } finally {
        this.isLoadingMore = false
      }
    },
    
    switchCategory(categoryId) {
      if (this.currentCategory === categoryId) return
      
      this.currentCategory = categoryId
      this.page = 1
      this.articles = []
      this.hasMore = true
      this.loadArticles()
    },
    
    loadMore() {
      if (this.hasMore && !this.isLoadingMore) {
        this.loadArticles()
      }
    },
    
    goDetail(article) {
      uni.navigateTo({
        url: `/pages/article/detail?id=${article.id}`
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

.category-section {
  background-color: $white;
  padding: 20rpx 0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.category-scroll {
  white-space: nowrap;
}

.category-list {
  display: flex;
  padding: 0 20rpx;
}

.category-item {
  flex-shrink: 0;
  padding: 16rpx 40rpx;
  margin-right: 20rpx;
  font-size: $font-size-base;
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
  height: calc(100vh - 100rpx);
}

.hot-section,
.article-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-lg;
  padding: 0 30rpx;
}

.section-header {
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
}

.section-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.hot-articles {
  padding: 10rpx 0;
}

.hot-item {
  display: flex;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.hot-image {
  width: 200rpx;
  height: 140rpx;
  border-radius: $border-radius-md;
  margin-right: 20rpx;
}

.hot-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.hot-title {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hot-meta {
  display: flex;
  gap: 20rpx;
}

.hot-views,
.hot-time {
  font-size: $font-size-xs;
  color: $text-muted;
}

.article-list {
  padding: 10rpx 0;
}

.article-item {
  display: flex;
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.article-cover {
  width: 220rpx;
  height: 160rpx;
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
  align-items: center;
  gap: 20rpx;
  margin-top: 10rpx;
}

.article-category {
  padding: 4rpx 12rpx;
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
  font-size: $font-size-xs;
  border-radius: $border-radius-sm;
}

.article-time,
.article-views {
  font-size: $font-size-xs;
  color: $text-muted;
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
