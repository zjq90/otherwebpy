<template>
	<view class="container">
		<!-- 搜索和筛选 -->
		<view class="search-section">
			<view class="search-box">
				<text class="search-icon">🔍</text>
				<input 
					class="search-input" 
					type="text" 
					placeholder="搜索设备编号、名称..."
					v-model="searchKeyword"
					@confirm="handleSearch"
				/>
			</view>
			
			<view class="filter-bar">
				<view 
					v-for="(filter, index) in filterOptions" 
					:key="index"
					class="filter-item"
					:class="{ 'active': currentFilter === filter.value }"
					@click="handleFilterChange(filter.value)"
				>
					<text class="filter-text">{{ filter.label }}</text>
					<text v-if="filter.count > 0" class="filter-count">{{ filter.count }}</text>
				</view>
			</view>
			
			<view class="type-filter">
				<view 
					v-for="(type, index) in typeOptions" 
					:key="index"
					class="type-item"
					:class="{ 'active': currentType === type.value }"
					@click="handleTypeChange(type.value)"
				>
					<text class="type-icon">{{ type.icon }}</text>
					<text class="type-text">{{ type.label }}</text>
				</view>
			</view>
		</view>
		
		<!-- 设备列表 -->
		<view class="device-list" v-if="deviceList.length > 0">
			<view 
				v-for="(device, index) in deviceList" 
				:key="device.id"
				class="device-card"
				:class="{ 'fault-card': device.status === 'fault' || device.status === 'warning' }"
				@click="goToDetail(device.id)"
			>
				<view class="card-left">
					<view 
						class="device-icon"
						:class="`status-${device.status}`"
					>
						<text class="icon-text">{{ getDeviceIcon(device.device_type) }}</text>
					</view>
					<view class="device-info">
						<view class="info-top">
							<text class="device-name">{{ device.device_name }}</text>
							<view class="status-badge">
								<text class="badge-text" :class="utils.getStatusClass(device.status)">
									{{ utils.getStatusName(device.status) }}
								</text>
							</view>
						</view>
						<view class="info-bottom">
							<text class="device-code">编号: {{ device.device_code }}</text>
							<text class="device-location">位置: {{ device.location || '-' }}</text>
						</view>
					</view>
				</view>
				
				<view class="card-right" v-if="device.current_status">
					<view class="metric-grid">
						<view class="metric-item">
							<text class="metric-value">{{ utils.formatNumber(device.current_status.current) }}</text>
							<text class="metric-unit">A</text>
							<text class="metric-label">电流</text>
						</view>
						<view class="metric-item">
							<text class="metric-value" :class="{ 'high-temp': device.current_status.temperature > 80 }">
								{{ utils.formatNumber(device.current_status.temperature) }}
							</text>
							<text class="metric-unit">°C</text>
							<text class="metric-label">温度</text>
						</view>
						<view class="metric-item">
							<text class="metric-value">{{ utils.formatNumber(device.total_running_hours, 1) }}</text>
							<text class="metric-unit">h</text>
							<text class="metric-label">运行时长</text>
						</view>
					</view>
				</view>
				
				<view class="card-arrow">
					<text class="arrow-text">›</text>
				</view>
			</view>
		</view>
		
		<!-- 空状态 -->
		<view class="empty-state" v-else-if="!loading">
			<text class="empty-icon">📭</text>
			<text class="empty-text">暂无设备数据</text>
			<text class="empty-tip">请检查筛选条件或刷新页面</text>
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
			searchKeyword: '',
			currentFilter: 'all',
			currentType: 'all',
			deviceList: [],
			loading: false,
			page: 1,
			pageSize: 10,
			hasMore: true,
			filterOptions: [
				{ label: '全部', value: 'all', count: 0 },
				{ label: '正常', value: 'normal', count: 0 },
				{ label: '预警', value: 'warning', count: 0 },
				{ label: '故障', value: 'fault', count: 0 }
			],
			typeOptions: [
				{ label: '全部', value: 'all', icon: '🏭' },
				{ label: '搅拌主机', value: 'mixer', icon: '⚙️' },
				{ label: '皮带秤', value: 'belt_scale', icon: '📏' },
				{ label: '空压机', value: 'compressor', icon: '💨' }
			]
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
				const params = {
					page: this.page,
					page_size: this.pageSize
				}
				
				if (this.searchKeyword) {
					params.keyword = this.searchKeyword
				}
				
				if (this.currentFilter !== 'all') {
					params.status = this.currentFilter
				}
				
				if (this.currentType !== 'all') {
					params.device_type = this.currentType
				}
				
				const res = await api.device.getList(params)
				
				if (res.code === 200) {
					if (this.page === 1) {
						this.deviceList = res.data?.items || []
					} else {
						this.deviceList = [...this.deviceList, ...(res.data?.items || [])]
					}
					
					this.hasMore = this.page < (res.total_pages || 1)
					
					// 更新统计数量
					this.updateFilterCounts()
				}
			} catch (err) {
				console.error('加载设备列表失败:', err)
			} finally {
				this.loading = false
			}
		},
		
		/**
		 * 更新筛选统计数量
		 */
		async updateFilterCounts() {
			try {
				const res = await api.test.getQuickStats()
				if (res.code === 200) {
					this.filterOptions[0].count = res.data?.devices?.total || 0
					this.filterOptions[1].count = res.data?.devices?.normal || 0
					this.filterOptions[2].count = res.data?.devices?.warning || 0
					this.filterOptions[3].count = res.data?.devices?.fault || 0
				}
			} catch (err) {
				console.error('获取统计数据失败:', err)
			}
		},
		
		/**
		 * 加载更多
		 */
		loadMoreData() {
			this.page++
			this.loadData()
		},
		
		/**
		 * 搜索
		 */
		handleSearch() {
			this.page = 1
			this.hasMore = true
			this.loadData()
		},
		
		/**
		 * 筛选状态变化
		 */
		handleFilterChange(value) {
			if (this.currentFilter !== value) {
				this.currentFilter = value
				this.page = 1
				this.hasMore = true
				this.loadData()
			}
		},
		
		/**
		 * 设备类型变化
		 */
		handleTypeChange(value) {
			if (this.currentType !== value) {
				this.currentType = value
				this.page = 1
				this.hasMore = true
				this.loadData()
			}
		},
		
		/**
		 * 获取设备图标
		 */
		getDeviceIcon(type) {
			const iconMap = {
				'mixer': '⚙️',
				'belt_scale': '📏',
				'compressor': '💨'
			}
			return iconMap[type] || '🏭'
		},
		
		/**
		 * 跳转到详情页
		 */
		goToDetail(deviceId) {
			uni.navigateTo({
				url: `/pages/device/detail?id=${deviceId}`
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

/* 搜索区域 */
.search-section {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
}

.search-box {
	display: flex;
	align-items: center;
	background-color: #f5f5f5;
	border-radius: 40rpx;
	padding: 16rpx 24rpx;
	margin-bottom: 24rpx;
}

.search-icon {
	font-size: 28rpx;
	margin-right: 16rpx;
}

.search-input {
	flex: 1;
	font-size: 28rpx;
	color: #333;
}

/* 筛选栏 */
.filter-bar {
	display: flex;
	gap: 16rpx;
	margin-bottom: 24rpx;
	flex-wrap: wrap;
}

.filter-item {
	display: flex;
	align-items: center;
	padding: 12rpx 24rpx;
	background-color: #f5f5f5;
	border-radius: 32rpx;
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

.filter-count {
	font-size: 20rpx;
	color: #999;
	margin-left: 8rpx;
	background-color: #e0e0e0;
	padding: 2rpx 8rpx;
	border-radius: 10rpx;
}

.filter-item.active .filter-count {
	background-color: #1677ff;
	color: #fff;
}

/* 类型筛选 */
.type-filter {
	display: flex;
	gap: 16rpx;
}

.type-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 16rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
}

.type-item.active {
	background-color: #e6f7ff;
	border: 2rpx solid #1677ff;
}

.type-icon {
	font-size: 36rpx;
	margin-bottom: 8rpx;
}

.type-text {
	font-size: 22rpx;
	color: #666;
}

.type-item.active .type-text {
	color: #1677ff;
	font-weight: 500;
}

/* 设备列表 */
.device-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.device-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	display: flex;
	align-items: center;
}

.device-card.fault-card {
	background-color: #fffbfb;
	border-left: 4rpx solid #ff4d4f;
}

.card-left {
	display: flex;
	align-items: flex-start;
	flex: 1;
}

.device-icon {
	width: 96rpx;
	height: 96rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.device-icon.status-normal {
	background-color: #f6ffed;
}

.device-icon.status-warning {
	background-color: #fffbe6;
	animation: pulse 2s infinite;
}

.device-icon.status-fault {
	background-color: #fff2f0;
	animation: pulse 1s infinite;
}

@keyframes pulse {
	0%, 100% { transform: scale(1); }
	50% { transform: scale(1.05); }
}

.device-info {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.info-top {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 12rpx;
}

.device-name {
	font-size: 32rpx;
	font-weight: 500;
	color: #333;
}

.status-badge {
	margin-left: 16rpx;
}

.badge-text {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 6rpx;
}

.info-bottom {
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.device-code,
.device-location {
	font-size: 24rpx;
	color: #999;
}

.card-right {
	flex-shrink: 0;
	margin-right: 16rpx;
}

.metric-grid {
	display: flex;
	gap: 24rpx;
}

.metric-item {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.metric-value {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.metric-value.high-temp {
	color: #ff4d4f;
}

.metric-unit {
	font-size: 20rpx;
	color: #999;
	margin-left: 4rpx;
}

.metric-label {
	font-size: 20rpx;
	color: #999;
	margin-top: 4rpx;
}

.card-arrow {
	flex-shrink: 0;
}

.arrow-text {
	font-size: 40rpx;
	color: #ccc;
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
