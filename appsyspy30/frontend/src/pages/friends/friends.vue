<template>
    <view class="friends-container">
        <!-- 自定义导航栏 -->
        <view class="custom-nav" :style="{ paddingTop: statusBarHeight + 'px' }">
            <view class="nav-content">
                <text class="nav-title">好友</text>
                <view class="nav-actions">
                    <view class="icon-btn" @click="goToSearch">
                        <text class="icon">🔍</text>
                    </view>
                </view>
            </view>
            <!-- Tab切换 -->
            <view class="tabs">
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'friends' }"
                    @click="switchTab('friends')"
                >
                    <text>我的好友</text>
                </view>
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'requests' }"
                    @click="switchTab('requests')"
                >
                    <text>好友请求</text>
                    <view v-if="pendingRequestsCount > 0" class="badge">
                        {{ pendingRequestsCount }}
                    </view>
                </view>
            </view>
        </view>

        <!-- 内容区域 -->
        <scroll-view 
            class="content-scroll" 
            scroll-y 
            :refresher-enabled="true"
            :refresher-triggered="isRefreshing"
            @refresherrefresh="onRefresh"
        >
            <!-- 好友列表 -->
            <view v-if="currentTab === 'friends'" class="friends-section">
                <view class="section-header">
                    <text class="section-title">好友 ({{ friends.length }})</text>
                </view>

                <!-- 空状态 -->
                <view v-if="friends.length === 0 && !loading" class="empty-state">
                    <text class="empty-icon">👥</text>
                    <text class="empty-text">暂无好友</text>
                    <text class="empty-hint" @click="goToSearch">去搜索添加好友</text>
                </view>

                <!-- 好友列表 -->
                <view class="friend-list">
                    <view 
                        class="friend-item" 
                        v-for="item in friends" 
                        :key="item.friendship_id"
                        @click="goToProfile(item.friend_id)"
                    >
                        <image 
                            class="friend-avatar" 
                            :src="item.friend_avatar || defaultAvatar" 
                            mode="aspectFill"
                        ></image>
                        <view class="friend-info">
                            <text class="friend-name">{{ item.friend_nickname || item.friend_username }}</text>
                            <text class="friend-stats">积分: {{ item.friend_points || 0 }}</text>
                        </view>
                        <view class="friend-actions">
                            <view class="action-btn" @click.stop="goToChat(item.friend_id, item.friend_nickname || item.friend_username)">
                                <text class="action-text">发消息</text>
                            </view>
                        </view>
                    </view>
                </view>
            </view>

            <!-- 好友请求 -->
            <view v-if="currentTab === 'requests'" class="requests-section">
                <!-- 收到的请求 -->
                <view class="requests-block">
                    <view class="section-header">
                        <text class="section-title">收到的请求</text>
                    </view>

                    <view v-if="receivedRequests.length === 0" class="empty-list">
                        <text class="empty-text">暂无收到的好友请求</text>
                    </view>

                    <view class="request-list">
                        <view 
                            class="request-item" 
                            v-for="item in receivedRequests" 
                            :key="item.id"
                        >
                            <image 
                                class="requester-avatar" 
                                :src="item.requester_avatar || defaultAvatar" 
                                mode="aspectFill"
                            ></image>
                            <view class="requester-info">
                                <text class="requester-name">{{ item.requester_nickname || item.requester_username }}</text>
                                <text class="request-time">{{ formatTime(item.created_at) }}</text>
                            </view>
                            <view class="request-actions" v-if="item.status === 'pending'">
                                <view class="btn-accept" @click="acceptRequest(item.id)">
                                    <text>接受</text>
                                </view>
                                <view class="btn-reject" @click="rejectRequest(item.id)">
                                    <text>拒绝</text>
                                </view>
                            </view>
                            <view class="request-status" v-else>
                                <text :class="item.status === 'accepted' ? 'status-accepted' : 'status-rejected'">
                                    {{ item.status === 'accepted' ? '已接受' : '已拒绝' }}
                                </text>
                            </view>
                        </view>
                    </view>
                </view>

                <!-- 发出的请求 -->
                <view class="requests-block">
                    <view class="section-header">
                        <text class="section-title">我发出的请求</text>
                    </view>

                    <view v-if="sentRequests.length === 0" class="empty-list">
                        <text class="empty-text">暂无发出的好友请求</text>
                    </view>

                    <view class="request-list">
                        <view 
                            class="request-item" 
                            v-for="item in sentRequests" 
                            :key="item.id"
                        >
                            <image 
                                class="requester-avatar" 
                                :src="item.invitee_avatar || defaultAvatar" 
                                mode="aspectFill"
                            ></image>
                            <view class="requester-info">
                                <text class="requester-name">{{ item.invitee_nickname || item.invitee_username }}</text>
                                <text class="request-time">{{ formatTime(item.created_at) }}</text>
                            </view>
                            <view class="request-status">
                                <text :class="'status-' + item.status">
                                    {{ getStatusText(item.status) }}
                                </text>
                            </view>
                        </view>
                    </view>
                </view>
            </view>
        </scroll-view>
    </view>
