<template>
    <view class="invitations-container">
        <!-- 自定义导航栏 -->
        <view class="custom-nav" :style="{ paddingTop: statusBarHeight + 'px' }">
            <view class="nav-content">
                <text class="nav-title">邀请有礼</text>
            </view>
        </view>

        <!-- 内容区域 -->
        <scroll-view class="content-scroll" scroll-y>
            <!-- 邀请卡片 -->
            <view class="invite-card-section">
                <view class="invite-card">
                    <view class="card-header">
                        <text class="card-title">我的邀请码</text>
                        <text class="card-subtitle">分享给好友，一起健身</text>
                    </view>

                    <view class="invite-code-section">
                        <text class="invite-code-label">邀请码</text>
                        <view class="code-display">
                            <text class="code-text">{{ inviteCode || '---' }}</text>
                            <view class="copy-btn" @click="copyCode">
                                <text class="copy-text">复制</text>
                            </view>
                        </view>
                    </view>

                    <view class="share-section">
                        <view class="share-btn" @click="shareInvite">
                            <text class="share-icon">📤</text>
                            <text class="share-text">分享邀请</text>
                        </view>
                    </view>
                </view>

                <!-- 奖励说明 -->
                <view class="reward-info">
                    <view class="reward-item">
                        <text class="reward-icon">🎁</text>
                        <view class="reward-detail">
                            <text class="reward-title">邀请奖励</text>
                            <text class="reward-desc">成功邀请好友办卡，双方均可获得积分奖励</text>
                        </view>
                    </view>
                </view>
            </view>

            <!-- 统计数据 -->
            <view class="stats-section">
                <view class="section-header">
                    <text class="section-title">邀请统计</text>
                </view>

                <view class="stats-grid">
                    <view class="stat-item">
                        <text class="stat-value">{{ stats.total_invited || 0 }}</text>
                        <text class="stat-label">总邀请</text>
                    </view>
                    <view class="stat-item">
                        <text class="stat-value">{{ stats.pending || 0 }}</text>
                        <text class="stat-label">待接受</text>
                    </view>
                    <view class="stat-item">
                        <text class="stat-value">{{ stats.completed || 0 }}</text>
                        <text class="stat-label">已完成</text>
                    </view>
                    <view class="stat-item">
                        <text class="stat-value">{{ stats.rewards_claimed || 0 }}</text>
                        <text class="stat-label">已领奖</text>
                    </view>
                </view>
            </view>

            <!-- 邀请记录 -->
            <view class="records-section">
                <view class="section-header">
                    <text class="section-title">邀请记录</text>
                    <text class="section-more" @click="goToRecords">查看全部 ›</text>
                </view>

                <!-- 空状态 -->
                <view v-if="invitations.length === 0" class="empty-state">
                    <text class="empty-icon">📋</text>
                    <text class="empty-text">暂无邀请记录</text>
                </view>

                <!-- 记录列表 -->
                <view class="record-list">
                    <view 
                        class="record-item" 
                        v-for="item in invitations" 
                        :key="item.id"
                    >
                        <image 
                            class="invitee-avatar" 
                            :src="item.invitee_avatar || defaultAvatar" 
                            mode="aspectFill"
                        ></image>
                        <view class="record-info">
                            <text class="invitee-name">{{ item.invitee_nickname || item.invitee_username || '未注册' }}</text>
                            <text class="record-time">{{ formatTime(item.created_at) }}</text>
                        </view>
                        <view class="record-status">
                            <text :class="'status-' + item.status">
                                {{ getStatusText(item.status) }}
                            </text>
                        </view>
                    </view>
                </view>
            </view>

            <!-- 邀请表单 -->
            <view class="invite-form-section">
                <view class="section-header">
                    <text class="section-title">直接邀请</text>
                </view>

                <view class="form-section">
                    <view class="form-item">
                        <text class="form-label">手机号</text>
                        <input 
                            class="form-input" 
                            type="number" 
                            placeholder="请输入好友手机号"
                            v-model="inviteForm.phone"
                            placeholder-class="placeholder-text"
                        />
                    </view>

                    <view class="form-item">
                        <text class="form-label">邮箱</text>
                        <input 
                            class="form-input" 
                            type="text" 
                            placeholder="请输入好友邮箱（可选）"
                            v-model="inviteForm.email"
                            placeholder-class="placeholder-text"
                        />
                    </view>

                    <button 
                        class="invite-btn" 
                        :loading="inviting"
                        @click="sendInvitation"
                    >
                        发送邀请
                    </button>
                </view>
            </view>
        </scroll-view>
    </view>
</template>

