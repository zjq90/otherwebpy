<template>
    <view class="mine-container">
        <!-- 顶部用户信息卡片 -->
        <view class="user-card-section">
            <view class="user-card">
                <view class="user-info-row">
                    <image 
                        class="user-avatar" 
                        :src="userInfo?.avatar || defaultAvatar" 
                        mode="aspectFill"
                    ></image>
                    <view class="user-detail">
                        <text class="user-name">{{ userInfo?.nickname || userInfo?.username || '未设置昵称' }}</text>
                        <text class="user-username">@{{ userInfo?.username }}</text>
                    </view>
                    <view class="edit-btn" @click="goToEdit">
                        <text class="edit-icon">✏️</text>
                    </view>
                </view>

                <!-- 数据统计 -->
                <view class="stats-row">
                    <view class="stat-item" @click="goToMyPosts">
                        <text class="stat-value">{{ stats.posts || 0 }}</text>
                        <text class="stat-label">动态</text>
                    </view>
                    <view class="stat-divider"></view>
                    <view class="stat-item" @click="goToFriends">
                        <text class="stat-value">{{ stats.friends || 0 }}</text>
                        <text class="stat-label">好友</text>
                    </view>
                    <view class="stat-divider"></view>
                    <view class="stat-item">
                        <text class="stat-value">{{ stats.points || 0 }}</text>
                        <text class="stat-label">积分</text>
                    </view>
                </view>
            </view>
        </view>

        <!-- 功能菜单 -->
        <view class="menu-section">
            <!-- 我的动态 -->
            <view class="menu-item" @click="goToMyPosts">
                <view class="menu-left">
                    <text class="menu-icon">📝</text>
                    <text class="menu-title">我的动态</text>
                </view>
                <text class="menu-arrow">›</text>
            </view>

            <!-- 我的收藏 -->
            <view class="menu-item" @click="goToFavorites">
                <view class="menu-left">
                    <text class="menu-icon">⭐</text>
                    <text class="menu-title">我的收藏</text>
                </view>
                <text class="menu-arrow">›</text>
            </view>

            <!-- 我的成就 -->
            <view class="menu-item" @click="goToAchievements">
                <view class="menu-left">
                    <text class="menu-icon">🏆</text>
                    <text class="menu-title">我的成就</text>
                </view>
                <text class="menu-arrow">›</text>
            </view>
        </view>

        <!-- 设置菜单 -->
        <view class="menu-section">
            <!-- 账号设置 -->
            <view class="menu-item" @click="goToAccountSettings">
                <view class="menu-left">
                    <text class="menu-icon">⚙️</text>
                    <text class="menu-title">账号设置</text>
                </view>
                <text class="menu-arrow">›</text>
            </view>

            <!-- 隐私设置 -->
            <view class="menu-item" @click="goToPrivacySettings">
                <view class="menu-left">
                    <text class="menu-icon">🔒</text>
                    <text class="menu-title">隐私设置</text>
                </view>
                <text class="menu-arrow">›</text>
            </view>

            <!-- 帮助与反馈 -->
            <view class="menu-item" @click="goToHelp">
                <view class="menu-left">
                    <text class="menu-icon">❓</text>
                    <text class="menu-title">帮助与反馈</text>
                </view>
                <text class="menu-arrow">›</text>
            </view>

            <!-- 关于我们 -->
            <view class="menu-item" @click="goToAbout">
                <view class="menu-left">
                    <text class="menu-icon">ℹ️</text>
                    <text class="menu-title">关于我们</text>
                </view>
                <text class="menu-arrow">›</text>
            </view>
        </view>

        <!-- 退出登录 -->
        <view class="logout-section">
            <button class="logout-btn" @click="handleLogout">
                退出登录
            </button>
        </view>

        <!-- 版本信息 -->
        <view class="version-section">
            <text class="version-text">版本 1.0.0</text>
        </view>
    </view>
</template>

<script>
import { getUserInfo, removeToken, removeUserInfo } from '@/utils/auth'
import { authApi } from '@/api/auth'