</template>

<script>
import { friendsApi } from '@/api/friends'

export default {
    data() {
        return {
            statusBarHeight: 0,
            defaultAvatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fitness%20avatar%20icon%20simple&image_size=square',
            currentTab: 'friends',
            friends: [],
            receivedRequests: [],
            sentRequests: [],
            pendingRequestsCount: 0,
            loading: false,
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
         * 切换Tab
         */
        switchTab(tab) {
            this.currentTab = tab
        },

        /**
         * 刷新数据
         */
        async onRefresh() {
            this.isRefreshing = true
            await this.loadData()
            this.isRefreshing = false
        },

        /**
         * 加载数据
         */
        async loadData() {
            this.loading = true
            await Promise.all([
                this.loadFriends(),
                this.loadReceivedRequests(),
                this.loadSentRequests()
            ])
            this.loading = false
        },

        /**
         * 加载好友列表
         */
        async loadFriends() {
            try {
                const res = await friendsApi.getFriends()
                this.friends = res.items || []
            } catch (error) {
                console.error('加载好友列表失败:', error)
            }
        },

        /**
         * 加载收到的好友请求
         */
        async loadReceivedRequests() {
            try {
                const res = await friendsApi.getFriendRequests()
                this.receivedRequests = res.items || []
                this.pendingRequestsCount = this.receivedRequests.filter(r => r.status === 'pending').length
            } catch (error) {
                console.error('加载好友请求失败:', error)
            }
        },

        /**
         * 加载发出的好友请求
         */
        async loadSentRequests() {
            try {
                const res = await friendsApi.getSentFriendRequests()
                this.sentRequests = res.items || []
            } catch (error) {
                console.error('加载发出的请求失败:', error)
            }
        },

        /**
         * 接受好友请求
         */
        async acceptRequest(id) {
            try {
                await friendsApi.acceptFriendRequest(id)
                uni.showToast({
                    title: '已接受',
                    icon: 'success'
                })
                this.loadData()
            } catch (error) {
                console.error('接受失败:', error)
            }
        },

        /**
         * 拒绝好友请求
         */
        async rejectRequest(id) {
            try {
                await friendsApi.rejectFriendRequest(id)
                uni.showToast({
                    title: '已拒绝',
                    icon: 'success'
                })
                this.loadData()
            } catch (error) {
                console.error('拒绝失败:', error)
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
         * 获取状态文本
         */
        getStatusText(status) {
            const map = {
                'pending': '等待中',
                'accepted': '已接受',
                'rejected': '已拒绝'
            }
            return map[status] || status
        },

        /**
         * 页面跳转
         */
        goToSearch() {
            uni.navigateTo({
                url: '/pages/friends/search'
            })
        },

        goToProfile(userId) {
            uni.navigateTo({
                url: `/pages/friends/profile?id=${userId}`
            })
        },

        goToChat(friendId, friendName) {
            uni.navigateTo({
                url: `/pages/friends/chat?friendId=${friendId}&friendName=${encodeURIComponent(friendName)}`
            })
        }
    }
}
</script>

<style scoped>
.friends-container {
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

/* Tab切换 */
.tabs {
    display: flex;
    padding: 0 30rpx 20rpx;
}

.tab-item {
    position: relative;
    padding: 16rpx 40rpx;
    margin-right: 40rpx;
}

.tab-item text {
    font-size: 30rpx;
    color: #666666;
}

.tab-item.active text {
    color: #333333;
    font-weight: 500;
}

.tab-item.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 40rpx;
    height: 6rpx;
    background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 3rpx;
}

.badge {
    position: absolute;
    top: 8rpx;
    right: 10rpx;
    min-width: 28rpx;
    height: 28rpx;
    background: #FF5252;
    border-radius: 14rpx;
    font-size: 18rpx;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 6rpx;
}

/* 滚动区域 */
.content-scroll {
    height: calc(100vh - 88rpx - 100rpx - var(--status-bar-height));
}

/* 通用区块 */
.friends-section,
.requests-section {
    padding: 20rpx;
}

.section-header {
    padding: 16rpx 0;
}

.section-title {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
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
    font-size: 28rpx;
    color: #999999;
    margin-bottom: 16rpx;
}

.empty-hint {
    font-size: 26rpx;
    color: #4CAF50;
}

.empty-list {
    padding: 40rpx 0;
    text-align: center;
}

/* 好友列表 */
.friend-list {
    display: flex;
    flex-direction: column;
}

.friend-item {
    display: flex;
    align-items: center;
    background: #FFFFFF;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 16rpx;
}

.friend-avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
}

.friend-info {
    flex: 1;
    margin-left: 20rpx;
}

.friend-name {
    font-size: 30rpx;
    color: #333333;
    font-weight: 500;
}

.friend-stats {
    font-size: 24rpx;
    color: #999999;
    margin-top: 6rpx;
}

.friend-actions {
    display: flex;
    align-items: center;
}

.action-btn {
    padding: 12rpx 32rpx;
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 24rpx;
}

.action-text {
    font-size: 24rpx;
    color: #FFFFFF;
}

/* 好友请求 */
.requests-block {
    background: #FFFFFF;
    border-radius: 16rpx;
    padding: 0 24rpx;
    margin-bottom: 20rpx;
}

.request-list {
    display: flex;
    flex-direction: column;
}

.request-item {
    display: flex;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #F5F5F5;
}

.request-item:last-child {
    border-bottom: none;
}

.requester-avatar {
    width: 72rpx;
    height: 72rpx;
    border-radius: 50%;
}

.requester-info {
    flex: 1;
    margin-left: 16rpx;
}

.requester-name {
    font-size: 28rpx;
    color: #333333;
}

.request-time {
    font-size: 22rpx;
    color: #999999;
    margin-top: 4rpx;
}

.request-actions {
    display: flex;
    align-items: center;
}

.btn-accept,
.btn-reject {
    padding: 10rpx 28rpx;
    border-radius: 20rpx;
    margin-left: 16rpx;
}

.btn-accept {
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
}

.btn-accept text {
    font-size: 24rpx;
    color: #FFFFFF;
}

.btn-reject {
    background: #F5F5F5;
}

.btn-reject text {
    font-size: 24rpx;
    color: #666666;
}

.request-status {
    padding: 8rpx 24rpx;
    border-radius: 20rpx;
}

.status-pending {
    color: #FF9800;
    background: #FFF3E0;
}

.status-accepted {
    color: #4CAF50;
    background: #E8F5E9;
}

.status-rejected {
    color: #F44336;
    background: #FFEBEE;
}
</style>
