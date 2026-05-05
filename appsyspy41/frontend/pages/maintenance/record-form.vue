<template>
	<view class="container">
		<!-- 表单卡片 -->
		<view class="form-card">
			<view class="section-header">
				<text class="section-title">📋 保养记录</text>
			</view>
			
			<!-- 设备信息展示 -->
			<view class="device-info-section" v-if="taskInfo.device_name">
				<view class="info-label">保养设备</view>
				<view class="info-value-row">
					<text class="device-name">{{ taskInfo.device_name }}</text>
					<text class="device-code">{{ taskInfo.device_code }}</text>
				</view>
			</view>
			
			<!-- 保养内容 -->
			<view class="form-item">
				<view class="form-label">
					<text class="required">*</text>
					<text>保养内容</text>
				</view>
				<textarea 
					class="form-textarea" 
					placeholder="请详细描述保养内容..."
					v-model="formData.maintenance_content"
					:disabled="submitting"
				></textarea>
			</view>
			
			<!-- 保养结果 -->
			<view class="form-item">
				<view class="form-label">
					<text class="required">*</text>
					<text>保养结果</text>
				</view>
				<view class="result-options">
					<view 
						v-for="(option, index) in resultOptions" 
						:key="index"
						class="result-item"
						:class="{ 'active': formData.maintenance_result === option.value }"
						@click="selectResult(option.value)"
					>
						<text class="result-icon">{{ option.icon }}</text>
						<text class="result-text">{{ option.label }}</text>
					</view>
				</view>
			</view>
			
			<!-- 备注信息 -->
			<view class="form-item">
				<view class="form-label">
					<text>备注信息</text>
				</view>
				<textarea 
					class="form-textarea" 
					placeholder="请填写其他备注信息（选填）..."
					v-model="formData.remark"
					:disabled="submitting"
				></textarea>
			</view>
			
			<!-- 照片上传 -->
			<view class="form-item">
				<view class="form-label">
					<text>保养照片</text>
					<text class="form-tip">（可上传多张）</text>
				</view>
				<view class="photo-section">
					<view class="photo-list">
						<view 
							v-for="(photo, index) in formData.photoUrls" 
							:key="index"
							class="photo-item"
						>
							<image class="photo-img" :src="photo" mode="aspectFill"></image>
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
		</view>
		
		<!-- 操作指南提示 -->
		<view class="guide-card" v-if="taskInfo.operation_guide">
			<view class="guide-header">
				<text class="guide-title">📖 操作指南</text>
			</view>
			<view class="guide-content">
				<text class="guide-text">{{ taskInfo.operation_guide }}</text>
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
				<text v-if="!submitting">确认提交</text>
				<text v-else>提交中...</text>
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
			taskId: null,
			deviceId: null,
			taskInfo: {},
			submitting: false,
			resultOptions: [
				{ label: '正常', value: 'normal', icon: '✅' },
				{ label: '需关注', value: 'warning', icon: '⚠️' },
				{ label: '异常', value: 'fault', icon: '❌' }
			],
			formData: {
				maintenance_content: '',
				maintenance_result: 'normal',
				remark: '',
				photoUrls: []
			}
		}
	},
	
	onLoad(options) {
		if (options.taskId) {
			this.taskId = parseInt(options.taskId)
		}
		if (options.deviceId) {
			this.deviceId = parseInt(options.deviceId)
		}
		
		if (this.taskId) {
			this.loadTaskInfo()
		}
	},
	
	methods: {
		/**
		 * 加载任务信息
		 */
		async loadTaskInfo() {
			try {
				const res = await api.maintenance.getTaskDetail(this.taskId)
				
				if (res.code === 200) {
					this.taskInfo = res.data || {}
				}
			} catch (err) {
				console.error('加载任务信息失败:', err)
			}
		},
		
		/**
		 * 选择保养结果
		 */
		selectResult(value) {
			if (!this.submitting) {
				this.formData.maintenance_result = value
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
		 * 删除照片
		 */
		deletePhoto(index) {
			this.formData.photoUrls.splice(index, 1)
		},
		
		/**
		 * 提交保养记录
		 */
		async handleSubmit() {
			// 验证表单
			if (!this.formData.maintenance_content.trim()) {
				utils.showError('请填写保养内容')
				return
			}
			
			if (!this.taskId) {
				utils.showError('缺少任务信息')
				return
			}
			
			if (!this.deviceId) {
				utils.showError('缺少设备信息')
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
				const recordData = {
					task_id: this.taskId,
					device_id: this.deviceId,
					operator_id: currentUser.id,
					maintenance_content: this.formData.maintenance_content.trim(),
					maintenance_result: this.formData.maintenance_result,
					remark: this.formData.remark.trim() || '',
					photo_urls: JSON.stringify(this.formData.photoUrls)
				}
				
				const res = await api.maintenance.createRecord(recordData)
				
				if (res.code === 200) {
					utils.showSuccess('保养记录提交成功')
					
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
				console.error('提交保养记录失败:', err)
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

/* 表单卡片 */
.form-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
}

.section-header {
	margin-bottom: 24rpx;
	padding-bottom: 16rpx;
	border-bottom: 1rpx solid #f0f0f0;
}

.section-title {
	font-size: 30rpx;
	font-weight: 500;
	color: #333;
}

/* 设备信息展示 */
.device-info-section {
	margin-bottom: 24rpx;
	padding: 20rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
}

.info-label {
	font-size: 24rpx;
	color: #999;
	margin-bottom: 8rpx;
}

.info-value-row {
	display: flex;
	align-items: center;
}

.device-name {
	font-size: 30rpx;
	font-weight: 500;
	color: #333;
	margin-right: 16rpx;
}

.device-code {
	font-size: 24rpx;
	color: #999;
}

/* 表单项 */
.form-item {
	margin-bottom: 24rpx;
}

.form-label {
	display: flex;
	align-items: center;
	margin-bottom: 12rpx;
}

.required {
	color: #ff4d4f;
	font-size: 28rpx;
	margin-right: 4rpx;
}

.form-label text:not(.required) {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.form-tip {
	font-size: 22rpx;
	color: #999;
	margin-left: 8rpx;
	font-weight: normal;
}

.form-textarea {
	width: 100%;
	min-height: 160rpx;
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

/* 结果选项 */
.result-options {
	display: flex;
	gap: 16rpx;
}

.result-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 24rpx 16rpx;
	background-color: #fafafa;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.result-item.active {
	background-color: #e6f7ff;
	border-color: #1677ff;
}

.result-icon {
	font-size: 40rpx;
	margin-bottom: 8rpx;
}

.result-text {
	font-size: 26rpx;
	color: #666;
}

.result-item.active .result-text {
	color: #1677ff;
	font-weight: 500;
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

/* 操作指南卡片 */
.guide-card {
	background-color: #fff;
	border-radius: 16rpx;
	padding: 24rpx;
	margin-bottom: 24rpx;
}

.guide-header {
	margin-bottom: 16rpx;
}

.guide-title {
	font-size: 28rpx;
	font-weight: 500;
	color: #333;
}

.guide-content {
	padding: 20rpx;
	background-color: #fffbe6;
	border-radius: 12rpx;
}

.guide-text {
	font-size: 26rpx;
	color: #666;
	line-height: 1.8;
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
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
	color: #fff;
}

.btn-disabled {
	background-color: #d9d9d9;
	opacity: 0.7;
}
</style>
