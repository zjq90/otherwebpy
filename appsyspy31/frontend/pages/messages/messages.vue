<template>
    <view class="messages-container">
        <view class="message-tabs">
            <view 
                class="tab-item" 
                v-for="tab in tabs" 
                :key="tab.value" 
                :class="{ 'active': currentTab === tab.value }"
                @click="switchTab(tab.value)"
            >
                <text class="tab-name">{{ tab.name }}</text>
                <view class="tab-badge" v-if="tab.count > 0">
                    <text>{{ tab.count > 99 ? '99+' : tab.count }}</text>
                </view>
            </view>
        </view>
        
        <view class="message-content">
            <view class="message-list" v-if="messageList.length > 0">
                <view 
                    class="message-item" 
                    v-for="item in messageList" 
                    :key="item.id"
                    :class="{ 'unread': !item.is_read }"
                    @click="openMessage(item)"
                >
                    <view class="message-icon" :class="item.message_type">
                        <text>{{ getMessageIcon(item.message_type) }}</text>
                    </view>
                    <view class="message-info">
                        <view class="message-header">
                            <text class="message-title">{{ item.title }}</text>
                            <text class="message-time">{{ formatTime(item.created_at) }}</text>
                        </view>
                        <view class="message-preview">
                            <text class="message-content-text">{{ item.content }}</text>
                        </view>
                    </view>
                    <view class="message-dot" v-if="!item.is_read"></view>
                </view>
            </view>
            
            <view class="empty-state" v-else>
                <text class="empty-icon">📭</text>
                <text class="empty-text">暂无{{ currentTabName }}消息</text>
            </view>
        </view>
        
        <view class="bottom-actions" v-if="messageList.length > 0">
            <view class="action-btn" @click="markAllAsRead">
                <text class="btn-icon">📖</text>
                <text class="btn-text">全部已读</text>
            </view>
            <view class="action-btn" @click="clearAll">
                <text class="btn-icon">🗑️</text>
                <text class="btn-text">清空消息</text>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref, computed, onShow } from 'vue'
import { messageApi } from '@/utils/api'
import { showLoading, hideLoading, showToast, showConfirm } from '@/utils'

const currentTab = ref('all')
const messageList = ref([])

const tabs = ref([
    { name: '全部', value: 'all', count: 0 },
    { name: '系统', value: 'system', count: 0 },
    { name: '课程', value: 'course', count: 0 },
    { name: '活动', value: 'activity', count: 0 },
])

const currentTabName = computed(() => {
    const tab = tabs.value.find(t => t.value === currentTab.value)
    return tab ? tab.name : ''
})

const getMessageIcon = (type) => {
    const icons = {
        system: '🔔',
        course: '📚',
        activity: '🎉',
        promotion: '🎁',
        service: '💼'
    }
    return icons[type] || '📩'
}

const formatTime = (time) => {
    if (!time) return ''
    const date = new Date(time)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return Math.floor(diff / 60000) + '分钟前'
    if (diff < 86400000) return Math.floor(diff / 3600000) + '小时前'
    if (diff < 604800000) return Math.floor(diff / 86400000) + '天前'
    
    return date.toLocaleDateString()
}

const switchTab = (value) => {
    currentTab.value = value
    fetchMessages()
}

const fetchMessages = async () => {
    try {
        showLoading('加载中...')
        const params = {
            page: 1,
            size: 50
        }
        if (currentTab.value !== 'all') {
            params.message_type = currentTab.value
        }
        
        const res = await messageApi.getList(params)
        if (res.code === 200) {
            messageList.value = res.data.items || []
        }
    } catch (error) {
        console.error('获取消息列表失败:', error)
    } finally {
        hideLoading()
    }
}

const fetchUnreadCounts = async () => {
    try {
        const res = await messageApi.getUnreadCount()
        if (res.code === 200) {
            tabs.value[0].count = res.data.total || 0
        }
    } catch (error) {
        console.error('获取未读数量失败:', error)
    }
}