<script>
import { invitationsApi } from '@/api/invitations'
import { getUserInfo } from '@/utils/auth'

export default {
    data() {
        return {
            statusBarHeight: 0,
            defaultAvatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fitness%20avatar%20icon%20simple&image_size=square',
            userInfo: null,
            inviteCode: '',
            stats: {
                total_invited: 0,
                pending: 0,
                completed: 0,
                rewards_claimed: 0
            },
            invitations: [],
            inviteForm: {
                phone: '',
                email: ''
            },
            inviting: false
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
         * 加载数据
         */
        async loadData() {
            this.userInfo = getUserInfo()
            await Promise.all([
                this.loadInviteCode(),
                this.loadStats(),
                this.loadInvitations()
            ])
        },

        /**
         * 加载邀请码
         */
        async loadInviteCode() {
            try {
                const res = await invitationsApi.getMyInviteCode()
                this.inviteCode = res.invite_code || ''
            } catch (error) {
                console.error('加载邀请码失败:', error)
            }
        },

        /**
         * 加载统计数据
         */
        async loadStats() {
            try {
                const res = await invitationsApi.getInvitationStats()
                this.stats = {
                    total_invited: res.total_invited || 0,
                    pending: res.pending || 0,
                    completed: res.completed || 0,
                    rewards_claimed: res.rewards_claimed || 0
                }
            } catch (error) {
                console.error('加载统计失败:', error)
            }
        },

        /**
         * 加载邀请记录
         */
        async loadInvitations() {
            try {
                const res = await invitationsApi.getSentInvitations({
                    limit: 5
                })
                this.invitations = res.items || []
            } catch (error) {
                console.error('加载邀请记录失败:', error)
            }
        },

        /**
         * 复制邀请码
         */
        copyCode() {
            if (!this.inviteCode) {
                uni.showToast({
                    title: '暂无邀请码',
                    icon: 'none'
                })
                return
            }

            uni.setClipboardData({
                data: this.inviteCode,
                success: () => {
                    uni.showToast({
                        title: '复制成功',
                        icon: 'success'
                    })
                }
            })
        },

        /**
         * 分享邀请
         */
        shareInvite() {
            uni.showActionSheet({
                itemList: ['分享到微信', '生成海报', '复制链接'],
                success: (res) => {
                    switch (res.tapIndex) {
                        case 0:
                            uni.showToast({
                                title: '请使用微信分享',
                                icon: 'none'
                            })
                            break
                        case 1:
                            uni.showToast({
                                title: '海报生成中...',
                                icon: 'loading'
                            })
                            break
                        case 2:
                            this.copyCode()
                            break
                    }
                }
            })
        },

        /**
         * 发送邀请
         */
        async sendInvitation() {
            if (!this.inviteForm.phone.trim()) {
                uni.showToast({
                    title: '请输入手机号',
                    icon: 'none'
                })
                return
            }

            this.inviting = true

            try {
                const data = {
                    invitee_phone: this.inviteForm.phone
                }
                if (this.inviteForm.email.trim()) {
                    data.invitee_email = this.inviteForm.email
                }

                await invitationsApi.createInvitation(data)

                uni.showToast({
                    title: '邀请已发送',
                    icon: 'success'
                })

                // 重置表单
                this.inviteForm = {
                    phone: '',
                    email: ''
                }

                // 刷新数据
                this.loadData()

            } catch (error) {
                console.error('发送邀请失败:', error)
            } finally {
                this.inviting = false
            }
        },

        /**
         * 格式化时间
         */
        formatTime(timeStr) {
            if (!timeStr) return ''
            return timeStr.split('T')[0]
        },

        /**
         * 获取状态文本
         */
        getStatusText(status) {
            const map = {
                'pending': '等待中',
                'accepted': '已接受',
                'registered': '已注册',
                'completed': '已完成',
                'expired': '已过期'
            }
            return map[status] || status
        },

        /**
         * 页面跳转
         */
        goToRecords() {
            uni.navigateTo({
                url: '/pages/invitations/records'
            })
        }
    }
}
</script>

<style scoped>
.invitations-container {
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

/* 滚动区域 */
.content-scroll {
    height: calc(100vh - 88rpx - var(--status-bar-height));
}

/* 邀请卡片 */
.invite-card-section {
    padding: 20rpx;
}

.invite-card {
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 24rpx;
    padding: 40rpx;
    margin-bottom: 20rpx;
}

.card-header {
    text-align: center;
    margin-bottom: 30rpx;
}

.card-title {
    font-size: 32rpx;
    font-weight: bold;
    color: #FFFFFF;
    display: block;
    margin-bottom: 8rpx;
}

.card-subtitle {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.9);
}

/* 邀请码 */
.invite-code-section {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 16rpx;
    padding: 30rpx;
    margin-bottom: 30rpx;
}

.invite-code-label {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
    display: block;
    margin-bottom: 16rpx;
}

.code-display {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.code-text {
    font-size: 48rpx;
    font-weight: bold;
    color: #FFFFFF;
    letter-spacing: 8rpx;
}

.copy-btn {
    padding: 12rpx 32rpx;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 20rpx;
}

.copy-text {
    font-size: 24rpx;
    color: #FFFFFF;
}

/* 分享按钮 */
.share-section {
    display: flex;
    justify-content: center;
}

.share-btn {
    display: flex;
    align-items: center;
    padding: 16rpx 48rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 24rpx;
}

.share-icon {
    font-size: 36rpx;
    margin-right: 12rpx;
}

.share-text {
    font-size: 28rpx;
    color: #FFFFFF;
}

/* 奖励说明 */
.reward-info {
    background: #FFFFFF;
    border-radius: 16rpx;
    padding: 24rpx;
}

.reward-item {
    display: flex;
    align-items: flex-start;
}

.reward-icon {
    font-size: 40rpx;
    margin-right: 16rpx;
}

.reward-detail {
    flex: 1;
}

.reward-title {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
    display: block;
    margin-bottom: 6rpx;
}

.reward-desc {
    font-size: 24rpx;
    color: #666666;
    line-height: 1.5;
}

/* 统计区域 */
.stats-section {
    background: #FFFFFF;
    margin: 0 20rpx 20rpx;
    border-radius: 16rpx;
    padding: 24rpx;
}

.section-header {
    padding-bottom: 20rpx;
    border-bottom: 1rpx solid #F5F5F5;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.section-title {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
}

.section-more {
    font-size: 24rpx;
    color: #999999;
}

.stats-grid {
    display: flex;
    padding-top: 20rpx;
}

.stat-item {
    flex: 1;
    text-align: center;
}

.stat-value {
    font-size: 40rpx;
    font-weight: bold;
    color: #4CAF50;
    display: block;
    margin-bottom: 8rpx;
}

.stat-label {
    font-size: 22rpx;
    color: #999999;
}

/* 邀请记录 */
.records-section {
    background: #FFFFFF;
    margin: 0 20rpx 20rpx;
    border-radius: 16rpx;
    padding: 24rpx;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 60rpx 0;
}

.empty-icon {
    font-size: 80rpx;
    margin-bottom: 16rpx;
}

.empty-text {
    font-size: 26rpx;
    color: #999999;
}

.record-list {
    display: flex;
    flex-direction: column;
    padding-top: 20rpx;
}

.record-item {
    display: flex;
    align-items: center;
    padding: 16rpx 0;
    border-bottom: 1rpx solid #F5F5F5;
}

.record-item:last-child {
    border-bottom: none;
}

.invitee-avatar {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
}

.record-info {
    flex: 1;
    margin-left: 16rpx;
}

.invitee-name {
    font-size: 28rpx;
    color: #333333;
    display: block;
}

.record-time {
    font-size: 22rpx;
    color: #999999;
    margin-top: 4rpx;
}

.record-status text {
    font-size: 22rpx;
    padding: 6rpx 16rpx;
    border-radius: 10rpx;
}

.status-pending {
    color: #FF9800;
    background: #FFF3E0;
}

.status-accepted,
.status-registered {
    color: #4CAF50;
    background: #E8F5E9;
}

.status-completed {
    color: #2196F3;
    background: #E3F2FD;
}

.status-expired {
    color: #999999;
    background: #F5F5F5;
}

/* 邀请表单 */
.invite-form-section {
    background: #FFFFFF;
    margin: 0 20rpx 20rpx;
    border-radius: 16rpx;
    padding: 24rpx;
}

.form-section {
    padding-top: 20rpx;
}

.form-item {
    display: flex;
    align-items: center;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #F5F5F5;
}

.form-item:last-of-type {
    border-bottom: none;
}

.form-label {
    width: 120rpx;
    font-size: 28rpx;
    color: #333333;
}

.form-input {
    flex: 1;
    font-size: 28rpx;
    color: #333333;
}

.placeholder-text {
    color: #CCCCCC;
}

.invite-btn {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    color: #FFFFFF;
    font-size: 30rpx;
    font-weight: 500;
    border-radius: 44rpx;
    margin-top: 30rpx;
    border: none;
}

.invite-btn::after {
    border: none;
}
</style>
