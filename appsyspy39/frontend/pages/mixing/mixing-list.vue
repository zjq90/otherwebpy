<template>
	<view class="mixing-list-container">
		<!-- 搜索和筛选 -->
		<view class="search-section">
			<view class="search-box">
				<text class="iconfont icon-search"></text>
				<input 
					class="search-input" 
					type="text" 
					v-model="searchKeyword" 
					placeholder="搜索任务编号"
					placeholder-class="input-placeholder"
					@confirm="handleSearch"
				/>
			</view>
		</view>
		
		<!-- 状态筛选 -->
		<view class="filter-tabs">
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === '' }"
				@click="handleFilter('')"
			>
				全部
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === 'abnormal' }"
				@click="handleFilter('abnormal')"
			>
				异常
				<text class="tab-badge" v-if="abnormalCount > 0">{{ abnormalCount }}</text>
			</view>
		</view>
		
		<!-- 搅拌记录列表 -->
		<scroll-view 
			class="mixing-scroll" 
			scroll-y
			@scrolltolower="loadMore"
			refresher-enabled
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<view class="mixing-list" v-if="mixingList.length > 0">
				<view 
					class="mixing-card" 
					v-for="(record, index) in mixingList" 
					:key="record.id"
					@click="goToDetail(record.id)"
				>
					<!-- 头部信息 -->
					<view class="card-header">
						<view class="task-info">
							<text class="task-no">任务 #{{ record.task_id }}</text>
							<text class="batch-no">第{{ record.batch_no }}盘</text>
						</view>
						<view class="status-badge" :class="record.status">
							{{ getStatusText(record.status) }}
						</view>
					</view>
					
					<!-- 搅拌参数 -->
					<view class="card-body">
						<view class="param-grid">
							<view class="param-item">
								<text class="param-label">搅拌时长</text>
								<text class="param-value">{{ record.mixing_time_seconds }}秒</text>
							</view>
							<view class="param-item">
								<text class="param-label">搅拌转速</text>
								<text class="param-value">{{ record.rotation_speed || '-' }} RPM</text>
							</view>
							<view class="param-item">
								<text class="param-label">当前温度</text>
								<text class="param-value">{{ record.current_temperature || '-' }}℃</text>
							</view>
						</view>
					</view>
					
					<!-- 质量信息 -->
					<view class="card-footer" v-if="record.slump_actual || record.quality_status">
						<view class="quality-info">
							<text class="quality-label" v-if="record.slump_actual">坍落度: {{ record.slump_actual }}mm</text>
							<view 
								class="quality-badge" 
								v-if="record.quality_status"
								:class="record.quality_status"
							>
								{{ record.quality_status === 'qualified' ? '合格' : '不合格' }}
							</view>
						</view>
					</view>
					
					<!-- 异常提示 -->
					<view class="abnormal-alert" v-if="record.is_abnormal">
						<text class="alert-icon">⚠️</text>
						<view class="alert-content">
							<text class="alert-type">{{ getAbnormalTypeText(record.abnormal_type) }}</text>
							<text class="alert-desc" v-if="record.abnormal_description">{{ record.abnormal_description }}</text>
						</view>
					</view>
					
					<!-- 底部时间 -->
					<view class="card-time">
						<text class="record-time">{{ formatTime(record.created_at) }}</text>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-else-if="!loading && mixingList.length === 0">
				<text class="empty-icon">⚙️</text>
				<text class="empty-text">暂无搅拌记录</text>
				<text class="empty-tip">请先选择任务进行搅拌操作</text>
			</view>
			
			<!-- 加载更多 -->
			<view class="load-more" v-if="loading && page > 1">
				<text>加载中...</text>
			</view>
			
			<!-- 没有更多 -->
			<view class="no-more" v-if="!hasMore && mixingList.length > 0">
				<text>没有更多了</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
