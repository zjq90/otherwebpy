<template>
	<view class="formula-adjust-container">
		<!-- 任务和配方信息 -->
		<view class="info-card" v-if="baseFormula">
			<view class="card-header">
				<text class="card-title">当前配方</text>
			</view>
			<view class="card-body">
				<view class="info-item">
					<text class="info-label">配方名称</text>
					<text class="info-value">{{ baseFormula.formula_name }}</text>
				</view>
				<view class="info-item">
					<text class="info-label">混凝土标号</text>
					<text class="info-value">{{ baseFormula.concrete_grade }}</text>
				</view>
				<view class="info-item">
					<text class="info-label">当前水灰比</text>
					<text class="info-value">{{ baseFormula.water_cement_ratio }}</text>
				</view>
			</view>
		</view>
		
		<!-- 调整原因 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">调整原因</text>
				<text class="card-required">*</text>
			</view>
			<view class="card-body">
				<textarea 
					class="reason-input" 
					v-model="formData.adjustment_reason"
					placeholder="请输入调整原因，如：现场砂石含水率变化、气温影响等"
					placeholder-class="input-placeholder"
					:maxlength="500"
				></textarea>
				<view class="char-count">
					<text>{{ formData.adjustment_reason.length }}/500</text>
				</view>
				
				<!-- 快捷原因 -->
				<view class="quick-reasons">
					<view 
						class="reason-tag" 
						v-for="(reason, index) in quickReasons" 
						:key="index"
						@click="addQuickReason(reason)"
					>
						{{ reason }}
					</view>
				</view>
			</view>
		</view>
		
		<!-- 参数调整 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">参数调整</text>
				<text class="card-tip">留空则使用原配方值</text>
			</view>
			
			<view class="card-body">
				<!-- 水灰比 -->
				<view class="adjust-item">
					<view class="adjust-header">
						<text class="adjust-label">水灰比</text>
						<text class="adjust-orig">原值：{{ baseFormula.water_cement_ratio }}</text>
					</view>
					<input 
						class="adjust-input" 
						type="digit" 
						v-model="formData.new_water_cement_ratio"
						placeholder="请输入新的水灰比"
						placeholder-class="input-placeholder"
					/>
				</view>
				
				<!-- 材料用量 -->
				<view class="adjust-section">
					<text class="section-title">材料用量调整（kg/m³）</text>
					
					<view class="material-grid">
						<view class="material-item">
							<text class="material-label">水泥</text>
							<view class="material-input-box">
								<text class="material-orig">{{ baseFormula.cement }}</text>
								<text class="material-arrow">→</text>
								<input 
									class="material-input" 
									type="digit" 
									v-model="formData.new_cement"
									placeholder="新值"
								/>
							</view>
						</view>
						
						<view class="material-item">
							<text class="material-label">水</text>
							<view class="material-input-box">
								<text class="material-orig">{{ baseFormula.water }}</text>
								<text class="material-arrow">→</text>
								<input 
									class="material-input" 
									type="digit" 
									v-model="formData.new_water"
									placeholder="新值"
								/>
							</view>
						</view>
						
						<view class="material-item">
							<text class="material-label">砂子</text>
							<view class="material-input-box">
								<text class="material-orig">{{ baseFormula.sand }}</text>
								<text class="material-arrow">→</text>
								<input 
									class="material-input" 
									type="digit" 
									v-model="formData.new_sand"
									placeholder="新值"
								/>
							</view>
						</view>
						
						<view class="material-item">
							<text class="material-label">石子</text>
							<view class="material-input-box">
								<text class="material-orig">{{ baseFormula.stone }}</text>
								<text class="material-arrow">→</text>
								<input 
									class="material-input" 
									type="digit" 
									v-model="formData.new_stone"
									placeholder="新值"
								/>
							</view>
						</view>
						
						<view class="material-item">
							<text class="material-label">外加剂</text>
							<view class="material-input-box">
								<text class="material-orig">{{ baseFormula.admixture || 0 }}</text>
								<text class="material-arrow">→</text>
								<input 
									class="material-input" 
									type="digit" 
									v-model="formData.new_admixture"
									placeholder="新值"
								/>
							</view>
						</view>
					</view>
				</view>
				
				<!-- 外加剂掺量 -->
				<view class="adjust-item">
					<view class="adjust-header">
						<text class="adjust-label">外加剂掺量（%）</text>
					</view>
					<input 
						class="adjust-input" 
						type="digit" 
						v-model="formData.new_admixture_dosage"
						placeholder="请输入外加剂掺量百分比"
						placeholder-class="input-placeholder"
					/>
				</view>
			</view>
		</view>
		
		<!-- 备注 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">备注说明</text>
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
				确认调整
			</button>
		</view>
	</view>
</template>

