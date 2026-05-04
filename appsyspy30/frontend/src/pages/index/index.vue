<template>
    <view class="home-container">
        <!-- 顶部状态栏 -->
        <view class="status-bar" :style="{ paddingTop: statusBarHeight + 'px' }">
            <view class="header">
                <text class="app-name">健身社交</text>
                <view class="header-actions">
                    <view class="icon-btn" @click="goToSearch">
                        <text class="icon">🔍</text>
                    </view>
                    <view class="icon-btn" @click="goToMessages">
                        <text class="icon">💬</text>
                        <view v-if="unreadCount > 0" class="badge">{{ unreadCount }}</view>
                    </view>
                </view>
            </view>
        </view>

        <!-- 滚动内容区域 -->
        <scroll-view 
            class="scroll-content" 
            scroll-y 
            @scrolltolower="loadMorePosts"
            :refresher-enabled="true"
            :refresher-triggered="isRefreshing"
            @refresherrefresh="onRefresh"
        >
            <!-- 用户信息卡片 -->
            <view class="user-card" v-if="userInfo">
                <view class="user-info">
                    <image class="avatar" :src="userInfo.avatar || defaultAvatar" mode="aspectFill"></image>
                    <view class="user-detail">
                        <text class="nickname">{{ userInfo.nickname || userInfo.username }}</text>
                        <view class="user-stats">
                            <text class="stat-item">积分: {{ userInfo.points || 0 }}</text>
                        </view>
                    </view>
                </view>
                <view class="quick-actions">
                    <view class="action-item" @click="goToCreatePost">
                        <text class="action-icon">📝</text>
                        <text class="action-text">发动态</text>
                    </view>
                    <view class="action-item" @click="goToFriends">
                        <text class="action-icon">👥</text>
                        <text class="action-text">好友</text>
                    </view>
                    <view class="action-item" @click="goToChallenges">
                        <text class="action-icon">🏆</text>
                        <text class="action-text">挑战</text>
                    </view>
                    <view class="action-item" @click="goToInvitations">
                        <text class="action-icon">🎁</text>
                        <text class="action-text">邀请</text>
                    </view>
                </view>
            </view>

            <!-- 进行中的挑战 -->
            <view class="section" v-if="myChallenges.length > 0">
                <view class="section-header">
                    <text class="section-title">进行中的挑战</text>
                    <text class="section-more" @click="goToMyChallenges">查看全部 ›</text>
                </view>
                <view class="challenge-list">
                    <view 
                        class="challenge-item" 
                        v-for="item in myChallenges" 
                        :key="item.id"
                        @click="goToChallengeDetail(item.id)"
                    >
                        <view class="challenge-info">
                            <text class="challenge-name">{{ item.challenge_name }}</text>
                            <view class="progress-bar">
                                <view class="progress-fill" :style="{ width: item.progress + '%' }"></view>
                            </view>
                            <text class="progress-text">{{ item.progress }}%</text>
                        </view>
                    </view>
                </view>
            </view>

            <!-- 动态列表 -->
            <view class="section">
                <view class="section-header">
                    <text class="section-title">动态广场</text>
                    <text class="section-more" @click="goToPosts">更多 ›</text>
                </view>
                <view class="post-list">
                    <!-- 空状态 -->
                    <view v-if="posts.length === 0 && !loading" class="empty-state">
                        <text class="empty-icon">📭</text>
                        <text class="empty-text">暂无动态</text>
                    </view>

                    <!-- 动态项 -->
                    <view 
                        class="post-item" 
                        v-for="item in posts" 
                        :key="item.id"
                        @click="goToPostDetail(item.id)"
                    >
                        <view class="post-header">
                            <image 
                                class="post-avatar" 
                                :src="item.author_avatar || defaultAvatar" 
                                mode="aspectFill"
                            ></image>
                            <view class="post-author-info">
                                <text class="post-author">{{ item.author_nickname || item.author_username }}</text>
                                <text class="post-time">{{ formatTime(item.created_at) }}</text>
                            </view>
                            <view class="post-category">{{ getCategoryText(item.post_type) }}</view>
                        </view>

                        <view class="post-content" v-if="item.content">
                            <text class="post-text">{{ item.content }}</text>
                        </view>

                        <view class="post-images" v-if="item.media_urls && item.media_urls.length > 0">
                            <image 
                                class="post-image" 
                                v-for="(img, idx) in item.media_urls.slice(0, 3)" 
                                :key="idx"
                                :src="img"
                                mode="aspectFill"
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
                            <view class="action-btn">
                                <text class="action-icon">↗️</text>
                                <text class="action-count">分享</text>
                            </view>
                        </view>
                    </view>
                </view>

                <!-- 加载状态 -->
                <view v-if="loading" class="loading-state">
                    <text>加载中...</text>
                </view>

                <view v-if="noMore" class="no-more">
                    <text>没有更多了</text>
                </view>
            </view>
        </scroll-view>
    </view>
