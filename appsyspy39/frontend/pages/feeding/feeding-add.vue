<template>
	<view class="feeding-add-container">
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
		
		<!-- 投料方式 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">投料方式</text>
			</view>
			<view class="card-body">
				<view class="method-options">
					<view 
						class="method-item" 
						:class="{ active: formData.feeding_method === 'scan' }"
						@click="formData.feeding_method = 'scan'"
					>
						<text class="method-icon">📷</text>
						<text class="method-text">扫码录入</text>
					</view>
					<view 
						class="method-item" 
						:class="{ active: formData.feeding_method === 'manual' }"
						@click="formData.feeding_method = 'manual'"
					>
						<text class="method-icon">✏️</text>
						<text class="method-text">手动录入</text>
					</view>
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
				<view class="input-row">
					<text class="input-label">本盘方量</text>
					<input 
						class="input-box" 
						type="digit" 
						v-model="formData.batch_quantity"
						placeholder="请输入本盘方量"
						placeholder-class="input-placeholder"
					/>
					<text class="input-unit">m³</text>
				</view>
			</view>
		</view>
		
		<!-- 材料用量 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">材料用量（kg）</text>
				<text class="card-tip">实际投料量</text>
			</view>
			<view class="card-body">
				<!-- 水泥 -->
				<view class="material-section">
					<view class="section-header">
						<text class="material-name">水泥</text>
						<text class="theory-tip" v-if="theoryValues.cement">
							理论: {{ theoryValues.cement }} kg
						</text>
					</view>
					<view class="input-group">
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">条码</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.cement_barcode"
								placeholder="扫描或输入条码"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">批号</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.cement_lot"
								placeholder="输入批号"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item">
							<text class="item-label">实际用量</text>
							<input 
								class="item-input" 
								type="digit" 
								v-model="formData.cement_actual"
								placeholder="请输入实际用量"
								placeholder-class="input-placeholder"
							/>
							<text class="item-unit">kg</text>
						</view>
					</view>
				</view>
				
				<!-- 水 -->
				<view class="material-section">
					<view class="section-header">
						<text class="material-name">水</text>
						<text class="theory-tip" v-if="theoryValues.water">
							理论: {{ theoryValues.water }} kg
						</text>
					</view>
					<view class="input-group">
						<view class="input-item">
							<text class="item-label">实际用量</text>
							<input 
								class="item-input" 
								type="digit" 
								v-model="formData.water_actual"
								placeholder="请输入实际用量"
								placeholder-class="input-placeholder"
							/>
							<text class="item-unit">kg</text>
						</view>
					</view>
				</view>
				
				<!-- 砂子 -->
				<view class="material-section">
					<view class="section-header">
						<text class="material-name">砂子</text>
						<text class="theory-tip" v-if="theoryValues.sand">
							理论: {{ theoryValues.sand }} kg
						</text>
					</view>
					<view class="input-group">
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">条码</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.sand_barcode"
								placeholder="扫描或输入条码"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">批号</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.sand_lot"
								placeholder="输入批号"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item">
							<text class="item-label">实际用量</text>
							<input 
								class="item-input" 
								type="digit" 
								v-model="formData.sand_actual"
								placeholder="请输入实际用量"
								placeholder-class="input-placeholder"
							/>
							<text class="item-unit">kg</text>
						</view>
					</view>
				</view>
				
				<!-- 石子 -->
				<view class="material-section">
					<view class="section-header">
						<text class="material-name">石子</text>
						<text class="theory-tip" v-if="theoryValues.stone">
							理论: {{ theoryValues.stone }} kg
						</text>
					</view>
					<view class="input-group">
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">条码</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.stone_barcode"
								placeholder="扫描或输入条码"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">批号</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.stone_lot"
								placeholder="输入批号"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item">
							<text class="item-label">实际用量</text>
							<input 
								class="item-input" 
								type="digit" 
								v-model="formData.stone_actual"
								placeholder="请输入实际用量"
								placeholder-class="input-placeholder"
							/>
							<text class="item-unit">kg</text>
						</view>
					</view>
				</view>
				
				<!-- 外加剂 -->
				<view class="material-section" v-if="formulaInfo && formulaInfo.admixture">
					<view class="section-header">
						<text class="material-name">外加剂</text>
						<text class="theory-tip" v-if="theoryValues.admixture">
							理论: {{ theoryValues.admixture }} kg
						</text>
					</view>
					<view class="input-group">
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">条码</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.admixture_barcode"
								placeholder="扫描或输入条码"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item" v-if="formData.feeding_method === 'scan'">
							<text class="item-label">批号</text>
							<input 
								class="item-input" 
								type="text" 
								v-model="formData.admixture_lot"
								placeholder="输入批号"
								placeholder-class="input-placeholder"
							/>
						</view>
						<view class="input-item">
							<text class="item-label">实际用量</text>
							<input 
								class="item-input" 
								type="digit" 
								v-model="formData.admixture_actual"
								placeholder="请输入实际用量"
								placeholder-class="input-placeholder"
							/>
							<text class="item-unit">kg</text>
						</view>
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
				确认录入
			</button>
		</view>
	</view>
