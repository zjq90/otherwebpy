<template>
	<view class="container">
		<!-- 统计概览 -->
		<view class="stats-card">
			<view class="stats-row">
				<view class="stat-item" @click="filterByStatus('all')">
					<text class="stat-value">{{ safeTotal }}</text>
					<text class="stat-label">全部任务</text>
				</view>
				<view class="stat-item pending" @click="filterByStatus('pending')">
					<text class="stat-value">{{ safePendingCount }}</text>
					<text class="stat-label">待处理</text>
				</view>
				<view class="stat-item overdue" @click="filterByStatus('overdue')">
					<text class="stat-value">{{ safeOverdueCount }}</text>
					<text class="stat-label">已超期</text>
				</view>
				<view class="stat-item completed" @click="filterByStatus('completed')">
					<text class="stat-value">{{ safeCompletedCount }}</text>
					<text class="stat-label">已完成</text>
				</view>
			</view>
		</view>
		
		<!-- 筛选栏 -->
		<view class="filter-section">
			<view 
				v-for="(filter, index) in filterOptions" 
				:key="index"
				class="filter-item"
				:class="{ 'active': currentStatus === filter.value }"
				@click="handleStatusFilter(filter.value)"
			>
				<text class="filter-text">{{ filter.label }}</text>
			</view>
		</view>
		
		<!-- 即将到期提醒 -->
		<view class="upcoming-section" v-if="upcomingTasks.length > 0">
			<view class="section-header">
				<text class="section-title">⚠️ 即将到期提醒</text>
			</view>
			<view class="upcoming-list">
				<view 
					v-for="(task, index) in upcomingTasks" 
					:key="task.id"
					class="upcoming-item"
					:class="{ 'overdue': task.status === 'overdue' }"
					@click="goToDetail(task.id)"
				>
					<view class="upcoming-left">
						<text class="device-name">{{ task.device_name }}</text>
						<text class="task-name">{{ task.task_name }}</text>
					</view>
					<view class="upcoming-right">
						<text class="progress-text">{{ task.total_running_hours }}/{{ task.next_maintenance_hours }}h</text>
						<text class="status-text" :class="utils.getStatusClass(task.status)">
							{{ utils.getStatusName(task.status) }}
						</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 任务列表 -->
		<view class="task-list" v-if="taskList.length > 0">
			<view 
				v-for="(task, index) in taskList" 
				:key="task.id"
				class="task-card"
				:class="{ 
					'overdue-card': task.status === 'overdue',
					'pending-card': task.status === 'pending',
					'completed-card': task.status === 'completed'
				}"
				@click="goToDetail(task.id)"
			>
				<view class="card-header">
					<view class="task-info">
						<view class="device-icon" :class="`priority-${task.priority}`">
							<text class="icon-text">{{ getPriorityIcon(task.priority) }}</text>
						</view>
						<view class="info-text">
							<text class="device-name">{{ task.device_name || '设备' }}</text>
							<text class="task-name">{{ task.task_name }}</text>
						</view>
					</view>
					<view class="status-badge">
						<text class="badge-text" :class="utils.getStatusClass(task.status)">
							{{ utils.getStatusName(task.status) }}
						</text>
					</view>
				</view>
				
				<view class="card-body">
					<view class="info-row" v-if="task.task_description">
						<text class="info-label">任务描述:</text>
						<text class="info-value">{{ task.task_description }}</text>
					</view>
					<view class="info-row">
						<text class="info-label">保养周期:</text>
						<text class="info-value">{{ task.maintenance_cycle_hours }}小时</text>
					</view>
					<view class="progress-section">
						<view class="progress-label">
							<text>运行进度: {{ task.last_maintenance_hours || 0 }}h → {{ task.next_maintenance_hours || 0 }}h</text>
						</view>
						<view class="progress-bar">
							<view 
								class="progress-fill"
								:class="{ 'warning': getProgressPercent(task) > 80, 'danger': getProgressPercent(task) > 100 }"
								:style="{ width: getProgressPercent(task) + '%' }"
							></view>
						</view>
					</view>
				</view>
				
				<view class="card-footer">
					<text class="device-code">{{ task.device_code }}</text>
					<text class="priority-tag" :class="utils.getPriorityClass(task.priority)">
						优先级: {{ utils.getPriorityName(task.priority) }}
					</text>
				</view>
			</view>
		</view>
		
		<!-- 空状态 -->
		<view class="empty-state" v-else-if="!loading">
			<text class="empty-icon">🔧</text>
			<text class="empty-text">暂无保养任务</text>
			<text class="empty-tip">系统将根据设备运行时长自动生成保养提醒</text>
		</view>
		
		<!-- 加载中 -->
		<view class="loading-state" v-if="loading">
			<text class="loading-text">加载中...</text>
		</view>
		
		<!-- 加载更多 -->
		<view class="load-more" v-if="!loading && hasMore">
			<text class="load-more-text" @click="loadMoreData">加载更多</text>
		</view>
	</view>