/**
 * 搅拌记录列表页面
 * 功能：
 * - 搅拌记录列表展示
 * - 异常筛选
 * - 搜索功能
 * - 查看详情
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 搜索关键词
			searchKeyword: '',
			// 当前筛选
			currentFilter: '',
			// 搅拌记录列表
			mixingList: [],
			// 分页
			page: 1,
			pageSize: 10,
			hasMore: true,
			// 加载状态
			loading: false,
			refreshing: false,
			// 异常数量
			abnormalCount: 0
		}
	},
	
	onLoad(options) {
		// 如果有传入的任务ID
		if (options.taskId) {
			this.taskId = parseInt(options.taskId)
		}
		this.loadData()
	},
	
	onShow() {
		if (!this.loading) {
			this.onRefresh()
		}
	},
	
	methods: {
		/**
		 * 加载数据
		 */
		async loadData(isRefresh = false) {
			if (this.loading) return
			
			this.loading = true
			
			try {
				const params = {
					page: this.page,
					page_size: this.pageSize
				}
				
				// 异常筛选
				if (this.currentFilter === 'abnormal') {
					params.is_abnormal = true
				}
				
				const res = await api.mixing.getList(params)
				
				if (res && res.records) {
					const newRecords = res.records
					
					if (isRefresh) {
						this.mixingList = newRecords
					} else {
						this.mixingList = [...this.mixingList, ...newRecords]
					}
					
					this.hasMore = newRecords.length >= this.pageSize
					
					// 统计异常数量（第一次加载时）
					if (isRefresh || this.page === 1) {
						this.abnormalCount = this.mixingList.filter(r => r.is_abnormal).length
					}
				}
			} catch (error) {
				console.log('加载搅拌记录失败:', error)
			} finally {
				this.loading = false
				this.refreshing = false
			}
		},
		
		/**
		 * 下拉刷新
		 */
		async onRefresh() {
			this.refreshing = true
			this.page = 1
			this.hasMore = true
			await this.loadData(true)
		},
		
		/**
		 * 上拉加载更多
		 */
		loadMore() {
			if (this.hasMore && !this.loading) {
				this.page++
				this.loadData()
			}
		},
		
		/**
		 * 搜索
		 */
		handleSearch() {
			this.onRefresh()
		},
		
		/**
		 * 筛选
		 */
		handleFilter(filter) {
			if (this.currentFilter === filter) return
			this.currentFilter = filter
			this.onRefresh()
		},
		
		/**
		 * 格式化时间
		 */
		formatTime(time) {
			if (!time) return ''
			const date = new Date(time)
			const month = String(date.getMonth() + 1).padStart(2, '0')
			const day = String(date.getDate()).padStart(2, '0')
			const hour = String(date.getHours()).padStart(2, '0')
			const minute = String(date.getMinutes()).padStart(2, '0')
			return `${month}-${day} ${hour}:${minute}`
		},
		
		/**
		 * 获取状态文本
		 */
		getStatusText(status) {
			const statusMap = {
				'mixing': '搅拌中',
				'completed': '已完成',
				'abnormal': '异常'
			}
			return statusMap[status] || status
		},
		
		/**
		 * 获取异常类型文本
		 */
		getAbnormalTypeText(type) {
			const typeMap = {
				'material_shortage': '缺料',
				'equipment_fault': '设备故障',
				'quality_issue': '质量问题',
				'other': '其他'
			}
			return typeMap[type] || type || '异常'
		},
		
		// ========== 页面跳转 ==========
		
		goToDetail(recordId) {
			uni.navigateTo({
				url: `/pages/mixing/mixing-detail?id=${recordId}`
			})
		}
	}
}
</script>

<style scoped>
/* 搅拌列表页面样式 */
.mixing-list-container {
	height: 100vh;
	display: flex;
	flex-direction: column;
	background: #F5F7FA;
}

