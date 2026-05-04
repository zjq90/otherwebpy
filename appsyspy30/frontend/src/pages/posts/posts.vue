<template>
    <view class="posts-container">
        <!-- 自定义导航栏 -->
        <view class="custom-nav" :style="{ paddingTop: statusBarHeight + 'px' }">
            <view class="nav-content">
                <text class="nav-title">动态广场</text>
                <view class="nav-actions">
                    <view class="icon-btn" @click="goToCreatePost">
                        <text class="icon">✏️</text>
                    </view>
                </view>
            </view>
            <!-- 筛选Tab -->
            <view class="filter-tabs">
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'all' }"
                    @click="switchTab('all')"
                >
                    <text>全部</text>
                </view>
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'training' }"
                    @click="switchTab('training')"
                >
                    <text>训练</text>
                </view>
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'diet' }"
                    @click="switchTab('diet')"
                >
                    <text>饮食</text>
                </view>
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'achievement' }"
                    @click="switchTab('achievement')"
                >
                    <text>成果</text>
                </view>
            </view>
        </view>

        <!-- 动态列表 -->
        <scroll-view 
            class="posts-scroll" 
            scroll-y 
            @scrolltolower="loadMore"
            :refresher-enabled="true"
            :refresher-triggered="isRefreshing"
            @refresherrefresh="onRefresh"
        >
            <view class="post-list">
                <!-- 空状态 -->
                <view v-if="posts.length === 0 && !loading" class="empty-state">
                    <text class="empty-icon">📝</text>
                    <text class="empty-text">暂无动态</text>
                    <text class="empty-hint" @click="goToCreatePost">发布第一条动态吧</text>
                </view>

                <!-- 动态项 -->
                <view 
                    class="post-item" 
                    v-for="item in posts" 
                    :key="item.id"
                    @click="goToDetail(item.id)"
                >
                    <view class="post-header">
                        <image 
                            class="post-avatar" 
                            :src="item.author_avatar || defaultAvatar" 
                            mode="aspectFill"
                        ></image>
                        <view class="post-author-info">
                            <text class="post-author">{{ item.author_nickname || item.author_username }}</text>
                            <view class="post-meta">
                                <text class="post-time">{{ formatTime(item.created_at) }}</text>
                                <view class="post-type-badge">{{ getTypeText(item.post_type) }}</view>
                            </view>
                        </view>
                    </view>

                    <view class="post-content" v-if="item.content">
                        <text class="post-text">{{ item.content }}</text>
                    </view>

                    <view class="post-images" v-if="item.media_urls && item.media_urls.length > 0">
                        <image 
                            class="post-image" 
                            v-for="(img, idx) in item.media_urls.slice(0, 9)" 
                            :key="idx"
                            :src="img"
                            mode="aspectFill"
                            :class="item.media_urls.length === 1 ? 'single-image' : ''"
                        ></image>
                    </view>

                    <view class="post-actions">
                        <view class="action-btn" @click.stop="toggleLike(item)">
                            <text class="action-icon">{{ item.is_liked ? '❤️' : '🤍' }}</text>
                            <text class="action-count">{{ item.likes_count || 0 }}</text>
                        </view>
                        <view class="action-btn">
                            <text class="action-icon">💬</text>
                            <text class="action-count">{{ item.comments_count || 0 }}</text>
                        </view>
                        <view class="action-btn" @click.stop="sharePost(item)">
                            <text class="action-icon">↗️</text>
                            <text class="action-count">{{ item.shares_count || 0 }}</text>
                        </view>
                    </view>
                </view>
            </view>

            <!-- 加载状态 -->
            <view v-if="loading" class="loading-state">
                <text>加载中...</text>
            </view>

            <view v-if="noMore && posts.length > 0" class="no-more">
                <text>没有更多了</text>
            </view>
        </scroll-view>
    </view>
</template>

<script>
import { postsApi } from '@/api/posts'