</template>

<script>
import api from '@/api/index.js'
import utils from '@/utils/index.js'

export default {
	data() {
		return {
			utils,
			maintenanceStats: {},
			upcomingTasks: [],
			taskList: [],
			currentStatus: 'all',
			loading: false,
			page: 1,
			pageSize: 10,
			hasMore: true,
			filterOptions: [
				{ label: '全部', value: 'all' },
				{ label: '待处理', value: 'pending' },
				{ label: '已超期', value: 'overdue' },
				{ label: '已完成', value: 'completed' }
			]
		}
	},
	
	computed: {
		safeTotal() {
			return (this.maintenanceStats && this.maintenanceStats.statistics && this.maintenanceStats.statistics.total) || 0
		},
		
		safePendingCount() {
			return (this.maintenanceStats && this.maintenanceStats.statistics && this.maintenanceStats.statistics.pending_count) || 0
		},
		
		safeOverdueCount() {
			return (this.maintenanceStats && this.maintenanceStats.statistics && this.maintenanceStats.statistics.overdue_count) || 0
		},
		
		safeCompletedCount() {
			return (this.maintenanceStats && this.maintenanceStats.statistics && this.maintenanceStats.statistics.completed_count) || 0
		}
	},
	
	onLoad() {
		this.loadData()
	},
	
	onShow() {
		this.loadData()
	},
	
	onPullDownRefresh() {
		this.page = 1
		this.hasMore = true
		this.loadData().finally(() => {
			uni.stopPullDownRefresh()
		})
	},
	
	onReachBottom() {
		if (this.hasMore && !this.loading) {
			this.loadMoreData()
		}
	},
	
	methods: {
		/**
		 * 加载数据
		 */
		async loadData() {
			this.loading = true
			
			try {
				// 加载统计数据
				const statsRes = await api.maintenance.getOverview()
				if (statsRes.code === 200) {
					this.maintenanceStats = statsRes.data
					this.upcomingTasks = statsRes.data?.upcoming_tasks || []
				}
				
				// 加载任务列表
				await this.loadTaskList()
			} catch (err) {
				console.error('加载数据失败:', err)
			} finally {
				this.loading = false
			}
		},
		
		/**
		 * 加载任务列表
		 */
		async loadTaskList() {
			const params = {
				page: this.page,
				page_size: this.pageSize
			}
			
			if (this.currentStatus !== 'all') {
				params.status = this.currentStatus
			}
			
			try {
				const res = await api.maintenance.getTaskList(params)
				
				if (res.code === 200) {
					if (this.page === 1) {
						this.taskList = res.data?.items || []
					} else {
						this.taskList = [...this.taskList, ...(res.data?.items || [])]
					}
					
					this.hasMore = this.page < (res.total_pages || 1)
				}
			} catch (err) {
				console.error('加载任务列表失败:', err)
			}
		},
		
		/**
		 * 加载更多
		 */
		loadMoreData() {
			this.page++
			this.loadTaskList()
		},
		
		/**
		 * 按状态筛选
		 */
		filterByStatus(status) {
			this.currentStatus = status
			this.page = 1
			this.hasMore = true
			this.loadTaskList()
		},
		
		/**
		 * 状态筛选变化
		 */
		handleStatusFilter(value) {
			if (this.currentStatus !== value) {
				this.currentStatus = value
				this.page = 1
				this.hasMore = true
				this.loadTaskList()
			}
		},
		
		/**
		 * 获取进度百分比
		 */
		getProgressPercent(task) {
			if (!task.next_maintenance_hours) return 0
			const current = task.last_maintenance_hours || 0
			const next = task.next_maintenance_hours
			return Math.min((current / next) * 100, 150)
		},
		
		/**
		 * 获取优先级图标
		 */
		getPriorityIcon(priority) {
			const iconMap = {
				'high': '🔴',
				'medium': '🟡',
				'low': '🟢'
			}
			return iconMap[priority] || '⚙️'
		},
		
		/**
		 * 跳转到详情页
		 */
		goToDetail(taskId) {
			uni.navigateTo({
				url: `/pages/maintenance/task-detail?id=${taskId}`
			})
		}
	}
}
</script>

<style scoped>
.container {
	padding: 24rpx;
	background-color: #f5f5f5;
	min-height: 100vh;
}

/* 统计卡片 */
.stats-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
}

