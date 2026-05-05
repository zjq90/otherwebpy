<template>
    <view class="production-container">
        <!-- 顶部操作栏 -->
        <view class="header-section">
            <view class="search-box">
                <text class="search-icon">🔍</text>
                <input 
                    class="search-input" 
                    placeholder="搜索任务编号..."
                    v-model="searchKeyword"
                    @confirm="handleSearch"
                />
            </view>
            <view class="add-btn" @click="goToAdd">
                <text class="add-icon">+</text>
            </view>
        </view>

        <!-- 状态筛选 -->
        <view class="filter-tabs">
            <view 
                class="tab-item" 
                :class="{ active: activeStatus === 'all' }"
                @click="activeStatus = 'all'"
            >
                全部
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeStatus === 'pending' }"
                @click="activeStatus = 'pending'"
            >
                待执行
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeStatus === 'executing' }"
                @click="activeStatus = 'executing'"
            >
                进行中
            </view>
            <view 
                class="tab-item" 
                :class="{ active: activeStatus === 'completed' }"
                @click="activeStatus = 'completed'"
            >
                已完成
            </view>
        </view>

        <!-- 任务列表 -->
        <view class="task-list">
            <view 
                class="task-card" 
                v-for="task in filteredTasks" 
                :key="task.id"
                @click="goToDetail(task)"
            >
                <view class="task-header">
                    <text class="task-code">{{ task.task_code }}</text>
                    <view class="status-tag" :class="`status-${task.status}`">
                        {{ getStatusText(task.status) }}
                    </view>
                </view>
                
                <view class="task-info">
                    <view class="info-row">
                        <text class="info-label">混凝土类型：</text>
                        <text class="info-value">{{ task.concrete_type }}</text>
                    </view>
                    <view class="info-row">
                        <text class="info-label">计划方量：</text>
                        <text class="info-value">{{ task.planned_volume }} m³</text>
                    </view>
                    <view class="info-row" v-if="task.actual_volume">
                        <text class="info-label">实际方量：</text>
                        <text class="info-value">{{ task.actual_volume }} m³</text>
                    </view>
                    <view class="info-row">
                        <text class="info-label">项目名称：</text>
                        <text class="info-value">{{ task.project_name }}</text>
                    </view>
                    <view class="info-row">
                        <text class="info-label">任务描述：</text>
                        <text class="info-value">{{ task.description || '无' }}</text>
                    </view>
                </view>

                <view class="task-footer">
                    <view class="footer-left">
                        <text class="time-label">计划时间：</text>
                        <text class="time-value">{{ task.planned_start_time || '-' }}</text>
                    </view>
                    <view class="footer-right" v-if="task.status === 'pending'">
                        <view class="action-btn start-btn" @click.stop="startTask(task)">
                            开始生产
                        </view>
                    </view>
                    <view class="footer-right" v-else-if="task.status === 'executing'">
                        <view class="action-btn record-btn" @click.stop="submitRecord(task)">
                            提交记录
                        </view>
                        <view class="action-btn complete-btn" @click.stop="completeTask(task)">
                            完成
                        </view>
                    </view>
                </view>
            </view>

            <!-- 空状态 -->
            <view class="empty-state" v-if="filteredTasks.length === 0">
                <text class="empty-icon">🏭</text>
                <text class="empty-text">暂无生产任务</text>
            </view>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            searchKeyword: '',
            activeStatus: 'all',
            tasks: [
                {
                    id: 1,
                    task_code: 'PT20240115001',
                    concrete_type: 'C30',
                    planned_volume: 500,
                    actual_volume: 0,
                    project_name: '城东小区建设项目',
                    description: '主体结构混凝土供应',
                    status: 'pending',
                    planned_start_time: '2024-01-15 14:00',
                    operator_id: 2
                },
                {
                    id: 2,
                    task_code: 'PT20240115002',
                    concrete_type: 'C25',
                    planned_volume: 300,
                    actual_volume: 150,
                    project_name: '市政道路改造工程',
                    description: '路面浇筑混凝土',
                    status: 'executing',
                    planned_start_time: '2024-01-15 09:00',
                    operator_id: 2
                },
                {
                    id: 3,
                    task_code: 'PT20240114001',
                    concrete_type: 'C35',
                    planned_volume: 800,
                    actual_volume: 800,
                    project_name: '商业中心建设项目',
                    description: '地下室浇筑',
                    status: 'completed',
                    planned_start_time: '2024-01-14 08:00',
                    completed_time: '2024-01-14 18:30',
                    operator_id: 2
                }
            ]
        }
    },
    computed: {
        filteredTasks() {
            let result = this.tasks
            
            // 状态筛选
            if (this.activeStatus !== 'all') {
                result = result.filter(t => t.status === this.activeStatus)
            }
            
            // 关键词搜索
            if (this.searchKeyword) {
                result = result.filter(t => 
                    t.task_code.toLowerCase().includes(this.searchKeyword.toLowerCase()) ||
                    t.project_name.toLowerCase().includes(this.searchKeyword.toLowerCase())
                )
            }
            
            return result
        }
    },
    methods: {
        getStatusText(status) {
            const map = {
                pending: '待执行',
                executing: '进行中',
                completed: '已完成'
            }
            return map[status] || status
        },
        
        handleSearch() {
            // 搜索逻辑已在computed中处理
        },
        
        goToAdd() {
            uni.showToast({
                title: '新建任务功能开发中',
                icon: 'none'
            })
        },
        
        goToDetail(task) {
            uni.showToast({
                title: `查看任务: ${task.task_code}`,
                icon: 'none'
            })
        },
        
        startTask(task) {
            uni.showModal({
                title: '确认',
                content: `确定要开始生产任务 ${task.task_code} 吗？`,
                success: (res) => {
                    if (res.confirm) {
                        task.status = 'executing'
                        uni.showToast({
                            title: '任务已开始',
                            icon: 'success'
                        })
                    }
                }
            })
        },
        
        submitRecord(task) {
            uni.showToast({
                title: '提交生产记录功能开发中',
                icon: 'none'
            })
        },
        
        completeTask(task) {
            uni.showModal({
                title: '确认',
                content: `确定要完成生产任务 ${task.task_code} 吗？`,
                success: (res) => {
                    if (res.confirm) {
                        task.status = 'completed'
                        task.actual_volume = task.planned_volume
                        uni.showToast({
                            title: '任务已完成',
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
.production-container {
    min-height: 100vh;
    background-color: #f5f5f5;
}

/* 顶部操作栏 */
.header-section {
    display: flex;
    align-items: center;
    padding: 20rpx;
    background: #ffffff;
}

.search-box {
    flex: 1;
    display: flex;
    align-items: center;
    background: #f5f5f5;
    border-radius: 40rpx;
    padding: 16rpx 24rpx;
    margin-right: 20rpx;
}

.search-icon {
    font-size: 28rpx;
    margin-right: 12rpx;
}

.search-input {
    flex: 1;
    font-size: 28rpx;
    color: #333333;
}

.add-btn {
    width: 72rpx;
    height: 72rpx;
    background: #1890ff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.add-icon {
    font-size: 40rpx;
    color: #ffffff;
    font-weight: 300;
}

/* 状态筛选 */
.filter-tabs {
    display: flex;
    background: #ffffff;
    padding: 0 20rpx;
    margin-top: 2rpx;
    overflow-x: auto;
}

.tab-item {
    flex-shrink: 0;
    padding: 24rpx 32rpx;
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
.task-list {
    padding: 20rpx;
}

.task-card {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.04);
}

.task-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 20rpx;
}

.task-code {
    font-size: 30rpx;
    font-weight: 600;
    color: #333333;
}

.task-info {
    background: #fafafa;
    border-radius: 12rpx;
    padding: 16rpx 20rpx;
    margin-bottom: 20rpx;
}

.info-row {
    display: flex;
    align-items: flex-start;
    margin-bottom: 12rpx;
}

.info-row:last-child {
    margin-bottom: 0;
}

.info-label {
    font-size: 26rpx;
    color: #999999;
    width: 160rpx;
    flex-shrink: 0;
}

.info-value {
    font-size: 26rpx;
    color: #333333;
    flex: 1;
}

.task-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 16rpx;
    border-top: 1rpx solid #f0f0f0;
}

.footer-left {
    display: flex;
    align-items: center;
}

.time-label {
    font-size: 24rpx;
    color: #999999;
}

.time-value {
    font-size: 24rpx;
    color: #333333;
}

.footer-right {
    display: flex;
    align-items: center;
}

.action-btn {
    padding: 12rpx 24rpx;
    border-radius: 8rpx;
    font-size: 26rpx;
    margin-left: 16rpx;
}

.start-btn {
    background: #1890ff;
    color: #ffffff;
}

.record-btn {
    background: #13c2c2;
    color: #ffffff;
}

.complete-btn {
    background: #52c41a;
    color: #ffffff;
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