export default {
    data() {
        return {
            statusBarHeight: 0,
            defaultAvatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fitness%20avatar%20icon%20simple&image_size=square',
            posts: [],
            currentTab: 'all',
            page: 1,
            pageSize: 10,
            loading: false,
            noMore: false,
            isRefreshing: false
        }
    },
    onShow() {
        this.loadPosts()
    },
    onLoad() {
        this.getStatusBarHeight()
    },
    methods: {
        /**
         * 获取状态栏高度
         */
        getStatusBarHeight() {
            const systemInfo = uni.getSystemInfoSync()
            this.statusBarHeight = systemInfo.statusBarHeight
        },

        /**
         * 切换Tab
         */
        switchTab(tab) {
            if (this.currentTab === tab) return
            this.currentTab = tab
            this.page = 1
            this.noMore = false
            this.posts = []
            this.loadPosts()
        },

        /**
         * 刷新数据
         */
        async onRefresh() {
            this.isRefreshing = true
            this.page = 1
            this.noMore = false
            await this.loadPosts()
            this.isRefreshing = false
        },

        /**
         * 加载动态列表
         */
        async loadPosts() {
            if (this.loading) return
            this.loading = true

            try {
                const params = {
                    page: this.page,
                    limit: this.pageSize
                }

                if (this.currentTab !== 'all') {
                    params.post_type = this.currentTab
                }

                const res = await postsApi.getPosts(params)

                const newPosts = res.items || []

                if (this.page === 1) {
                    this.posts = newPosts
                } else {
                    this.posts = [...this.posts, ...newPosts]
                }

                if (newPosts.length < this.pageSize) {
                    this.noMore = true
                }

            } catch (error) {
                console.error('加载动态失败:', error)
            } finally {
                this.loading = false
            }
        },

        /**
         * 加载更多
         */
        loadMore() {
            if (!this.noMore && !this.loading) {
                this.page++
                this.loadPosts()
            }
        },

        /**
         * 切换点赞状态
         */
        async toggleLike(item) {
            try {
                const res = await postsApi.toggleLike(item.id)
                item.is_liked = res.is_liked
                item.likes_count = res.likes_count
            } catch (error) {
                console.error('点赞失败:', error)
            }
        },

        /**
         * 分享动态
         */
        async sharePost(item) {
            try {
                await postsApi.sharePost(item.id)
                item.shares_count = (item.shares_count || 0) + 1
                uni.showToast({
                    title: '分享成功',
                    icon: 'success'
                })
            } catch (error) {
                console.error('分享失败:', error)
            }
        },

        /**
         * 格式化时间
         */
        formatTime(timeStr) {
            if (!timeStr) return ''
            const date = new Date(timeStr)
            const now = new Date()
            const diff = now - date
            const minutes = Math.floor(diff / 60000)
            const hours = Math.floor(diff / 3600000)
            const days = Math.floor(diff / 86400000)

            if (minutes < 1) return '刚刚'
            if (minutes < 60) return `${minutes}分钟前`
            if (hours < 24) return `${hours}小时前`
            if (days < 7) return `${days}天前`

            return timeStr.split('T')[0]
        },

        /**
         * 获取类型文本
         */
        getTypeText(type) {
            const map = {
                'training': '🏃 训练',
                'diet': '🥗 饮食',
                'achievement': '🏆 成果'
            }
            return map[type] || '📝 动态'
        },

        /**
         * 跳转创建动态
         */
        goToCreatePost() {
            uni.navigateTo({
                url: '/pages/posts/create'
            })
        },

        /**
         * 跳转详情
         */
        goToDetail(id) {
            uni.navigateTo({
                url: `/pages/posts/detail?id=${id}`
            })
        }
    }
}
</script>

<style scoped>
.posts-container {
    min-height: 100vh;
    background: #F5F5F5;
}

/* 自定义导航栏 */
.custom-nav {
    background: #FFFFFF;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.nav-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 88rpx;
    padding: 0 30rpx;
}

.nav-title {
    font-size: 34rpx;
    font-weight: bold;
    color: #333333;
}

.nav-actions {
    display: flex;
    align-items: center;
}

.icon-btn {
    width: 64rpx;
    height: 64rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.icon {
    font-size: 44rpx;
}

/* 筛选Tab */
.filter-tabs {
    display: flex;
    padding: 0 30rpx 20rpx;
    border-bottom: 1rpx solid #F5F5F5;
}

.tab-item {
    padding: 16rpx 32rpx;
    margin-right: 20rpx;
    border-radius: 24rpx;
    background: #F5F5F5;
}

.tab-item text {
    font-size: 26rpx;
    color: #666666;
}

.tab-item.active {
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
}

.tab-item.active text {
    color: #FFFFFF;
    font-weight: 500;
}

/* 滚动区域 */
.posts-scroll {
    height: calc(100vh - 88rpx - 100rpx - var(--status-bar-height));
}

/* 动态列表 */
.post-list {
    padding: 20rpx;
}

.post-item {
    background: #FFFFFF;
    border-radius: 20rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
}

.post-header {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;
}

.post-avatar {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
}

.post-author-info {
    flex: 1;
    margin-left: 16rpx;
}

.post-author {
    font-size: 30rpx;
    font-weight: 500;
    color: #333333;
}

.post-meta {
    display: flex;
    align-items: center;
    margin-top: 6rpx;
}

.post-time {
    font-size: 22rpx;
    color: #999999;
}

.post-type-badge {
    font-size: 20rpx;
    color: #4CAF50;
    background: #E8F5E9;
    padding: 2rpx 10rpx;
    border-radius: 6rpx;
    margin-left: 12rpx;
}

/* 动态内容 */
.post-content {
    margin-bottom: 16rpx;
}

.post-text {
    font-size: 28rpx;
    color: #333333;
    line-height: 1.7;
}

/* 图片网格 */
.post-images {
    display: flex;
    flex-wrap: wrap;
    margin-bottom: 16rpx;
}

.post-image {
    width: 200rpx;
    height: 200rpx;
    border-radius: 12rpx;
    margin-right: 12rpx;
    margin-bottom: 12rpx;
}

.single-image {
    width: 100%;
    height: 400rpx;
}

/* 操作按钮 */
.post-actions {
    display: flex;
    align-items: center;
    padding-top: 16rpx;
    border-top: 1rpx solid #F5F5F5;
}

.action-btn {
    display: flex;
    align-items: center;
    margin-right: 50rpx;
}

.action-icon {
    font-size: 40rpx;
    margin-right: 8rpx;
}

.action-count {
    font-size: 24rpx;
    color: #666666;
}

/* 空状态 */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 100rpx 0;
}

.empty-icon {
    font-size: 100rpx;
    margin-bottom: 24rpx;
}

.empty-text {
    font-size: 30rpx;
    color: #999999;
    margin-bottom: 16rpx;
}

.empty-hint {
    font-size: 26rpx;
    color: #4CAF50;
}

/* 加载状态 */
.loading-state,
.no-more {
    display: flex;
    justify-content: center;
    padding: 30rpx;
    font-size: 26rpx;
    color: #999999;
}
</style>