<script>
/**
 * 配方调整页面
 * 功能：
 * - 显示原配方参数
 * - 输入调整原因
 * - 微调各项参数
 * - 提交调整记录
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 任务ID和配方ID
			taskId: null,
			formulaId: null,
			// 基础配方信息
			baseFormula: {},
			// 表单数据
			formData: {
				adjustment_reason: '',
				new_water_cement_ratio: '',
				new_cement: '',
				new_water: '',
				new_sand: '',
				new_stone: '',
				new_admixture: '',
				new_admixture_dosage: '',
				remarks: ''
			},
			// 快捷原因
			quickReasons: [
				'砂石含水率变化',
				'气温影响调整',
				'坍落度要求调整',
				'现场实际情况',
				'外加剂效果调整'
			],
			// 提交状态
			submitting: false
		}
	},
	
	onLoad(options) {
		if (options.taskId) {
			this.taskId = parseInt(options.taskId)
		}
		if (options.formulaId) {
			this.formulaId = parseInt(options.formulaId)
			this.loadFormulaDetail()
		}
	},
	
	methods: {
		/**
		 * 加载配方详情
		 */
		async loadFormulaDetail() {
			uni.showLoading({ title: '加载中...' })
			
			try {
				const res = await api.formulas.getDetail(this.formulaId)
				this.baseFormula = res
			} catch (error) {
				console.log('加载配方详情失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 添加快捷原因
		 */
		addQuickReason(reason) {
			if (this.formData.adjustment_reason) {
				if (!this.formData.adjustment_reason.includes(reason)) {
					this.formData.adjustment_reason += '；' + reason
				}
			} else {
				this.formData.adjustment_reason = reason
			}
		},
		
		/**
		 * 重置表单
		 */
		resetForm() {
			this.formData = {
				adjustment_reason: '',
				new_water_cement_ratio: '',
				new_cement: '',
				new_water: '',
				new_sand: '',
				new_stone: '',
				new_admixture: '',
				new_admixture_dosage: '',
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
		 * 提交调整
		 */
		async handleSubmit() {
			// 验证调整原因
			if (!this.formData.adjustment_reason.trim()) {
				uni.showToast({
					title: '请输入调整原因',
					icon: 'none'
				})
				return
			}
			
			// 构建提交数据
			const submitData = {
				task_id: this.taskId,
				base_formula_id: this.formulaId,
				adjustment_reason: this.formData.adjustment_reason.trim()
			}
			
			// 添加调整后的参数（如果有填写）
			if (this.formData.new_water_cement_ratio) {
				submitData.new_water_cement_ratio = parseFloat(this.formData.new_water_cement_ratio)
			}
			if (this.formData.new_cement) {
				submitData.new_cement = parseFloat(this.formData.new_cement)
			}
			if (this.formData.new_water) {
				submitData.new_water = parseFloat(this.formData.new_water)
			}
			if (this.formData.new_sand) {
				submitData.new_sand = parseFloat(this.formData.new_sand)
			}
			if (this.formData.new_stone) {
				submitData.new_stone = parseFloat(this.formData.new_stone)
			}
			if (this.formData.new_admixture) {
				submitData.new_admixture = parseFloat(this.formData.new_admixture)
			}
			if (this.formData.new_admixture_dosage) {
				submitData.new_admixture_dosage = parseFloat(this.formData.new_admixture_dosage)
			}
			if (this.formData.remarks) {
				submitData.remarks = this.formData.remarks.trim()
			}
			
			// 确认提交
			const confirm = await this.showModal('确认调整', '确定要提交此配方调整吗？调整记录将同步到后台。')
			if (!confirm) return
			
			this.submitting = true
			
			try {
				await api.formulas.adjust(submitData)
				
				uni.showToast({
					title: '调整成功',
					icon: 'success'
				})
				
				// 返回上一页
				setTimeout(() => {
					uni.navigateBack()
				}, 1500)
			} catch (error) {
				console.log('提交调整失败:', error)
			} finally {
				this.submitting = false
			}
		}
	}
}
</script>

<style scoped>
/* 配方调整页面样式 */
.formula-adjust-container {
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
	margin-left: 16rpx;
}

.card-body {
	padding: 30rpx;
}

/* 信息项 */
.info-item {
	display: flex;
	margin-bottom: 20rpx;
}

.info-item:last-child {
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

/* 调整原因输入 */
.reason-input {
	width: 100%;
	height: 180rpx;
	background: #FAFAFA;
	border-radius: 16rpx;
	padding: 20rpx;
	font-size: 28rpx;
	color: #333333;
}

.input-placeholder {
	color: #CCCCCC;
}

.char-count {
	text-align: right;
	font-size: 24rpx;
	color: #999999;
	margin-top: 12rpx;
}

/* 快捷原因 */
.quick-reasons {
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
	margin-top: 20rpx;
	padding-top: 20rpx;
	border-top: 2rpx dashed #F0F0F0;
}

.reason-tag {
	font-size: 24rpx;
	color: #1890FF;
	background: #E6F7FF;
	padding: 10rpx 20rpx;
	border-radius: 8rpx;
}

/* 调整项 */
.adjust-item {
	margin-bottom: 30rpx;
}

.adjust-item:last-child {
	margin-bottom: 0;
}

.adjust-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.adjust-label {
	font-size: 28rpx;
	color: #333333;
}

.adjust-orig {
	font-size: 24rpx;
	color: #999999;
}

.adjust-input {
	width: 100%;
	height: 88rpx;
	background: #FAFAFA;
	border-radius: 16rpx;
	padding: 0 24rpx;
	font-size: 28rpx;
	color: #333333;
}

/* 材料网格 */
.adjust-section {
	padding: 24rpx 0;
	border-top: 2rpx solid #F5F5F5;
	border-bottom: 2rpx solid #F5F5F5;
	margin: 24rpx 0;
}

.section-title {
	font-size: 26rpx;
	color: #999999;
	margin-bottom: 24rpx;
	display: block;
}

.material-grid {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
}

.material-item {
	width: calc(50% - 10rpx);
	display: flex;
	flex-direction: column;
}

.material-label {
	font-size: 26rpx;
	color: #666666;
	margin-bottom: 12rpx;
}

.material-input-box {
	display: flex;
	align-items: center;
	background: #FAFAFA;
	border-radius: 12rpx;
	padding: 16rpx 20rpx;
}

.material-orig {
	font-size: 26rpx;
	color: #999999;
}

.material-arrow {
	font-size: 26rpx;
	color: #CCCCCC;
	margin: 0 12rpx;
}

.material-input {
	flex: 1;
	font-size: 28rpx;
	color: #1890FF;
	text-align: right;
}

/* 备注输入 */
.remark-input {
	width: 100%;
	height: 120rpx;
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