const openMessage = async (item) => {
    try {
        if (!item.is_read) {
            await messageApi.markAsRead(item.id)
            item.is_read = true
            tabs.value[0].count = Math.max(0, tabs.value[0].count - 1)
        }
    } catch (error) {
        console.error('标记已读失败:', error)
    }
}

const markAllAsRead = async () => {
    try {
        const ids = messageList.value.filter(item => !item.is_read).map(item => item.id)
        if (ids.length === 0) {
            showToast('没有未读消息')
            return
        }
        
        await messageApi.markBatchAsRead({ message_ids: ids })
        messageList.value.forEach(item => {
            item.is_read = true
        })
        tabs.value[0].count = 0
        showToast('已全部标记为已读', 'success')
    } catch (error) {
        console.error('批量标记已读失败:', error)
    }
}

const clearAll = async () => {
    const confirmed = await showConfirm('确定要清空所有消息吗？')
    if (confirmed) {
        showToast('清空成功', 'success')
        messageList.value = []
    }
}

onShow(() => {
    fetchMessages()
    fetchUnreadCounts()
})
</script>

<style lang="scss" scoped>
.messages-container {
    min-height: 100vh;
    background: $bg-color;
}

.message-tabs {
    display: flex;
    background: #ffffff;
    padding: 20rpx 30rpx;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.tab-item {
    position: relative;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16rpx 0;
}

.tab-name {
    font-size: 28rpx;
    color: #666666;
    font-weight: 400;
}

.tab-item.active .tab-name {
    color: $primary-color;
    font-weight: 500;
}

.tab-badge {
    position: absolute;
    top: 8rpx;
    right: 20rpx;
    min-width: 28rpx;
    height: 28rpx;
    background: $danger-color;
    border-radius: 14rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 6rpx;
    
    text {
        font-size: 20rpx;
        color: #ffffff;
    }
}

.message-content {
    padding: 20rpx;
}

.message-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
}

.message-item {
    display: flex;
    align-items: center;
    background: #ffffff;
    border-radius: 16rpx;
    padding: 24rpx;
    position: relative;
}

.message-item.unread {
    background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.message-icon {
    width: 88rpx;
    height: 88rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
    flex-shrink: 0;
    
    text {
        font-size: 40rpx;
    }
}

.message-icon.system {
    background: rgba(102, 126, 234, 0.1);
}

.message-icon.course {
    background: rgba(240, 147, 251, 0.1);
}

.message-icon.activity {
    background: rgba(250, 112, 154, 0.1);
}

.message-icon.promotion {
    background: rgba(250, 225, 64, 0.1);
}

.message-info {
    flex: 1;
    min-width: 0;
}

.message-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10rpx;
}

.message-title {
    font-size: 28rpx;
    font-weight: 500;
    color: #333333;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 400rpx;
}

.message-time {
    font-size: 22rpx;
    color: #999999;
    flex-shrink: 0;
    margin-left: 16rpx;
}

.message-preview {
    overflow: hidden;
}

.message-content-text {
    font-size: 24rpx;
    color: #666666;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.message-dot {
    width: 16rpx;
    height: 16rpx;
    background: $danger-color;
    border-radius: 50%;
    margin-left: 16rpx;
    flex-shrink: 0;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 120rpx 0;
}

.empty-icon {
    font-size: 120rpx;
    margin-bottom: 30rpx;
}

.empty-text {
    font-size: 28rpx;
    color: #999999;
}

.bottom-actions {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    background: #ffffff;
    padding: 20rpx 30rpx;
    padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
    box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20rpx 0;
    border-radius: 12rpx;
}

.action-btn:first-child {
    margin-right: 20rpx;
    background: rgba(102, 126, 234, 0.1);
}

.action-btn:last-child {
    background: rgba(255, 71, 87, 0.1);
}

.btn-icon {
    font-size: 32rpx;
    margin-right: 10rpx;
}

.btn-text {
    font-size: 26rpx;
    color: #333333;
}
</style>
