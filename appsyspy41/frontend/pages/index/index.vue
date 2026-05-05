<template>
	<view class="container">
		<!-- 用户信息头部 -->
		<view class="header-card">
			<view class="user-info">
				<view class="user-avatar">
					<text class="avatar-text">{{ userInitial }}</text>
				</view>
				<view class="user-detail">
					<text class="user-name">{{ safeUserName }}</text>
					<text class="user-role">{{ roleName }}</text>
				</view>
			</view>
			<view class="header-decoration">
				<text class="decoration-icon">⚙️</text>
			</view>
		</view>
		
		<!-- 统计卡片 -->
		<view class="stats-section">
			<view class="section-title">
				<text class="title-text">运行概览</text>
			</view>
			
			<view class="stats-grid">
				<!-- 设备统计 -->
				<view class="stat-card device-card" @click="goToDeviceList">
					<view class="stat-icon">
						<text class="icon-text">🏭</text>
					</view>
					<view class="stat-info">
						<text class="stat-value">{{ safeDeviceTotal }}</text>
						<text class="stat-label">设备总数</text>
					</view>
					<view class="stat-status">
						<view class="status-dot normal" v-if="showDeviceNormalDot"></view>
						<text class="status-text">{{ safeDeviceNormal }}正常</text>
					</view>
				</view>
				
				<!-- 故障预警 -->
				<view class="stat-card fault-card" @click="goToFaultList">
					<view class="stat-icon warning-icon" v-if="hasFaults">
						<text class="icon-text">⚠️</text>
					</view>
					<view class="stat-icon" v-else>
						<text class="icon-text">✅</text>
					</view>
					<view class="stat-info">
						<text class="stat-value">{{ faultCount }}</text>
						<text class="stat-label">故障预警</text>
					</view>
					<view class="stat-status">
						<view class="status-dot fault" v-if="hasFaults"></view>
						<text class="status-text">{{ hasFaults ? '需处理' : '正常' }}</text>
					</view>
				</view>
				
				<!-- 保养任务 -->
				<view class="stat-card maintenance-card" @click="goToMaintenanceList">
					<view class="stat-icon">
						<text class="icon-text">🔧</text>
					</view>
					<view class="stat-info">
						<text class="stat-value">{{ safeMaintenancePending }}</text>
						<text class="stat-label">待保养</text>
					</view>
					<view class="stat-status">
						<view class="status-dot warning" v-if="showMaintenanceOverdueDot"></view>
						<text class="status-text">{{ safeMaintenanceOverdue }}超期</text>
					</view>
				</view>
				
				<!-- 待处理报修 -->
				<view class="stat-card report-card" @click="goToFaultList">
					<view class="stat-icon">
						<text class="icon-text">📋</text>
					</view>
					<view class="stat-info">
						<text class="stat-value">{{ safeFaultPending }}</text>
						<text class="stat-label">待报修</text>
					</view>
					<view class="stat-status">
						<view class="status-dot processing"></view>
						<text class="status-text">{{ safeFaultProcessing }}处理中</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 关键设备状态 -->
		<view class="devices-section">
			<view class="section-header">
				<view class="section-title">
					<text class="title-text">关键设备状态</text>
				</view>
				<view class="more-btn" @click="goToDeviceList">
					<text class="more-text">查看全部</text>
					<text class="more-arrow">›</text>
				</view>
			</view>
			
			<view class="device-list" v-if="keyDevices.length > 0">
				<view 
					v-for="(device, index) in keyDevices" 
					:key="device.id"
					class="device-item"
					:class="{ 'fault-item': device.status === 'fault' || device.status === 'warning' }"
					@click="goToDeviceDetail(device.id)"
				>
					<view class="device-left">
						<view 
							class="device-status-icon"
							:class="`status-${device.status}`"
						>
							<text class="icon-text">{{ getDeviceIcon(device.device_type) }}</text>
						</view>
						<view class="device-info">
							<text class="device-name">{{ device.device_name }}</text>
							<text class="device-code">{{ device.device_code }}</text>
						</view>
					</view>
					
					<view class="device-right">
						<view class="status-tag">
							<text class="tag-text" :class="utils.getStatusClass(device.status)">
								{{ utils.getStatusName(device.status) }}
							</text>
						</view>
						<view class="device-metrics" v-if="device.current_status">
							<view class="metric-item">
								<text class="metric-label">电流</text>
								<text class="metric-value">{{ utils.formatNumber(device.current_status.current) }}A</text>
							</view>
							<view class="metric-item">
								<text class="metric-label">温度</text>
								<text class="metric-value">{{ utils.formatNumber(device.current_status.temperature) }}°C</text>
							</view>
						</view>
					</view>
				</view>
			</view>
			
			<view class="empty-state" v-else>
				<text class="empty-text">暂无设备数据</text>
			</view>
		</view>
		
		<!-- 快捷操作 -->
		<view class="quick-actions">
			<view class="section-title">
				<text class="title-text">快捷操作</text>
			</view>
			
			<view class="actions-grid">
				<view class="action-item" @click="goToReportForm">
					<view class="action-icon report-icon">
						<text class="icon-text">🚨</text>
					</view>
					<text class="action-label">提交报修</text>
				</view>
				
				<view class="action-item" @click="goToMaintenanceList">
					<view class="action-icon maintenance-icon">
						<text class="icon-text">🔧</text>
					</view>
					<text class="action-label">保养任务</text>
				</view>
				
				<view class="action-item" @click="goToDeviceList">
					<view class="action-icon device-icon">
						<text class="icon-text">🏭</text>
					</view>
					<text class="action-label">设备列表</text>
				</view>
				
				<view class="action-item" @click="goToMyPage">
					<view class="action-icon user-icon">
						<text class="icon-text">👤</text>
					</view>
					<text class="action-label">个人中心</text>
				</view>
			</view>
		</view>
		
		<!-- 下拉刷新提示 -->
		<view class="refresh-tip" v-if="refreshing">
			<text class="tip-text">刷新中...</text>
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
			currentUser: null,
			quickStats: {},
			keyDevices: [],
			refreshing: false,
			alertTimer: null
		}
	},
	
	computed: {
		userInitial() {
			if (this.currentUser && this.currentUser.real_name) {
				return this.currentUser.real_name.charAt(0)
			}
			return '用'
		},
		
		roleName() {
			const role = this.currentUser && this.currentUser.role
			return utils.getRoleName(role)
		},
		
		faultCount() {
			const warning = (this.quickStats && this.quickStats.devices && this.quickStats.devices.warning) || 0
			const fault = (this.quickStats && this.quickStats.devices && this.quickStats.devices.fault) || 0
			return warning + fault
		},
		
		hasFaults() {
			return this.faultCount > 0
		},
		
		safeUserName() {
			return (this.currentUser && this.currentUser.real_name) || '用户'
		},
		
		safeDeviceTotal() {
			return (this.quickStats && this.quickStats.devices && this.quickStats.devices.total) || 0
		},
		
		safeDeviceNormal() {
			return (this.quickStats && this.quickStats.devices && this.quickStats.devices.normal) || 0
		},
		
		showDeviceNormalDot() {
			return this.quickStats && this.quickStats.devices && this.quickStats.devices.normal > 0
		},
		
		safeMaintenancePending() {
			return (this.quickStats && this.quickStats.maintenance && this.quickStats.maintenance.pending) || 0
		},
		
		safeMaintenanceOverdue() {
			return (this.quickStats && this.quickStats.maintenance && this.quickStats.maintenance.overdue) || 0
		},
		
		showMaintenanceOverdueDot() {
			return this.quickStats && this.quickStats.maintenance && this.quickStats.maintenance.overdue > 0
		},
		
		safeFaultPending() {
			return (this.quickStats && this.quickStats.faults && this.quickStats.faults.pending) || 0
		},
		
		safeFaultProcessing() {
			return (this.quickStats && this.quickStats.faults && this.quickStats.faults.processing) || 0
		}
	},
	
	onLoad() {
		this.currentUser = utils.getCurrentUser()
		this.loadData()
	},
	
	onShow() {
		this.loadData()
		this.startAlertMonitor()
	},
	
	onUnload() {
		this.stopAlertMonitor()
	},
	
	onPullDownRefresh() {
		this.refreshing = true
		this.loadData().finally(() => {
			uni.stopPullDownRefresh()
			this.refreshing = false
		})
	},
	
	methods: {
		/**
		 * 加载数据
		 */
		async loadData() {
			try {
				// 加载快速统计
				const statsRes = await api.test.getQuickStats()
				if (statsRes.code === 200) {
					this.quickStats = statsRes.data
					
					// 如果有故障设备，触发震动提醒
					if (this.hasFaults) {
						utils.vibrate(2) // 长震动
					}
				}
				
				// 加载设备列表（前5个）
				const deviceRes = await api.device.getList({ page_size: 5 })
				if (deviceRes.code === 200) {
					this.keyDevices = deviceRes.data?.items || []
				}
			} catch (err) {
				console.error('加载数据失败:', err)
			}
		},
		
		/**
		 * 启动故障报警监控
		 */
		startAlertMonitor() {
			// 每30秒检查一次故障状态
			this.alertTimer = setInterval(() => {
				this.checkAlerts()
			}, 30000)
		},
		
		/**
		 * 停止故障报警监控
		 */
		stopAlertMonitor() {
			if (this.alertTimer) {
				clearInterval(this.alertTimer)
				this.alertTimer = null
			}
		},
		
		/**
		 * 检查报警状态
		 */
		async checkAlerts() {
			try {
				const res = await api.test.getQuickStats()
				if (res.code === 200) {
					const newFaultCount = (res.data?.devices?.warning || 0) + 
										 (res.data?.devices?.fault || 0)
					
					// 如果故障数量增加，触发震动提醒
					if (newFaultCount > this.faultCount) {
						utils.vibrate(2) // 长震动
						uni.showToast({
							title: '有新的设备故障报警！',
							icon: 'none',
							duration: 3000
						})
					}
					
					this.quickStats = res.data
				}
			} catch (err) {
				console.error('检查报警失败:', err)
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
		 * 页面跳转
		 */
		goToDeviceList() {
			uni.navigateTo({
				url: '/pages/device/list'
			})
		},
		
		goToDeviceDetail(deviceId) {
			uni.navigateTo({
				url: `/pages/device/detail?id=${deviceId}`
			})
		},
		
		goToMaintenanceList() {
			uni.navigateTo({
				url: '/pages/maintenance/task-list'
			})
		},
		
		goToFaultList() {
			uni.navigateTo({
				url: '/pages/fault/report-list'
			})
		},
		
		goToReportForm() {
			uni.navigateTo({
				url: '/pages/fault/report-form'
			})
		},
		
		goToMyPage() {
			uni.switchTab({
				url: '/pages/my/my'
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

/* 头部卡片 */
.header-card {
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
	border-radius: 24rpx;
	padding: 32rpx;
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24rpx;
}

.user-info {
	display: flex;
	align-items: center;
}

.user-avatar {
	width: 96rpx;
	height: 96rpx;
	border-radius: 50%;
	background-color: rgba(255, 255, 255, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.avatar-text {
	font-size: 40rpx;
	font-weight: bold;
	color: #fff;
}

.user-detail {
	display: flex;
	flex-direction: column;
}

.user-name {
	font-size: 36rpx;
	font-weight: bold;
	color: #fff;
	margin-bottom: 8rpx;
}

.user-role {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.header-decoration {
	opacity: 0.3;
}

.decoration-icon {
	font-size: 80rpx;
}

/* 统计区域 */
.stats-section {
	margin-bottom: 24rpx;
}

.section-title {
	margin-bottom: 16rpx;
}

.title-text {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.stats-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.stat-card {
	flex: 1;
	min-width: calc(50% - 8rpx);
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	display: flex;
	flex-direction: column;
}

.stat-icon {
	width: 64rpx;
	height: 64rpx;
	border-radius: 12rpx;
	background-color: #f5f5f5;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 16rpx;
}

.warning-icon {
	background-color: #fffbe6;
	animation: pulse 1s infinite;
}

@keyframes pulse {
	0%, 100% { transform: scale(1); }
	50% { transform: scale(1.1); }
}

.icon-text {
	font-size: 32rpx;
}

.stat-info {
	margin-bottom: 12rpx;
}

.stat-value {
	font-size: 40rpx;
	font-weight: bold;
	color: #333;
}

.stat-label {
	font-size: 24rpx;
	color: #999;
	margin-left: 8rpx;
}

.stat-status {
	display: flex;
	align-items: center;
}

.status-dot {
	width: 12rpx;
	height: 12rpx;
	border-radius: 50%;
	margin-right: 8rpx;
}

.status-dot.normal {
	background-color: #52c41a;
}

.status-dot.warning {
	background-color: #faad14;
}

.status-dot.fault {
	background-color: #ff4d4f;
}

.status-dot.processing {
	background-color: #13c2c2;
}

.status-text {
	font-size: 22rpx;
	color: #999;
}

/* 设备列表区域 */
.devices-section {
	margin-bottom: 24rpx;
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.more-btn {
	display: flex;
	align-items: center;
}

.more-text {
	font-size: 26rpx;
	color: #1677ff;
}

.more-arrow {
	font-size: 28rpx;
	color: #1677ff;
	margin-left: 4rpx;
}

.device-list {
	background-color: #fff;
	border-radius: 16rpx;
	overflow: hidden;
}

.device-item {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	padding: 24rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.device-item:last-child {
	border-bottom: none;
}

.device-item.fault-item {
	background-color: #fffbfb;
}

.device-left {
	display: flex;
	align-items: flex-start;
	flex: 1;
}

.device-status-icon {
	width: 80rpx;
	height: 80rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.device-status-icon.status-normal {
	background-color: #f6ffed;
}

.device-status-icon.status-warning {
	background-color: #fffbe6;
	animation: blink 1s infinite;
}

.device-status-icon.status-fault {
	background-color: #fff2f0;
	animation: blink 0.5s infinite;
}

@keyframes blink {
	0%, 100% { opacity: 1; }
	50% { opacity: 0.5; }
}

.device-info {
	display: flex;
	flex-direction: column;
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
}

.device-right {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
}

.status-tag {
	margin-bottom: 12rpx;
}

.tag-text {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 6rpx;
}

.device-metrics {
	display: flex;
	gap: 16rpx;
}

.metric-item {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
}

.metric-label {
	font-size: 20rpx;
	color: #999;
	margin-bottom: 4rpx;
}

.metric-value {
	font-size: 24rpx;
	color: #333;
	font-weight: 500;
}

.empty-state {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 48rpx;
	text-align: center;
}

.empty-text {
	font-size: 28rpx;
	color: #999;
}

/* 快捷操作 */
.quick-actions {
	margin-bottom: 24rpx;
}

.actions-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
}

.action-item {
	flex: 1;
	min-width: calc(25% - 12rpx);
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 16rpx 8rpx;
}

.action-icon {
	width: 88rpx;
	height: 88rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 12rpx;
}

.report-icon {
	background-color: #fff2f0;
}

.maintenance-icon {
	background-color: #fffbe6;
}

.device-icon {
	background-color: #e6f7ff;
}

.user-icon {
	background-color: #f6ffed;
}

.action-label {
	font-size: 24rpx;
	color: #666;
}

/* 刷新提示 */
.refresh-tip {
	text-align: center;
	padding: 24rpx;
}

.tip-text {
	font-size: 24rpx;
	color: #999;
}
</style>
