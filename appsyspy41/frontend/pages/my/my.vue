<template>
	<view class="container">
		<!-- 用户信息头部 -->
		<view class="user-header">
			<view class="header-bg"></view>
			<view class="user-info">
				<view class="user-avatar">
					<text class="avatar-text">{{ userInitial }}</text>
				</view>
				<view class="user-detail">
					<text class="user-name">{{ safeUserName }}</text>
					<view class="user-meta">
						<text class="user-role">{{ roleName }}</text>
						<text class="user-username">@{{ safeUserUsername }}</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 我的统计 -->
		<view class="stats-card">
			<view class="card-title">
				<text class="title-text">我的概览</text>
			</view>
			<view class="stats-grid">
				<view class="stat-item" @click="goToMyReports">
					<view class="stat-icon report-icon">
						<text class="icon-text">📋</text>
					</view>
					<text class="stat-value">{{ safeFaultsPending }}</text>
					<text class="stat-label">待处理报修</text>
				</view>
				<view class="stat-item" @click="goToMaintenance">
					<view class="stat-icon maintenance-icon">
						<text class="icon-text">🔧</text>
					</view>
					<text class="stat-value">{{ safeMaintenancePending }}</text>
					<text class="stat-label">待保养任务</text>
				</view>
				<view class="stat-item" @click="goToDeviceList">
					<view class="stat-icon device-icon">
						<text class="icon-text">🏭</text>
					</view>
					<text class="stat-value">{{ safeDevicesTotal }}</text>
					<text class="stat-label">设备总数</text>
				</view>
			</view>
		</view>
		
		<!-- 功能菜单 -->
		<view class="menu-section">
			<view class="menu-group">
				<view class="menu-item" @click="goToMyReports">
					<view class="item-left">
						<view class="item-icon blue-icon">
							<text class="icon-text">📝</text>
						</view>
						<text class="item-text">我的报修</text>
					</view>
					<view class="item-right">
						<text class="item-badge" v-if="showFaultsPendingBadge">
							{{ safeFaultsPending }}
						</text>
						<text class="item-arrow">›</text>
					</view>
				</view>
				
				<view class="menu-item" @click="goToMaintenance">
					<view class="item-left">
						<view class="item-icon orange-icon">
							<text class="icon-text">🔧</text>
						</view>
						<text class="item-text">保养任务</text>
					</view>
					<view class="item-right">
						<text class="item-badge" v-if="showMaintenanceOverdueBadge">
							{{ safeMaintenanceOverdue }}
						</text>
						<text class="item-arrow">›</text>
					</view>
				</view>
				
				<view class="menu-item" @click="goToDeviceList">
					<view class="item-left">
						<view class="item-icon green-icon">
							<text class="icon-text">🏭</text>
						</view>
						<text class="item-text">设备列表</text>
					</view>
					<view class="item-right">
						<text class="item-arrow">›</text>
					</view>
				</view>
			</view>
			
			<!-- 测试工具菜单（仅管理员可见） -->
			<view class="menu-group" v-if="isAdmin">
				<view class="menu-header">
					<text class="header-text">测试工具</text>
				</view>
				
				<view class="menu-item" @click="resetDatabase">
					<view class="item-left">
						<view class="item-icon red-icon">
							<text class="icon-text">🔄</text>
						</view>
						<text class="item-text">重置数据库</text>
					</view>
					<view class="item-right">
						<text class="item-arrow">›</text>
					</view>
				</view>
				
				<view class="menu-item" @click="generateTestData">
					<view class="item-left">
						<view class="item-icon purple-icon">
							<text class="icon-text">📊</text>
						</view>
						<text class="item-text">生成测试数据</text>
					</view>
					<view class="item-right">
						<text class="item-arrow">›</text>
					</view>
				</view>
				
				<view class="menu-item" @click="simulateFaultAlarm">
					<view class="item-left">
						<view class="item-icon danger-icon">
							<text class="icon-text">⚠️</text>
						</view>
						<text class="item-text">模拟故障报警</text>
					</view>
					<view class="item-right">
						<text class="item-arrow">›</text>
					</view>
				</view>
			</view>
			
			<!-- 设置菜单 -->
			<view class="menu-group">
				<view class="menu-item" @click="showAbout">
					<view class="item-left">
						<view class="item-icon gray-icon">
							<text class="icon-text">ℹ️</text>
						</view>
						<text class="item-text">关于我们</text>
					</view>
					<view class="item-right">
						<text class="item-arrow">›</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 退出登录按钮 -->
		<view class="logout-section">
			<button class="logout-btn" @click="handleLogout">
				<text class="btn-text">退出登录</text>
			</button>
		</view>
		
		<!-- 设备选择弹窗（用于模拟故障） -->
		<view class="modal-mask" v-if="showDeviceModal" @click="hideDeviceModal">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">选择设备</text>
					<text class="modal-close" @click="hideDeviceModal">✕</text>
				</view>
				<view class="modal-body">
					<view 
						v-for="(device, index) in deviceList" 
						:key="device.id"
						class="device-option"
						:class="{ 'active': selectedDeviceId === device.id }"
						@click="selectDevice(device.id)"
					>
						<view class="option-info">
							<text class="option-name">{{ device.device_name }}</text>
							<text class="option-code">{{ device.device_code }}</text>
						</view>
						<view class="option-status">
							<text class="status-text" :class="utils.getStatusClass(device.status)">
								{{ utils.getStatusName(device.status) }}
							</text>
						</view>
					</view>
				</view>
				<view class="modal-footer">
					<button class="modal-btn cancel-btn" @click="hideDeviceModal">取消</button>
					<button class="modal-btn confirm-btn" @click="confirmSimulateFault">确认模拟</button>
				</view>
			</view>
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
			showDeviceModal: false,
			deviceList: [],
			selectedDeviceId: null
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
		
		safeUserName() {
			return (this.currentUser && this.currentUser.real_name) || '用户'
		},
		
		safeUserUsername() {
			return (this.currentUser && this.currentUser.username) || ''
		},
		
		safeFaultsPending() {
			return (this.quickStats && this.quickStats.faults && this.quickStats.faults.pending) || 0
		},
		
		safeMaintenancePending() {
			return (this.quickStats && this.quickStats.maintenance && this.quickStats.maintenance.pending) || 0
		},
		
		safeDevicesTotal() {
			return (this.quickStats && this.quickStats.devices && this.quickStats.devices.total) || 0
		},
		
		showFaultsPendingBadge() {
			return this.quickStats && this.quickStats.faults && this.quickStats.faults.pending > 0
		},
		
		showMaintenanceOverdueBadge() {
			return this.quickStats && this.quickStats.maintenance && this.quickStats.maintenance.overdue > 0
		},
		
		safeMaintenanceOverdue() {
			return (this.quickStats && this.quickStats.maintenance && this.quickStats.maintenance.overdue) || 0
		},
		
		isAdmin() {
			return this.currentUser && this.currentUser.role === 'admin'
		}
	},
	
	onLoad() {
		this.currentUser = utils.getCurrentUser()
		this.loadData()
	},
	
	onShow() {
		this.currentUser = utils.getCurrentUser()
		this.loadData()
	},
	
	onPullDownRefresh() {
		this.loadData().finally(() => {
			uni.stopPullDownRefresh()
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
				}
				
				// 加载设备列表（用于模拟故障）
				const deviceRes = await api.device.getList({ page_size: 20 })
				if (deviceRes.code === 200) {
					this.deviceList = deviceRes.data?.items || []
				}
			} catch (err) {
				console.error('加载数据失败:', err)
			}
		},
		
		/**
		 * 页面跳转
		 */
		goToMyReports() {
			uni.switchTab({
				url: '/pages/fault/report-list'
			})
		},
		
		goToMaintenance() {
			uni.switchTab({
				url: '/pages/maintenance/task-list'
			})
		},
		
		goToDeviceList() {
			uni.switchTab({
				url: '/pages/device/list'
			})
		},
		
		/**
		 * 重置数据库
		 */
		async resetDatabase() {
			const confirmed = await utils.showConfirm(
				'确定要重置数据库吗？所有数据将被清除并重新初始化。',
				'确认重置'
			)
			
			if (!confirmed) return
			
			utils.showLoading('重置中...')
			
			try {
				const res = await api.test.resetDatabase()
				if (res.code === 200) {
					utils.showSuccess('重置成功')
					this.loadData()
				}
			} catch (err) {
				console.error('重置数据库失败:', err)
				utils.showError('重置失败')
			} finally {
				utils.hideLoading()
			}
		},
		
		/**
		 * 生成测试数据
		 */
		async generateTestData() {
			utils.showLoading('生成中...')
			
			try {
				const res = await api.test.generateDeviceStatus(null, 24)
				if (res.code === 200) {
					utils.showSuccess('生成成功')
					this.loadData()
				}
			} catch (err) {
				console.error('生成测试数据失败:', err)
				utils.showError('生成失败')
			} finally {
				utils.hideLoading()
			}
		},
		
		/**
		 * 模拟故障报警
		 */
		simulateFaultAlarm() {
			if (this.deviceList.length === 0) {
				utils.showError('暂无设备可选')
				return
			}
			this.selectedDeviceId = this.deviceList[0]?.id || null
			this.showDeviceModal = true
		},
		
		/**
		 * 隐藏设备选择弹窗
		 */
		hideDeviceModal() {
			this.showDeviceModal = false
		},
		
		/**
		 * 选择设备
		 */
		selectDevice(deviceId) {
			this.selectedDeviceId = deviceId
		},
		
		/**
		 * 确认模拟故障
		 */
		async confirmSimulateFault() {
			if (!this.selectedDeviceId) {
				utils.showError('请选择设备')
				return
			}
			
			this.hideDeviceModal()
			utils.showLoading('模拟中...')
			
			try {
				const res = await api.test.generateFaultAlarm(this.selectedDeviceId, 'temperature')
				if (res.code === 200) {
					utils.showSuccess('模拟成功')
					utils.vibrate(2)
					this.loadData()
				}
			} catch (err) {
				console.error('模拟故障失败:', err)
				utils.showError('模拟失败')
			} finally {
				utils.hideLoading()
			}
		},
		
		/**
		 * 显示关于
		 */
		showAbout() {
			uni.showModal({
				title: '关于',
				content: '设备管理系统 v1.0.0\n\n技术栈:\n- 后端: Python + FastAPI + SQLite\n- 前端: UniApp + Vue.js\n\n功能模块:\n- 设备状态监控\n- 保养任务管理\n- 故障报修处理',
				showCancel: false
			})
		},
		
		/**
		 * 退出登录
		 */
		async handleLogout() {
			const confirmed = await utils.showConfirm(
				'确定要退出登录吗？',
				'确认退出'
			)
			
			if (!confirmed) return
			
			// 清除登录信息
			utils.clearLoginInfo()
			
			// 跳转到登录页
			uni.reLaunch({
				url: '/pages/login/login'
			})
		}
	}
}
</script>

