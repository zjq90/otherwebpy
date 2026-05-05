<template>
	<view class="container">
		<!-- 设备状态头部 -->
		<view class="status-header" :class="`status-${device.status}`">
			<view class="header-content">
				<view class="device-icon">
					<text class="icon-text">{{ getDeviceIcon(device.device_type) }}</text>
				</view>
				<view class="header-info">
					<text class="device-name">{{ device.device_name }}</text>
					<text class="device-code">{{ device.device_code }}</text>
				</view>
				<view class="status-badge">
					<text class="badge-text" :class="utils.getStatusClass(device.status)">
						{{ utils.getStatusName(device.status) }}
					</text>
				</view>
			</view>
		</view>
		
		<!-- 实时运行数据 -->
		<view class="metrics-card" v-if="device.current_status">
			<view class="card-title">
				<text class="title-text">实时运行数据</text>
				<text class="update-time">{{ utils.formatDateTime(device.current_status.recorded_at) }}</text>
			</view>
			
			<view class="metrics-grid">
				<view class="metric-item">
					<view class="metric-header">
						<text class="metric-icon">⚡</text>
						<text class="metric-label">电流</text>
					</view>
					<view class="metric-value-wrapper">
						<text class="metric-value">{{ utils.formatNumber(device.current_status.current) }}</text>
						<text class="metric-unit">A</text>
					</view>
					<view class="metric-bar">
						<view 
							class="bar-fill" 
							:class="getBarClass(device.current_status.current, 200)"
							:style="{ width: getBarWidth(device.current_status.current, 200) }"
						></view>
					</view>
				</view>
				
				<view class="metric-item">
					<view class="metric-header">
						<text class="metric-icon">🌡️</text>
						<text class="metric-label">温度</text>
					</view>
					<view class="metric-value-wrapper">
						<text 
							class="metric-value" 
							:class="{ 'danger': device.current_status.temperature > 80 }"
						>
							{{ utils.formatNumber(device.current_status.temperature) }}
						</text>
						<text class="metric-unit">°C</text>
					</view>
					<view class="metric-bar">
						<view 
							class="bar-fill" 
							:class="getBarClass(device.current_status.temperature, 100)"
							:style="{ width: getBarWidth(device.current_status.temperature, 100) }"
						></view>
					</view>
				</view>
				
				<view class="metric-item">
					<view class="metric-header">
						<text class="metric-icon">🔋</text>
						<text class="metric-label">电压</text>
					</view>
					<view class="metric-value-wrapper">
						<text class="metric-value">{{ utils.formatNumber(device.current_status.voltage) }}</text>
						<text class="metric-unit">V</text>
					</view>
					<view class="metric-bar">
						<view 
							class="bar-fill bar-normal"
							:style="{ width: getBarWidth(device.current_status.voltage, 400) }"
						></view>
					</view>
				</view>
				
				<view class="metric-item">
					<view class="metric-header">
						<text class="metric-icon">⚙️</text>
						<text class="metric-label">功率</text>
					</view>
					<view class="metric-value-wrapper">
						<text class="metric-value">{{ utils.formatNumber(device.current_status.power) }}</text>
						<text class="metric-unit">kW</text>
					</view>
					<view class="metric-bar">
						<view 
							class="bar-fill bar-normal"
							:style="{ width: getBarWidth(device.current_status.power, 500) }"
						></view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 设备基本信息 -->
		<view class="info-card">
			<view class="card-title">
				<text class="title-text">设备信息</text>
			</view>
			
			<view class="info-list">
				<view class="info-item">
					<text class="info-label">设备类型</text>
					<text class="info-value">{{ utils.getDeviceTypeName(device.device_type) }}</text>
				</view>
				
				<view class="info-item">
					<text class="info-label">安装位置</text>
					<text class="info-value">{{ device.location || '-' }}</text>
				</view>
				
				<view class="info-item">
					<text class="info-label">规格型号</text>
					<text class="info-value">{{ device.specification || '-' }}</text>
				</view>
				
				<view class="info-item">
					<text class="info-label">生产厂商</text>
					<text class="info-value">{{ device.manufacturer || '-' }}</text>
				</view>
				
				<view class="info-item">
					<text class="info-label">安装日期</text>
					<text class="info-value">{{ device.install_date ? utils.formatDate(device.install_date) : '-' }}</text>
				</view>
				
				<view class="info-item">
					<text class="info-label">累计运行</text>
					<text class="info-value">{{ utils.formatNumber(device.total_running_hours, 1) }} 小时</text>
				</view>
			</view>
		</view>
		
		<!-- 状态历史 -->
		<view class="history-card">
			<view class="card-title">
				<text class="title-text">状态历史</text>
				<text class="more-text" @click="loadMoreHistory">加载更多</text>
			</view>
			
			<view class="history-list" v-if="statusHistory.length > 0">
				<view 
					v-for="(item, index) in statusHistory" 
					:key="index"
					class="history-item"
					:class="{ 'danger-item': item.status === 'fault', 'warning-item': item.status === 'warning' }"
				>
					<view class="history-time">
						<text class="time-text">{{ utils.formatTime(item.recorded_at) }}</text>
						<text class="date-text">{{ utils.formatDate(item.recorded_at) }}</text>
					</view>
					
					<view class="history-content">
						<view class="content-top">
							<view class="status-tag">
								<text class="tag-text" :class="utils.getStatusClass(item.status)">
									{{ utils.getStatusName(item.status) }}
								</text>
							</view>
							<text v-if="item.alarm_level !== 'none'" class="alarm-text">
								报警级别: {{ item.alarm_level === 'high' ? '高' : item.alarm_level === 'medium' ? '中' : '低' }}
							</text>
						</view>
						<view class="content-metrics">
							<text class="metric-text">电流: {{ utils.formatNumber(item.current) }}A</text>
							<text class="metric-text">温度: {{ utils.formatNumber(item.temperature) }}°C</text>
							<text class="metric-text">运行: {{ utils.formatNumber(item.running_hours, 1) }}h</text>
						</view>
					</view>
				</view>
			</view>
			
			<view class="empty-state" v-else>
				<text class="empty-text">暂无状态历史</text>
			</view>
		</view>
		
		<!-- 底部操作栏 -->
		<view class="bottom-actions">
			<button class="action-btn btn-warning" @click="goToMaintenance">
				<text class="btn-icon">🔧</text>
				<text class="btn-text">保养记录</text>
			</button>
			<button class="action-btn btn-danger" @click="goToReport">
				<text class="btn-icon">🚨</text>
				<text class="btn-text">提交报修</text>
			</button>
		</view>
		
		<!-- 加载中 -->
		<view class="loading-mask" v-if="loading">
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
			deviceId: null,
			device: {},
			statusHistory: [],
			loading: false,
			historyPage: 1,
			historyPageSize: 10,
			hasMoreHistory: true
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.deviceId = parseInt(options.id)
			this.loadData()
		} else {
			utils.showError('缺少设备ID')
			uni.navigateBack()
		}
	},
	
	onShow() {
		if (this.deviceId) {
			this.loadData()
		}
	},
	
	onPullDownRefresh() {
		this.loadData().finally(() => {
			uni.stopPullDownRefresh()
		})
	},
	
	methods: {
		/**
		 * 加载设备详情数据
		 */
		async loadData() {
			this.loading = true
			
			try {
				// 加载设备详情
				const deviceRes = await api.device.getDetail(this.deviceId)
				if (deviceRes.code === 200) {
					this.device = deviceRes.data
					
					// 如果有故障，触发震动提醒
					if (this.device.status === 'fault' || this.device.status === 'warning') {
						utils.vibrate(2)
					}
				}
				
				// 加载状态历史
				await this.loadStatusHistory()
			} catch (err) {
				console.error('加载设备详情失败:', err)
				utils.showError('加载失败')
			} finally {
				this.loading = false
			}
		},
		
		/**
		 * 加载状态历史
		 */
		async loadStatusHistory() {
			try {
				const params = {
					page: this.historyPage,
					page_size: this.historyPageSize
				}
				
				const res = await api.device.getStatusHistory(this.deviceId, params)
				
				if (res.code === 200) {
					const items = res.data?.items || []
					
					if (this.historyPage === 1) {
						this.statusHistory = items
					} else {
						this.statusHistory = [...this.statusHistory, ...items]
					}
					
					this.hasMoreHistory = this.historyPage < (res.total_pages || 1)
				}
			} catch (err) {
				console.error('加载状态历史失败:', err)
			}
		},
		
		/**
		 * 加载更多历史
		 */
		loadMoreHistory() {
			if (this.hasMoreHistory) {
				this.historyPage++
				this.loadStatusHistory()
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
		 * 获取进度条宽度百分比
		 */
		getBarWidth(value, max) {
			if (!value) return '0%'
			const percent = Math.min((value / max) * 100, 100)
			return `${percent}%`
		},
		
		/**
		 * 获取进度条颜色类
		 */
		getBarClass(value, max) {
			if (!value) return 'bar-normal'
			const percent = value / max
			if (percent > 0.8) return 'bar-danger'
			if (percent > 0.6) return 'bar-warning'
			return 'bar-normal'
		},
		
		/**
		 * 跳转到保养记录
		 */
		goToMaintenance() {
			uni.navigateTo({
				url: '/pages/maintenance/task-list'
			})
		},
		
		/**
		 * 跳转到提交报修
		 */
		goToReport() {
			uni.navigateTo({
				url: `/pages/fault/report-form?device_id=${this.deviceId}`
			})
		}
	}
}
</script>

<style scoped>
.container {
	padding-bottom: 140rpx;
	background-color: #f5f5f5;
	min-height: 100vh;
}

/* 状态头部 */
.status-header {
	padding: 40rpx 32rpx;
	background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
}

.status-header.status-warning {
	background: linear-gradient(135deg, #faad14 0%, #ffc53d 100%);
}

.status-header.status-fault {
	background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
}

.header-content {
	display: flex;
	align-items: center;
}

.device-icon {
	width: 112rpx;
	height: 112rpx;
	border-radius: 24rpx;
	background-color: rgba(255, 255, 255, 0.2);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.icon-text {
	font-size: 56rpx;
}

.header-info {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.device-name {
	font-size: 36rpx;
	font-weight: bold;
	color: #fff;
	margin-bottom: 8rpx;
}

.device-code {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.status-badge {
	margin-left: 16rpx;
}

.badge-text {
	font-size: 24rpx;
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
	background-color: rgba(255, 255, 255, 0.2);
	color: #fff;
}

/* 卡片通用样式 */
.info-card,
.metrics-card,
.history-card {
	background-color: #fff;
	border-radius: 16rpx;
	margin: 24rpx;
	padding: 24rpx;
}

.card-title {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24rpx;
	padding-bottom: 16rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.title-text {
	font-size: 30rpx;
	font-weight: bold;
	color: #333;
}

.update-time {
	font-size: 22rpx;
	color: #999;
}

.more-text {
	font-size: 24rpx;
	color: #1677ff;
}

/* 实时运行数据 */
.metrics-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 24rpx;
}

.metric-item {
	flex: 1;
	min-width: calc(50% - 12rpx);
	background-color: #fafafa;
	border-radius: 12rpx;
	padding: 20rpx;
}

.metric-header {
	display: flex;
	align-items: center;
	margin-bottom: 12rpx;
}

.metric-icon {
	font-size: 28rpx;
	margin-right: 8rpx;
}

.metric-label {
	font-size: 24rpx;
	color: #666;
}

.metric-value-wrapper {
	display: flex;
	align-items: baseline;
	margin-bottom: 12rpx;
}

.metric-value {
	font-size: 40rpx;
	font-weight: bold;
	color: #333;
}

.metric-value.danger {
	color: #ff4d4f;
}

.metric-unit {
	font-size: 20rpx;
	color: #999;
	margin-left: 4rpx;
}

.metric-bar {
	height: 8rpx;
	background-color: #e8e8e8;
	border-radius: 4rpx;
	overflow: hidden;
}

.bar-fill {
	height: 100%;
	border-radius: 4rpx;
	transition: width 0.3s ease;
}

.bar-normal {
	background-color: #52c41a;
}

.bar-warning {
	background-color: #faad14;
}

.bar-danger {
	background-color: #ff4d4f;
}

/* 设备信息列表 */
.info-list {
	display: flex;
	flex-direction: column;
}

.info-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 0;
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

/* 状态历史 */
.history-list {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.history-item {
	display: flex;
	padding: 16rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
}

.history-item.danger-item {
	background-color: #fff2f0;
	border-left: 4rpx solid #ff4d4f;
}

.history-item.warning-item {
	background-color: #fffbe6;
	border-left: 4rpx solid #faad14;
}

.history-time {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding-right: 16rpx;
	margin-right: 16rpx;
	border-right: 1rpx solid #e8e8e8;
	min-width: 100rpx;
}

.time-text {
	font-size: 26rpx;
	font-weight: 500;
	color: #333;
}

.date-text {
	font-size: 20rpx;
	color: #999;
	margin-top: 4rpx;
}

.history-content {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.content-top {
	display: flex;
	align-items: center;
	margin-bottom: 8rpx;
}

.alarm-text {
	font-size: 22rpx;
	color: #ff4d4f;
	margin-left: 16rpx;
}

.content-metrics {
	display: flex;
	gap: 16rpx;
	flex-wrap: wrap;
}

.metric-text {
	font-size: 22rpx;
	color: #666;
}

/* 空状态 */
.empty-state {
	padding: 40rpx;
	text-align: center;
}

.empty-text {
	font-size: 26rpx;
	color: #999;
}

/* 底部操作栏 */
.bottom-actions {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background-color: #fff;
	padding: 20rpx 24rpx;
	padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
	display: flex;
	gap: 24rpx;
	box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
	flex: 1;
	height: 88rpx;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	gap: 8rpx;
}

.btn-warning {
	background: linear-gradient(135deg, #faad14 0%, #ffc53d 100%);
	color: #fff;
}

.btn-danger {
	background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
	color: #fff;
}

.btn-icon {
	font-size: 32rpx;
}

.btn-text {
	font-size: 28rpx;
	font-weight: 500;
}

/* 加载遮罩 */
.loading-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(255, 255, 255, 0.8);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.loading-text {
	font-size: 28rpx;
	color: #666;
}
</style>
