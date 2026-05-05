<template>
	<view class="container">
		<!-- 状态头部 -->
		<view class="status-header" :class="`status-${reportData.status}`">
			<view class="status-icon">
				<text class="icon-text">{{ getStatusIcon(reportData.status) }}</text>
			</view>
			<view class="status-info">
				<view class="status-row">
					<text class="status-text" :class="utils.getStatusClass(reportData.status)">
						{{ utils.getStatusName(reportData.status) }}
					</text>
					<view class="level-badge" :class="reportData.fault_level">
						<text class="level-icon">{{ getLevelIcon(reportData.fault_level) }}</text>
						<text class="level-text">{{ utils.getFaultLevelName(reportData.fault_level) }}级</text>
					</view>
				</view>
				<text class="report-title">{{ reportData.fault_title }}</text>
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
					<text class="device-name">{{ reportData.device_name || '-' }}</text>
					<text class="device-code">编号: {{ reportData.device_code || '-' }}</text>
					<text class="device-location">位置: {{ reportData.location || '-' }}</text>
				</view>
			</view>
		</view>
		
		<!-- 报修信息 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">报修信息</text>
			</view>
			<view class="info-list">
				<view class="info-item">
					<text class="info-label">上报人</text>
					<text class="info-value">{{ reportData.reporter_name || '-' }}</text>
				</view>
				<view class="info-item" v-if="reportData.reporter_phone">
					<text class="info-label">联系电话</text>
					<text class="info-value link" @click="makePhoneCall(reportData.reporter_phone)">
						{{ reportData.reporter_phone }} 📞
					</text>
				</view>
				<view class="info-item">
					<text class="info-label">上报时间</text>
					<text class="info-value">{{ utils.formatDateTime(reportData.created_at) }}</text>
				</view>
				<view class="info-item" v-if="reportData.assignee_name">
					<text class="info-label">维修人员</text>
					<text class="info-value">{{ reportData.assignee_name }}</text>
				</view>
				<view class="info-item" v-if="reportData.assignee_phone">
					<text class="info-label">维修电话</text>
					<text class="info-value link" @click="makePhoneCall(reportData.assignee_phone)">
						{{ reportData.assignee_phone }} 📞
					</text>
				</view>
			</view>
		</view>
		
		<!-- 故障描述 -->
		<view class="section-card" v-if="reportData.fault_description">
			<view class="section-header">
				<text class="section-title">故障描述</text>
			</view>
			<view class="description-content">
				<text class="description-text">{{ reportData.fault_description }}</text>
			</view>
		</view>
		
		<!-- 故障照片 -->
		<view class="section-card" v-if="photoUrls.length > 0">
			<view class="section-header">
				<text class="section-title">故障照片</text>
				<text class="photo-count">{{ photoUrls.length }}张</text>
			</view>
			<view class="photo-grid">
				<view 
					v-for="(photo, index) in photoUrls" 
					:key="index"
					class="photo-item"
					@click="previewPhoto(photo, index)"
				>
					<image class="photo-img" :src="photo" mode="aspectFill"></image>
				</view>
			</view>
		</view>
		
		<!-- 维修记录 -->
		<view class="section-card" v-if="repairRecords.length > 0">
			<view class="section-header">
				<text class="section-title">维修进度</text>
				<text class="record-count">{{ repairRecords.length }}条记录</text>
			</view>
			<view class="timeline">
				<view 
					v-for="(record, index) in repairRecords" 
					:key="record.id"
					class="timeline-item"
				>
					<view class="timeline-left">
						<view class="timeline-dot" :class="getActionClass(record.action)"></view>
						<view class="timeline-line" v-if="index < repairRecords.length - 1"></view>
					</view>
					<view class="timeline-content">
						<view class="content-header">
							<text class="action-text">{{ getActionText(record.action) }}</text>
							<text class="progress-text" v-if="record.progress !== null">
								进度: {{ record.progress }}%
							</text>
						</view>
						<view class="content-body" v-if="record.description">
							<text class="description">{{ record.description }}</text>
						</view>
						<view class="content-footer">
							<text class="operator">{{ record.operator_name || '系统' }}</text>
							<text class="time">{{ utils.formatDateTime(record.created_at) }}</text>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 操作按钮区域 -->
		<view class="action-section" v-if="reportData.status !== 'completed'">
			<!-- 待处理状态：分配或取消 -->
			<view class="action-row" v-if="reportData.status === 'pending'">
				<button class="action-btn btn-primary" @click="showAssignModal">
					<text>分配维修人员</text>
				</button>
				<button class="action-btn btn-secondary" @click="handleCancel">
					<text>取消报修</text>
				</button>
			</view>
			
			<!-- 处理中状态：更新进度或完成 -->
			<view class="action-row" v-else-if="reportData.status === 'processing'">
				<button class="action-btn btn-primary" @click="showProgressModal">
					<text>更新进度</text>
				</button>
				<button class="action-btn btn-success" @click="handleComplete">
					<text>完成维修</text>
				</button>
			</view>
		</view>
		
		<!-- 已完成提示 -->
		<view class="completed-section" v-else>
			<view class="completed-icon">
				<text class="icon-text">✅</text>
			</view>
			<text class="completed-text">该报修已完成</text>
		</view>
		
		<!-- 分配维修人员弹窗 -->
		<view class="modal-mask" v-if="showAssign" @click="closeAssignModal">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">选择维修人员</text>
				</view>
				<view class="modal-body">
					<view class="user-list">
						<view 
							v-for="(user, index) in repairUsers" 
							:key="user.id"
							class="user-item"
							:class="{ 'selected': selectedUserId === user.id }"
							@click="selectUser(user)"
						>
							<view class="user-avatar">
								<text class="avatar-text">{{ getInitial(user.real_name) }}</text>
							</view>
							<view class="user-info">
								<text class="user-name">{{ user.real_name }}</text>
								<text class="user-phone">{{ user.phone || '-' }}</text>
							</view>
							<view class="user-check" v-if="selectedUserId === user.id">
								<text class="check-icon">✓</text>
							</view>
						</view>
					</view>
				</view>
				<view class="modal-footer">
					<button class="modal-btn cancel" @click="closeAssignModal">取消</button>
					<button class="modal-btn confirm" :disabled="!selectedUser" @click="handleAssign">确认分配</button>
				</view>
			</view>
		</view>
		
		<!-- 更新进度弹窗 -->
		<view class="modal-mask" v-if="showProgress" @click="closeProgressModal">
			<view class="modal-content" @click.stop>
				<view class="modal-header">
					<text class="modal-title">更新维修进度</text>
				</view>
				<view class="modal-body">
					<view class="form-item">
						<text class="form-label">进度百分比</text>
						<view class="progress-selector">
							<button 
								v-for="percent in progressOptions" 
								:key="percent"
								class="percent-btn"
								:class="{ 'active': progressForm.progress === percent }"
								@click="progressForm.progress = percent"
							>
								<text>{{ percent }}%</text>
							</button>
						</view>
					</view>
					<view class="form-item">
						<text class="form-label">进度描述</text>
						<textarea 
							class="form-textarea" 
							placeholder="请描述当前维修进度..."
							v-model="progressForm.description"
						></textarea>
					</view>
				</view>
				<view class="modal-footer">
					<button class="modal-btn cancel" @click="closeProgressModal">取消</button>
					<button class="modal-btn confirm" @click="handleUpdateProgress">确认更新</button>
				</view>
			</view>
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
			reportId: null,
			reportData: {},
			repairRecords: [],
			photoUrls: [],
			loading: false,
			showAssign: false,
			showProgress: false,
			repairUsers: [],
			selectedUser: null,
			progressForm: {
				progress: 50,
				description: ''
			},
			progressOptions: [10, 25, 50, 75, 90, 100]
		}
	},
	
	computed: {
		selectedUserId() {
			return this.selectedUser && this.selectedUser.id
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.reportId = parseInt(options.id)
			this.loadReportDetail()
		}
	},
	
	onShow() {
		if (this.reportId) {
			this.loadReportDetail()
		}
	},
	
	methods: {
		/**
		 * 加载报修详情
		 */
		async loadReportDetail() {
			if (!this.reportId) return
			
			this.loading = true
			
			try {
				const res = await api.fault.getReportDetail(this.reportId)
				
				if (res.code === 200) {
					this.reportData = res.data || {}
					this.repairRecords = res.data?.repair_records || []
					
					// 解析照片URL
					if (res.data.photo_urls) {
						try {
							this.photoUrls = JSON.parse(res.data.photo_urls)
						} catch {
							this.photoUrls = []
						}
					}
				}
			} catch (err) {
				console.error('加载报修详情失败:', err)
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
				'processing': '🔧',
				'completed': '✅'
			}
			return iconMap[status] || '📋'
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
		 * 拨打电话
		 */
		makePhoneCall(phoneNumber) {
			uni.makePhoneCall({
				phoneNumber: phoneNumber
			})
		},
		
		/**
		 * 预览照片
		 */
		previewPhoto(photo, index) {
			uni.previewImage({
				urls: this.photoUrls,
				current: index
			})
		},
		
		/**
		 * 获取操作文本
		 */
		getActionText(action) {
			const actionMap = {
				'created': '提交报修',
				'assigned': '分配工单',
				'processing': '维修中',
				'updated': '更新进度',
				'completed': '完成维修'
			}
			return actionMap[action] || action
		},
		
		/**
		 * 获取操作样式类
		 */
		getActionClass(action) {
			const classMap = {
				'created': 'created',
				'assigned': 'assigned',
				'processing': 'processing',
				'updated': 'updated',
				'completed': 'completed'
			}
			return classMap[action] || 'default'
		},
		
		/**
		 * 显示分配弹窗
		 */
		async showAssignModal() {
			// 加载维修人员列表
			try {
				const res = await api.auth.getUsers({ role: 'repair' })
				if (res.code === 200) {
					this.repairUsers = res.data?.items || []
					this.selectedUser = null
					this.showAssign = true
				}
			} catch (err) {
				console.error('加载维修人员列表失败:', err)
				utils.showError('加载维修人员列表失败')
			}
		},
		
		/**
		 * 关闭分配弹窗
		 */
		closeAssignModal() {
			this.showAssign = false
			this.selectedUser = null
		},
		
		/**
		 * 选择维修人员
		 */
		selectUser(user) {
			this.selectedUser = user
		},
		
		/**
		 * 处理分配
		 */
		async handleAssign() {
			if (!this.selectedUser) {
				utils.showError('请选择维修人员')
				return
			}
			
			try {
				const res = await api.fault.assignReport(this.reportId, this.selectedUser.id)
				
				if (res.code === 200) {
					utils.showSuccess('分配成功')
					this.closeAssignModal()
					this.loadReportDetail()
				} else {
					utils.showError(res.message || '分配失败')
				}
			} catch (err) {
				console.error('分配失败:', err)
				utils.showError('分配失败')
			}
		},
		
		/**
		 * 显示进度弹窗
		 */
		showProgressModal() {
			this.progressForm = {
				progress: 50,
				description: ''
			}
			this.showProgress = true
		},
		
		/**
		 * 关闭进度弹窗
		 */
		closeProgressModal() {
			this.showProgress = false
		},
		
		/**
		 * 更新进度
		 */
		async handleUpdateProgress() {
			const currentUser = utils.getCurrentUser()
			if (!currentUser || !currentUser.id) {
				utils.showError('请先登录')
				return
			}
			
			const recordData = {
				report_id: this.reportId,
				operator_id: currentUser.id,
				action: 'updated',
				description: this.progressForm.description || '更新维修进度',
				progress: this.progressForm.progress
			}
			
			try {
				const res = await api.fault.createRecord(recordData)
				
				if (res.code === 200) {
					utils.showSuccess('进度更新成功')
					this.closeProgressModal()
					this.loadReportDetail()
				} else {
					utils.showError(res.message || '更新失败')
				}
			} catch (err) {
				console.error('更新进度失败:', err)
				utils.showError('更新失败')
			}
		},
		
		/**
		 * 完成维修
		 */
		async handleComplete() {
			const confirmed = await utils.showConfirm('确认该报修已完成吗？完成后设备状态将恢复正常。', '完成确认')
			
			if (!confirmed) return
			
			const currentUser = utils.getCurrentUser()
			if (!currentUser || !currentUser.id) {
				utils.showError('请先登录')
				return
			}
			
			try {
				const res = await api.fault.completeReport(this.reportId, currentUser.id)
				
				if (res.code === 200) {
					utils.showSuccess('报修已完成')
					this.loadReportDetail()
				} else {
					utils.showError(res.message || '操作失败')
				}
			} catch (err) {
				console.error('完成报修失败:', err)
				utils.showError('操作失败')
			}
		},
		
		/**
		 * 取消报修
		 */
		async handleCancel() {
			const confirmed = await utils.showConfirm('确定要取消该报修吗？', '取消确认')
			
			if (!confirmed) return
			
			try {
				const res = await api.fault.deleteReport(this.reportId)
				
				if (res.code === 200) {
					utils.showSuccess('报修已取消')
					uni.navigateBack({
						delta: 1
					})
				} else {
					utils.showError(res.message || '取消失败')
				}
			} catch (err) {
				console.error('取消报修失败:', err)
				utils.showError('取消失败')
			}
		},
		
		/**
		 * 获取姓名首字母
		 */
		getInitial(name) {
			if (!name) return '用'
			return name.charAt(0)
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
	background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%);
}

.status-header.status-processing {
	background: linear-gradient(135deg, #fffbe6 0%, #ffe58f 100%);
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

.status-row {
	display: flex;
	align-items: center;
	margin-bottom: 8rpx;
}

.status-text {
	font-size: 24rpx;
	padding: 4rpx 16rpx;
	border-radius: 4rpx;
	margin-right: 12rpx;
}

.level-badge {
	display: flex;
	align-items: center;
	padding: 4rpx 12rpx;
	border-radius: 4rpx;
}

.level-badge.high {
	background-color: rgba(255, 77, 79, 0.2);
}

.level-badge.medium {
	background-color: rgba(250, 173, 20, 0.2);
}

.level-badge.low {
	background-color: rgba(82, 196, 26, 0.2);
}

.level-icon {
	font-size: 20rpx;
	margin-right: 4rpx;
}

.level-text {
	font-size: 20rpx;
	color: #666;
}

.report-title {
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

.photo-count,
.record-count {
	font-size: 22rpx;
	color: #999;
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

.device-code,
.device-location {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 4rpx;
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

.info-value.link {
	color: #1677ff;
}

/* 故障描述 */
.description-content {
	padding: 20rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
}

.description-text {
	font-size: 28rpx;
	color: #333;
	line-height: 1.8;
}

/* 照片网格 */
.photo-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
}

.photo-item {
	width: calc(33.33% - 8rpx);
	aspect-ratio: 1;
	border-radius: 8rpx;
	overflow: hidden;
}

.photo-img {
	width: 100%;
	height: 100%;
}

/* 时间线 */
.timeline {
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

.timeline-item {
	display: flex;
}

.timeline-left {
	display: flex;
	flex-direction: column;
	align-items: center;
	margin-right: 20rpx;
	flex-shrink: 0;
}

.timeline-dot {
	width: 20rpx;
	height: 20rpx;
	border-radius: 50%;
	background-color: #d9d9d9;
	flex-shrink: 0;
}

.timeline-dot.created {
	background-color: #1677ff;
}

.timeline-dot.assigned {
	background-color: #faad14;
}

.timeline-dot.processing {
	background-color: #faad14;
}

.timeline-dot.updated {
	background-color: #13c2c2;
}

.timeline-dot.completed {
	background-color: #52c41a;
}

.timeline-line {
	width: 2rpx;
	flex: 1;
	min-height: 40rpx;
	background-color: #f0f0f0;
}

.timeline-content {
	flex: 1;
	padding-bottom: 8rpx;
}

.content-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 8rpx;
}

.action-text {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
}

.progress-text {
	font-size: 24rpx;
	color: #1677ff;
}

.content-body {
	margin-bottom: 8rpx;
}

.content-body .description {
	font-size: 26rpx;
	color: #666;
	line-height: 1.6;
}

.content-footer {
	display: flex;
	justify-content: space-between;
	align-items: center;
}

.operator {
	font-size: 22rpx;
	color: #999;
}

.time {
	font-size: 22rpx;
	color: #999;
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

.action-row {
	display: flex;
	gap: 16rpx;
}

.action-btn {
	flex: 1;
	height: 88rpx;
	border-radius: 12rpx;
	font-size: 30rpx;
	font-weight: 500;
}

.btn-primary:not(.btn-disabled) {
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
	color: #fff;
}

.btn-secondary:not(.btn-disabled) {
	background-color: #f5f5f5;
	color: #666;
}

.btn-success:not(.btn-disabled) {
	background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
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

/* 弹窗 */
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
	width: 90%;
	max-width: 600rpx;
	background-color: #fff;
	border-radius: 16rpx;
	overflow: hidden;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
}

.modal-header {
	padding: 24rpx;
	border-bottom: 1rpx solid #f0f0f0;
	text-align: center;
}

.modal-title {
	font-size: 32rpx;
	font-weight: 500;
	color: #333;
}

.modal-body {
	flex: 1;
	overflow-y: auto;
	padding: 24rpx;
	max-height: 50vh;
}

.modal-footer {
	display: flex;
	border-top: 1rpx solid #f0f0f0;
}

.modal-btn {
	flex: 1;
	height: 96rpx;
	font-size: 30rpx;
	border-radius: 0;
}

.modal-btn.cancel {
	color: #666;
	background-color: #fafafa;
	border-right: 1rpx solid #f0f0f0;
}

.modal-btn.confirm {
	color: #1677ff;
}

.modal-btn.confirm:disabled {
	color: #999;
	opacity: 0.7;
}

/* 用户列表 */
.user-list {
	display: flex;
	flex-direction: column;
	gap: 12rpx;
}

.user-item {
	display: flex;
	align-items: center;
	padding: 20rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.user-item.selected {
	background-color: #e6f7ff;
	border-color: #1677ff;
}

.user-avatar {
	width: 72rpx;
	height: 72rpx;
	border-radius: 50%;
	background-color: #1677ff;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.avatar-text {
	font-size: 32rpx;
	font-weight: bold;
	color: #fff;
}

.user-info {
	display: flex;
	flex-direction: column;
	flex: 1;
}

.user-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 4rpx;
}

.user-phone {
	font-size: 24rpx;
	color: #999;
}

.user-check {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background-color: #1677ff;
	display: flex;
	align-items: center;
	justify-content: center;
}

.check-icon {
	font-size: 24rpx;
	color: #fff;
	font-weight: bold;
}

/* 进度选择器 */
.progress-selector {
	display: flex;
	flex-wrap: wrap;
	gap: 12rpx;
	margin-top: 12rpx;
}

.percent-btn {
	flex: 1;
	min-width: calc(33.33% - 8rpx);
	height: 72rpx;
	border-radius: 12rpx;
	background-color: #f5f5f5;
	display: flex;
	align-items: center;
	justify-content: center;
}

.percent-btn.active {
	background-color: #e6f7ff;
	border: 2rpx solid #1677ff;
}

.percent-btn text {
	font-size: 28rpx;
	color: #666;
}

.percent-btn.active text {
	color: #1677ff;
	font-weight: 500;
}

/* 表单项 */
.form-item {
	margin-bottom: 24rpx;
}

.form-label {
	display: block;
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
	margin-bottom: 12rpx;
}

.form-textarea {
	width: 100%;
	min-height: 160rpx;
	padding: 16rpx;
	font-size: 28rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.form-textarea:focus {
	border-color: #1677ff;
	background-color: #fff;
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
