<template>
    <view class="profile-container">
        <!-- 用户信息头部 -->
        <view class="header-section">
            <view class="user-info">
                <view class="user-avatar">
                    <text class="avatar-text">{{ userInfo.real_name ? userInfo.real_name.charAt(0) : '用' }}</text>
                </view>
                <view class="user-detail">
                    <text class="user-name">{{ userInfo.real_name || userInfo.username }}</text>
                    <view class="user-status">
                        <text class="status-tag" v-for="role in userRoles" :key="role.id">{{ role.name }}</text>
                        <view class="verify-status" v-if="userInfo.is_verified">
                            <text class="verified-icon">✓</text>
                            <text class="verified-text">已认证</text>
                        </view>
                    </view>
                </view>
            </view>
            <view class="edit-btn" @click="goToProfileEdit">
                <text class="edit-icon">✏️</text>
            </view>
        </view>

        <!-- 功能菜单列表 -->
        <view class="menu-section">
            <!-- 个人设置 -->
            <view class="menu-group">
                <text class="group-title">个人设置</text>
                <view class="menu-list">
                    <view class="menu-item" @click="goTo('change-password')">
                        <view class="menu-icon" style="background: #1890ff">🔐</view>
                        <text class="menu-text">修改密码</text>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goTo('real-name-verify')" v-if="!userInfo.is_verified">
                        <view class="menu-icon" style="background: #faad14">🪪</view>
                        <text class="menu-text">实名认证</text>
                        <view class="menu-status">
                            <text class="status-pending">未完成</text>
                        </view>
                    </view>
                </view>
            </view>

            <!-- 系统设置 -->
            <view class="menu-group">
                <text class="group-title">系统设置</text>
                <view class="menu-list">
                    <view class="menu-item" @click="goTo('notification-setting')">
                        <view class="menu-icon" style="background: #52c41a">🔔</view>
                        <text class="menu-text">通知设置</text>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goTo('about')">
                        <view class="menu-icon" style="background: #722ed1">ℹ️</view>
                        <text class="menu-text">关于我们</text>
                        <text class="menu-arrow">›</text>
                    </view>
                </view>
            </view>

            <!-- 帮助与反馈 -->
            <view class="menu-group">
                <text class="group-title">帮助与反馈</text>
                <view class="menu-list">
                    <view class="menu-item" @click="goTo('help')">
                        <view class="menu-icon" style="background: #13c2c2">❓</view>
                        <text class="menu-text">使用帮助</text>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goTo('feedback')">
                        <view class="menu-icon" style="background: #eb2f96">💬</view>
                        <text class="menu-text">意见反馈</text>
                        <text class="menu-arrow">›</text>
                    </view>
                </view>
            </view>
        </view>

        <!-- 退出登录按钮 -->
        <view class="logout-section">
            <view class="btn-secondary logout-btn" @click="handleLogout">
                退出登录
            </view>
        </view>

        <!-- 版本信息 -->
        <view class="version-section">
            <text class="version-text">版本 v1.0.0</text>
        </view>
    </view>
</template>

<script>
import { logout } from '@/api/auth.js'

export default {
    data() {
        return {
            userInfo: {},
            userRoles: []
        }
    },
    onLoad() {
        this.loadUserInfo()
    },
    onShow() {
        this.loadUserInfo()
    },
    methods: {
        // 加载用户信息
        loadUserInfo() {
            const userInfo = uni.getStorageSync('userInfo')
            if (userInfo) {
                this.userInfo = userInfo
                this.userRoles = userInfo.roles || []
            }
        },

        // 跳转到页面
        goTo(page) {
            const pageMap = {
                'change-password': '/pages/change-password/change-password',
                'real-name-verify': '/pages/real-name-verify/real-name-verify',
                'notification-setting': '/pages/notification-setting/notification-setting',
                'about': '/pages/about/about',
                'help': '/pages/help/help',
                'feedback': '/pages/feedback/feedback'
            }
            const url = pageMap[page]
            if (url) {
                uni.navigateTo({ url })
            } else {
                uni.showToast({
                    title: '功能开发中',
                    icon: 'none'
                })
            }
        },

        // 编辑个人资料
        goToProfileEdit() {
            uni.showToast({
                title: '编辑功能开发中',
                icon: 'none'
            })
        },

        // 退出登录
        async handleLogout() {
            uni.showModal({
                title: '提示',
                content: '确定要退出登录吗？',
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            // 调用退出登录API
                            await logout()
                        } catch (err) {
                            console.error('退出登录API调用失败:', err)
                        }

                        // 清除本地存储
                        uni.removeStorageSync('token')
                        uni.removeStorageSync('userInfo')
                        uni.removeStorageSync('permissions')

                        // 跳转到登录页
                        uni.redirectTo({
                            url: '/pages/login/login'
                        })

                        uni.showToast({
                            title: '已退出登录',
                            icon: 'success'
                        })
                    }
                }
            })
        }
    }
}
</script>

<style scoped>
.profile-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 120rpx;
}

/* 头部用户信息 */
.header-section {
    background: linear-gradient(180deg, #1890ff 0%, #40a9ff 100%);
    padding: 40rpx;
    padding-top: calc(40rpx + var(--status-bar-height));
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
}

.user-info {
    display: flex;
    align-items: center;
}

.user-avatar {
    width: 120rpx;
    height: 120rpx;
    background: #ffffff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
    box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.15);
}

.avatar-text {
    font-size: 48rpx;
    font-weight: bold;
    color: #1890ff;
}

.user-detail {
    display: flex;
    flex-direction: column;
}

.user-name {
    font-size: 36rpx;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 16rpx;
}

.user-status {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.status-tag {
    font-size: 22rpx;
    color: #1890ff;
    background: rgba(255, 255, 255, 0.9);
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    margin-right: 12rpx;
    margin-bottom: 8rpx;
}

.verify-status {
    display: flex;
    align-items: center;
    background: rgba(246, 255, 237, 0.9);
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    margin-bottom: 8rpx;
}

.verified-icon {
    font-size: 18rpx;
    color: #52c41a;
    margin-right: 6rpx;
}

.verified-text {
    font-size: 22rpx;
    color: #52c41a;
}

.edit-btn {
    width: 64rpx;
    height: 64rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.edit-icon {
    font-size: 32rpx;
}

/* 功能菜单 */
.menu-section {
    margin-top: -40rpx;
    padding: 0 24rpx;
}

.menu-group {
    background: #ffffff;
    border-radius: 16rpx;
    margin-bottom: 20rpx;
    overflow: hidden;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.group-title {
    font-size: 24rpx;
    color: #999999;
    padding: 24rpx 28rpx 16rpx;
}

.menu-list {
    padding: 0 28rpx;
}

.menu-item {
    display: flex;
    align-items: center;
    padding: 28rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
    border-bottom: none;
}

.menu-icon {
    width: 64rpx;
    height: 64rpx;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    font-size: 32rpx;
}

.menu-text {
    flex: 1;
    font-size: 28rpx;
    color: #333333;
}

.menu-arrow {
    font-size: 32rpx;
    color: #d9d9d9;
}

.menu-status {
    margin-right: 16rpx;
}

.status-pending {
    font-size: 24rpx;
    color: #faad14;
    background: #fffbe6;
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
}

/* 退出登录 */
.logout-section {
    padding: 40rpx;
}

.logout-btn {
    width: 100%;
    padding: 28rpx 0;
    font-size: 32rpx;
}

/* 版本信息 */
.version-section {
    text-align: center;
    padding: 20rpx;
}

.version-text {
    font-size: 24rpx;
    color: #999999;
}
</style>