/* 搜索区域 */
.search-section {
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.search-box {
	display: flex;
	align-items: center;
	background: #F5F7FA;
	border-radius: 40rpx;
	padding: 16rpx 30rpx;
}

.icon-search {
	font-size: 32rpx;
	color: #999999;
	margin-right: 16rpx;
}

.search-input {
	flex: 1;
	font-size: 28rpx;
	color: #333333;
}

.input-placeholder {
	color: #CCCCCC;
}

/* 筛选标签 */
.filter-tabs {
	display: flex;
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	gap: 20rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.tab-item {
	flex-shrink: 0;
	font-size: 26rpx;
	color: #666666;
	padding: 10rpx 24rpx;
	border-radius: 30rpx;
	background: #F5F7FA;
	position: relative;
	display: flex;
	align-items: center;
}

.tab-item.active {
	background: #E6F7FF;
	color: #1890FF;
	font-weight: 500;
}

.tab-badge {
	font-size: 20rpx;
	color: #FFFFFF;
	background: #FF4D4F;
	padding: 2rpx 10rpx;
	border-radius: 10rpx;
	margin-left: 8rpx;
}

/* 滚动区域 */
.mixing-scroll {
	flex: 1;
}

.mixing-list {
	padding: 20rpx 30rpx;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

/* 搅拌记录卡片 */
.mixing-card {
	background: #FFFFFF;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 24rpx 30rpx;
	background: linear-gradient(90deg, #FAFAFA 0%, #FFFFFF 100%);
	border-bottom: 2rpx solid #F5F5F5;
}

.task-info {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.task-no {
	font-size: 26rpx;
	color: #1890FF;
	font-weight: 500;
}

.batch-no {
	font-size: 24rpx;
	color: #666666;
	background: #F5F7FA;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
}

.status-badge {
	font-size: 24rpx;
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
}

.status-badge.completed {
	background: #F0F0F0;
	color: #666666;
}

.status-badge.mixing {
	background: #E6F7FF;
	color: #1890FF;
}

.status-badge.abnormal {
	background: #FFF1F0;
	color: #FF4D4F;
}

/* 卡片主体 */
.card-body {
	padding: 24rpx 30rpx;
}

.param-grid {
	display: flex;
	gap: 30rpx;
}

.param-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20rpx;
	background: #FAFAFA;
	border-radius: 12rpx;
}

.param-label {
	font-size: 22rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.param-value {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

/* 卡片底部 */
.card-footer {
	padding: 16rpx 30rpx;
	background: #FAFAFA;
	border-top: 2rpx solid #F5F5F5;
}

.quality-info {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.quality-label {
	font-size: 24rpx;
	color: #666666;
}

.quality-badge {
	font-size: 22rpx;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
}

.quality-badge.qualified {
	background: #F6FFED;
	color: #52C41A;
}

.quality-badge.unqualified {
	background: #FFF1F0;
	color: #FF4D4F;
}

/* 异常提示 */
.abnormal-alert {
	display: flex;
	align-items: flex-start;
	padding: 20rpx 30rpx;
	background: #FFF1F0;
	border-top: 2rpx solid #FFA39E;
}

.alert-icon {
	font-size: 28rpx;
	margin-right: 12rpx;
	margin-top: 4rpx;
	flex-shrink: 0;
}

.alert-content {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.alert-type {
	font-size: 26rpx;
	color: #FF4D4F;
	font-weight: 500;
	margin-bottom: 6rpx;
}

.alert-desc {
	font-size: 24rpx;
	color: #CF1322;
	line-height: 1.5;
}

/* 时间 */
.card-time {
	padding: 16rpx 30rpx;
	background: #FAFAFA;
	border-top: 2rpx solid #F5F5F5;
}

.record-time {
	font-size: 22rpx;
	color: #999999;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 120rpx 0;
}

.empty-icon {
	font-size: 100rpx;
	margin-bottom: 30rpx;
}

.empty-text {
	font-size: 30rpx;
	color: #666666;
	margin-bottom: 12rpx;
}

.empty-tip {
	font-size: 24rpx;
	color: #999999;
}

/* 加载状态 */
.load-more,
.no-more {
	text-align: center;
	padding: 40rpx;
	font-size: 26rpx;
	color: #999999;
}
</style>