.stats-row {
	display: flex;
	justify-content: space-between;
}

.stat-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 16rpx 8rpx;
	border-radius: 12rpx;
	transition: background-color 0.3s;
}

.stat-item:active {
	background-color: #f5f5f5;
}

.stat-value {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 8rpx;
}

.stat-label {
	font-size: 22rpx;
	color: #999;
}

.stat-item.pending .stat-value {
	color: #faad14;
}

.stat-item.overdue .stat-value {
	color: #ff4d4f;
}

.stat-item.completed .stat-value {
	color: #52c41a;
}

/* 筛选栏 */
.filter-section {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 16rpx 24rpx;
	margin-bottom: 24rpx;
	display: flex;
	gap: 16rpx;
	overflow-x: auto;
}

.filter-item {
	flex-shrink: 0;
	padding: 12rpx 28rpx;
	border-radius: 32rpx;
	background-color: #f5f5f5;
}

.filter-item.active {
	background-color: #e6f7ff;
}

.filter-text {
	font-size: 26rpx;
	color: #666;
}

.filter-item.active .filter-text {
	color: #1677ff;
	font-weight: 500;
}

/* 即将到期提醒 */
.upcoming-section {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
}

.section-header {
	margin-bottom: 16rpx;
}

.section-title {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
}

.upcoming-list {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.upcoming-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16rpx;
	background-color: #fffbe6;
	border-radius: 12rpx;
	border-left: 4rpx solid #faad14;
}

.upcoming-item.overdue {
	background-color: #fff2f0;
	border-left-color: #ff4d4f;
}

.upcoming-left {
	display: flex;
	flex-direction: column;
}

.device-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 4rpx;
}

.task-name {
	font-size: 24rpx;
	color: #666;
}

.upcoming-right {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
}

.progress-text {
	font-size: 24rpx;
	color: #666;
	margin-bottom: 4rpx;
}

.status-text {
	font-size: 22rpx;
	padding: 2rpx 8rpx;
	border-radius: 4rpx;
}

/* 任务列表 */
.task-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.task-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
}

.task-card.overdue-card {
	border-left: 6rpx solid #ff4d4f;
	background-color: #fffbfb;
}

.task-card.pending-card {
	border-left: 6rpx solid #faad14;
}

.task-card.completed-card {
	border-left: 6rpx solid #52c41a;
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 16rpx;
}

.task-info {
	display: flex;
	align-items: center;
	flex: 1;
}

.device-icon {
	width: 72rpx;
	height: 72rpx;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.device-icon.priority-high {
	background-color: #fff2f0;
}

.device-icon.priority-medium {
	background-color: #fffbe6;
}

.device-icon.priority-low {
	background-color: #f6ffed;
}

.icon-text {
	font-size: 32rpx;
}

.info-text {
	display: flex;
	flex-direction: column;
}

.task-name {
	font-size: 26rpx;
	color: #666;
}

.status-badge {
	margin-left: 16rpx;
}

.badge-text {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 6rpx;
}

/* 卡片主体 */
.card-body {
	margin-bottom: 16rpx;
}

.info-row {
	display: flex;
	margin-bottom: 8rpx;
}

.info-label {
	font-size: 24rpx;
	color: #999;
	width: 120rpx;
	flex-shrink: 0;
}

.info-value {
	font-size: 24rpx;
	color: #333;
	flex: 1;
}

.progress-section {
	margin-top: 12rpx;
}

.progress-label {
	margin-bottom: 8rpx;
}

.progress-label text {
	font-size: 22rpx;
	color: #999;
}

.progress-bar {
	height: 12rpx;
	background-color: #f0f0f0;
	border-radius: 6rpx;
	overflow: hidden;
}

.progress-fill {
	height: 100%;
	background-color: #52c41a;
	border-radius: 6rpx;
	transition: width 0.3s;
}

.progress-fill.warning {
	background-color: #faad14;
}

.progress-fill.danger {
	background-color: #ff4d4f;
}

/* 卡片底部 */
.card-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding-top: 16rpx;
	border-top: 1rpx solid #f0f0f0;
}

.device-code {
	font-size: 22rpx;
	color: #999;
}

.priority-tag {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 6rpx;
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
	font-size: 30rpx;
	color: #666;
	margin-bottom: 16rpx;
}

.empty-tip {
	font-size: 26rpx;
	color: #999;
}

/* 加载中 */
.loading-state {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 50rpx 0;
}

.loading-text {
	font-size: 28rpx;
	color: #999;
}

/* 加载更多 */
.load-more {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 32rpx 0;
}

.load-more-text {
	font-size: 28rpx;
	color: #1677ff;
}
</style>
