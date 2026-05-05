<template>
	<view class="feeding-list-container">
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
				:class="{ active: currentFilter === 'warning' }"
				@click="handleFilter('warning')"
			>
				有预警
				<text class="tab-badge" v-if="warningCount > 0">{{ warningCount }}</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === 'critical' }"
				@click="handleFilter('critical')"
			>
				严重预警
			</view>
		</view>
		
		<!-- 投料记录列表 -->
		<scroll-view 
			class="feeding-scroll" 
			scroll-y
			@scrolltolower="loadMore"
			refresher-enabled
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<view class="feeding-list" v-if="feedingList.length > 0">
				<view 
					class="feeding-card" 
					v-for="(record, index) in feedingList" 
					:key="record.id"
					@click="goToDetail(record.id)"
				>
					<!-- 头部信息 -->
					<view class="card-header">
						<view class="task-info">
							<text class="task-no">任务 #{{ record.task_id }}</text>
							<text class="batch-no">第{{ record.batch_no }}盘</text>
						</view>
						<view class="warning-badge" v-if="record.has_warning">
							<view 
								class="badge-dot" 
								:class="record.warning_level"
							></view>
							<text class="badge-text">{{ record.warning_level === 'critical' ? '严重' : '警告' }}</text>
						</view>
					</view>
					
					<!-- 用量信息 -->
					<view class="card-body">
						<view class="quantity-row">
							<text class="quantity-label">本盘方量</text>
							<text class="quantity-value">{{ record.batch_quantity }} m³</text>
						</view>
						
						<!-- 偏差概览 -->
						<view class="deviation-summary">
							<view class="deviation-item" v-for="(item, idx) in getDeviationItems(record)" :key="idx">
								<text class="deviation-name">{{ item.name }}</text>
								<text 
									class="deviation-value" 
									:class="getDeviationClass(item.deviation)"
								>
									{{ item.deviation > 0 ? '+' : '' }}{{ item.deviation }}%
								</text>
							</view>
						</view>
					</view>
					
					<!-- 底部信息 -->
					<view class="card-footer">
						<text class="method-tag" :class="record.feeding_method">
							{{ record.feeding_method === 'scan' ? '扫码录入' : '手动录入' }}
						</text>
						<text class="record-time">{{ formatTime(record.created_at) }}</text>
					</view>
					
					<!-- 预警信息 -->
					<view class="warning-alert" v-if="record.has_warning && record.warning_message">
						<text class="warning-icon">⚠️</text>
						<text class="warning-text">{{ record.warning_message }}</text>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-else-if="!loading && feedingList.length === 0">
				<text class="empty-icon">📊</text>
				<text class="empty-text">暂无投料记录</text>
				<text class="empty-tip">请先选择任务进行投料操作</text>
			</view>
			
			<!-- 加载更多 -->
			<view class="load-more" v-if="loading && page > 1">
				<text>加载中...</text>
			</view>
			
			<!-- 没有更多 -->
			<view class="no-more" v-if="!hasMore && feedingList.length > 0">
				<text>没有更多了</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
/**
 * 投料记录列表页面
 * 功能：
 * - 投料记录列表展示
 * - 预警筛选
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
			// 投料记录列表
			feedingList: [],
			// 分页
			page: 1,
			pageSize: 10,
			hasMore: true,
			// 加载状态
			loading: false,
			refreshing: false,
			// 预警数量
			warningCount: 0
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
				
				// 预警筛选
				if (this.currentFilter === 'warning') {
					params.has_warning = true
				}
				
				const res = await api.feeding.getList(params)
				
				if (res && res.records) {
					const newRecords = res.records
					
					if (isRefresh) {
						this.feedingList = newRecords
					} else {
						this.feedingList = [...this.feedingList, ...newRecords]
					}
					
					this.hasMore = newRecords.length >= this.pageSize
					
					// 统计预警数量（第一次加载时）
					if (isRefresh || this.page === 1) {
						this.warningCount = this.feedingList.filter(r => r.has_warning && r.warning_level === 'warning').length
					}
				}
			} catch (error) {
				console.log('加载投料记录失败:', error)
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
		 * 获取偏差项
		 */
		getDeviationItems(record) {
			const items = []
			
			if (record.cement_deviation !== null && record.cement_deviation !== undefined) {
				items.push({ name: '水泥', deviation: record.cement_deviation })
			}
			if (record.sand_deviation !== null && record.sand_deviation !== undefined) {
				items.push({ name: '砂', deviation: record.sand_deviation })
			}
			if (record.stone_deviation !== null && record.stone_deviation !== undefined) {
				items.push({ name: '石', deviation: record.stone_deviation })
			}
			
			return items.slice(0, 3)
		},
		
		/**
		 * 获取偏差样式类
		 */
		getDeviationClass(deviation) {
			if (deviation === null || deviation === undefined) return ''
			const abs = Math.abs(deviation)
			if (abs >= 10) return 'critical'
			if (abs >= 5) return 'warning'
			return 'normal'
		},
		
		// ========== 页面跳转 ==========
		
		goToDetail(recordId) {
			uni.navigateTo({
				url: `/pages/feeding/feeding-detail?id=${recordId}`
			})
		}
	}
}
</script>

<style scoped>
/* 投料列表页面样式 */
.feeding-list-container {
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
.feeding-scroll {
	flex: 1;
}

.feeding-list {
	padding: 20rpx 30rpx;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

/* 投料记录卡片 */
.feeding-card {
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

.warning-badge {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 8rpx 16rpx;
	border-radius: 20rpx;
	background: #FFF7E6;
}

.badge-dot {
	width: 16rpx;
	height: 16rpx;
	border-radius: 50%;
}

.badge-dot.warning {
	background: #FA8C16;
}

.badge-dot.critical {
	background: #FF4D4F;
}

.badge-text {
	font-size: 22rpx;
	color: #FA8C16;
}

.warning-badge .badge-text.critical {
	color: #FF4D4F;
}

/* 卡片主体 */
.card-body {
	padding: 24rpx 30rpx;
}

.quantity-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
}

.quantity-label {
	font-size: 26rpx;
	color: #999999;
}

.quantity-value {
	font-size: 32rpx;
	color: #333333;
	font-weight: bold;
}

/* 偏差概览 */
.deviation-summary {
	display: flex;
	gap: 30rpx;
	padding: 20rpx;
	background: #FAFAFA;
	border-radius: 12rpx;
}

.deviation-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
}

.deviation-name {
	font-size: 22rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.deviation-value {
	font-size: 28rpx;
	font-weight: 500;
}

.deviation-value.normal {
	color: #52C41A;
}

.deviation-value.warning {
	color: #FA8C16;
}

.deviation-value.critical {
	color: #FF4D4F;
}

/* 卡片底部 */
.card-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16rpx 30rpx;
	background: #FAFAFA;
	border-top: 2rpx solid #F5F5F5;
}

.method-tag {
	font-size: 22rpx;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
}

.method-tag.scan {
	background: #E6F7FF;
	color: #1890FF;
}

.method-tag.manual {
	background: #FFF7E6;
	color: #FA8C16;
}

.record-time {
	font-size: 22rpx;
	color: #999999;
}

/* 预警提示 */
.warning-alert {
	display: flex;
	align-items: center;
	padding: 20rpx 30rpx;
	background: #FFF1F0;
	border-top: 2rpx solid #FFA39E;
}

.warning-icon {
	font-size: 28rpx;
	margin-right: 12rpx;
}

.warning-text {
	flex: 1;
	font-size: 24rpx;
	color: #FF4D4F;
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
