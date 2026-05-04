<template>
    <view class="challenges-container">
        <!-- 自定义导航栏 -->
        <view class="custom-nav" :style="{ paddingTop: statusBarHeight + 'px' }">
            <view class="nav-content">
                <text class="nav-title">挑战活动</text>
            </view>
            <!-- Tab切换 -->
            <view class="tabs">
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'active' }"
                    @click="switchTab('active')"
                >
                    <text>进行中</text>
                </view>
                <view 
                    class="tab-item" 
                    :class="{ active: currentTab === 'my' }"
                    @click="switchTab('my')"
                >
                    <text>我的挑战</text>
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
            @scrolltolower="loadMore"
        >
            <!-- 进行中的挑战列表 -->
            <view v-if="currentTab === 'active'" class="challenges-section">
                <!-- 空状态 -->
                <view v-if="challenges.length === 0 && !loading" class="empty-state">
                    <text class="empty-icon">🏆</text>
                    <text class="empty-text">暂无挑战活动</text>
                </view>

                <!-- 挑战列表 -->
                <view class="challenge-list">
                    <view 
                        class="challenge-card" 
                        v-for="item in challenges" 
                        :key="item.id"
                        @click="goToDetail(item.id)"
                    >
                        <!-- 封面区域 -->
                        <view class="challenge-cover" :style="{ background: getCoverGradient(item.challenge_type) }">
                            <view class="cover-content">
                                <text class="challenge-type-badge">{{ getTypeText(item.challenge_type) }}</text>
                                <text class="challenge-name">{{ item.name }}</text>
                                <view class="challenge-meta">
                                    <text class="meta-item">📅 {{ formatDate(item.start_date) }} - {{ formatDate(item.end_date) }}</text>
                                </view>
                            </view>
                        </view>

                        <!-- 信息区域 -->
                        <view class="challenge-info">
                            <view class="info-row">
                                <view class="info-item">
                                    <text class="info-label">奖励</text>
                                    <text class="info-value">{{ item.reward_description || '积分奖励' }}</text>
                                </view>
                                <view class="info-item">
                                    <text class="info-label">已参与</text>
                                    <text class="info-value">{{ item.participants_count || 0 }}人</text>
                                </view>
                            </view>

                            <view class="action-row">
                                <button class="btn-join" @click.stop="joinChallenge(item)">
                                    立即参与
                                </button>
                            </view>
                        </view>
                    </view>
                </view>
            </view>

            <!-- 我的挑战 -->
            <view v-if="currentTab === 'my'" class="my-challenges-section">
                <!-- 空状态 -->
                <view v-if="myChallenges.length === 0 && !loading" class="empty-state">
                    <text class="empty-icon">🎯</text>
                    <text class="empty-text">暂无参与的挑战</text>
                    <text class="empty-hint" @click="switchTab('active')">去参与一个挑战</text>
                </view>

                <!-- 进行中的挑战 -->
                <view v-if="activeMyChallenges.length > 0" class="section-block">
                    <view class="section-header">
                        <text class="section-title">进行中</text>
                    </view>
                    <view class="my-challenge-list">
                        <view 
                            class="my-challenge-item" 
                            v-for="item in activeMyChallenges" 
                            :key="item.id"
                            @click="goToMyDetail(item.id)"
                        >
                            <view class="my-challenge-info">
                                <text class="my-challenge-name">{{ item.challenge_name }}</text>
                                <view class="progress-section">
                                    <view class="progress-bar">
                                        <view class="progress-fill" :style="{ width: item.progress + '%' }"></view>
                                    </view>
                                    <text class="progress-text">{{ item.progress }}%</text>
                                </view>
                            </view>
                            <view class="my-challenge-status">
                                <text class="status-text">进行中</text>
                            </view>
                        </view>
                    </view>
                </view>

                <!-- 已完成的挑战 -->
                <view v-if="completedMyChallenges.length > 0" class="section-block">
                    <view class="section-header">
                        <text class="section-title">已完成</text>
                    </view>
                    <view class="my-challenge-list">
                        <view 
                            class="my-challenge-item completed" 
                            v-for="item in completedMyChallenges" 
                            :key="item.id"
                            @click="goToMyDetail(item.id)"
                        >
                            <view class="my-challenge-info">
                                <text class="my-challenge-name">{{ item.challenge_name }}</text>
                                <view class="progress-section">
                                    <text class="progress-text">完成进度: {{ item.progress }}%</text>
                                </view>
                            </view>
                            <view class="my-challenge-status">
                                <view v-if="item.reward_claimed" class="status-badge claimed">
                                    <text>奖励已领取</text>
                                </view>
                                <view v-else class="status-badge unclaimed" @click.stop="claimReward(item)">
                                    <text>领取奖励</text>
                                </view>
                            </view>
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
        </scroll-view>
    </view>