<style scoped>
.container {
	padding-bottom: 40rpx;
	background-color: #f5f5f5;
	min-height: 100vh;
}

/* 用户信息头部 */
.user-header {
	position: relative;
	padding: 48rpx 32rpx;
	padding-bottom: 80rpx;
}

.header-bg {
	position: absolute;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
	border-radius: 0 0 48rpx 48rpx;
}

.user-info {
	position: relative;
	display: flex;
	align-items: center;
}

.user-avatar {
	width: 120rpx;
	height: 120rpx;
	border-radius: 50%;
	background-color: rgba(255, 255, 255, 0.3);
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.avatar-text {
	font-size: 48rpx;
	font-weight: bold;
	color: #fff;
}

.user-detail {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.user-name {
	font-size: 36rpx;
	font-weight: bold;
	color: #fff;
	margin-bottom: 8rpx;
}

.user-meta {
	display: flex;
	align-items: center;
	gap: 16rpx;
}

.user-role {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.9);
	padding: 4rpx 16rpx;
	background-color: rgba(255, 255, 255, 0.2);
	border-radius: 20rpx;
}

.user-username {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.7);
}

/* 统计卡片 */
.stats-card {
	margin: -40rpx 24rpx 24rpx;
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-title {
	margin-bottom: 20rpx;
}

.title-text {
	font-size: 28rpx;
	font-weight: bold;
	color: #333;
}

.stats-grid {
	display: flex;
	gap: 24rpx;
}

.stat-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20rpx 0;
}

