<template>
	<view class="container">
		<!-- 任务状态头部 -->
		<view class="status-header" :class="`status-${taskData.status}`">
			<view class="status-icon">
				<text class="icon-text">{{ getStatusIcon(taskData.status) }}</text>
			</view>
			<view class="status-info">
				<text class="status-text" :class="utils.getStatusClass(taskData.status)">
					{{ utils.getStatusName(taskData.status) }}
				</text>
				<text class="task-name">{{ taskData.task_name }}</text>
			</view>
		</view>
		
		<!-- 设备信息 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">设备信息</text>
			</view>
			<view class="device-info-card">
				<view class="device-icon-wrapper">
					<text class="device-icon">🏭</text>
				</view>
				<view class="device-detail">
					<text class="device-name">{{ taskData.device_name || '-' }}</text>
					<text class="device-code">编号: {{ taskData.device_code || '-' }}</text>
					<text class="running-hours">运行时长: {{ taskData.total_running_hours || 0 }}小时</text>
				</view>
			</view>
		</view>
		
		<!-- 任务信息 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">任务信息</text>
				<view class="priority-badge" :class="utils.getPriorityClass(taskData.priority)">
					<text>{{ utils.getPriorityName(taskData.priority) }}优先级</text>
				</view>
			</view>
			<view class="info-list">
				<view class="info-item">
					<text class="info-label">保养周期</text>
					<text class="info-value">{{ taskData.maintenance_cycle_hours || 0 }}小时</text>
				</view>
				<view class="info-item">
					<text class="info-label">上次保养时长</text>
					<text class="info-value">{{ taskData.last_maintenance_hours || 0 }}小时</text>
				</view>
				<view class="info-item">
					<text class="info-label">下次保养时长</text>
					<text class="info-value highlight">{{ taskData.next_maintenance_hours || 0 }}小时</text>
				</view>
				<view class="info-item">
					<text class="info-label">当前进度</text>
					<view class="progress-wrapper">
						<view class="progress-bar">
							<view 
								class="progress-fill"
								:class="{ 'warning': progressPercent > 80, 'danger': progressPercent > 100 }"
								:style="{ width: progressPercent + '%' }"
							></view>
						</view>
						<text class="progress-text">{{ progressPercent }}%</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 操作指南 -->
		<view class="section-card" v-if="taskData.operation_guide">
			<view class="section-header">
				<text class="section-title">📋 操作指南</text>
			</view>
			<view class="guide-content">
				<text class="guide-text">{{ taskData.operation_guide }}</text>
			</view>
		</view>
		
		<!-- 任务描述 -->
		<view class="section-card" v-if="taskData.task_description">
			<view class="section-header">
				<text class="section-title">📝 任务描述</text>
			</view>
			<view class="description-content">
				<text class="description-text">{{ taskData.task_description }}</text>
			</view>
		</view>
		
		<!-- 操作按钮 -->
		<view class="action-section" v-if="taskData.status !== 'completed'">
			<button class="action-btn btn-primary" @click="goToRecordForm">
				<text class="btn-text">🔧 填写保养记录</text>
			</button>
		</view>
		
		<!-- 已完成提示 -->
		<view class="completed-section" v-else>
			<view class="completed-icon">
				<text class="icon-text">✅</text>
			</view>
			<text class="completed-text">该保养任务已完成</text>
		</view>
		
		<!-- 加载中 -->
		<view class="loading-state" v-if="loading">
			<text class="loading-text">加载中...</text>
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
			taskId: null,
			taskData: {},
			loading: false
		}
	},
	
	computed: {
		progressPercent() {
			if (!this.taskData.next_maintenance_hours) return 0
			const current = this.taskData.total_running_hours || 0
			const next = this.taskData.next_maintenance_hours
			return Math.min(Math.round((current / next) * 100), 150)
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.taskId = parseInt(options.id)
			this.loadTaskDetail()
		}
	},
	
	onShow() {
		if (this.taskId) {
			this.loadTaskDetail()
		}
	},
	
	methods: {
		/**
		 * 加载任务详情
		 */
		async loadTaskDetail() {
			if (!this.taskId) return
			
			this.loading = true
			
			try {
				const res = await api.maintenance.getTaskDetail(this.taskId)
				
				if (res.code === 200) {
					this.taskData = res.data || {}
				}
			} catch (err) {
				console.error('加载任务详情失败:', err)
				utils.showError('加载失败')
			} finally {
				this.loading = false
			}
		},
		
		/**
		 * 获取状态图标
		 */
		getStatusIcon(status) {
			const iconMap = {
				'pending': '⏳',
				'overdue': '⚠️',
				'processing': '🔄',
				'completed': '✅'
			}
			return iconMap[status] || '📋'
		},
		
		/**
		 * 跳转到保养记录表单
		 */
		goToRecordForm() {
			uni.navigateTo({
				url: `/pages/maintenance/record-form?taskId=${this.taskId}&deviceId=${this.taskData.device_id}`
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
	padding-bottom: 180rpx;
}

/* 状态头部 */
.status-header {
	display: flex;
	align-items: center;
	padding: 32rpx;
	border-radius: 16rpx;
	margin-bottom: 24rpx;
}

.status-header.status-pending {
	background: linear-gradient(135deg, #fffbe6 0%, #ffe58f 100%);
}

.status-header.status-overdue {
	background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
}

.status-header.status-processing {
	background: linear-gradient(135deg, #e6f7ff 0%, #91d5ff 100%);
}

.status-header.status-completed {
	background: linear-gradient(135deg, #f6ffed 0%, #b7eb8f 100%);
}

.status-icon {
	width: 96rpx;
	height: 96rpx;
	border-radius: 50%;
	background-color: rgba(255, 255, 255, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.icon-text {
	font-size: 48rpx;
}

.status-info {
	display: flex;
	flex-direction: column;
	flex: 1;
}

.status-text {
	font-size: 24rpx;
	padding: 4rpx 16rpx;
	border-radius: 4rpx;
	margin-bottom: 8rpx;
	width: fit-content;
}

.task-name {
	font-size: 32rpx;
	font-weight: 500;
	color: #333;
}

/* 通用卡片 */
.section-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.section-title {
	font-size: 30rpx;
	font-weight: 500;
	color: #333;
}

.priority-badge {
	font-size: 22rpx;
	padding: 4rpx 16rpx;
	border-radius: 4rpx;
}

/* 设备信息卡片 */
.device-info-card {
	display: flex;
	align-items: center;
	padding: 20rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
}

.device-icon-wrapper {
	width: 80rpx;
	height: 80rpx;
	border-radius: 16rpx;
	background-color: #e6f7ff;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.device-icon {
	font-size: 40rpx;
}

.device-detail {
	display: flex;
	flex-direction: column;
	flex: 1;
}

.device-name {
	font-size: 30rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 8rpx;
}

.device-code {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 4rpx;
}

.running-hours {
	font-size: 24rpx;
	color: #666;
}

/* 信息列表 */
.info-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16rpx 0;
	border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
	border-bottom: none;
}

.info-label {
	font-size: 28rpx;
	color: #666;
}

.info-value {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.info-value.highlight {
	color: #ff4d4f;
}

.progress-wrapper {
	display: flex;
	align-items: center;
	flex: 1;
	justify-content: flex-end;
}

.progress-bar {
	flex: 1;
	max-width: 300rpx;
	height: 16rpx;
	background-color: #f0f0f0;
	border-radius: 8rpx;
	margin-right: 16rpx;
	overflow: hidden;
}

.progress-fill {
	height: 100%;
	background-color: #52c41a;
	border-radius: 8rpx;
	transition: width 0.3s;
}

.progress-fill.warning {
	background-color: #faad14;
}

.progress-fill.danger {
	background-color: #ff4d4f;
}

.progress-text {
	font-size: 26rpx;
	color: #666;
	min-width: 80rpx;
	text-align: right;
}

/* 操作指南 */
.guide-content,
.description-content {
	padding: 20rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
}

.guide-text,
.description-text {
	font-size: 28rpx;
	color: #333;
	line-height: 1.8;
}

/* 操作按钮区域 */
.action-section {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background-color: #fff;
	padding: 24rpx;
	padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
	box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
	width: 100%;
	height: 96rpx;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: 500;
}

.btn-primary:not(.btn-disabled) {
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
}

.btn-text {
	color: #fff;
}

/* 已完成提示 */
.completed-section {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 80rpx 0;
}

.completed-icon {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background-color: #f6ffed;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 24rpx;
}

.completed-text {
	font-size: 30rpx;
	color: #52c41a;
}

/* 加载中 */
.loading-state {
	display: flex;
	align-items: center;
	justify-content: center;
	padding: 100rpx 0;
}

.loading-text {
	font-size: 28rpx;
	color: #999;
}
</style>
