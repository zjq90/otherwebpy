<template>
	<view class="container">
		<!-- 统计概览 -->
		<view class="stats-card">
			<view class="stats-row">
				<view class="stat-item" @click="filterByStatus('all')">
					<text class="stat-value">{{ safeTotal }}</text>
					<text class="stat-label">全部</text>
				</view>
				<view class="stat-item pending" @click="filterByStatus('pending')">
					<text class="stat-value">{{ safePendingCount }}</text>
					<text class="stat-label">待处理</text>
				</view>
				<view class="stat-item processing" @click="filterByStatus('processing')">
					<text class="stat-value">{{ safeProcessingCount }}</text>
					<text class="stat-label">处理中</text>
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
		
		<!-- 待处理提醒 -->
		<view class="pending-section" v-if="pendingReports.length > 0">
			<view class="section-header">
				<text class="section-title">🚨 紧急处理</text>
				<view class="level-badge high">
					<text>高优先级: {{ highLevelCount }}</text>
				</view>
			</view>
			<view class="pending-list">
				<view 
					v-for="(report, index) in pendingReports" 
					:key="report.id"
					class="pending-item"
					:class="`level-${report.fault_level}`"
					@click="goToDetail(report.id)"
				>
					<view class="pending-left">
						<view class="level-icon">
							<text class="icon-text">{{ getLevelIcon(report.fault_level) }}</text>
						</view>
						<view class="pending-info">
							<text class="report-title">{{ report.fault_title }}</text>
							<text class="report-device">{{ report.device_name }} · {{ utils.formatTime(report.created_at) }}</text>
						</view>
					</view>
					<view class="pending-right">
						<view class="status-badge">
							<text class="badge-text" :class="utils.getStatusClass(report.status)">
								{{ utils.getStatusName(report.status) }}
							</text>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 报修列表 -->
		<view class="report-list" v-if="reportList.length > 0">
			<view 
				v-for="(report, index) in reportList" 
				:key="report.id"
				class="report-card"
				:class="{ 
					'high-priority': report.fault_level === 'high',
					'pending-card': report.status === 'pending',
					'processing-card': report.status === 'processing',
					'completed-card': report.status === 'completed'
				}"
				@click="goToDetail(report.id)"
			>
				<view class="card-header">
					<view class="report-info">
						<view class="level-badge" :class="report.fault_level">
							<text class="level-icon">{{ getLevelIcon(report.fault_level) }}</text>
							<text class="level-text">{{ utils.getFaultLevelName(report.fault_level) }}级</text>
						</view>
						<text class="report-title">{{ report.fault_title }}</text>
					</view>
					<view class="status-badge">
						<text class="badge-text" :class="utils.getStatusClass(report.status)">
							{{ utils.getStatusName(report.status) }}
						</text>
					</view>
				</view>
				
				<view class="card-body">
					<view class="info-row">
						<view class="info-item">
							<text class="info-label">故障设备:</text>
							<text class="info-value">{{ report.device_name || '-' }}</text>
						</view>
						<view class="info-item">
							<text class="info-label">设备编号:</text>
							<text class="info-value">{{ report.device_code || '-' }}</text>
						</view>
					</view>
					<view class="info-row">
						<view class="info-item">
							<text class="info-label">上报人:</text>
							<text class="info-value">{{ report.reporter_name || '-' }}</text>
						</view>
						<view class="info-item" v-if="report.assignee_name">
							<text class="info-label">维修人:</text>
							<text class="info-value">{{ report.assignee_name }}</text>
						</view>
					</view>
					<view class="description-row" v-if="report.fault_description">
						<text class="info-label">故障描述:</text>
						<text class="description-text">{{ report.fault_description }}</text>
					</view>
				</view>
				
				<view class="card-footer">
					<text class="create-time">{{ utils.formatDateTime(report.created_at) }}</text>
					<view class="photo-indicator" v-if="report.photo_urls">
						<text class="photo-icon">📷</text>
						<text class="photo-text">有照片</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 空状态 -->
		<view class="empty-state" v-else-if="!loading">
			<text class="empty-icon">📋</text>
			<text class="empty-text">暂无故障报修</text>
			<text class="empty-tip">发现设备故障请及时提交报修</text>
		</view>
		
		<!-- 加载中 -->
		<view class="loading-state" v-if="loading">
			<text class="loading-text">加载中...</text>
		</view>
		
		<!-- 加载更多 -->
		<view class="load-more" v-if="!loading && hasMore">
			<text class="load-more-text" @click="loadMoreData">加载更多</text>
		</view>
		
		<!-- 提交报修按钮 -->
		<view class="fab-section">
			<button class="fab-btn" @click="goToReportForm">
				<text class="fab-icon">+</text>
				<text class="fab-text">提交报修</text>
			</button>
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
			faultStats: {},
			pendingReports: [],
			reportList: [],
			currentStatus: 'all',
			loading: false,
			page: 1,
			pageSize: 10,
			hasMore: true,
			filterOptions: [
				{ label: '全部', value: 'all' },
				{ label: '待处理', value: 'pending' },
				{ label: '处理中', value: 'processing' },
				{ label: '已完成', value: 'completed' }
			]
		}
	},
	
	computed: {
		highLevelCount() {
			return this.pendingReports.filter(r => r.fault_level === 'high').length
		},
		
		safeTotal() {
			return (this.faultStats && this.faultStats.statistics && this.faultStats.statistics.total) || 0
		},
		
		safePendingCount() {
			return (this.faultStats && this.faultStats.statistics && this.faultStats.statistics.pending_count) || 0
		},
		
		safeProcessingCount() {
			return (this.faultStats && this.faultStats.statistics && this.faultStats.statistics.processing_count) || 0
		},
		
		safeCompletedCount() {
			return (this.faultStats && this.faultStats.statistics && this.faultStats.statistics.completed_count) || 0
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
				const statsRes = await api.fault.getOverview()
				if (statsRes.code === 200) {
					this.faultStats = statsRes.data
					this.pendingReports = statsRes.data?.pending_reports || []
				}
				
				// 加载报修列表
				await this.loadReportList()
			} catch (err) {
				console.error('加载数据失败:', err)
			} finally {
				this.loading = false
			}
		},
		
		/**
		 * 加载报修列表
		 */
		async loadReportList() {
			const params = {
				page: this.page,
				page_size: this.pageSize
			}
			
			if (this.currentStatus !== 'all') {
				params.status = this.currentStatus
			}
			
			try {
				const res = await api.fault.getReportList(params)
				
				if (res.code === 200) {
					if (this.page === 1) {
						this.reportList = res.data?.items || []
					} else {
						this.reportList = [...this.reportList, ...(res.data?.items || [])]
					}
					
					this.hasMore = this.page < (res.total_pages || 1)
				}
			} catch (err) {
				console.error('加载报修列表失败:', err)
			}
		},
		
		/**
		 * 加载更多
		 */
		loadMoreData() {
			this.page++
			this.loadReportList()
		},
		
		/**
		 * 按状态筛选
		 */
		filterByStatus(status) {
			this.currentStatus = status
			this.page = 1
			this.hasMore = true
			this.loadReportList()
		},
		
		/**
		 * 状态筛选变化
		 */
		handleStatusFilter(value) {
			if (this.currentStatus !== value) {
				this.currentStatus = value
				this.page = 1
				this.hasMore = true
				this.loadReportList()
			}
		},
		
		/**
		 * 获取故障级别图标
		 */
		getLevelIcon(level) {
			const iconMap = {
				'high': '🔴',
				'medium': '🟡',
				'low': '🟢'
			}
			return iconMap[level] || '⚠️'
		},
		
		/**
		 * 跳转到详情页
		 */
		goToDetail(reportId) {
			uni.navigateTo({
				url: `/pages/fault/report-detail?id=${reportId}`
			})
		},
		
		/**
		 * 跳转到提交报修页面
		 */
		goToReportForm() {
			uni.navigateTo({
				url: '/pages/fault/report-form'
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
	color: #ff4d4f;
}

.stat-item.processing .stat-value {
	color: #faad14;
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

/* 待处理提醒 */
.pending-section {
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

.level-badge {
	display: flex;
	align-items: center;
	padding: 4rpx 12rpx;
	border-radius: 4rpx;
	font-size: 22rpx;
}

.level-badge.high {
	background-color: #fff2f0;
	color: #ff4d4f;
}

.level-badge.medium {
	background-color: #fffbe6;
	color: #faad14;
}

.level-badge.low {
	background-color: #f6ffed;
	color: #52c41a;
}

.pending-list {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.pending-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16rpx;
	border-radius: 12rpx;
}

.pending-item.level-high {
	background-color: #fff2f0;
	border-left: 4rpx solid #ff4d4f;
}

.pending-item.level-medium {
	background-color: #fffbe6;
	border-left: 4rpx solid #faad14;
}

.pending-item.level-low {
	background-color: #f6ffed;
	border-left: 4rpx solid #52c41a;
}

.pending-left {
	display: flex;
	align-items: center;
	flex: 1;
}

.level-icon {
	width: 56rpx;
	height: 56rpx;
	border-radius: 50%;
	background-color: rgba(255, 255, 255, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.icon-text {
	font-size: 28rpx;
}

.pending-info {
	display: flex;
	flex-direction: column;
	flex: 1;
}

.report-title {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 4rpx;
}

.report-device {
	font-size: 22rpx;
	color: #999;
}

.pending-right {
	flex-shrink: 0;
}

/* 报修列表 */
.report-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.report-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
}

.report-card.high-priority {
	border-left: 6rpx solid #ff4d4f;
}

.report-card.pending-card {
	background-color: #fffbfb;
}

.report-card.processing-card {
	background-color: #fffef5;
}

.report-card.completed-card {
	background-color: #f9fff4;
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	margin-bottom: 16rpx;
}

.report-info {
	display: flex;
	flex-direction: column;
	flex: 1;
}

.report-info .level-badge {
	align-self: flex-start;
	margin-bottom: 8rpx;
}

.report-info .level-badge text {
	font-size: 22rpx;
}

.report-title {
	font-size: 30rpx;
	font-weight: 500;
	color: #333;
}

.status-badge {
	margin-left: 16rpx;
	flex-shrink: 0;
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
	margin-bottom: 12rpx;
}

.info-item {
	display: flex;
	align-items: center;
	flex: 1;
}

.info-label {
	font-size: 24rpx;
	color: #999;
	margin-right: 8rpx;
}

.info-value {
	font-size: 24rpx;
	color: #333;
}

.description-row {
	display: flex;
	align-items: flex-start;
	margin-top: 12rpx;
	padding-top: 12rpx;
	border-top: 1rpx solid #f0f0f0;
}

.description-text {
	font-size: 24rpx;
	color: #666;
	flex: 1;
	line-height: 1.6;
}

/* 卡片底部 */
.card-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding-top: 16rpx;
	border-top: 1rpx solid #f0f0f0;
}

.create-time {
	font-size: 22rpx;
	color: #999;
}

.photo-indicator {
	display: flex;
	align-items: center;
}

.photo-icon {
	font-size: 24rpx;
	margin-right: 4rpx;
}

.photo-text {
	font-size: 22rpx;
	color: #1677ff;
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

/* 浮动按钮 */
.fab-section {
	position: fixed;
	bottom: 32rpx;
	right: 32rpx;
	z-index: 100;
}

.fab-btn {
	width: 140rpx;
	height: 140rpx;
	border-radius: 50%;
	background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
	box-shadow: 0 8rpx 24rpx rgba(255, 77, 79, 0.4);
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.fab-icon {
	font-size: 48rpx;
	color: #fff;
	font-weight: 300;
}

.fab-text {
	font-size: 20rpx;
	color: #fff;
	margin-top: 4rpx;
}
</style>
