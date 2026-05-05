<template>
    <view class="home-container">
        <!-- 顶部搜索栏 -->
        <view class="search-section">
            <view class="search-box">
                <text class="search-icon">🔍</text>
                <text class="search-placeholder">搜索功能、消息...</text>
            </view>
            <view class="notification-btn" @click="goToMessages">
                <text class="notification-icon">🔔</text>
                <view v-if="hasUnread" class="unread-dot"></view>
            </view>
        </view>

        <!-- 用户信息卡片 -->
        <view class="user-card" v-if="userInfo">
            <view class="user-info">
                <view class="user-avatar">
                    <text class="avatar-text">{{ userInfo.real_name ? userInfo.real_name.charAt(0) : '用' }}</text>
                </view>
                <view class="user-detail">
                    <text class="user-name">{{ userInfo.real_name || userInfo.username }}</text>
                    <view class="user-roles">
                        <text class="role-tag" v-for="role in userRoles" :key="role.id">{{ role.name }}</text>
                    </view>
                </view>
            </view>
            <view class="verify-status" v-if="userInfo.is_verified">
                <text class="verified-icon">✓</text>
                <text class="verified-text">已认证</text>
            </view>
        </view>

        <!-- 功能入口网格 -->
        <view class="function-section">
            <text class="section-title">功能入口</text>
            <view class="function-grid">
                <view 
                    class="function-item" 
                    v-for="item in functionList" 
                    :key="item.id"
                    @click="handleFunctionClick(item)"
                >
                    <view class="function-icon" :style="{ backgroundColor: item.color }">
                        <text class="icon-text">{{ item.icon }}</text>
                    </view>
                    <text class="function-name">{{ item.name }}</text>
                </view>
            </view>
        </view>

        <!-- 待办事项 -->
        <view class="todo-section">
            <view class="section-header">
                <text class="section-title">待办事项</text>
                <text class="section-more" @click="goToTasks">查看全部 ></text>
            </view>
            <view class="todo-list" v-if="todoList.length > 0">
                <view class="todo-item" v-for="item in todoList" :key="item.id" @click="handleTodoClick(item)">
                    <view class="todo-dot" :class="item.priority"></view>
                    <view class="todo-content">
                        <text class="todo-title">{{ item.title }}</text>
                        <text class="todo-desc">{{ item.description }}</text>
                    </view>
                    <text class="todo-time">{{ item.deadline }}</text>
                </view>
            </view>
            <view class="empty-state" v-else>
                <text class="empty-icon">📋</text>
                <text class="empty-text">暂无待办事项</text>
            </view>
        </view>

        <!-- 数据概览 -->
        <view class="overview-section">
            <text class="section-title">今日概览</text>
            <view class="overview-grid">
                <view class="overview-item" v-for="item in overviewList" :key="item.id">
                    <text class="overview-value">{{ item.value }}</text>
                    <text class="overview-label">{{ item.label }}</text>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
import { getCurrentUser } from '@/api/auth.js'

