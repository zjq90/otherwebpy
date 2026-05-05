<template>
    <view class="messages-container">
        <!-- 消息分类标签 -->
        <view class="category-tabs">
            <view 
                class="tab-item" 
                :class="{ active: activeCategory === 'all' }"
                @click="activeCategory = 'all'"
            >
                全部
                <text v-if="unreadCount > 0" class="badge">{{ unreadCount }}</text>
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeCategory === 'system' }"
                @click="activeCategory = 'system'"
            >
                系统通知
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeCategory === 'task' }"
                @click="activeCategory = 'task'"
            >
                任务通知
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeCategory === 'approval' }"
                @click="activeCategory = 'approval'"
            >
                审批通知
            </view>
        </view>

        <!-- 消息列表 -->
        <view class="messages-list">
            <view 
                class="message-item" 
                v-for="msg in filteredMessages" 
                :key="msg.id"
                :class="{ unread: !msg.is_read }"
                @click="handleMessageClick(msg)"
            >
                <view class="message-avatar" :style="{ backgroundColor: getAvatarColor(msg.type) }">
                    <text class="avatar-icon">{{ getAvatarIcon(msg.type) }}</text>
                </view>
                <view class="message-content">
                    <view class="message-header">
                        <text class="message-title">{{ msg.title }}</text>
                        <view v-if="!msg.is_read" class="unread-dot"></view>
                    </view>
                    <text class="message-desc">{{ msg.content }}</text>
                    <text class="message-time">{{ msg.create_time }}</text>
                </view>
            </view>

            <!-- 空状态 -->
            <view class="empty-state" v-if="filteredMessages.length === 0">
                <text class="empty-icon">🔔</text>
                <text class="empty-text">暂无消息</text>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            activeCategory: 'all',
            messages: [
                {
                    id: 1,
                    title: '新任务分配',
                    content: '您有一个新的生产任务待执行：生产任务 #20240101',
                    type: 'task',
                    is_read: false,
                    create_time: '2024-01-15 09:30'
                },
                {
                    id: 2,
                    title: '系统维护通知',
                    content: '系统将于今晚22:00进行维护，预计持续2小时，请提前保存数据。',
                    type: 'system',
                    is_read: false,
                    create_time: '2024-01-15 08:00'
                },
                {
                    id: 3,
                    title: '采购申请审批',
                    content: '您有一个采购申请待审批：砂石采购申请 #20240101',
                    type: 'approval',
                    is_read: false,
                    create_time: '2024-01-14 16:30'
                },
                {
                    id: 4,
                    title: '质量预警提醒',
                    content: '检测到原材料质量异常，请及时处理：水泥批次 #20240101',
                    type: 'system',
                    is_read: true,
                    create_time: '2024-01-14 14:20'
                },
                {
                    id: 5,
                    title: '任务完成通知',
                    content: '您分配的运输任务 #20240101 已完成，请注意查看。',
                    type: 'task',
                    is_read: true,
                    create_time: '2024-01-13 18:00'
                }
            ]
        }
    },
    computed: {
        unreadCount() {
            return this.messages.filter(m => !m.is_read).length
        },
        filteredMessages() {
            if (this.activeCategory === 'all') {
                return this.messages
            }
            return this.messages.filter(msg => msg.type === this.activeCategory)
        }
    },
    methods: {
        getAvatarColor(type) {
            const colors = {
                system: '#1890ff',
                task: '#52c41a',
                approval: '#faad14'
            }
            return colors[type] || '#1890ff'
        },
        getAvatarIcon(type) {
            const icons = {
                system: '⚙️',
                task: '📋',
                approval: '✅'
            }
            return icons[type] || '📧'
        },
        handleMessageClick(msg) {
            // 标记为已读
            msg.is_read = true
            uni.showToast({
                title: `查看: ${msg.title}`,
                icon: 'none'
            })
        }
    }
}
</script>

<style scoped>
.messages-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 120rpx;
}

/* 分类标签 */
.category-tabs {
    display: flex;
    background: #ffffff;
    padding: 0 20rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
    overflow-x: auto;
}

.tab-item {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    padding: 28rpx 32rpx;
    font-size: 28rpx;
    color: #666666;
    position: relative;
}

.tab-item.active {
    color: #1890ff;
    font-weight: 500;
}

.tab-item.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 48rpx;
    height: 6rpx;
    background: #1890ff;
    border-radius: 3rpx;
}

.badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 32rpx;
    height: 32rpx;
    padding: 0 8rpx;
    background: #ff4d4f;
    color: #ffffff;
    font-size: 20rpx;
    border-radius: 16rpx;
    margin-left: 8rpx;
}

/* 消息列表 */
.messages-list {
    padding: 24rpx;
}

.message-item {
    display: flex;
    background: #ffffff;
    border-radius: 16rpx;
    padding: 28rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.message-item.unread {
    background: #e6f7ff;
}

.message-avatar {
    width: 96rpx;
    height: 96rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
    flex-shrink: 0;
}

.avatar-icon {
    font-size: 44rpx;
}

.message-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.message-header {
    display: flex;
    align-items: center;
    margin-bottom: 12rpx;
}

.message-title {
    font-size: 30rpx;
    font-weight: 500;
    color: #333333;
    flex: 1;
}

.unread-dot {
    width: 16rpx;
    height: 16rpx;
    background: #ff4d4f;
    border-radius: 50%;
    margin-left: 12rpx;
}

.message-desc {
    font-size: 26rpx;
    color: #999999;
    line-height: 1.6;
    margin-bottom: 12rpx;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
}

.message-time {
    font-size: 22rpx;
    color: #999999;
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
}
</style>
