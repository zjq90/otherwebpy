<template>
    <view class="profile-container">
        <view class="profile-header">
            <view class="header-bg"></view>
            <view class="user-card">
                <view class="user-avatar" @click="goToEditProfile">
                    <text v-if="userInfo.real_name">{{ userInfo.real_name.charAt(0) }}</text>
                    <text v-else>会</text>
                </view>
                <view class="user-info">
                    <text class="user-name">{{ userInfo.real_name || userInfo.username }}</text>
                    <text class="user-role">{{ getRoleLabel(userInfo.role) }}</text>
                </view>
                <view class="edit-btn" @click="goToEditProfile">
                    <text class="edit-icon">⚙️</text>
                </view>
            </view>
            
            <view class="user-stats">
                <view class="stat-item" @click="goToMyBookings">
                    <text class="stat-value">{{ stats.bookings }}</text>
                    <text class="stat-label">预约次数</text>
                </view>
                <view class="stat-divider"></view>
                <view class="stat-item" @click="goToMyReviews">
                    <text class="stat-value">{{ stats.reviews }}</text>
                    <text class="stat-label">评价数量</text>
                </view>
                <view class="stat-divider"></view>
                <view class="stat-item" @click="goToPreferences">
                    <text class="stat-value">{{ stats.favorites }}</text>
                    <text class="stat-label">收藏课程</text>
                </view>
            </view>
        </view>
        
        <view class="menu-section">
            <view class="menu-group">
                <text class="group-title">我的服务</text>
                <view class="menu-list">
                    <view class="menu-item" @click="goToMyBookings">
                        <view class="menu-icon booking">📅</view>
                        <view class="menu-content">
                            <text class="menu-name">我的预约</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goToMyReviews">
                        <view class="menu-icon review">⭐</view>
                        <view class="menu-content">
                            <text class="menu-name">我的评价</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goToPreferences">
                        <view class="menu-icon preference">🎯</view>
                        <view class="menu-content">
                            <text class="menu-name">训练偏好</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                </view>
            </view>
            
            <view class="menu-group">
                <text class="group-title">消息联系</text>
                <view class="menu-list">
                    <view class="menu-item" @click="goToMessages">
                        <view class="menu-icon message">🔔</view>
                        <view class="menu-content">
                            <text class="menu-name">消息中心</text>
                        </view>
                        <view class="menu-badge" v-if="unreadCount > 0">
                            <text>{{ unreadCount > 99 ? '99+' : unreadCount }}</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goToChat">
                        <view class="menu-icon chat">💬</view>
                        <view class="menu-content">
                            <text class="menu-name">在线客服</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                </view>
            </view>
            
            <view class="menu-group">
                <text class="group-title">设置</text>
                <view class="menu-list">
                    <view class="menu-item" @click="goToEditProfile">
                        <view class="menu-icon info">👤</view>
                        <view class="menu-content">
                            <text class="menu-name">个人信息</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goToSecurity">
                        <view class="menu-icon security">🔒</view>
                        <view class="menu-content">
                            <text class="menu-name">账号安全</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                    <view class="menu-item" @click="goToAbout">
                        <view class="menu-icon about">ℹ️</view>
                        <view class="menu-content">
                            <text class="menu-name">关于我们</text>
                        </view>
                        <text class="menu-arrow">›</text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="logout-section">
            <view class="logout-btn" @click="handleLogout">
                <text class="logout-text">退出登录</text>
            </view>
        </view>
        
        <view class="version-info">
            <text>版本 1.0.0</text>
        </view>
    </view>
</template>

<script setup>
import { ref, onShow } from 'vue'
import { authApi, messageApi, chatApi } from '@/utils/api'
import { showConfirm, showToast } from '@/utils'

const userInfo = ref({})
const unreadCount = ref(0)
const stats = ref({
    bookings: 0,
    reviews: 0,
    favorites: 0
})

const getRoleLabel = (role) => {
    const labels = {
        MEMBER: '普通会员',
        COACH: '教练',
        STAFF: '工作人员',
        ADMIN: '管理员'
    }
    return labels[role] || '会员'
}

const fetchUserInfo = () => {
    const stored = uni.getStorageSync('userInfo')
    if (stored) {
        userInfo.value = JSON.parse(stored)
    }
}

const fetchUnreadCount = async () => {
    try {
        const [messageRes, chatRes] = await Promise.all([
            messageApi.getUnreadCount().catch(() => ({ data: { count: 0 } })),
            chatApi.getUnreadCount().catch(() => ({ data: { count: 0 } }))
        ])
        unreadCount.value = (messageRes.data?.count || 0) + (chatRes.data?.count || 0)
    } catch (error) {
        console.error('获取未读数量失败:', error)
    }
}

const goToEditProfile = () => {
    showToast('功能开发中')
}

const goToMyBookings = () => {
    uni.navigateTo({ url: '/pages/bookings/bookings' })
}

const goToMyReviews = () => {
    uni.navigateTo({ url: '/pages/reviews/reviews' })
}

