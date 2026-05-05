<template>
	<view class="mixing-add-container">
		<!-- 任务信息 -->
		<view class="info-card" v-if="taskInfo">
			<view class="card-header">
				<text class="card-title">当前任务</text>
			</view>
			<view class="card-body">
				<view class="info-row">
					<text class="info-label">任务编号</text>
					<text class="info-value">{{ taskInfo.task_no }}</text>
				</view>
				<view class="info-row">
					<text class="info-label">混凝土标号</text>
					<text class="info-value highlight">{{ taskInfo.concrete_grade }}</text>
				</view>
				<view class="info-row">
					<text class="info-label">项目名称</text>
					<text class="info-value">{{ taskInfo.project_name }}</text>
				</view>
			</view>
		</view>
		
		<!-- 盘信息 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">盘信息</text>
				<text class="card-required">*</text>
			</view>
			<view class="card-body">
				<view class="input-row">
					<text class="input-label">盘号</text>
					<input 
						class="input-box" 
						type="number" 
						v-model="formData.batch_no"
						placeholder="请输入盘号"
						placeholder-class="input-placeholder"
					/>
					<text class="input-unit">盘</text>
				</view>
			</view>
		</view>
		
		<!-- 搅拌参数 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">搅拌参数</text>
				<text class="card-required">*</text>
			</view>
			<view class="card-body">
				<view class="input-row">
					<text class="input-label">搅拌时长</text>
					<input 
						class="input-box" 
						type="number" 
						v-model="formData.mixing_time_seconds"
						placeholder="请输入搅拌时长"
						placeholder-class="input-placeholder"
					/>
					<text class="input-unit">秒</text>
				</view>
				
				<view class="input-row">
					<text class="input-label">搅拌转速</text>
					<input 
						class="input-box" 
						type="number" 
						v-model="formData.rotation_speed"
						placeholder="请输入搅拌转速（可选）"
						placeholder-class="input-placeholder"
					/>
					<text class="input-unit">RPM</text>
				</view>
				
				<view class="input-row">
					<text class="input-label">当前温度</text>
					<input 
						class="input-box" 
						type="digit" 
						v-model="formData.current_temperature"
						placeholder="请输入当前温度（可选）"
						placeholder-class="input-placeholder"
					/>
					<text class="input-unit">℃</text>
				</view>
			</view>
		</view>
		
		<!-- 异常情况 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">异常情况</text>
			</view>
			<view class="card-body">
				<view class="switch-row">
					<text class="switch-label">是否异常</text>
					<switch 
						:checked="formData.is_abnormal"
						@change="formData.is_abnormal = $event.detail.value"
						color="#1890FF"
					/>
				</view>
				
				<!-- 异常类型选择 -->
				<view class="abnormal-section" v-if="formData.is_abnormal">
					<text class="section-label">异常类型</text>
					<view class="type-options">
						<view 
							class="type-item" 
							:class="{ active: formData.abnormal_type === item.value }"
							v-for="item in abnormalTypes" 
							:key="item.value"
							@click="formData.abnormal_type = item.value"
						>
							{{ item.label }}
						</view>
					</view>
					
					<text class="section-label">异常情况说明</text>
					<textarea 
						class="desc-input" 
						v-model="formData.abnormal_description"
						placeholder="请详细描述异常情况"
						placeholder-class="input-placeholder"
					></textarea>
					
					<text class="section-label">处理措施</text>
					<textarea 
						class="desc-input" 
						v-model="formData.handling_measures"
						placeholder="请描述采取的处理措施"
						placeholder-class="input-placeholder"
					></textarea>
				</view>
			</view>
		</view>
		
		<!-- 质量检验 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">质量检验</text>
			</view>
			<view class="card-body">
				<view class="input-row">
					<text class="input-label">实测坍落度</text>
					<input 
						class="input-box" 
						type="digit" 
						v-model="formData.slump_actual"
						placeholder="请输入实测坍落度（可选）"
						placeholder-class="input-placeholder"
					/>
					<text class="input-unit">mm</text>
				</view>
				
				<view class="input-row">
					<text class="input-label">实测温度</text>
					<input 
						class="input-box" 
						type="digit" 
						v-model="formData.temperature_actual"
						placeholder="请输入实测温度（可选）"
						placeholder-class="input-placeholder"
					/>
					<text class="input-unit">℃</text>
				</view>
				
				<text class="section-label">质量状态</text>
				<view class="quality-options">
					<view 
						class="quality-item" 
						:class="{ active: formData.quality_status === 'qualified' }"
						@click="formData.quality_status = 'qualified'"
					>
						合格
					</view>
					<view 
						class="quality-item" 
						:class="{ active: formData.quality_status === 'unqualified' }"
						@click="formData.quality_status = 'unqualified'"
					>
						不合格
					</view>
				</view>
			</view>
		</view>
		
		<!-- 备注 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">备注</text>
			</view>
			<view class="card-body">
				<textarea 
					class="remark-input" 
					v-model="formData.remarks"
					placeholder="其他补充说明（可选）"
					placeholder-class="input-placeholder"
				></textarea>
			</view>
		</view>
		
		<!-- 底部操作 -->
		<view class="bottom-bar">
			<button class="bar-btn outline" @click="resetForm">
				重置
			</button>
			<button class="bar-btn primary" :loading="submitting" @click="handleSubmit">
				确认提交
			</button>
		</view>
	</view>
