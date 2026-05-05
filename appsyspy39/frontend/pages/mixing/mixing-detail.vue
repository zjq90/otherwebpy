<template>
	<view class="mixing-detail-container">
		<!-- 基本信息 -->
		<view class="info-card" v-if="recordInfo">
			<view class="card-header">
				<view class="header-left">
					<text class="task-no">任务 #{{ recordInfo.task_id }}</text>
					<text class="batch-no">第{{ recordInfo.batch_no }}盘</text>
				</view>
				<view class="status-badge" :class="recordInfo.status">
					{{ getStatusText(recordInfo.status) }}
				</view>
			</view>
			
			<view class="card-body">
				<view class="info-row">
					<text class="info-label">记录时间</text>
					<text class="info-value">{{ formatTime(recordInfo.created_at) }}</text>
				</view>
				
				<view class="info-row" v-if="recordInfo.completed_at">
					<text class="info-label">完成时间</text>
					<text class="info-value">{{ formatTime(recordInfo.completed_at) }}</text>
				</view>
			</view>
		</view>
		
		<!-- 搅拌参数 -->
		<view class="info-card">
			<view class="card-header">
				<text class="card-title">搅拌参数</text>
			</view>
			
			<view class="card-body">
				<view class="param-grid">
					<view class="param-item">
						<view class="param-icon time">
							<text class="iconfont icon-time"></text>
						</view>
						<view class="param-content">
							<text class="param-label">搅拌时长</text>
							<text class="param-value">{{ recordInfo.mixing_time_seconds }} 秒</text>
						</view>
					</view>
					
					<view class="param-item" v-if="recordInfo.rotation_speed">
						<view class="param-icon speed">
							<text class="iconfont icon-speed"></text>
						</view>
						<view class="param-content">
							<text class="param-label">搅拌转速</text>
							<text class="param-value">{{ recordInfo.rotation_speed }} RPM</text>
						</view>
					</view>
					
					<view class="param-item" v-if="recordInfo.current_temperature">
						<view class="param-icon temp">
							<text class="iconfont icon-temp"></text>
						</view>
						<view class="param-content">
							<text class="param-label">当前温度</text>
							<text class="param-value">{{ recordInfo.current_temperature }} ℃</text>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 异常信息 -->
		<view class="info-card abnormal-card" v-if="recordInfo && recordInfo.is_abnormal">
			<view class="card-header abnormal-header">
				<text class="alert-icon">⚠️</text>
				<text class="card-title abnormal-title">异常情况</text>
			</view>
			
			<view class="card-body">
				<view class="abnormal-row" v-if="recordInfo.abnormal_type">
					<text class="abnormal-label">异常类型</text>
					<text class="abnormal-value">
						<text class="type-badge">{{ getAbnormalTypeText(recordInfo.abnormal_type) }}</text>
					</text>
				</view>
				
				<view class="abnormal-row" v-if="recordInfo.abnormal_description">
					<text class="abnormal-label">情况说明</text>
					<text class="abnormal-desc">{{ recordInfo.abnormal_description }}</text>
				</view>
				
				<view class="abnormal-row" v-if="recordInfo.handling_measures">
					<text class="abnormal-label">处理措施</text>
					<text class="abnormal-desc">{{ recordInfo.handling_measures }}</text>
				</view>
			</view>
		</view>
		
		<!-- 质量检验 -->
		<view class="info-card" v-if="recordInfo && (recordInfo.slump_actual || recordInfo.quality_status)">
			<view class="card-header">
				<text class="card-title">质量检验</text>
			</view>
			
			<view class="card-body">
				<view class="quality-row" v-if="recordInfo.slump_actual">
					<text class="quality-label">实测坍落度</text>
					<text class="quality-value">{{ recordInfo.slump_actual }} mm</text>
				</view>
				
				<view class="quality-row" v-if="recordInfo.temperature_actual">
					<text class="quality-label">实测温度</text>
					<text class="quality-value">{{ recordInfo.temperature_actual }} ℃</text>
				</view>
				
				<view class="quality-row" v-if="recordInfo.quality_status">
					<text class="quality-label">质量状态</text>
					<view 
						class="quality-badge" 
						:class="recordInfo.quality_status"
					>
						{{ recordInfo.quality_status === 'qualified' ? '合格' : '不合格' }}
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
 * 搅拌记录详情页面
 * 功能：
 * - 显示搅拌记录详细信息
 * - 搅拌参数展示
 * - 异常情况展示
 * - 质量检验结果
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 记录ID
			recordId: null,
			// 记录信息
			recordInfo: null
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
				const res = await api.mixing.getDetail(this.recordId)
				this.recordInfo = res
			} catch (error) {
				console.log('加载搅拌详情失败:', error)
			} finally {
				uni.hideLoading()
			}
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
		 * 获取状态文本
		 */
		getStatusText(status) {
			const statusMap = {
				'mixing': '搅拌中',
				'completed': '已完成',
				'abnormal': '异常'
			}
			return statusMap[status] || status
		},
		
		/**
		 * 获取异常类型文本
		 */
		getAbnormalTypeText(type) {
			const typeMap = {
				'material_shortage': '缺料',
				'equipment_fault': '设备故障',
				'quality_issue': '质量问题',
				'other': '其他'
			}
			return typeMap[type] || type || '异常'
		}
	}
}
</script>