.stat-icon {
	width: 80rpx;
	height: 80rpx;
	border-radius: 16rpx;
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

.stat-value {
	font-size: 36rpx;
	font-weight: bold;
	color: #333;
	margin-bottom: 4rpx;
}

.stat-label {
	font-size: 22rpx;
	color: #999;
}

/* 菜单区域 */
.menu-section {
	margin: 24rpx;
}

.menu-group {
	background-color: #fff;
	border-radius: 16rpx;
	overflow: hidden;
	margin-bottom: 24rpx;
}

.menu-header {
	padding: 16rpx 24rpx;
	background-color: #fafafa;
}

.header-text {
	font-size: 24rpx;
	color: #999;
}

.menu-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 28rpx 24rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
	border-bottom: none;
}

.item-left {
	display: flex;
	align-items: center;
}

.item-icon {
	width: 64rpx;
	height: 64rpx;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.blue-icon {
	background-color: #e6f7ff;
}

.orange-icon {
	background-color: #fffbe6;
}

.green-icon {
	background-color: #f6ffed;
}

.red-icon {
	background-color: #fff2f0;
}

.purple-icon {
	background-color: #f9f0ff;
}

.danger-icon {
	background-color: #fff1f0;
}

.gray-icon {
	background-color: #f5f5f5;
}

.item-text {
	font-size: 30rpx;
	color: #333;
}

.item-right {
	display: flex;
	align-items: center;
	gap: 8rpx;
}

.item-badge {
	font-size: 20rpx;
	color: #fff;
	background-color: #ff4d4f;
	padding: 2rpx 10rpx;
	border-radius: 16rpx;
	min-width: 32rpx;
	text-align: center;
}

.item-arrow {
	font-size: 32rpx;
	color: #ccc;
}

/* 退出登录 */
.logout-section {
	margin: 48rpx 24rpx;
}

.logout-btn {
	width: 100%;
	height: 88rpx;
	background-color: #fff;
	border: 2rpx solid #ff4d4f;
	border-radius: 12rpx;
}

.btn-text {
	font-size: 30rpx;
	color: #ff4d4f;
	font-weight: 500;
}

/* 弹窗样式 */
.modal-mask {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background-color: rgba(0, 0, 0, 0.5);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
}

.modal-content {
	width: 80%;
	max-height: 70vh;
	background-color: #fff;
	border-radius: 16rpx;
	overflow: hidden;
	display: flex;
	flex-direction: column;
}

.modal-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 24rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.modal-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333;
}

.modal-close {
	font-size: 36rpx;
	color: #999;
}

.modal-body {
	flex: 1;
	overflow-y: auto;
	max-height: 400rpx;
	padding: 16rpx;
}

.device-option {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 20rpx 16rpx;
	border-radius: 12rpx;
	margin-bottom: 8rpx;
	border: 2rpx solid transparent;
}

.device-option.active {
	background-color: #e6f7ff;
	border-color: #1677ff;
}

.option-info {
	display: flex;
	flex-direction: column;
}

.option-name {
	font-size: 28rpx;
	color: #333;
	margin-bottom: 4rpx;
}

.option-code {
	font-size: 22rpx;
	color: #999;
}

.option-status {
	flex-shrink: 0;
}

.status-text {
	font-size: 22rpx;
	padding: 4rpx 12rpx;
	border-radius: 6rpx;
}

.modal-footer {
	display: flex;
	border-top: 1rpx solid #f0f0f0;
}

.modal-btn {
	flex: 1;
	height: 88rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 30rpx;
}

.cancel-btn {
	color: #666;
	border-right: 1rpx solid #f0f0f0;
}

.confirm-btn {
	color: #1677ff;
	font-weight: 500;
}
</style>
