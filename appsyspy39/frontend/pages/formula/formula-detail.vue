<template>
	<view class="formula-detail-container">
		<!-- 基础信息 -->
		<view class="info-card" v-if="formulaInfo">
			<view class="card-header">
				<view class="grade-box">
					<text class="grade-text">{{ formulaInfo.concrete_grade }}</text>
				</view>
				<view class="formula-info">
					<text class="formula-name">{{ formulaInfo.formula_name }}</text>
					<text class="formula-code">{{ formulaInfo.formula_code }}</text>
				</view>
				<view class="status-badge" :class="{ active: formulaInfo.is_active }">
					{{ formulaInfo.is_active ? '启用' : '禁用' }}
				</view>
			</view>
			
			<view class="card-body">
				<view class="info-row">
					<view class="info-item">
						<text class="info-label">水灰比</text>
						<text class="info-value highlight">{{ formulaInfo.water_cement_ratio }}</text>
					</view>
					<view class="info-item">
						<text class="info-label">坍落度</text>
						<text class="info-value">{{ formulaInfo.slump || '-' }} mm</text>
					</view>
					<view class="info-item">
						<text class="info-label">类型</text>
						<text class="info-value">{{ formulaInfo.is_standard ? '标准配方' : '自定义配方' }}</text>
					</view>
				</view>
				
				<view class="info-row" v-if="formulaInfo.admixture_type">
					<text class="info-label">外加剂类型</text>
					<text class="info-value">{{ formulaInfo.admixture_type }}</text>
				</view>
				
				<view class="info-row" v-if="formulaInfo.remarks">
					<text class="info-label">备注说明</text>
					<text class="info-value">{{ formulaInfo.remarks }}</text>
				</view>
			</view>
		</view>
		
		<!-- 材料用量 -->
		<view class="info-card">
			<view class="card-title">
				<text class="title-text">材料用量（每立方米）</text>
			</view>
			
			<view class="material-list">
				<view class="material-item" v-for="(material, index) in materialList" :key="index">
					<view class="material-left">
						<view class="material-icon" :class="'icon-' + material.type">
							<text class="iconfont" :class="material.icon"></text>
						</view>
						<text class="material-name">{{ material.name }}</text>
					</view>
					<view class="material-right">
						<text class="material-qty">{{ material.value }} kg</text>
						<text class="material-unit">/ m³</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 材料比例图 -->
		<view class="info-card">
			<view class="card-title">
				<text class="title-text">材料比例示意</text>
			</view>
			
			<view class="ratio-chart">
				<view class="chart-bar">
					<view 
						class="bar-segment" 
						v-for="(material, index) in ratioList" 
						:key="index"
						:style="{ width: material.ratio + '%', backgroundColor: material.color }"
						:title="material.name + ': ' + material.ratio + '%'"
					></view>
				</view>
				<view class="chart-legend">
					<view class="legend-item" v-for="(material, index) in ratioList" :key="index">
						<view class="legend-dot" :style="{ backgroundColor: material.color }"></view>
						<text class="legend-text">{{ material.name }} ({{ material.ratio }}%)</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 底部操作栏 -->
		<view class="bottom-bar">
			<button class="bar-btn outline" @click="goBack">
				返回列表
			</button>
			<button class="bar-btn primary" @click="useFormula">
				使用此配方
			</button>
		</view>
	</view>
</template>

<script>
/**
 * 配方详情页面
 * 功能：
 * - 显示配方详细信息
 * - 显示材料用量和比例
 * - 快速使用配方
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 配方ID
			formulaId: null,
			// 配方信息
			formulaInfo: null,
			// 材料列表
			materialList: [],
			// 比例列表
			ratioList: []
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.formulaId = parseInt(options.id)
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
				this.formulaInfo = res
				
				// 构建材料列表
				this.buildMaterialList(res)
				
				// 计算比例
				this.calculateRatio(res)
			} catch (error) {
				console.log('加载配方详情失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 构建材料列表
		 */
		buildMaterialList(formula) {
			this.materialList = []
			
			// 水泥
			this.materialList.push({
				name: '水泥',
				value: formula.cement,
				type: 'cement',
				icon: 'icon-cement'
			})
			
			// 水
			this.materialList.push({
				name: '水',
				value: formula.water,
				type: 'water',
				icon: 'icon-water'
			})
			
			// 砂子
			this.materialList.push({
				name: '砂子',
				value: formula.sand,
				type: 'sand',
				icon: 'icon-sand'
			})
			
			// 石子
			this.materialList.push({
				name: '石子',
				value: formula.stone,
				type: 'stone',
				icon: 'icon-stone'
			})
			
			// 外加剂
			if (formula.admixture && formula.admixture > 0) {
				this.materialList.push({
					name: formula.admixture_type || '外加剂',
					value: formula.admixture,
					type: 'admixture',
					icon: 'icon-admixture'
				})
			}
			
			// 粉煤灰
			if (formula.fly_ash && formula.fly_ash > 0) {
				this.materialList.push({
					name: '粉煤灰',
					value: formula.fly_ash,
					type: 'flyash',
					icon: 'icon-flyash'
				})
			}
			
			// 矿粉
			if (formula.mineral_powder && formula.mineral_powder > 0) {
				this.materialList.push({
					name: '矿粉',
					value: formula.mineral_powder,
					type: 'mineral',
					icon: 'icon-mineral'
				})
			}
		},
		
		/**
		 * 计算材料比例
		 */
		calculateRatio(formula) {
			const total = formula.cement + formula.water + formula.sand + formula.stone +
				(formula.admixture || 0) + (formula.fly_ash || 0) + (formula.mineral_powder || 0)
			
			if (total === 0) return
			
			const colors = [
				'#1890FF', '#FA8C16', '#52C41A', '#722ED1', '#FF4D4F', '#13C2C2', '#EB2F96'
			]
			
			const mainMaterials = [
				{ name: '水泥', value: formula.cement, color: colors[0] },
				{ name: '水', value: formula.water, color: colors[1] },
				{ name: '砂子', value: formula.sand, color: colors[2] },
				{ name: '石子', value: formula.stone, color: colors[3] }
			]
			
			this.ratioList = mainMaterials.map((m, index) => ({
				...m,
				ratio: Math.round((m.value / total) * 100 * 10) / 10
			}))
		},
		
		/**
		 * 返回列表
		 */
		goBack() {
			uni.navigateBack()
		},
		
		/**
		 * 使用配方
		 */
		useFormula() {
			uni.showToast({
				title: '请选择任务后使用',
				icon: 'none'
			})
		}
	}
}
</script>