</template>

<script>
/**
 * 搅拌记录录入页面
 * 功能：
 * - 输入搅拌参数
 * - 记录异常情况
 * - 质量检验记录
 * - 提交搅拌记录
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 任务ID
			taskId: null,
			taskNo: '',
			// 任务信息
			taskInfo: null,
			// 异常类型选项
			abnormalTypes: [
				{ label: '缺料', value: 'material_shortage' },
				{ label: '设备故障', value: 'equipment_fault' },
				{ label: '质量问题', value: 'quality_issue' },
				{ label: '其他', value: 'other' }
			],
			// 表单数据
			formData: {
				batch_no: '',
				mixing_time_seconds: '',
				rotation_speed: '',
				current_temperature: '',
				
				// 异常
				is_abnormal: false,
				abnormal_type: '',
				abnormal_description: '',
				handling_measures: '',
				
				// 质量
				slump_actual: '',
				temperature_actual: '',
				quality_status: '',
				
				remarks: ''
			},
			// 提交状态
			submitting: false
		}
	},
	
	onLoad(options) {
		if (options.taskId) {
			this.taskId = parseInt(options.taskId)
		}
		if (options.taskNo) {
			this.taskNo = options.taskNo
		}
		
		// 加载任务信息
		if (this.taskId) {
			this.loadTaskInfo()
		}
	},
	
	methods: {
		/**
		 * 加载任务信息
		 */
		async loadTaskInfo() {
			uni.showLoading({ title: '加载中...' })
			
			try {
				const res = await api.tasks.getDetail(this.taskId)
				this.taskInfo = res
			} catch (error) {
				console.log('加载任务信息失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 重置表单
		 */
		resetForm() {
			this.formData = {
				batch_no: '',
				mixing_time_seconds: '',
				rotation_speed: '',
				current_temperature: '',
				
				is_abnormal: false,
				abnormal_type: '',
				abnormal_description: '',
				handling_measures: '',
				
				slump_actual: '',
				temperature_actual: '',
				quality_status: '',
				
				remarks: ''
			}
		},
		
		/**
		 * 显示确认对话框
		 */
		showModal(title, content) {
			return new Promise((resolve) => {
				uni.showModal({
					title,
					content,
					success: (res) => {
						resolve(res.confirm)
					}
				})
			})
		},
		
		/**
		 * 提交记录
		 */
		async handleSubmit() {
			// 验证必填项
			if (!this.formData.batch_no) {
				uni.showToast({ title: '请输入盘号', icon: 'none' })
				return
			}
			
			if (!this.formData.mixing_time_seconds) {
				uni.showToast({ title: '请输入搅拌时长', icon: 'none' })
				return
			}
			
			// 构建提交数据
			const submitData = {
				task_id: this.taskId,
				batch_no: parseInt(this.formData.batch_no),
				mixing_time_seconds: parseInt(this.formData.mixing_time_seconds)
			}
			
			// 添加可选参数
			if (this.formData.rotation_speed) {
				submitData.rotation_speed = parseInt(this.formData.rotation_speed)
			}
			if (this.formData.current_temperature) {
				submitData.current_temperature = parseFloat(this.formData.current_temperature)
			}
			
			// 异常信息
			submitData.is_abnormal = this.formData.is_abnormal
			if (this.formData.is_abnormal) {
				if (this.formData.abnormal_type) {
					submitData.abnormal_type = this.formData.abnormal_type
				}
				if (this.formData.abnormal_description) {
					submitData.abnormal_description = this.formData.abnormal_description
				}
				if (this.formData.handling_measures) {
					submitData.handling_measures = this.formData.handling_measures
				}
			}
			
			// 质量信息
			if (this.formData.slump_actual) {
				submitData.slump_actual = parseFloat(this.formData.slump_actual)
			}
			if (this.formData.temperature_actual) {
				submitData.temperature_actual = parseFloat(this.formData.temperature_actual)
			}
			if (this.formData.quality_status) {
				submitData.quality_status = this.formData.quality_status
			}
			
			// 备注
			if (this.formData.remarks) {
				submitData.remarks = this.formData.remarks
			}
			
			// 确认提交
			const confirm = await this.showModal('确认提交', '确定要提交此搅拌记录吗？')
			if (!confirm) return
			
			this.submitting = true
			
			try {
				await api.mixing.create(submitData)
				
				uni.showToast({
					title: '提交成功',
					icon: 'success'
				})
				
				// 返回上一页
				setTimeout(() => {
					uni.navigateBack()
				}, 1500)
			} catch (error) {
				console.log('提交搅拌记录失败:', error)
			} finally {
				this.submitting = false
			}
		}
	}
}
</script>

<style scoped>
/* 搅拌录入页面样式 */
.mixing-add-container {
	min-height: 100vh;
	background: #F5F7FA;
	padding-bottom: 140rpx;
}

/* 信息卡片 */
.info-card {
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.card-header {
	display: flex;
	align-items: center;
	padding: 24rpx 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.card-title {
	font-size: 30rpx;
	color: #333333;
	font-weight: 500;
}

.card-required {
	font-size: 28rpx;
	color: #FF4D4F;
	margin-left: 8rpx;
}

.card-body {
	padding: 30rpx;
}

/* 信息行 */
.info-row {
	display: flex;
	margin-bottom: 20rpx;
}

.info-row:last-child {
	margin-bottom: 0;
}

.info-label {
	width: 180rpx;
	font-size: 28rpx;
	color: #999999;
	flex-shrink: 0;
}

.info-value {
	flex: 1;
	font-size: 28rpx;
	color: #333333;
}

.info-value.highlight {
	color: #1890FF;
	font-weight: 500;
}

/* 输入行 */
.input-row {
	display: flex;
	align-items: center;
	margin-bottom: 24rpx;
}

.input-row:last-child {
	margin-bottom: 0;
}

.input-label {
	width: 160rpx;
	font-size: 28rpx;
	color: #666666;
	flex-shrink: 0;
}

.input-box {
	flex: 1;
	height: 80rpx;
	background: #FAFAFA;
	border-radius: 12rpx;
	padding: 0 20rpx;
	font-size: 28rpx;
	color: #333333;
}

.input-unit {
	font-size: 26rpx;
	color: #999999;
	margin-left: 12rpx;
	width: 60rpx;
	flex-shrink: 0;
}

.input-placeholder {
	color: #CCCCCC;
}

/* 开关行 */
.switch-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24rpx;
}

.switch-label {
	font-size: 28rpx;
	color: #666666;
}

/* 异常区域 */
.abnormal-section {
	padding: 24rpx;
	background: #FFF1F0;
	border-radius: 16rpx;
}

.section-label {
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 16rpx;
	display: block;
}

/* 类型选项 */
.type-options {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
	margin-bottom: 24rpx;
}

.type-item {
	font-size: 26rpx;
	color: #666666;
	padding: 12rpx 24rpx;
	background: #FFFFFF;
	border-radius: 8rpx;
	border: 2rpx solid #E8E8E8;
}

.type-item.active {
	color: #1890FF;
	background: #E6F7FF;
	border-color: #1890FF;
}

/* 描述输入 */
.desc-input {
	width: 100%;
	height: 160rpx;
	background: #FFFFFF;
	border-radius: 12rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 24rpx;
}

/* 质量选项 */
.quality-options {
	display: flex;
	gap: 30rpx;
}

.quality-item {
	flex: 1;
	font-size: 28rpx;
	color: #666666;
	padding: 20rpx;
	background: #FAFAFA;
	border-radius: 12rpx;
	border: 2rpx solid #E8E8E8;
	text-align: center;
}

.quality-item.active {
	background: #F6FFED;
	color: #52C41A;
	border-color: #52C41A;
}

.quality-item:nth-child(2).active {
	background: #FFF1F0;
	color: #FF4D4F;
	border-color: #FF4D4F;
}

/* 备注输入 */
.remark-input {
	width: 100%;
	height: 160rpx;
	background: #FAFAFA;
	border-radius: 16rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
}

/* 底部操作栏 */
.bottom-bar {
	position: fixed;
	bottom: 0;
	left: 0;
	right: 0;
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
	display: flex;
	gap: 24rpx;
	border-top: 2rpx solid #F0F0F0;
	box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.bar-btn {
	flex: 1;
	height: 88rpx;
	line-height: 88rpx;
	font-size: 30rpx;
	border-radius: 44rpx;
	border: none;
}

.bar-btn.outline {
	background: transparent;
	color: #666666;
	border: 2rpx solid #E0E0E0;
}

.bar-btn.primary {
	background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
	color: #FFFFFF;
}
</style>
