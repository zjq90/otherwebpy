<template>
	<view class="container">
		<!-- 选择设备 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">
					<text class="required">*</text>
					选择故障设备
				</text>
			</view>
			<view class="device-selector" @click="showDevicePicker">
				<view class="selector-content" v-if="selectedDevice">
					<view class="selected-icon">
						<text class="icon-text">{{ getDeviceIcon(selectedDevice.device_type) }}</text>
					</view>
					<view class="selected-info">
						<text class="device-name">{{ selectedDevice.device_name }}</text>
						<text class="device-code">{{ selectedDevice.device_code }}</text>
					</view>
					<view class="selector-arrow">
						<text class="arrow-text">›</text>
					</view>
				</view>
				<view class="placeholder" v-else>
					<text class="placeholder-text">请选择故障设备</text>
					<text class="placeholder-arrow">›</text>
				</view>
			</view>
		</view>
		
		<!-- 故障标题 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">
					<text class="required">*</text>
					故障标题
				</text>
			</view>
			<input 
				class="form-input" 
				type="text" 
				placeholder="请简要描述故障问题（如：搅拌主机温度过高）"
				v-model="formData.fault_title"
				:disabled="submitting"
				maxlength="50"
			/>
			<view class="char-count">
				<text class="count-text">{{ formData.fault_title.length }}/50</text>
			</view>
		</view>
		
		<!-- 故障级别 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">
					<text class="required">*</text>
					故障级别
				</text>
			</view>
			<view class="level-options">
				<view 
					v-for="(level, index) in levelOptions" 
					:key="level.value"
					class="level-item"
					:class="{ 
						'active': formData.fault_level === level.value,
						`level-${level.value}`: true
					}"
					@click="selectLevel(level.value)"
				>
					<text class="level-icon">{{ level.icon }}</text>
					<text class="level-label">{{ level.label }}</text>
					<text class="level-desc">{{ level.desc }}</text>
				</view>
			</view>
		</view>
		
		<!-- 故障描述 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">故障详细描述</text>
			</view>
			<textarea 
				class="form-textarea" 
				placeholder="请详细描述故障现象、发生时间、影响范围等信息..."
				v-model="formData.fault_description"
				:disabled="submitting"
				maxlength="500"
			></textarea>
			<view class="char-count">
				<text class="count-text">{{ formData.fault_description.length }}/500</text>
			</view>
		</view>
		
		<!-- 故障照片 -->
		<view class="section-card">
			<view class="section-header">
				<text class="section-title">故障照片</text>
				<text class="photo-tip">（可上传多张，帮助维修人员了解情况）</text>
			</view>
			<view class="photo-section">
				<view class="photo-list">
					<view 
						v-for="(photo, index) in formData.photoUrls" 
						:key="index"
						class="photo-item"
					>
						<image class="photo-img" :src="photo" mode="aspectFill" @click="previewPhoto(index)"></image>
						<view class="photo-delete" @click="deletePhoto(index)">
							<text class="delete-icon">×</text>
						</view>
					</view>
					<view class="add-photo" @click="chooseImage" v-if="formData.photoUrls.length < 9">
						<text class="add-icon">+</text>
						<text class="add-text">添加照片</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 提交提醒 -->
		<view class="tips-card">
			<view class="tips-header">
				<text class="tips-icon">💡</text>
				<text class="tips-title">提交须知</text>
			</view>
			<view class="tips-list">
				<view class="tips-item">
					<text class="tips-dot">•</text>
					<text class="tips-text">提交报修后，系统将自动派单给维修人员</text>
				</view>
				<view class="tips-item">
					<text class="tips-dot">•</text>
					<text class="tips-text">请尽可能详细描述故障并上传照片</text>
				</view>
				<view class="tips-item">
					<text class="tips-dot">•</text>
					<text class="tips-text">故障级别为"高"的报修将优先处理</text>
				</view>
			</view>
		</view>
		
		<!-- 提交按钮 -->
		<view class="submit-section">
			<button 
				class="submit-btn" 
				:class="{ 'btn-disabled': submitting }"
				:disabled="submitting"
				@click="handleSubmit"
			>
				<text v-if="!submitting">提交报修</text>
				<text v-else>提交中...</text>
			</button>
		</view>
		
		<!-- 设备选择弹窗 -->
		<view class="modal-mask" v-if="showDeviceModal" @click="closeDeviceModal">
			<view class="modal-content device-modal" @click.stop>
				<view class="modal-header">
					<text class="modal-title">选择设备</text>
					<view class="modal-close" @click="closeDeviceModal">
						<text class="close-icon">×</text>
					</view>
				</view>
				
				<!-- 搜索框 -->
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
				
				<!-- 设备列表 -->
				<scroll-view class="device-list" scroll-y>
					<view 
						v-for="(device, index) in deviceList" 
						:key="device.id"
						class="device-item"
						:class="{ 'selected': selectedDeviceId === device.id }"
						@click="selectDevice(device)"
					>
						<view class="device-icon-wrapper" :class="`type-${device.device_type}`">
							<text class="icon-text">{{ getDeviceIcon(device.device_type) }}</text>
						</view>
						<view class="device-info">
							<view class="info-top">
								<text class="device-name">{{ device.device_name }}</text>
								<view class="status-badge" :class="`status-${device.status}`">
									<text class="badge-text">{{ utils.getStatusName(device.status) }}</text>
								</view>
							</view>
							<view class="info-bottom">
								<text class="device-code">编号: {{ device.device_code }}</text>
								<text class="device-location">位置: {{ device.location || '-' }}</text>
							</view>
						</view>
						<view class="device-check" v-if="selectedDeviceId === device.id">
							<text class="check-icon">✓</text>
						</view>
					</view>
					
					<!-- 空状态 -->
					<view class="empty-state" v-if="deviceList.length === 0 && !loadingDevices">
						<text class="empty-icon">📭</text>
						<text class="empty-text">暂无设备</text>
					</view>
					
					<!-- 加载中 -->
					<view class="loading-state" v-if="loadingDevices">
						<text class="loading-text">加载中...</text>
					</view>
				</scroll-view>
				
				<view class="modal-footer">
					<button class="modal-btn confirm" @click="confirmDeviceSelection">确认选择</button>
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
			submitting: false,
			selectedDevice: null,
			showDeviceModal: false,
			deviceList: [],
			loadingDevices: false,
			searchKeyword: '',
			levelOptions: [
				{ label: '高', value: 'high', icon: '🔴', desc: '紧急故障，影响生产' },
				{ label: '中', value: 'medium', icon: '🟡', desc: '一般故障，需关注' },
				{ label: '低', value: 'low', icon: '🟢', desc: '轻微故障，可延后' }
			],
			formData: {
				fault_title: '',
				fault_description: '',
				fault_level: 'medium',
				photoUrls: []
			}
		}
	},
	
	computed: {
		selectedDeviceId() {
			return this.selectedDevice && this.selectedDevice.id
		}
	},
	
	onLoad() {
		// 页面加载时不自动加载设备列表，点击选择时再加载
	},
	
	methods: {
		/**
		 * 显示设备选择弹窗
		 */
		async showDevicePicker() {
			this.showDeviceModal = true
			await this.loadDeviceList()
		},
		
		/**
		 * 关闭设备选择弹窗
		 */
		closeDeviceModal() {
			this.showDeviceModal = false
		},
		
		/**
		 * 加载设备列表
		 */
		async loadDeviceList() {
			this.loadingDevices = true
			
			try {
				const params = {
					page: 1,
					page_size: 100
				}
				
				if (this.searchKeyword) {
					params.keyword = this.searchKeyword
				}
				
				const res = await api.device.getList(params)
				
				if (res.code === 200) {
					this.deviceList = res.data?.items || []
				}
			} catch (err) {
				console.error('加载设备列表失败:', err)
			} finally {
				this.loadingDevices = false
			}
		},
		
		/**
		 * 搜索设备
		 */
		handleSearch() {
			this.loadDeviceList()
		},
		
		/**
		 * 选择设备
		 */
		selectDevice(device) {
			this.selectedDevice = device
		},
		
		/**
		 * 确认选择设备
		 */
		confirmDeviceSelection() {
			if (!this.selectedDevice) {
				utils.showError('请选择一个设备')
				return
			}
			this.closeDeviceModal()
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
		 * 选择故障级别
		 */
		selectLevel(level) {
			if (!this.submitting) {
				this.formData.fault_level = level
			}
		},
		
		/**
		 * 选择照片
		 */
		chooseImage() {
			const remaining = 9 - this.formData.photoUrls.length
			if (remaining <= 0) {
				utils.showError('最多只能上传9张照片')
				return
			}
			
			uni.chooseImage({
				count: remaining,
				sizeType: ['compressed'],
				sourceType: ['album', 'camera'],
				success: (res) => {
					this.formData.photoUrls = [
						...this.formData.photoUrls,
						...res.tempFilePaths
					]
				}
			})
		},
		
		/**
		 * 预览照片
		 */
		previewPhoto(index) {
			uni.previewImage({
				urls: this.formData.photoUrls,
				current: index
			})
		},
		
		/**
		 * 删除照片
		 */
		deletePhoto(index) {
			this.formData.photoUrls.splice(index, 1)
		},
		
		/**
		 * 提交报修
		 */
		async handleSubmit() {
			// 验证表单
			if (!this.selectedDevice) {
				utils.showError('请选择故障设备')
				return
			}
			
			if (!this.formData.fault_title.trim()) {
				utils.showError('请填写故障标题')
				return
			}
			
			if (this.formData.fault_title.length < 5) {
				utils.showError('故障标题至少5个字符')
				return
			}
			
			const currentUser = utils.getCurrentUser()
			if (!currentUser || !currentUser.id) {
				utils.showError('请先登录')
				uni.redirectTo({
					url: '/pages/login/login'
				})
				return
			}
			
			this.submitting = true
			
			try {
				// 注意：这里需要传递reporter_id参数
				// 查看后端API：create_fault_report 接收 reporter_id 参数
				
				const reportData = {
					device_id: this.selectedDevice.id,
					fault_title: this.formData.fault_title.trim(),
					fault_description: this.formData.fault_description.trim() || '',
					fault_level: this.formData.fault_level,
					photo_urls: JSON.stringify(this.formData.photoUrls)
				}
				
				// 调用API时需要传递 reporter_id
				const res = await api.fault.createReport(reportData, currentUser.id)
				
				if (res.code === 200) {
					utils.showSuccess('报修提交成功')
					
					// 延迟返回，让用户看到提示
					setTimeout(() => {
						uni.navigateBack({
							delta: 1
						})
					}, 1500)
				} else {
					utils.showError(res.message || '提交失败')
				}
			} catch (err) {
				console.error('提交报修失败:', err)
				utils.showError('提交失败，请重试')
			} finally {
				this.submitting = false
			}
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

/* 通用卡片 */
.section-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
}

.section-header {
	margin-bottom: 16rpx;
}

.section-title {
	font-size: 30rpx;
	font-weight: 500;
	color: #333;
}

.required {
	color: #ff4d4f;
	margin-right: 4rpx;
}

.photo-tip {
	font-size: 22rpx;
	color: #999;
	margin-left: 8rpx;
	font-weight: normal;
}

/* 设备选择器 */
.device-selector {
	display: flex;
	align-items: center;
	padding: 20rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.device-selector:active {
	background-color: #f5f5f5;
}

.selector-content {
	display: flex;
	align-items: center;
	flex: 1;
}

.selected-icon {
	width: 64rpx;
	height: 64rpx;
	border-radius: 12rpx;
	background-color: #e6f7ff;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.icon-text {
	font-size: 32rpx;
}

.selected-info {
	display: flex;
	flex-direction: column;
	flex: 1;
}

.device-name {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-bottom: 4rpx;
}

.device-code {
	font-size: 24rpx;
	color: #999;
}

.selector-arrow,
.placeholder-arrow {
	flex-shrink: 0;
}

.arrow-text {
	font-size: 32rpx;
	color: #999;
}

.placeholder {
	display: flex;
	justify-content: space-between;
	align-items: center;
	flex: 1;
}

.placeholder-text {
	font-size: 28rpx;
	color: #999;
}

/* 表单输入 */
.form-input {
	width: 100%;
	height: 88rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333;
	background-color: #fafafa;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.form-input:focus {
	border-color: #1677ff;
	background-color: #fff;
}

.char-count {
	text-align: right;
	margin-top: 8rpx;
}

.count-text {
	font-size: 22rpx;
	color: #999;
}

.form-textarea {
	width: 100%;
	min-height: 200rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333;
	background-color: #fafafa;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.form-textarea:focus {
	border-color: #1677ff;
	background-color: #fff;
}

/* 故障级别选项 */
.level-options {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.level-item {
	display: flex;
	align-items: center;
	padding: 20rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.level-item.active {
	background-color: #e6f7ff;
	border-color: #1677ff;
}

.level-item.level-high.active {
	background-color: #fff2f0;
	border-color: #ff4d4f;
}

.level-item.level-medium.active {
	background-color: #fffbe6;
	border-color: #faad14;
}

.level-item.level-low.active {
	background-color: #f6ffed;
	border-color: #52c41a;
}

.level-icon {
	font-size: 36rpx;
	margin-right: 16rpx;
}

.level-label {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
	margin-right: 16rpx;
}

.level-desc {
	font-size: 24rpx;
	color: #999;
	flex: 1;
}

/* 照片上传 */
.photo-section {
	margin-top: 12rpx;
}

.photo-list {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.photo-item {
	position: relative;
	width: 160rpx;
	height: 160rpx;
}

.photo-img {
	width: 100%;
	height: 100%;
	border-radius: 8rpx;
}

.photo-delete {
	position: absolute;
	top: -12rpx;
	right: -12rpx;
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background-color: rgba(0, 0, 0, 0.6);
	display: flex;
	align-items: center;
	justify-content: center;
}

.delete-icon {
	font-size: 28rpx;
	color: #fff;
}

.add-photo {
	width: 160rpx;
	height: 160rpx;
	border: 2rpx dashed #d9d9d9;
	border-radius: 8rpx;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
}

.add-icon {
	font-size: 48rpx;
	color: #999;
	margin-bottom: 8rpx;
}

.add-text {
	font-size: 22rpx;
	color: #999;
}

/* 提示卡片 */
.tips-card {
	background-color: #fffbe6;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
	border-left: 6rpx solid #faad14;
}

.tips-header {
	display: flex;
	align-items: center;
	margin-bottom: 16rpx;
}

.tips-icon {
	font-size: 28rpx;
	margin-right: 8rpx;
}

.tips-title {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
}

.tips-list {
	display: flex;
	flex-direction: column;
	gap: 8rpx;
}

.tips-item {
	display: flex;
	align-items: flex-start;
}

.tips-dot {
	font-size: 24rpx;
	color: #999;
	margin-right: 8rpx;
	flex-shrink: 0;
}

.tips-text {
	font-size: 24rpx;
	color: #666;
	line-height: 1.6;
}

/* 提交按钮区域 */
.submit-section {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background-color: #fff;
	padding: 24rpx;
	padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
	box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.submit-btn {
	width: 100%;
	height: 96rpx;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: 500;
}

.submit-btn:not(.btn-disabled) {
	background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
	color: #fff;
}

.btn-disabled {
	background-color: #d9d9d9;
	opacity: 0.7;
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
	align-items: flex-end;
	z-index: 1000;
}

.modal-content {
	width: 100%;
	background-color: #fff;
	border-radius: 24rpx 24rpx 0 0;
	overflow: hidden;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
}

.device-modal {
	max-height: 70vh;
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
	font-weight: 500;
	color: #333;
}

.modal-close {
	width: 56rpx;
	height: 56rpx;
	display: flex;
	align-items: center;
	justify-content: center;
}

.close-icon {
	font-size: 40rpx;
	color: #999;
}

/* 搜索框 */
.search-box {
	display: flex;
	align-items: center;
	padding: 16rpx 24rpx;
	background-color: #fafafa;
	border-bottom: 1rpx solid #f0f0f0;
}

.search-icon {
	font-size: 28rpx;
	margin-right: 12rpx;
}

.search-input {
	flex: 1;
	height: 72rpx;
	font-size: 28rpx;
	color: #333;
}

/* 设备列表 */
.device-list {
	flex: 1;
	max-height: 60vh;
}

.device-item {
	display: flex;
	align-items: center;
	padding: 20rpx 24rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.device-item.selected {
	background-color: #e6f7ff;
}

.device-icon-wrapper {
	width: 72rpx;
	height: 72rpx;
	border-radius: 12rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 16rpx;
}

.device-icon-wrapper.type-mixer {
	background-color: #e6f7ff;
}

.device-icon-wrapper.type-belt_scale {
	background-color: #f6ffed;
}

.device-icon-wrapper.type-compressor {
	background-color: #fffbe6;
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
	margin-bottom: 8rpx;
}

.info-bottom {
	display: flex;
	gap: 16rpx;
}

.status-badge {
	flex-shrink: 0;
}

.badge-text {
	font-size: 20rpx;
	padding: 2rpx 8rpx;
	border-radius: 4rpx;
}

.device-location {
	font-size: 22rpx;
	color: #999;
}

.device-check {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background-color: #1677ff;
	display: flex;
	align-items: center;
	justify-content: center;
	flex-shrink: 0;
}

.check-icon {
	font-size: 24rpx;
	color: #fff;
	font-weight: bold;
}

.modal-footer {
	padding: 24rpx;
	border-top: 1rpx solid #f0f0f0;
}

.modal-btn.confirm {
	width: 100%;
	height: 88rpx;
	border-radius: 12rpx;
	font-size: 30rpx;
	font-weight: 500;
	color: #fff;
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
}

/* 空状态和加载状态 */
.empty-state,
.loading-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 80rpx 0;
}

.empty-icon {
	font-size: 64rpx;
	margin-bottom: 16rpx;
}

.empty-text,
.loading-text {
	font-size: 26rpx;
	color: #999;
}
</style>