<style scoped>
/* 配方详情页面样式 */
.formula-detail-container {
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
	padding: 30rpx;
	background: linear-gradient(90deg, #FAFAFA 0%, #FFFFFF 100%);
	border-bottom: 2rpx solid #F0F0F0;
}

.grade-box {
	background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
	padding: 16rpx 28rpx;
	border-radius: 16rpx;
	margin-right: 24rpx;
	flex-shrink: 0;
}

.grade-text {
	font-size: 36rpx;
	color: #FFFFFF;
	font-weight: bold;
}

.formula-info {
	flex: 1;
	min-width: 0;
	display: flex;
	flex-direction: column;
}

.formula-name {
	font-size: 30rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 8rpx;
}

.formula-code {
	font-size: 24rpx;
	color: #999999;
}

.status-badge {
	font-size: 24rpx;
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
	background: #F0F0F0;
	color: #999999;
	margin-left: 16rpx;
	flex-shrink: 0;
}

.status-badge.active {
	background: #F6FFED;
	color: #52C41A;
}

/* 卡片主体 */
.card-body {
	padding: 30rpx;
}

.info-row {
	display: flex;
	margin-bottom: 24rpx;
	align-items: flex-start;
}

.info-row:last-child {
	margin-bottom: 0;
}

.info-item {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 20rpx;
	background: #FAFAFA;
	border-radius: 16rpx;
	margin: 0 10rpx;
}

.info-item:first-child {
	margin-left: 0;
}

.info-item:last-child {
	margin-right: 0;
}

.info-label {
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 12rpx;
}

.info-value {
	font-size: 32rpx;
	color: #333333;
	font-weight: bold;
}

.info-value.highlight {
	color: #1890FF;
}

.info-row .info-label {
	width: 160rpx;
	font-size: 28rpx;
	color: #999999;
	flex-shrink: 0;
}

.info-row .info-value {
	flex: 1;
	font-size: 28rpx;
	color: #333333;
	font-weight: normal;
}

/* 卡片标题 */
.card-title {
	display: flex;
	align-items: center;
	padding: 24rpx 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.title-text {
	font-size: 30rpx;
	color: #333333;
	font-weight: 500;
}

/* 材料列表 */
.material-list {
	padding: 20rpx 30rpx;
}

.material-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 24rpx 0;
	border-bottom: 2rpx solid #F5F5F5;
}

.material-item:last-child {
	border-bottom: none;
}

.material-left {
	display: flex;
	align-items: center;
}

.material-icon {
	width: 72rpx;
	height: 72rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
}

.icon-cement {
	background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
}

.icon-water {
	background: linear-gradient(135deg, #13C2C2 0%, #36CFBA 100%);
}

.icon-sand {
	background: linear-gradient(135deg, #FA8C16 0%, #FFA940 100%);
}

.icon-stone {
	background: linear-gradient(135deg, #722ED1 0%, #9254DE 100%);
}

.icon-admixture {
	background: linear-gradient(135deg, #EB2F96 0%, #F759AB 100%);
}

.icon-flyash {
	background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.icon-mineral {
	background: linear-gradient(135deg, #A0D911 0%, #BAE637 100%);
}

.material-icon .iconfont {
	font-size: 36rpx;
	color: #FFFFFF;
}

.material-name {
	font-size: 28rpx;
	color: #333333;
}

.material-right {
	display: flex;
	align-items: baseline;
}

.material-qty {
	font-size: 32rpx;
	color: #1890FF;
	font-weight: bold;
}

.material-unit {
	font-size: 22rpx;
	color: #999999;
	margin-left: 4rpx;
}

/* 比例图 */
.ratio-chart {
	padding: 30rpx;
}

.chart-bar {
	height: 60rpx;
	background: #F5F5F5;
	border-radius: 30rpx;
	display: flex;
	overflow: hidden;
	margin-bottom: 30rpx;
}

.bar-segment {
	height: 100%;
	transition: width 0.3s ease;
}

.chart-legend {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
}

.legend-item {
	display: flex;
	align-items: center;
	flex: 0 0 45%;
}

.legend-dot {
	width: 16rpx;
	height: 16rpx;
	border-radius: 50%;
	margin-right: 12rpx;
}

.legend-text {
	font-size: 24rpx;
	color: #666666;
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
	color: #1890FF;
	border: 2rpx solid #1890FF;
}

.bar-btn.primary {
	background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
	color: #FFFFFF;
}
</style>