export default {
    data() {
        return {
            defaultAvatar: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=fitness%20avatar%20icon%20simple&image_size=square',
            userInfo: null,
            stats: {
                posts: 0,
                friends: 0,
                points: 0
            }
        }
    },
    onShow() {
        this.loadData()
    },
    methods: {
        /**
         * 加载数据
         */
        async loadData() {
            this.userInfo = getUserInfo()
            
            // 从本地存储获取用户信息
            if (this.userInfo) {
                this.stats.points = this.userInfo.points || 0
            }

            // 尝试从服务器获取最新用户信息
            try {
                const res = await authApi.getCurrentUser()
                if (res) {
                    this.userInfo = res
                    this.stats.points = res.points || 0
                }
            } catch (error) {
                console.error('获取用户信息失败:', error)
            }
        },

        /**
         * 退出登录
         */
        handleLogout() {
            uni.showModal({
                title: '提示',
                content: '确定要退出登录吗？',
                success: (res) => {
                    if (res.confirm) {
                        // 清除登录状态
                        removeToken()
                        removeUserInfo()

                        uni.showToast({
                            title: '已退出登录',
                            icon: 'success'
                        })

                        // 跳转到登录页
                        setTimeout(() => {
                            uni.reLaunch({
                                url: '/pages/login/login'
                            })
                        }, 1000)
                    }
                }
            })
        },

        /**
         * 页面跳转
         */
        goToEdit() {
            uni.navigateTo({
                url: '/pages/mine/edit'
            })
        },

        goToMyPosts() {
            uni.navigateTo({
                url: '/pages/mine/my-posts'
            })
        },

        goToFriends() {
            uni.switchTab({
                url: '/pages/friends/friends'
            })
        },

        goToFavorites() {
            uni.navigateTo({
                url: '/pages/mine/favorites'
            })
        },

        goToAchievements() {
            uni.navigateTo({
                url: '/pages/mine/achievements'
            })
        },

        goToAccountSettings() {
            uni.navigateTo({
                url: '/pages/mine/account-settings'
            })
        },

        goToPrivacySettings() {
            uni.navigateTo({
                url: '/pages/mine/privacy-settings'
            })
        },

        goToHelp() {
            uni.navigateTo({
                url: '/pages/mine/help'
            })
        },

        goToAbout() {
            uni.navigateTo({
                url: '/pages/mine/about'
            })
        }
    }
}
</script>

<style scoped>
.mine-container {
    min-height: 100vh;
    background: #F5F5F5;
    padding-bottom: 40rpx;
}

/* 用户卡片区域 */
.user-card-section {
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    padding: 0 30rpx 30rpx;
}

.user-card {
    padding-top: calc(var(--status-bar-height) + 20rpx);
}

.user-info-row {
    display: flex;
    align-items: center;
    margin-bottom: 30rpx;
}

.user-avatar {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    border: 4rpx solid #FFFFFF;
}

.user-detail {
    flex: 1;
    margin-left: 24rpx;
}

.user-name {
    font-size: 36rpx;
    font-weight: bold;
    color: #FFFFFF;
    display: block;
    margin-bottom: 8rpx;
}

.user-username {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
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

/* 统计行 */
.stats-row {
    display: flex;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 16rpx;
    padding: 24rpx 0;
}

.stat-item {
    flex: 1;
    text-align: center;
}

.stat-value {
    font-size: 36rpx;
    font-weight: bold;
    color: #FFFFFF;
    display: block;
    margin-bottom: 8rpx;
}

.stat-label {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.9);
}

.stat-divider {
    width: 2rpx;
    background: rgba(255, 255, 255, 0.3);
    margin: 8rpx 0;
}

/* 菜单区域 */
.menu-section {
    background: #FFFFFF;
    margin: 20rpx;
    border-radius: 16rpx;
    overflow: hidden;
}

.menu-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28rpx 24rpx;
    border-bottom: 1rpx solid #F5F5F5;
}

.menu-item:last-child {
    border-bottom: none;
}

.menu-left {
    display: flex;
    align-items: center;
}

.menu-icon {
    font-size: 40rpx;
    margin-right: 20rpx;
}

.menu-title {
    font-size: 28rpx;
    color: #333333;
}

.menu-arrow {
    font-size: 36rpx;
    color: #CCCCCC;
}

/* 退出登录 */
.logout-section {
    padding: 0 20rpx;
    margin-top: 40rpx;
}

.logout-btn {
    width: 100%;
    height: 88rpx;
    line-height: 88rpx;
    background: #FFFFFF;
    color: #F44336;
    font-size: 30rpx;
    border-radius: 16rpx;
    border: none;
}

.logout-btn::after {
    border: none;
}

/* 版本信息 */
.version-section {
    display: flex;
    justify-content: center;
    margin-top: 40rpx;
}

.version-text {
    font-size: 22rpx;
    color: #CCCCCC;
}
</style>
