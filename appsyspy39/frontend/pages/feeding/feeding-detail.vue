<template>
	<view class="feeding-detail-container">
		<!-- 基本信息 -->
		<view class="info-card" v-if="recordInfo">
			<view class="card-header">
				<view class="header-left">
					<text class="task-no">任务 #{{ recordInfo.task_id }}</text>
					<text class="batch-no">第{{ recordInfo.batch_no }}盘</text>
				</view>
				<view class="warning-badge" v-if="recordInfo.has_warning">
					<view 
						class="badge-dot" 
						:class="recordInfo.warning_level"
					></view>
					<text class="badge-text">{{ recordInfo.warning_level === 'critical' ? '严重预警' : '预警' }}</text>
				</view>
			</view>
			
			<view class="card-body">
				<view class="info-row">
					<text class="info-label">投料方式</text>
					<text class="info-value">
						<text class="method-tag" :class="recordInfo.feeding_method">
							{{ recordInfo.feeding_method === 'scan' ? '扫码录入' : '手动录入' }}
						</text>
					</text>
				</view>
				
				<view class="info-row">
					<text class="info-label">本盘方量</text>
					<text class="info-value highlight">{{ recordInfo.batch_quantity }} m³</text>
				</view>
				
				<view class="info-row">
					<text class="info-label">投料时间</text>
					<text class="info-value">{{ formatTime(recordInfo.created_at) }}</text>
				</view>
			</view>
			
			<!-- 预警信息 -->
			<view class="warning-alert" v-if="recordInfo.has_warning && recordInfo.warning_message">
				<view class="alert-header">
					<text class="alert-icon">⚠️</text>
					<text class="alert-title">{{ recordInfo.warning_level === 'critical' ? '严重预警' : '投料偏差预警' }}</text>
				</view>
				<text class="alert-content">{{ recordInfo.warning_message }}</text>
			</view>
		</view>
		
		<!-- 用量对比 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">用量对比</text>
				<text class="card-tip">单位：kg</text>
			</view>
			
			<view class="card-body">
				<view 
					class="material-row" 
					v-for="(material, index) in materialList" 
					:key="index"
					:class="{ 'has-warning': material.hasWarning }"
				>
					<view class="material-header">
						<text class="material-name">{{ material.name }}</text>
						<view 
							class="deviation-badge" 
							v-if="material.deviation !== null && material.deviation !== undefined"
							:class="getDeviationClass(material.deviation)"
						>
							<text>{{ material.deviation > 0 ? '+' : '' }}{{ material.deviation }}%</text>
						</view>
					</view>
					
					<view class="comparison-row">
						<view class="comparison-item">
							<text class="item-label">理论用量</text>
							<text class="item-value theory">{{ material.theory }}</text>
						</view>
						
						<text class="comparison-arrow">→</text>
						
						<view class="comparison-item">
							<text class="item-label">实际用量</text>
							<text class="item-value actual" :class="getDeviationClass(material.deviation)">
								{{ material.actual }}
							</text>
						</view>
					</view>
					
					<!-- 偏差进度条 -->
					<view class="deviation-bar" v-if="material.deviation !== null && material.deviation !== undefined">
						<view class="bar-bg">
							<view 
								class="bar-fill" 
								:class="getDeviationClass(material.deviation)"
								:style="{ width: getDeviationWidth(material.deviation) + '%' }"
							></view>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 扫码信息 -->
		<view class="info-card" v-if="hasBarcodeInfo">
			<view class="card-header">
				<text class="card-title">扫码信息</text>
			</view>
			
			<view class="card-body">
				<view class="barcode-row" v-if="recordInfo.cement_barcode || recordInfo.cement_lot">
					<text class="barcode-label">水泥</text>
					<view class="barcode-info">
						<text v-if="recordInfo.cement_barcode" class="barcode-text">条码: {{ recordInfo.cement_barcode }}</text>
						<text v-if="recordInfo.cement_lot" class="barcode-text">批号: {{ recordInfo.cement_lot }}</text>
					</view>
				</view>
				
				<view class="barcode-row" v-if="recordInfo.sand_barcode || recordInfo.sand_lot">
					<text class="barcode-label">砂子</text>
					<view class="barcode-info">
						<text v-if="recordInfo.sand_barcode" class="barcode-text">条码: {{ recordInfo.sand_barcode }}</text>
						<text v-if="recordInfo.sand_lot" class="barcode-text">批号: {{ recordInfo.sand_lot }}</text>
					</view>
				</view>
				
				<view class="barcode-row" v-if="recordInfo.stone_barcode || recordInfo.stone_lot">
					<text class="barcode-label">石子</text>
					<view class="barcode-info">
						<text v-if="recordInfo.stone_barcode" class="barcode-text">条码: {{ recordInfo.stone_barcode }}</text>
						<text v-if="recordInfo.stone_lot" class="barcode-text">批号: {{ recordInfo.stone_lot }}</text>
					</view>
				</view>
				
				<view class="barcode-row" v-if="recordInfo.admixture_barcode || recordInfo.admixture_lot">
					<text class="barcode-label">外加剂</text>
					<view class="barcode-info">
						<text v-if="recordInfo.admixture_barcode" class="barcode-text">条码: {{ recordInfo.admixture_barcode }}</text>
						<text v-if="recordInfo.admixture_lot" class="barcode-text">批号: {{ recordInfo.admixture_lot }}</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 备注 -->
		<view class="info-card" v-if="recordInfo && recordInfo.remarks">
			<view class="card-header">
				<text class="card-title">备注</text>
			</view>
			<view class="card-body">
				<text class="remark-text">{{ recordInfo.remarks }}</text>
			</view>
		</view>
	</view>
