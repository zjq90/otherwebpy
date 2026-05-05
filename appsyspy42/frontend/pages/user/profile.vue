<template>
    <view class="page-container">
        <view class="user-header" v-if="userInfo">
            <view class="user-avatar">
                <text>{{ userInfo.real_name ? userInfo.real_name.charAt(0) : '用' }}</text>
            </view>
            <view class="user-info">
                <text class="user-name">{{ userInfo.real_name || '未设置' }}</text>
                <view class="role-tag" :class="userInfo.role === '管理员' ? 'admin' : 'purchaser'">
                    {{ userInfo.role }}
                </view>
            </view>
        </view>
        
        <view class="user-info-card" v-if="userInfo">
            <view class="info-item">
                <text class="info-label">用户名</text>
                <text class="info-value">{{ userInfo.username }}</text>
            </view>
            <view class="info-item" v-if="userInfo.phone">
                <text class="info-label">联系电话</text>
                <text class="info-value">{{ userInfo.phone }}</text>
            </view>
            <view class="info-item" v-if="userInfo.email">
                <text class="info-label">邮箱</text>
                <text class="info-value">{{ userInfo.email }}</text>
            </view>
        </view>
        
        <view class="menu-section">
            <view class="section-title">功能菜单</view>
            
            <view class="menu-list">
                <view class="menu-item" @click="goToMyPurchases">
                    <view class="menu-icon" style="background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);">
                        <text class="uni-icon uni-icon-list"></text>
                    </view>
                    <view class="menu-content">
                        <text class="menu-title">我的采购申请</text>
                        <text class="menu-desc">查看我提交的所有采购申请</text>
                    </view>
                    <view class="menu-arrow">
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </view>
                
                <view class="menu-item" @click="goToPendingApprovals" v-if="isAdmin">
                    <view class="menu-icon" style="background: linear-gradient(135deg, #fa8c16 0%, #ffa940 100%);">
                        <text class="uni-icon uni-icon-notice"></text>
                    </view>
                    <view class="menu-content">
                        <text class="menu-title">待审批申请</text>
                        <text class="menu-desc">审批采购员提交的采购申请</text>
                    </view>
                    <view class="menu-arrow">
                        <view class="badge" v-if="pendingCount > 0">{{ pendingCount }}</view>
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </view>
                
                <view class="menu-item" @click="goToInventoryAlerts">
                    <view class="menu-icon" style="background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);">
                        <text class="uni-icon uni-icon-warning"></text>
                    </view>
                    <view class="menu-content">
                        <text class="menu-title">库存预警</text>
                        <text class="menu-desc">查看低库存预警提醒</text>
                    </view>
                    <view class="menu-arrow">
                        <view class="badge" v-if="alertCount > 0">{{ alertCount }}</view>
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="menu-section">
            <view class="section-title">系统功能</view>
            
            <view class="menu-list">
                <view class="menu-item" @click="showAbout">
                    <view class="menu-icon" style="background: linear-gradient(135deg, #722ed1 0%, #9254de 100%);">
                        <text class="uni-icon uni-icon-info"></text>
                    </view>
                    <view class="menu-content">
                        <text class="menu-title">关于系统</text>
                        <text class="menu-desc">版本信息、功能介绍</text>
                    </view>
                    <view class="menu-arrow">
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </view>
                
                <view class="menu-item" @click="goToSettings">
                    <view class="menu-icon" style="background: linear-gradient(135deg, #13c2c2 0%, #36cfc9 100%);">
                        <text class="uni-icon uni-icon-settings"></text>
                    </view>
                    <view class="menu-content">
                        <text class="menu-title">系统设置</text>
                        <text class="menu-desc">应用配置、个人设置</text>
                    </view>
                    <view class="menu-arrow">
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="logout-section">
            <button class="logout-btn" @click="handleLogout">
                退出登录
            </button>
        </view>
    </view>
</template>

<script>
/**
 * 个人中心页面
 * 功能：展示用户信息、功能菜单、系统功能入口
 */
import config from '@/utils/config.js'