<style scoped>
/* 搅拌详情页面样式 */
.mixing-detail-container {
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

.status-badge {
	font-size: 24rpx;
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
}

.status-badge.completed {
	background: #F0F0F0;
	color: #666666;
}

.status-badge.mixing {
	background: #E6F7FF;
	color: #1890FF;
}

.status-badge.abnormal {
	background: #FFF1F0;
	color: #FF4D4F;
}

.card-title {
	font-size: 30rpx;
	color: #333333;
	font-weight: 500;
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

/* 参数网格 */
.param-grid {
	display: flex;
	flex-direction: column;
	gap: 30rpx;
}

.param-item {
	display: flex;
	align-items: center;
}

.param-icon {
	width: 80rpx;
	height: 80rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.param-icon.time {
	background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
}

.param-icon.speed {
	background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.param-icon.temp {
	background: linear-gradient(135deg, #FA8C16 0%, #FFA940 100%);
}

.param-icon .iconfont {
	font-size: 40rpx;
	color: #FFFFFF;
}

.param-content {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.param-label {
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 6rpx;
}

.param-value {
	font-size: 32rpx;
	color: #333333;
	font-weight: 500;
}

/* 异常卡片 */
.abnormal-card {
	border: 2rpx solid #FFA39E;
}

.abnormal-header {
	background: #FFF1F0;
	border-bottom: 2rpx solid #FFA39E;
}

.alert-icon {
	font-size: 32rpx;
	margin-right: 12rpx;
}

.abnormal-title {
	color: #FF4D4F;
}

/* 异常行 */
.abnormal-row {
	margin-bottom: 24rpx;
}

.abnormal-row:last-child {
	margin-bottom: 0;
}

.abnormal-label {
	font-size: 26rpx;
	color: #999999;
	margin-bottom: 12rpx;
	display: block;
}

.abnormal-value {
	display: flex;
	align-items: center;
}

.type-badge {
	font-size: 26rpx;
	color: #FFFFFF;
	background: #FF4D4F;
	padding: 8rpx 20rpx;
	border-radius: 8rpx;
}

.abnormal-desc {
	font-size: 26rpx;
	color: #666666;
	line-height: 1.6;
}

/* 质量行 */
.quality-row {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 20rpx;
	padding-bottom: 20rpx;
	border-bottom: 2rpx solid #F5F5F5;
}

.quality-row:last-child {
	margin-bottom: 0;
	padding-bottom: 0;
	border-bottom: none;
}

.quality-label {
	font-size: 28rpx;
	color: #666666;
}

.quality-value {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

.quality-badge {
	font-size: 26rpx;
	padding: 8rpx 20rpx;
	border-radius: 8rpx;
}

.quality-badge.qualified {
	background: #F6FFED;
	color: #52C41A;
}

.quality-badge.unqualified {
	background: #FFF1F0;
	color: #FF4D4F;
}

/* 备注 */
.remark-text {
	font-size: 28rpx;
	color: #666666;
	line-height: 1.6;
}
</style>