</template>

<script>
/**
 * 投料记录详情页面
 * 功能：
 * - 显示投料记录详细信息
 * - 用量对比展示
 * - 偏差可视化
 * - 扫码信息展示
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 记录ID
			recordId: null,
			// 记录信息
			recordInfo: null,
			// 材料列表
			materialList: [],
			// 是否有条码信息
			hasBarcodeInfo: false
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.recordId = parseInt(options.id)
			this.loadRecordDetail()
		}
	},
	
	methods: {
		/**
		 * 加载记录详情
		 */
		async loadRecordDetail() {
			uni.showLoading({ title: '加载中...' })
			
			try {
				const res = await api.feeding.getDetail(this.recordId)
				this.recordInfo = res
				
				// 构建材料列表
				this.buildMaterialList(res)
				
				// 检查是否有条码信息
				this.checkBarcodeInfo(res)
			} catch (error) {
				console.log('加载投料详情失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 构建材料列表
		 */
		buildMaterialList(record) {
			this.materialList = []
			
			// 水泥
			if (record.cement_actual !== null && record.cement_actual !== undefined) {
				this.materialList.push({
					name: '水泥',
					theory: record.cement_theory,
					actual: record.cement_actual,
					deviation: record.cement_deviation,
					hasWarning: record.cement_deviation !== null && 
						record.cement_deviation !== undefined && 
						Math.abs(record.cement_deviation) >= 5
				})
			}
			
			// 水
			if (record.water_actual !== null && record.water_actual !== undefined) {
				this.materialList.push({
					name: '水',
					theory: record.water_theory,
					actual: record.water_actual,
					deviation: record.water_deviation,
					hasWarning: record.water_deviation !== null && 
						record.water_deviation !== undefined && 
						Math.abs(record.water_deviation) >= 5
				})
			}
			
			// 砂子
			if (record.sand_actual !== null && record.sand_actual !== undefined) {
				this.materialList.push({
					name: '砂子',
					theory: record.sand_theory,
					actual: record.sand_actual,
					deviation: record.sand_deviation,
					hasWarning: record.sand_deviation !== null && 
						record.sand_deviation !== undefined && 
						Math.abs(record.sand_deviation) >= 5
				})
			}
			
			// 石子
			if (record.stone_actual !== null && record.stone_actual !== undefined) {
				this.materialList.push({
					name: '石子',
					theory: record.stone_theory,
					actual: record.stone_actual,
					deviation: record.stone_deviation,
					hasWarning: record.stone_deviation !== null && 
						record.stone_deviation !== undefined && 
						Math.abs(record.stone_deviation) >= 5
				})
			}
			
			// 外加剂
			if (record.admixture_actual !== null && record.admixture_actual !== undefined) {
				this.materialList.push({
					name: '外加剂',
					theory: record.admixture_theory,
					actual: record.admixture_actual,
					deviation: record.admixture_deviation,
					hasWarning: record.admixture_deviation !== null && 
						record.admixture_deviation !== undefined && 
						Math.abs(record.admixture_deviation) >= 5
				})
			}
		},
		
		/**
		 * 检查是否有条码信息
		 */
		checkBarcodeInfo(record) {
			this.hasBarcodeInfo = !!(
				record.cement_barcode || record.cement_lot ||
				record.sand_barcode || record.sand_lot ||
				record.stone_barcode || record.stone_lot ||
				record.admixture_barcode || record.admixture_lot
			)
		},
		
		/**
		 * 格式化时间
		 */
		formatTime(time) {
			if (!time) return ''
			const date = new Date(time)
			const year = date.getFullYear()
			const month = String(date.getMonth() + 1).padStart(2, '0')
			const day = String(date.getDate()).padStart(2, '0')
			const hour = String(date.getHours()).padStart(2, '0')
			const minute = String(date.getMinutes()).padStart(2, '0')
			return `${year}-${month}-${day} ${hour}:${minute}`
		},
		
		/**
		 * 获取偏差样式类
		 */
		getDeviationClass(deviation) {
			if (deviation === null || deviation === undefined) return ''
			const abs = Math.abs(deviation)
			if (abs >= 10) return 'critical'
			if (abs >= 5) return 'warning'
			return 'normal'
		},
		
		/**
		 * 获取偏差宽度
		 */
		getDeviationWidth(deviation) {
			if (deviation === null || deviation === undefined) return 50
			const abs = Math.abs(deviation)
			// 最大显示20%
			const width = Math.min(abs * 5, 100)
			return Math.max(width, 10)
		}
	}
}
</script>

<style scoped>
/* 投料详情页面样式 */
.feeding-detail-container {
	min-height: 100vh;
	background: #F5F7FA;
	padding-bottom: 40rpx;
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
	justify-content: space-between;
	align-items: center;
	padding: 24rpx 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.header-left {
	display: flex;
	align-items: center;
	gap: 20rpx;
}

.task-no {
	font-size: 28rpx;
	color: #1890FF;
	font-weight: 500;
}

.batch-no {
	font-size: 26rpx;
	color: #666666;
	background: #F5F7FA;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
}

.warning-badge {
	display: flex;
	align-items: center;
	gap: 8rpx;
	padding: 10rpx 20rpx;
	border-radius: 24rpx;
	background: #FFF7E6;
}

.badge-dot {
	width: 16rpx;
	height: 16rpx;
	border-radius: 50%;
}

.badge-dot.warning {
	background: #FA8C16;
}

.badge-dot.critical {
	background: #FF4D4F;
}

.badge-text {
	font-size: 24rpx;
	color: #FA8C16;
}

.warning-badge.critical {
	background: #FFF1F0;
}

.warning-badge.critical .badge-text {
	color: #FF4D4F;
}

.card-title {
	font-size: 30rpx;
	color: #333333;
	font-weight: 500;
}

.card-tip {
	font-size: 24rpx;
	color: #999999;
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

.method-tag {
	font-size: 24rpx;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
}

.method-tag.scan {
	background: #E6F7FF;
	color: #1890FF;
}

.method-tag.manual {
	background: #FFF7E6;
	color: #FA8C16;
}

/* 预警提示 */
.warning-alert {
	padding: 24rpx 30rpx;
	background: #FFF1F0;
	border-top: 2rpx solid #FFA39E;
}

.alert-header {
	display: flex;
	align-items: center;
	margin-bottom: 12rpx;
}

.alert-icon {
	font-size: 32rpx;
	margin-right: 12rpx;
}

.alert-title {
	font-size: 28rpx;
	color: #FF4D4F;
	font-weight: 500;
}

.alert-content {
	font-size: 26rpx;
	color: #CF1322;
	line-height: 1.6;
}

/* 材料行 */
.material-row {
	padding: 24rpx 0;
	border-bottom: 2rpx solid #F5F5F5;
}

.material-row:last-child {
	border-bottom: none;
	padding-bottom: 0;
}

.material-row.has-warning {
	background: #FFF1F0;
	margin: 0 -30rpx;
	padding: 24rpx 30rpx;
	border-radius: 12rpx;
}

.material-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 16rpx;
}

.material-name {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

.deviation-badge {
	font-size: 24rpx;
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
}

.deviation-badge.normal {
	background: #F6FFED;
	color: #52C41A;
}

.deviation-badge.warning {
	background: #FFF7E6;
	color: #FA8C16;
}

.deviation-badge.critical {
	background: #FFF1F0;
	color: #FF4D4F;
}

/* 用量对比 */
.comparison-row {
	display: flex;
	align-items: center;
	justify-content: space-between;
	margin-bottom: 16rpx;
}

.comparison-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 16rpx;
	background: #FAFAFA;
	border-radius: 12rpx;
}

.item-label {
	font-size: 22rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.item-value {
	font-size: 32rpx;
	font-weight: 500;
}

.item-value.theory {
	color: #666666;
}

.item-value.actual {
	color: #333333;
}

.item-value.actual.normal {
	color: #52C41A;
}

.item-value.actual.warning {
	color: #FA8C16;
}

.item-value.actual.critical {
	color: #FF4D4F;
}

.comparison-arrow {
	font-size: 32rpx;
	color: #999999;
	margin: 0 20rpx;
}

/* 偏差进度条 */
.deviation-bar {
	display: flex;
	align-items: center;
}

.bar-bg {
	flex: 1;
	height: 12rpx;
	background: #F0F0F0;
	border-radius: 6rpx;
	overflow: hidden;
	position: relative;
}

.bar-fill {
	height: 100%;
	position: absolute;
	left: 50%;
	transform: translateX(-50%);
	border-radius: 6rpx;
}

.bar-fill.normal {
	background: #52C41A;
}

.bar-fill.warning {
	background: #FA8C16;
}

.bar-fill.critical {
	background: #FF4D4F;
}

/* 扫码信息 */
.barcode-row {
	display: flex;
	margin-bottom: 20rpx;
}

.barcode-row:last-child {
	margin-bottom: 0;
}

.barcode-label {
	width: 120rpx;
	font-size: 26rpx;
	color: #999999;
	flex-shrink: 0;
}

.barcode-info {
	flex: 1;
	display: flex;
	flex-wrap: wrap;
	gap: 16rpx;
}

.barcode-text {
	font-size: 24rpx;
	color: #666666;
	background: #F5F7FA;
	padding: 6rpx 12rpx;
	border-radius: 6rpx;
}

/* 备注 */
.remark-text {
	font-size: 28rpx;
	color: #666666;
	line-height: 1.6;
}
</style>