export default {
    data() {
        return {
            userInfo: null,
            userRoles: [],
            hasUnread: true,
            functionList: [],
            todoList: [],
            overviewList: [
                { id: 1, value: '12', label: '待处理任务' },
                { id: 2, value: '8', label: '今日完成' },
                { id: 3, value: '3', label: '待审批' },
                { id: 4, value: '95%', label: '完成率' }
            ]
        }
    },
    onLoad() {
        this.loadUserInfo()
        this.loadFunctionList()
        this.loadTodoList()
    },
    onShow() {
        // 每次显示页面时刷新用户信息
        this.loadUserInfo()
    },
    methods: {
        // 加载用户信息
        async loadUserInfo() {
            try {
                const userInfo = uni.getStorageSync('userInfo')
                if (userInfo) {
                    this.userInfo = userInfo
                    this.userRoles = userInfo.roles || []
                }
            } catch (err) {
                console.error('获取用户信息失败:', err)
            }
        },

        // 根据角色加载功能列表
        loadFunctionList() {
            const userInfo = uni.getStorageSync('userInfo')
            const roles = userInfo?.roles || []
            const roleCodes = roles.map(r => r.code)

            // 基础功能
            let baseFunctions = [
                { id: 'task', name: '我的任务', icon: '📋', color: '#1890ff', path: '/pages/tabbar/tasks/tasks' }
            ]

            // 根据角色添加对应功能
            if (roleCodes.includes('admin')) {
                baseFunctions = baseFunctions.concat([
                    { id: 'user-manage', name: '用户管理', icon: '👥', color: '#52c41a', path: '/pages/user-manage/user-manage' },
                    { id: 'role-manage', name: '角色管理', icon: '🔑', color: '#faad14', path: '/pages/role-manage/role-manage' },
                    { id: 'approval', name: '审批管理', icon: '✅', color: '#722ed1', path: '/pages/approval/approval' }
                ])
            }

            if (roleCodes.includes('operator') || roleCodes.includes('admin')) {
                baseFunctions = baseFunctions.concat([
                    { id: 'production', name: '生产任务', icon: '🏭', color: '#13c2c2', path: '/pages/production/production' },
                    { id: 'production-record', name: '生产记录', icon: '📝', color: '#eb2f96', path: '/pages/production-record/production-record' }
                ])
            }

            if (roleCodes.includes('tester') || roleCodes.includes('admin')) {
                baseFunctions = baseFunctions.concat([
                    { id: 'material-inspect', name: '原料检验', icon: '🔬', color: '#fa8c16', path: '/pages/material-inspect/material-inspect' },
                    { id: 'quality-report', name: '质量报告', icon: '📊', color: '#1890ff', path: '/pages/quality-report/quality-report' },
                    { id: 'quality-warning', name: '质量预警', icon: '⚠️', color: '#ff4d4f', path: '/pages/quality-warning/quality-warning' }
                ])
            }

            if (roleCodes.includes('purchaser') || roleCodes.includes('admin')) {
                baseFunctions = baseFunctions.concat([
                    { id: 'inventory', name: '库存管理', icon: '📦', color: '#52c41a', path: '/pages/inventory/inventory' },
                    { id: 'purchase-request', name: '采购申请', icon: '🛒', color: '#1890ff', path: '/pages/purchase-request/purchase-request' },
                    { id: 'supplier', name: '供应商管理', icon: '🏢', color: '#faad14', path: '/pages/supplier/supplier' }
                ])
            }

            if (roleCodes.includes('dispatcher') || roleCodes.includes('admin')) {
                baseFunctions = baseFunctions.concat([
                    { id: 'vehicle', name: '车辆管理', icon: '🚛', color: '#722ed1', path: '/pages/vehicle/vehicle' },
                    { id: 'transport-task', name: '运输任务', icon: '🚚', color: '#13c2c2', path: '/pages/transport-task/transport-task' }
                ])
            }

            this.functionList = baseFunctions
        },

        // 加载待办列表
        loadTodoList() {
            this.todoList = [
                { id: 1, title: '生产任务 #20240101', description: '待执行的搅拌任务', deadline: '14:00', priority: 'high' },
                { id: 2, title: '原料检验申请', description: '水泥批次检验待录入', deadline: '16:00', priority: 'medium' },
                { id: 3, title: '采购申请审批', description: '砂石采购申请待审批', deadline: '今天', priority: 'low' }
            ]
        },

        // 功能点击
        handleFunctionClick(item) {
            if (item.path) {
                uni.navigateTo({
                    url: item.path
                })
            } else {
                uni.showToast({
                    title: `${item.name}功能开发中`,
                    icon: 'none'
                })
            }
        },

        // 待办点击
        handleTodoClick(item) {
            uni.showToast({
                title: `查看: ${item.title}`,
                icon: 'none'
            })
        },

        // 跳转到消息页面
        goToMessages() {
            uni.switchTab({
                url: '/pages/tabbar/messages/messages'
            })
        },

        // 跳转到任务页面
        goToTasks() {
            uni.switchTab({
                url: '/pages/tabbar/tasks/tasks'
            })
        }
    }
}
</script>

<style scoped>
.home-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 120rpx;
}