</template>

<script>
import { challengesApi } from '@/api/challenges'

export default {
    data() {
        return {
            statusBarHeight: 0,
            currentTab: 'active',
            challenges: [],
            myChallenges: [],
            page: 1,
            pageSize: 10,
            loading: false,
            noMore: false,
            isRefreshing: false
        }
    },
    computed: {
        activeMyChallenges() {
            return this.myChallenges.filter(item => !item.is_completed)
        },
        completedMyChallenges() {
            return this.myChallenges.filter(item => item.is_completed)
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
            this.page = 1
            this.noMore = false
            this.loadData()
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
         * 加载数据
         */
        async loadData() {
            if (this.currentTab === 'active') {
                await this.loadChallenges()
            } else {
                await this.loadMyChallenges()
            }
        },

        /**
         * 加载挑战列表
         */
        async loadChallenges() {
            if (this.loading) return
            this.loading = true

            try {
                const res = await challengesApi.getChallenges({
                    page: this.page,
                    limit: this.pageSize,
                    is_active: true
                })

                const newItems = res.items || []

                if (this.page === 1) {
                    this.challenges = newItems
                } else {
                    this.challenges = [...this.challenges, ...newItems]
                }

                if (newItems.length < this.pageSize) {
                    this.noMore = true
                }

            } catch (error) {
                console.error('加载挑战失败:', error)
            } finally {
                this.loading = false
            }
        },

        /**
         * 加载我的挑战
         */
        async loadMyChallenges() {
            try {
                const res = await challengesApi.getMyChallenges()
                this.myChallenges = res.items || []
            } catch (error) {
                console.error('加载我的挑战失败:', error)
            }
        },

        /**
         * 加载更多
         */
        loadMore() {
            if (this.currentTab === 'active' && !this.noMore && !this.loading) {
                this.page++
                this.loadChallenges()
            }
        },

        /**
         * 参与挑战
         */
        async joinChallenge(item) {
            try {
                await challengesApi.joinChallenge(item.id)
                uni.showToast({
                    title: '参与成功',
                    icon: 'success'
                })
            } catch (error) {
                console.error('参与失败:', error)
            }
        },

        /**
         * 领取奖励
         */
        async claimReward(item) {
            try {
                await challengesApi.claimChallengeReward(item.id)
                item.reward_claimed = true
                uni.showToast({
                    title: '奖励已领取',
                    icon: 'success'
                })
            } catch (error) {
                console.error('领取失败:', error)
            }
        },

        /**
         * 获取封面渐变颜色
         */
        getCoverGradient(type) {
            const gradients = {
                'weight_loss': 'linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%)',
                'steps': 'linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%)',
                'workout': 'linear-gradient(135deg, #2196F3 0%, #03A9F4 100%)'
            }
            return gradients[type] || 'linear-gradient(135deg, #9C27B0 0%, #E040FB 100%)'
        },

        /**
         * 获取类型文本
         */
        getTypeText(type) {
            const map = {
                'weight_loss': '🔥 减脂',
                'steps': '🚶 步数',
                'workout': '💪 训练'
            }
            return map[type] || '🎯 挑战'
        },

        /**
         * 格式化日期
         */
        formatDate(dateStr) {
            if (!dateStr) return ''
            return dateStr.split('T')[0]
        },

        /**
         * 页面跳转
         */
        goToDetail(id) {
            uni.navigateTo({
                url: `/pages/challenges/detail?id=${id}`
            })
        },

        goToMyDetail(id) {
            uni.navigateTo({
                url: `/pages/challenges/my-detail?id=${id}`
            })
        }
    }
}
</script>

<style scoped>
.challenges-container {
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
    justify-content: center;
    height: 88rpx;
    padding: 0 30rpx;
}

.nav-title {
    font-size: 34rpx;
    font-weight: bold;
    color: #333333;
}

/* Tab切换 */
.tabs {
    display: flex;
    padding: 0 30rpx 20rpx;
}

.tab-item {
    position: relative;
    padding: 16rpx 60rpx;
    text-align: center;
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

/* 滚动区域 */
.content-scroll {
    height: calc(100vh - 88rpx - 100rpx - var(--status-bar-height));
}

/* 通用区块 */
.challenges-section,
.my-challenges-section {
    padding: 20rpx;
}

/* 空状态 */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 120rpx 0;
}

.empty-icon {
    font-size: 120rpx;
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

/* 挑战卡片 */
.challenge-list {
    display: flex;
    flex-direction: column;
}

.challenge-card {
    background: #FFFFFF;
    border-radius: 20rpx;
    margin-bottom: 24rpx;
    overflow: hidden;
}

.challenge-cover {
    height: 240rpx;
    position: relative;
}

.cover-content {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 30rpx;
    background: linear-gradient(transparent, rgba(0,0,0,0.3));
}

.challenge-type-badge {
    display: inline-block;
    padding: 6rpx 16rpx;
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12rpx;
    font-size: 22rpx;
    color: #333333;
    margin-bottom: 12rpx;
}

.challenge-name {
    display: block;
    font-size: 32rpx;
    font-weight: bold;
    color: #FFFFFF;
    margin-bottom: 12rpx;
}

.challenge-meta {
    display: flex;
}

.meta-item {
    font-size: 22rpx;
    color: rgba(255, 255, 255, 0.9);
}

/* 挑战信息 */
.challenge-info {
    padding: 24rpx;
}

.info-row {
    display: flex;
    margin-bottom: 20rpx;
}

.info-item {
    flex: 1;
}

.info-label {
    display: block;
    font-size: 22rpx;
    color: #999999;
    margin-bottom: 6rpx;
}

.info-value {
    font-size: 26rpx;
    color: #333333;
    font-weight: 500;
}

.action-row {
    display: flex;
    justify-content: flex-end;
}

.btn-join {
    padding: 16rpx 48rpx;
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 24rpx;
    margin: 0;
    line-height: 1;
}

.btn-join::after {
    border: none;
}

.btn-join text {
    font-size: 26rpx;
    color: #FFFFFF;
}

/* 我的挑战 */
.section-block {
    background: #FFFFFF;
    border-radius: 16rpx;
    padding: 0 24rpx;
    margin-bottom: 20rpx;
}

.section-header {
    padding: 20rpx 0;
    border-bottom: 1rpx solid #F5F5F5;
}

.section-title {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
}

.my-challenge-list {
    display: flex;
    flex-direction: column;
}

.my-challenge-item {
    display: flex;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #F5F5F5;
}

.my-challenge-item:last-child {
    border-bottom: none;
}

.my-challenge-item.completed .my-challenge-name {
    color: #999999;
}

.my-challenge-info {
    flex: 1;
}

.my-challenge-name {
    font-size: 28rpx;
    color: #333333;
    margin-bottom: 12rpx;
}

.progress-section {
    display: flex;
    align-items: center;
}

.progress-bar {
    flex: 1;
    height: 12rpx;
    background: #F5F5F5;
    border-radius: 6rpx;
    margin-right: 16rpx;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 6rpx;
}

.progress-text {
    font-size: 22rpx;
    color: #999999;
}

.my-challenge-status {
    margin-left: 20rpx;
}

.status-text {
    font-size: 24rpx;
    color: #4CAF50;
    background: #E8F5E9;
    padding: 8rpx 20rpx;
    border-radius: 12rpx;
}

.status-badge {
    padding: 8rpx 20rpx;
    border-radius: 12rpx;
}

.status-badge text {
    font-size: 24rpx;
}

.status-badge.claimed {
    background: #E8F5E9;
}

.status-badge.claimed text {
    color: #4CAF50;
}

.status-badge.unclaimed {
    background: linear-gradient(135deg, #FF9800 0%, #FFC107 100%);
}

.status-badge.unclaimed text {
    color: #FFFFFF;
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
