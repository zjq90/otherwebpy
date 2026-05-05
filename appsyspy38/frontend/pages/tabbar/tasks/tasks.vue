<template>
    <view class="tasks-container">
        <!-- 状态筛选标签 -->
        <view class="filter-tabs">
            <view 
                class="tab-item" 
                :class="{ active: activeTab === 'all' }"
                @click="activeTab = 'all'"
            >
                全部
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeTab === 'pending' }"
                @click="activeTab = 'pending'"
            >
                待处理
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeTab === 'executing' }"
                @click="activeTab = 'executing'"
            >
                进行中
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeTab === 'completed' }"
                @click="activeTab = 'completed'"
            >
                已完成
            </view>
        </view>

        <!-- 任务列表 -->
        <view class="tasks-list">
            <view class="task-card" v-for="task in filteredTasks" :key="task.id" @click="goToTaskDetail(task)">
                <view class="task-header">
                    <text class="task-title">{{ task.title }}</text>
                    <view class="status-tag" :class="`status-${task.status}`">
                        {{ getStatusText(task.status) }}
                    </view>
                </view>
                <view class="task-info">
                    <text class="task-desc">{{ task.description }}</text>
                </view>
                <view class="task-meta">
                    <view class="meta-item">
                        <text class="meta-icon">⏰</text>
                        <text class="meta-text">{{ task.deadline }}</text>
                    </view>
                    <view class="meta-item">
                        <text class="meta-icon">👤</text>
                        <text class="meta-text">{{ task.assignee }}</text>
                    </view>
                    <view class="meta-item" v-if="task.priority">
                        <text class="meta-icon">⚡</text>
                        <text class="meta-text" :class="`priority-${task.priority}`">{{ getPriorityText(task.priority) }}</text>
                    </view>
                </view>
            </view>

            <!-- 空状态 -->
            <view class="empty-state" v-if="filteredTasks.length === 0">
                <text class="empty-icon">📋</text>
                <text class="empty-text">暂无相关任务</text>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            activeTab: 'all',
            tasks: [
                {
                    id: 1,
                    title: '生产任务 #20240101',
                    description: 'C30混凝土，需求500方，搅拌站1号机',
                    status: 'pending',
                    deadline: '2024-01-15 14:00',
                    assignee: '张三',
                    priority: 'high'
                },
                {
                    id: 2,
                    title: '原料检验 - 水泥批次',
                    description: '华新水泥P.O42.5，批次20240101',
                    status: 'executing',
                    deadline: '2024-01-15 16:00',
                    assignee: '李四',
                    priority: 'medium'
                },
                {
                    id: 3,
                    title: '运输任务 #20240101',
                    description: '运往项目A，C30混凝土200方',
                    status: 'executing',
                    deadline: '2024-01-15 18:00',
                    assignee: '王五',
                    priority: 'high'
                },
                {
                    id: 4,
                    title: '采购申请审批',
                    description: '砂石采购申请，数量1000吨',
                    status: 'pending',
                    deadline: '2024-01-16 10:00',
                    assignee: '赵六',
                    priority: 'low'
                },
                {
                    id: 5,
                    title: '质量报告审核',
                    description: '2024年1月上旬质量报告',
                    status: 'completed',
                    deadline: '2024-01-10 17:00',
                    assignee: '钱七',
                    priority: 'medium'
                }
            ]
        }
    },
    computed: {
        filteredTasks() {
            if (this.activeTab === 'all') {
                return this.tasks
            }
            return this.tasks.filter(task => task.status === this.activeTab)
        }
    },
    methods: {
        getStatusText(status) {
            const map = {
                pending: '待处理',
                executing: '进行中',
                completed: '已完成'
            }
            return map[status] || status
        },
        getPriorityText(priority) {
            const map = {
                low: '低',
                medium: '中',
                high: '高'
            }
            return map[priority] || priority
        },
        goToTaskDetail(task) {
            uni.showToast({
                title: `查看: ${task.title}`,
                icon: 'none'
            })
        }
    }
}
</script>

<style scoped>
.tasks-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 120rpx;
}

/* 筛选标签 */
.filter-tabs {
    display: flex;
    background: #ffffff;
    padding: 0 20rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
    overflow-x: auto;
}

.tab-item {
    flex-shrink: 0;
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

/* 任务列表 */
.tasks-list {
    padding: 24rpx;
}

.task-card {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 28rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.task-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16rpx;
}

.task-title {
    font-size: 30rpx;
    font-weight: 500;
    color: #333333;
    flex: 1;
}

.task-info {
    margin-bottom: 20rpx;
}

.task-desc {
    font-size: 26rpx;
    color: #999999;
    line-height: 1.6;
}

.task-meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.meta-item {
    display: flex;
    align-items: center;
    margin-right: 32rpx;
    margin-bottom: 8rpx;
}

.meta-icon {
    font-size: 24rpx;
    margin-right: 8rpx;
}

.meta-text {
    font-size: 24rpx;
    color: #999999;
}

.meta-text.priority-high {
    color: #ff4d4f;
}

.meta-text.priority-medium {
    color: #faad14;
}

.meta-text.priority-low {
    color: #52c41a;
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