/* 搜索栏 */
.search-section {
    display: flex;
    align-items: center;
    padding: 32rpx 40rpx;
    background: linear-gradient(180deg, #1890ff 0%, #40a9ff 100%);
}

.search-box {
    flex: 1;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 44rpx;
    padding: 16rpx 28rpx;
    margin-right: 24rpx;
}

.search-icon {
    font-size: 32rpx;
    margin-right: 16rpx;
}

.search-placeholder {
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.8);
}

.notification-btn {
    position: relative;
    width: 72rpx;
    height: 72rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
}

.notification-icon {
    font-size: 36rpx;
}

.unread-dot {
    position: absolute;
    top: 8rpx;
    right: 8rpx;
    width: 16rpx;
    height: 16rpx;
    background: #ff4d4f;
    border-radius: 50%;
}

/* 用户卡片 */
.user-card {
    background: #ffffff;
    border-radius: 24rpx;
    margin: -40rpx 40rpx 32rpx;
    padding: 32rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.user-info {
    display: flex;
    align-items: center;
}

.user-avatar {
    width: 96rpx;
    height: 96rpx;
    background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
}

.avatar-text {
    font-size: 40rpx;
    color: #ffffff;
    font-weight: 500;
}

.user-detail {
    display: flex;
    flex-direction: column;
}

.user-name {
    font-size: 32rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 12rpx;
}

.user-roles {
    display: flex;
    flex-wrap: wrap;
}

.role-tag {
    font-size: 22rpx;
    color: #1890ff;
    background: #e6f7ff;
    padding: 6rpx 16rpx;
    border-radius: 20rpx;
    margin-right: 12rpx;
}

.verify-status {
    display: flex;
    align-items: center;
    background: #f6ffed;
    padding: 8rpx 20rpx;
    border-radius: 20rpx;
}

.verified-icon {
    font-size: 20rpx;
    color: #52c41a;
    margin-right: 8rpx;
}

.verified-text {
    font-size: 24rpx;
    color: #52c41a;
}

/* 功能入口 */
.function-section {
    padding: 0 40rpx;
    margin-bottom: 32rpx;
}

.section-title {
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
    margin-bottom: 24rpx;
}

.function-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 24rpx;
}

.function-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.function-icon {
    width: 96rpx;
    height: 96rpx;
    border-radius: 24rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12rpx;
}

.icon-text {
    font-size: 44rpx;
}

.function-name {
    font-size: 24rpx;
    color: #666666;
}

/* 待办事项 */
.todo-section {
    padding: 0 40rpx;
    margin-bottom: 32rpx;
}

.section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 24rpx;
}

.section-more {
    font-size: 24rpx;
    color: #1890ff;
}

.todo-list {
    background: #ffffff;
    border-radius: 16rpx;
    overflow: hidden;
}

.todo-item {
    display: flex;
    align-items: center;
    padding: 24rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.todo-item:last-child {
    border-bottom: none;
}

.todo-dot {
    width: 12rpx;
    height: 12rpx;
    border-radius: 50%;
    margin-right: 20rpx;
}

.todo-dot.high {
    background: #ff4d4f;
}

.todo-dot.medium {
    background: #faad14;
}

.todo-dot.low {
    background: #52c41a;
}

.todo-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.todo-title {
    font-size: 28rpx;
    color: #333333;
    margin-bottom: 8rpx;
}

.todo-desc {
    font-size: 24rpx;
    color: #999999;
}

.todo-time {
    font-size: 24rpx;
    color: #faad14;
}

/* 数据概览 */
.overview-section {
    padding: 0 40rpx;
    margin-bottom: 32rpx;
}

.overview-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20rpx;
}

.overview-item {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 32rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.overview-value {
    font-size: 44rpx;
    font-weight: 600;
    color: #1890ff;
    margin-bottom: 8rpx;
}

.overview-label {
    font-size: 24rpx;
    color: #999999;
}

/* 空状态 */
.empty-state {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 60rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.empty-icon {
    font-size: 80rpx;
    margin-bottom: 20rpx;
}

.empty-text {
    font-size: 28rpx;
    color: #999999;
}
</style>
