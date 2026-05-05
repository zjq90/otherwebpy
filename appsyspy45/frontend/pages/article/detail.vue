<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-content">
      <view class="article-section" v-if="article">
        <view class="article-title">{{ article.title }}</view>
        
        <view class="article-meta">
          <view class="meta-item">
            <text class="meta-icon">📅</text>
            <text class="meta-text">{{ formatTime(article.created_at) }}</text>
          </view>
          <view class="meta-item">
            <text class="meta-icon">👁️</text>
            <text class="meta-text">{{ article.view_count }}阅读</text>
          </view>
          <view class="meta-item" v-if="article.author">
            <text class="meta-icon">✍️</text>
            <text class="meta-text">{{ article.author }}</text>
          </view>
        </view>
        
        <view class="article-cover" v-if="article.cover_image">
          <image :src="article.cover_image" mode="aspectFill"></image>
        </view>
        
        <view class="article-content">
          <text class="content-text">{{ article.content || '暂无内容' }}</text>
        </view>
        
        <view class="article-tags" v-if="article.tags && article.tags.length > 0">
          <text class="tag-item" v-for="(tag, index) in article.tags" :key="index">{{ tag }}</text>
        </view>
        
        <view class="article-actions">
          <view class="action-item" :class="{ liked: isLiked }" @click="toggleLike">
            <text class="action-icon">{{ isLiked ? '❤️' : '🤍' }}</text>
            <text class="action-text">{{ likeCount }}点赞</text>
          </view>
          <view class="action-item" @click="shareArticle">
            <text class="action-icon">📤</text>
            <text class="action-text">分享</text>
          </view>
        </view>
      </view>
      
      <view class="related-section" v-if="relatedArticles.length > 0">
        <view class="section-header">
          <text class="section-title">相关推荐</text>
        </view>
        <view class="related-list">
          <view class="related-item" v-for="(item, index) in relatedArticles" :key="index" @click="goDetail(item)">
            <text class="related-title">{{ item.title }}</text>
            <text class="related-views">{{ item.view_count }}阅读</text>
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
      articleId: null,
      article: null,
      relatedArticles: [],
      isLiked: false,
      likeCount: 0
    }
  },
  
  onLoad(options) {
    if (options.id) {
      this.articleId = parseInt(options.id)
      this.loadArticleDetail()
    }
  },
  
  methods: {
    formatTime(time) {
      return utils.formatDateTime(time)
    },
    
    async loadArticleDetail() {
      if (!this.articleId) return
      
      utils.showLoading('加载中...')
      
      try {
        const res = await api.get(`/article/${this.articleId}`)
        if (res.code === 200) {
          this.article = res.data
          this.likeCount = res.data.like_count || 0
          this.isLiked = res.data.is_liked || false
          
          await this.loadRelatedArticles()
        }
      } catch (e) {
        console.error('加载文章详情失败:', e)
      } finally {
        utils.hideLoading()
      }
    },
    
    async loadRelatedArticles() {
      try {
        const res = await api.get('/article/recommend', { limit: 5, exclude_id: this.articleId })
        if (res.code === 200) {
          this.relatedArticles = res.data.list || []
        }
      } catch (e) {
        console.error('加载相关文章失败:', e)
      }
    },
    
    async toggleLike() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      try {
        const res = await api.post(`/article/${this.articleId}/like`)
        if (res.code === 200) {
          this.isLiked = res.data.is_liked
          this.likeCount = res.data.like_count
          
          utils.showToast(this.isLiked ? '点赞成功' : '已取消点赞')
        }
      } catch (e) {
        console.error('点赞失败:', e)
      }
    },
    
    shareArticle() {
      utils.showToast('请点击右上角分享')
    },
    
    goDetail(article) {
      this.articleId = article.id
      this.loadArticleDetail()
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
}

.scroll-content {
  min-height: 100vh;
}

.article-section {
  background-color: $white;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.article-title {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $text-color;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 30rpx;
  margin-bottom: 30rpx;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-icon {
  font-size: 28rpx;
  margin-right: 8rpx;
}

.meta-text {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.article-cover {
  width: 100%;
  margin-bottom: 30rpx;
  border-radius: $border-radius-md;
  overflow: hidden;
}

.article-cover image {
  width: 100%;
  height: 400rpx;
}

.article-content {
  margin-bottom: 30rpx;
}

.content-text {
  font-size: $font-size-base;
  color: $text-color;
  line-height: 2;
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 30rpx;
}

.tag-item {
  padding: 8rpx 24rpx;
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
  font-size: $font-size-sm;
  border-radius: 30rpx;
}

.article-actions {
  display: flex;
  justify-content: center;
  gap: 60rpx;
  padding-top: 30rpx;
  border-top: 1rpx solid $border-color;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 10rpx;
}

.action-icon {
  font-size: 36rpx;
}

.action-text {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.related-section {
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

.related-list {
  padding: 10rpx 0;
}

.related-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.related-title {
  flex: 1;
  font-size: $font-size-base;
  color: $text-color;
  margin-right: 20rpx;
  
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.related-views {
  font-size: $font-size-sm;
  color: $text-muted;
  flex-shrink: 0;
}

.bottom-spacer {
  height: 40rpx;
}
</style>