</template>

<script>
/**
 * 投料录入页面
 * 功能：
 * - 选择投料方式（扫码/手动）
 * - 输入盘号和方量
 * - 录入各材料实际用量
 * - 提交投料记录
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
			// 配方信息
			formulaInfo: null,
			// 理论用量
			theoryValues: {
				cement: 0,
				water: 0,
				sand: 0,
				stone: 0,
				admixture: 0
			},
			// 表单数据
			formData: {
				feeding_method: 'manual',
				batch_no: '',
				batch_quantity: '',
				
				// 水泥
				cement_barcode: '',
				cement_lot: '',
				cement_actual: '',
				
				// 水
				water_actual: '',
				
				// 砂子
				sand_barcode: '',
				sand_lot: '',
				sand_actual: '',
				
				// 石子
				stone_barcode: '',
				stone_lot: '',
				stone_actual: '',
				
				// 外加剂
				admixture_barcode: '',
				admixture_lot: '',
				admixture_actual: '',
				
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
		
		// 加载任务和配方信息
		if (this.taskId) {
			this.loadTaskInfo()
		}
	},
	
	watch: {
		// 监听方量变化，计算理论用量
		'formData.batch_quantity'(newVal) {
			this.calculateTheoryValues()
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
				
				// 获取配方信息
				if (res.formula_info) {
					this.formulaInfo = res.formula_info
				}
			} catch (error) {
				console.log('加载任务信息失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 计算理论用量
		 */
		calculateTheoryValues() {
			if (!this.formulaInfo || !this.formData.batch_quantity) {
				return
			}
			
			const qty = parseFloat(this.formData.batch_quantity) || 0
			
			this.theoryValues = {
				cement: this.formulaInfo.cement * qty,
				water: this.formulaInfo.water * qty,
				sand: this.formulaInfo.sand * qty,
				stone: this.formulaInfo.stone * qty,
				admixture: (this.formulaInfo.admixture || 0) * qty
			}
		},
		
		/**
		 * 重置表单
		 */
		resetForm() {
			this.formData = {
				feeding_method: 'manual',
				batch_no: '',
				batch_quantity: '',
				
				cement_barcode: '',
				cement_lot: '',
				cement_actual: '',
				
				water_actual: '',
				
				sand_barcode: '',
				sand_lot: '',
				sand_actual: '',
				
				stone_barcode: '',
				stone_lot: '',
				stone_actual: '',
				
				admixture_barcode: '',
				admixture_lot: '',
				admixture_actual: '',
				
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
		 * 提交录入
		 */
		async handleSubmit() {
			// 验证必填项
			if (!this.formData.batch_no) {
				uni.showToast({ title: '请输入盘号', icon: 'none' })
				return
			}
			
			if (!this.formData.batch_quantity) {
				uni.showToast({ title: '请输入本盘方量', icon: 'none' })
				return
			}
			
			// 构建提交数据
			const submitData = {
				task_id: this.taskId,
				batch_no: parseInt(this.formData.batch_no),
				batch_quantity: parseFloat(this.formData.batch_quantity),
				feeding_method: this.formData.feeding_method
			}
			
			// 添加材料用量
			if (this.formData.cement_actual) {
				submitData.cement_actual = parseFloat(this.formData.cement_actual)
			}
			if (this.formData.water_actual) {
				submitData.water_actual = parseFloat(this.formData.water_actual)
			}
			if (this.formData.sand_actual) {
				submitData.sand_actual = parseFloat(this.formData.sand_actual)
			}
			if (this.formData.stone_actual) {
				submitData.stone_actual = parseFloat(this.formData.stone_actual)
			}
			if (this.formData.admixture_actual) {
				submitData.admixture_actual = parseFloat(this.formData.admixture_actual)
			}
			
			// 添加条码信息（扫码方式）
			if (this.formData.feeding_method === 'scan') {
				if (this.formData.cement_barcode) submitData.cement_barcode = this.formData.cement_barcode
				if (this.formData.cement_lot) submitData.cement_lot = this.formData.cement_lot
				if (this.formData.sand_barcode) submitData.sand_barcode = this.formData.sand_barcode
				if (this.formData.sand_lot) submitData.sand_lot = this.formData.sand_lot
				if (this.formData.stone_barcode) submitData.stone_barcode = this.formData.stone_barcode
				if (this.formData.stone_lot) submitData.stone_lot = this.formData.stone_lot
				if (this.formData.admixture_barcode) submitData.admixture_barcode = this.formData.admixture_barcode
				if (this.formData.admixture_lot) submitData.admixture_lot = this.formData.admixture_lot
			}
			
			// 添加备注
			if (this.formData.remarks) {
				submitData.remarks = this.formData.remarks
			}
			
			// 确认提交
			const confirm = await this.showModal('确认录入', '确定要提交此投料记录吗？系统将自动计算偏差并检查预警。')
			if (!confirm) return
			
			this.submitting = true
			
			try {
				await api.feeding.create(submitData)
				
				uni.showToast({
					title: '录入成功',
					icon: 'success'
				})
				
				// 返回上一页
				setTimeout(() => {
					uni.navigateBack()
				}, 1500)
			} catch (error) {
				console.log('提交投料记录失败:', error)
			} finally {
				this.submitting = false
			}
		}
	}
}
</script>