const goToPreferences = () => {
    uni.navigateTo({ url: '/pages/preferences/preferences' })
}

const goToMessages = () => {
    uni.switchTab({ url: '/pages/messages/messages' })
}

const goToChat = () => {
    uni.navigateTo({ url: '/pages/chat/chat' })
}

const goToSecurity = () => {
    showToast('功能开发中')
}

const goToAbout = () => {
    showToast('功能开发中')
}

const handleLogout = async () => {
    const confirmed = await showConfirm('确定要退出登录吗？')
    if (confirmed) {
        try {
            await authApi.logout()
        } catch (error) {
            console.error('退出登录失败:', error)
        } finally {
            uni.removeStorageSync('token')
            uni.removeStorageSync('userInfo')
            showToast('已退出登录', 'success')
            setTimeout(() => {
                uni.reLaunch({ url: '/pages/login/login' })
            }, 1000)
        }
    }
}

onShow(() => {
    fetchUserInfo()
    fetchUnreadCount()
})
</script>

<style lang="scss" scoped>
.profile-container {
    min-height: 100vh;
    background: $bg-color;
    padding-bottom: 60rpx;
}

.profile-header {
    position: relative;
    padding-bottom: 30rpx;
}

.header-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 300rpx;
    background: linear-gradient(135deg, $primary-color 0%, $secondary-color 100%);
    border-radius: 0 0 40rpx 40rpx;
}

.user-card {
    position: relative;
    display: flex;
    align-items: center;
    padding: 80rpx 30rpx 40rpx;
}

.user-avatar {
    width: 120rpx;
    height: 120rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 4rpx solid rgba(255, 255, 255, 0.3);
    
    text {
        font-size: 48rpx;
        color: #ffffff;
        font-weight: bold;
    }
}

.user-info {
    flex: 1;
    margin-left: 24rpx;
}

.user-name {
    font-size: 36rpx;
    font-weight: 500;
    color: #ffffff;
    display: block;
}

.user-role {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
    margin-top: 8rpx;
    display: block;
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
    font-size: 28rpx;
}

.user-stats {
    position: relative;
    display: flex;
    background: #ffffff;
    border-radius: 20rpx;
    margin: 0 30rpx;
    padding: 30rpx 0;
    box-shadow: 0 8rpx 30rpx rgba(0, 0, 0, 0.05);
}

.stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-value {
    font-size: 40rpx;
    font-weight: 600;
    color: $primary-color;
}

.stat-label {
    font-size: 24rpx;
    color: #666666;
    margin-top: 8rpx;
}

.stat-divider {
    width: 1rpx;
    height: 60rpx;
    background: #eeeeee;
    align-self: center;
}

.menu-section {
    padding: 20rpx 30rpx;
}

.menu-group {
    margin-bottom: 30rpx;
}

.group-title {
    font-size: 26rpx;
    color: #999999;
    margin-bottom: 20rpx;
    display: block;
    padding-left: 10rpx;
}

.menu-list {
    background: #ffffff;
    border-radius: 20rpx;
    overflow: hidden;
}

.menu-item {
    display: flex;
    align-items: center;
    padding: 28rpx 30rpx;
    border-bottom: 1rpx solid #f5f5f5;
    
    &:last-child {
        border-bottom: none;
    }
}

.menu-icon {
    width: 64rpx;
    height: 64rpx;
    border-radius: 14rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    font-size: 32rpx;
}

.menu-icon.booking { background: rgba(102, 126, 234, 0.1); }
.menu-icon.review { background: rgba(250, 112, 154, 0.1); }
.menu-icon.preference { background: rgba(250, 225, 64, 0.1); }
.menu-icon.message { background: rgba(79, 172, 254, 0.1); }
.menu-icon.chat { background: rgba(0, 242, 254, 0.1); }
.menu-icon.info { background: rgba(240, 147, 251, 0.1); }
.menu-icon.security { background: rgba(255, 71, 87, 0.1); }
.menu-icon.about { background: rgba(118, 75, 162, 0.1); }

.menu-content {
    flex: 1;
}

.menu-name {
    font-size: 28rpx;
    color: #333333;
}

.menu-badge {
    min-width: 32rpx;
    height: 32rpx;
    background: $danger-color;
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 8rpx;
    margin-right: 16rpx;
    
    text {
        font-size: 20rpx;
        color: #ffffff;
    }
}

.menu-arrow {
    font-size: 32rpx;
    color: #cccccc;
}

.logout-section {
    padding: 0 30rpx;
    margin-top: 20rpx;
}

.logout-btn {
    background: #ffffff;
    border-radius: 20rpx;
    padding: 32rpx 0;
    text-align: center;
}

.logout-text {
    font-size: 30rpx;
    color: $danger-color;
    font-weight: 500;
}

.version-info {
    text-align: center;
    padding: 40rpx 0;
    
    text {
        font-size: 24rpx;
        color: #cccccc;
    }
}
</style>