</template>

<script>
import { postsApi } from '@/api/posts'
import { challengesApi } from '@/api/challenges'
import { friendsApi } from '@/api/friends'
import { getUserInfo } from '@/utils/auth'

export default {
    data() {
        return {
            statusBarHeight: 0,
            defaultAvatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fitness%20avatar%20icon%20simple&image_size=square',
            userInfo: null,
            posts: [],
            myChallenges: [],
            unreadCount: 0,
            page: 1,
            pageSize: 10,
            loading: false,
            noMore: false,
            isRefreshing: false
        }
    },
    onShow() {
        this.loadData()
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
         * 加载所有数据
         */
        async loadData() {
            this.userInfo = getUserInfo()
            await Promise.all([
                this.loadPosts(),
                this.loadMyChallenges(),
                this.loadUnreadCount()
            ])
        },

        /**
         * 刷新数据
         */
        async onRefresh() {
            this.isRefreshing = true
            this.page = 1
            this.noMore = false
            await this.loadData()
            this.isRefreshing = false
        },

        /**
         * 加载动态列表
         */
        async loadPosts() {
            if (this.loading) return
            this.loading = true

            try {
                const res = await postsApi.getPosts({
                    page: this.page,
                    limit: this.pageSize
                })

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
        loadMorePosts() {
            if (!this.noMore && !this.loading) {
                this.page++
                this.loadPosts()
            }
        },

        /**
         * 加载我参与的挑战
         */
        async loadMyChallenges() {
            try {
                const res = await challengesApi.getMyChallenges({
                    is_completed: false
                })
                this.myChallenges = (res.items || []).slice(0, 3)
            } catch (error) {
                console.error('加载挑战失败:', error)
            }
        },

        /**
         * 加载未读消息数
         */
        async loadUnreadCount() {
            try {
                const res = await friendsApi.getUnreadMessageCount()
                this.unreadCount = res.count || 0
            } catch (error) {
                console.error('加载未读消息失败:', error)
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
         * 获取分类文本
         */
        getCategoryText(type) {
            const map = {
                'training': '训练',
                'diet': '饮食',
                'achievement': '成果'
            }
            return map[type] || '动态'
        },

        // 页面跳转
        goToSearch() {
            uni.navigateTo({ url: '/pages/friends/search' })
        },
        goToMessages() {
            uni.navigateTo({ url: '/pages/friends/conversations' })
        },
        goToCreatePost() {
            uni.navigateTo({ url: '/pages/posts/create' })
        },
        goToFriends() {
            uni.switchTab({ url: '/pages/friends/friends' })
        },
        goToChallenges() {
            uni.switchTab({ url: '/pages/challenges/challenges' })
        },
        goToInvitations() {
            uni.switchTab({ url: '/pages/invitations/invitations' })
        },
        goToMyChallenges() {
            uni.navigateTo({ url: '/pages/challenges/my' })
        },
        goToChallengeDetail(id) {
            uni.navigateTo({ url: `/pages/challenges/detail?id=${id}` })
        },
        goToPosts() {
            uni.switchTab({ url: '/pages/posts/posts' })
        },
        goToPostDetail(id) {
            uni.navigateTo({ url: `/pages/posts/detail?id=${id}` })
        }
    }
}
</script>

<style scoped>
.home-container {
    min-height: 100vh;
    background: #F5F5F5;
}

/* 状态栏 */
.status-bar {
    background: #FFFFFF;
    position: sticky;
    top: 0;
    z-index: 100;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 88rpx;
    padding: 0 30rpx;
}

.app-name {
    font-size: 36rpx;
    font-weight: bold;
    color: #333333;
}

.header-actions {
    display: flex;
    align-items: center;
}

.icon-btn {
    position: relative;
    margin-left: 30rpx;
}

.icon {
    font-size: 44rpx;
}

.badge {
    position: absolute;
    top: -8rpx;
    right: -8rpx;
    min-width: 32rpx;
    height: 32rpx;
    background: #FF5252;
    border-radius: 16rpx;
    font-size: 20rpx;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 6rpx;
}

/* 滚动内容 */
.scroll-content {
    height: calc(100vh - 88rpx - var(--status-bar-height));
}

/* 用户卡片 */
.user-card {
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    margin: 20rpx;
    border-radius: 24rpx;
    padding: 30rpx;
}

.user-info {
    display: flex;
    align-items: center;
    margin-bottom: 30rpx;
}

.avatar {
    width: 88rpx;
    height: 88rpx;
    border-radius: 50%;
    border: 4rpx solid #FFFFFF;
}

.user-detail {
    margin-left: 20rpx;
}

.nickname {
    font-size: 32rpx;
    font-weight: 500;
    color: #FFFFFF;
}

.user-stats {
    margin-top: 8rpx;
}

.stat-item {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.9);
}

.quick-actions {
    display: flex;
    justify-content: space-around;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 16rpx;
    padding: 20rpx 0;
}

.action-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.action-icon {
    font-size: 48rpx;
    margin-bottom: 8rpx;
}

.action-text {
    font-size: 24rpx;
    color: #FFFFFF;
}

/* 通用区块 */
.section {
    background: #FFFFFF;
    margin-bottom: 20rpx;
    padding: 24rpx;
}

.section:first-of-type {
    margin-top: 20rpx;
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20rpx;
}

.section-title {
    font-size: 30rpx;
    font-weight: 500;
    color: #333333;
}

.section-more {
    font-size: 24rpx;
    color: #999999;
}

/* 挑战列表 */
.challenge-list {
    display: flex;
    flex-direction: column;
}

.challenge-item {
    display: flex;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #F5F5F5;
}

.challenge-item:last-child {
    border-bottom: none;
}

.challenge-info {
    flex: 1;
}

.challenge-name {
    font-size: 28rpx;
    color: #333333;
    margin-bottom: 12rpx;
}

.progress-bar {
    height: 8rpx;
    background: #F5F5F5;
    border-radius: 4rpx;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 4rpx;
}

.progress-text {
    font-size: 22rpx;
    color: #999999;
    margin-top: 8rpx;
}

/* 动态列表 */
.post-list {
    display: flex;
    flex-direction: column;
}

.post-item {
    padding: 20rpx 0;
    border-bottom: 1rpx solid #F5F5F5;
}

.post-item:last-child {
    border-bottom: none;
}

.post-header {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;
}

.post-avatar {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
}

.post-author-info {
    flex: 1;
    margin-left: 16rpx;
}

.post-author {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
}

.post-time {
    font-size: 22rpx;
    color: #999999;
    margin-top: 4rpx;
}

.post-category {
    font-size: 22rpx;
    color: #4CAF50;
    background: #E8F5E9;
    padding: 4rpx 12rpx;
    border-radius: 8rpx;
}

.post-content {
    margin-bottom: 16rpx;
}

.post-text {
    font-size: 28rpx;
    color: #333333;
    line-height: 1.6;
}

.post-images {
    display: flex;
    margin-bottom: 16rpx;
}

.post-image {
    width: 160rpx;
    height: 160rpx;
    border-radius: 12rpx;
    margin-right: 12rpx;
}

.post-actions {
    display: flex;
    align-items: center;
}

.action-btn {
    display: flex;
    align-items: center;
    margin-right: 40rpx;
}

.action-icon {
    font-size: 36rpx;
    margin-right: 6rpx;
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
    padding: 60rpx 0;
}

.empty-icon {
    font-size: 80rpx;
    margin-bottom: 20rpx;
}

.empty-text {
    font-size: 28rpx;
    color: #999999;
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