<style scoped>
/* 投料录入页面样式 */
.feeding-add-container {
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

.card-tip {
	font-size: 24rpx;
	color: #999999;
	margin-left: auto;
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

/* 投料方式选项 */
.method-options {
	display: flex;
	gap: 30rpx;
}

.method-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 30rpx;
	background: #FAFAFA;
	border-radius: 16rpx;
	border: 2rpx solid #E8E8E8;
}

.method-item.active {
	background: #E6F7FF;
	border-color: #1890FF;
}

.method-icon {
	font-size: 48rpx;
	margin-bottom: 12rpx;
}

.method-text {
	font-size: 26rpx;
	color: #666666;
}

.method-item.active .method-text {
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

/* 材料区块 */
.material-section {
	margin-bottom: 30rpx;
	padding-bottom: 30rpx;
	border-bottom: 2rpx dashed #F0F0F0;
}

.material-section:last-child {
	margin-bottom: 0;
	padding-bottom: 0;
	border-bottom: none;
}

.section-header {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
}

.material-name {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

.theory-tip {
	font-size: 24rpx;
	color: #1890FF;
	background: #E6F7FF;
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
	margin-left: 16rpx;
}

/* 输入组 */
.input-group {
	display: flex;
	flex-direction: column;
	gap: 16rpx;
}

.input-item {
	display: flex;
	align-items: center;
}

.item-label {
	width: 140rpx;
	font-size: 26rpx;
	color: #999999;
	flex-shrink: 0;
}

.item-input {
	flex: 1;
	height: 72rpx;
	background: #FAFAFA;
	border-radius: 12rpx;
	padding: 0 16rpx;
	font-size: 26rpx;
	color: #333333;
}

.item-unit {
	font-size: 24rpx;
	color: #999999;
	margin-left: 12rpx;
	width: 50rpx;
	flex-shrink: 0;
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