export default {
    data() {
        return {
            userInfo: null,
            isAdmin: false,
            pendingCount: 0,
            alertCount: 0
        }
    },
    
    onShow() {
        this.loadUserInfo()
        this.loadCounts()
    },
    
    methods: {
        loadUserInfo() {
            this.userInfo = uni.getStorageSync(config.userInfoKey)
            this.isAdmin = this.userInfo?.role === '管理员'
        },
        
        async loadCounts() {
            try {
                if (this.isAdmin) {
                    const res = await this.$api.getPendingCount()
                    this.pendingCount = res.count || 0
                }
                
                const alertRes = await this.$api.getLowStockAlerts({ is_read: 0, is_handled: 0 })
                this.alertCount = alertRes.list?.length || 0
            } catch (err) {
                console.error('加载数量失败:', err)
            }
        },
        
        goToMyPurchases() {
            uni.navigateTo({
                url: '/pages/purchase/list'
            })
        },
        
        goToPendingApprovals() {
            uni.navigateTo({
                url: '/pages/purchase/list'
            })
        },
        
        goToInventoryAlerts() {
            uni.navigateTo({
                url: '/pages/inventory/alerts'
            })
        },
        
        showAbout() {
            uni.showModal({
                title: '关于系统',
                content: '库存管理系统 v1.0.0\n\n技术栈：\n- 后端：Python + FastAPI + SQLite\n- 前端：uniapp + Vue.js\n\n功能模块：\n- 库存实时查询\n- 采购申请管理\n- 供应商管理\n\n© 2024 库存管理系统',
                showCancel: false,
                confirmText: '知道了'
            })
        },
        
        goToSettings() {
            uni.showToast({
                title: '设置功能开发中',
                icon: 'none'
            })
        },
        
        handleLogout() {
            uni.showModal({
                title: '确认退出',
                content: '确定要退出登录吗？',
                success: (res) => {
                    if (res.confirm) {
                        uni.removeStorageSync(config.tokenKey)
                        uni.removeStorageSync(config.userInfoKey)
                        
                        uni.showToast({
                            title: '已退出登录',
                            icon: 'success'
                        })
                        
                        setTimeout(() => {
                            uni.reLaunch({
                                url: '/pages/login/login'
                            })
                        }, 1000)
                    }
                }
            })
        }
    }
}
</script>

<style scoped>
.page-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 40rpx;
}

.user-header {
    display: flex;
    align-items: center;
    padding: 40rpx 30rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
}

.user-avatar {
    width: 120rpx;
    height: 120rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
}

.user-avatar text {
    font-size: 48rpx;
    color: #fff;
    font-weight: 500;
}

.user-info {
    display: flex;
    flex-direction: column;
}

.user-name {
    font-size: 36rpx;
    font-weight: 600;
    color: #fff;
    margin-bottom: 12rpx;
}

.role-tag {
    font-size: 22rpx;
    padding: 6rpx 20rpx;
    border-radius: 20rpx;
    align-self: flex-start;
}

.role-tag.admin {
    background: rgba(82, 196, 26, 0.3);
    color: #95de64;
}

.role-tag.purchaser {
    background: rgba(250, 173, 20, 0.3);
    color: #ffd591;
}

.user-info-card {
    background: #fff;
    margin: 20rpx;
    border-radius: 16rpx;
    overflow: hidden;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24rpx 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
    border-bottom: none;
}

.info-label {
    font-size: 28rpx;
    color: #999;
}

.info-value {
    font-size: 28rpx;
    color: #333;
}

.menu-section {
    background: #fff;
    margin: 20rpx;
    border-radius: 16rpx;
    overflow: hidden;
}

.section-title {
    font-size: 26rpx;
    color: #999;
    padding: 20rpx 30rpx;
    background: #fafafa;
}

.menu-list {
    padding: 0 30rpx;
}

.menu-item {
    display: flex;
    align-items: center;
    padding: 24rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
    border-bottom: none;
}

.menu-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 16rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
}

.menu-icon text {
    font-size: 40rpx;
    color: #fff;
}

.menu-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.menu-title {
    font-size: 30rpx;
    color: #333;
    margin-bottom: 6rpx;
}

.menu-desc {
    font-size: 24rpx;
    color: #999;
}

.menu-arrow {
    display: flex;
    align-items: center;
    position: relative;
}

.menu-arrow text {
    font-size: 28rpx;
    color: #999;
}

.badge {
    position: absolute;
    top: -12rpx;
    left: -40rpx;
    min-width: 36rpx;
    height: 36rpx;
    background: #ff4d4f;
    color: #fff;
    font-size: 20rpx;
    border-radius: 18rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 10rpx;
}

.logout-section {
    padding: 40rpx 30rpx;
}

.logout-btn {
    width: 100%;
    height: 88rpx;
    background: #fff;
    color: #ff4d4f;
    font-size: 32rpx;
    border-radius: 44rpx;
    border: 1rpx solid #ff4d4f;
}

.logout-btn::after {
    border: none;
}
</style>
