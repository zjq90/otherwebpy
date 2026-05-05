<template>
	<view class="task-detail-container">
		<!-- 任务信息卡片 -->
		<view class="info-card" v-if="taskInfo">
			<view class="card-header">
				<view class="task-no-box">
					<text class="task-no">{{ taskInfo.task_no }}</text>
				</view>
				<view class="status-tag" :class="'status-' + taskInfo.status">
					{{ getStatusText(taskInfo.status) }}
				</view>
			</view>
			
			<view class="card-body">
				<view class="info-item">
					<text class="info-label">项目名称</text>
					<text class="info-value">{{ taskInfo.project_name }}</text>
				</view>
				
				<view class="info-item">
					<text class="info-label">项目地址</text>
					<text class="info-value">{{ taskInfo.project_address || '暂无' }}</text>
				</view>
				
				<view class="info-item">
					<text class="info-label">客户名称</text>
					<text class="info-value">{{ taskInfo.customer_name || '暂无' }}</text>
				</view>
				
				<view class="info-row">
					<view class="info-box">
						<text class="box-label">混凝土标号</text>
						<text class="box-value highlight">{{ taskInfo.concrete_grade }}</text>
					</view>
					<view class="info-box">
						<text class="box-label">生产数量</text>
						<text class="box-value">{{ taskInfo.quantity }} m³</text>
					</view>
				</view>
				
				<view class="info-item" v-if="taskInfo.operator_name">
					<text class="info-label">接单人</text>
					<text class="info-value">{{ taskInfo.operator_name }}</text>
				</view>
				
				<view class="info-item time-item">
					<text class="info-label">交货时间</text>
					<text class="info-value time">{{ formatTime(taskInfo.delivery_time) }}</text>
				</view>
				
				<view class="info-item" v-if="taskInfo.remarks">
					<text class="info-label">备注</text>
					<text class="info-value">{{ taskInfo.remarks }}</text>
				</view>
			</view>
		</view>
		
		<!-- 配方信息 -->
		<view class="info-card" v-if="taskInfo.formula_info">
			<view class="card-title">
				<text class="iconfont icon-formula"></text>
				<text class="title-text">配合比配方</text>
			</view>
			
			<view class="formula-info">
				<view class="formula-header">
					<text class="formula-name">{{ taskInfo.formula_info.formula_name }}</text>
					<text class="formula-code">{{ taskInfo.formula_info.formula_code }}</text>
				</view>
				
				<view class="formula-grid">
					<view class="grid-item">
						<text class="grid-label">水灰比</text>
						<text class="grid-value">{{ taskInfo.formula_info.water_cement_ratio }}</text>
					</view>
					<view class="grid-item">
						<text class="grid-label">坍落度</text>
						<text class="grid-value">{{ taskInfo.formula_info.slump || '-' }} mm</text>
					</view>
				</view>
				
				<view class="material-list">
					<view class="material-item" v-for="(material, index) in formulaMaterials" :key="index">
						<text class="material-name">{{ material.name }}</text>
						<text class="material-qty">{{ material.value }} kg/m³</text>
					</view>
				</view>
				
				<view class="formula-footer">
					<button class="view-btn" @click="goToFormulaDetail">查看详情</button>
					<button class="adjust-btn" v-if="taskInfo.status === 'in_progress'" @click="goToAdjust">调整配方</button>
				</view>
			</view>
		</view>
		
		<!-- 快捷操作 -->
		<view class="quick-actions" v-if="taskInfo && taskInfo.status !== 'completed' && taskInfo.status !== 'cancelled'">
			<view class="action-item" v-if="taskInfo.status === 'pending'" @click="handleAccept">
				<view class="action-icon bg-blue">
					<text class="iconfont icon-accept"></text>
				</view>
				<text class="action-text">接单</text>
			</view>
			
			<view class="action-item" v-if="taskInfo.status === 'accepted'" @click="handleStart">
				<view class="action-icon bg-green">
					<text class="iconfont icon-play"></text>
				</view>
				<text class="action-text">开始生产</text>
			</view>
			
			<view class="action-item" v-if="taskInfo.status === 'in_progress'" @click="goToFeeding">
				<view class="action-icon bg-orange">
					<text class="iconfont icon-feeding"></text>
				</view>
				<text class="action-text">投料录入</text>
			</view>
			
			<view class="action-item" v-if="taskInfo.status === 'in_progress'" @click="goToMixing">
				<view class="action-icon bg-purple">
					<text class="iconfont icon-mixing"></text>
				</view>
				<text class="action-text">搅拌记录</text>
			</view>
			
			<view class="action-item" v-if="taskInfo.status === 'in_progress'" @click="handleComplete">
				<view class="action-icon bg-success">
					<text class="iconfont icon-complete"></text>
				</view>
				<text class="action-text">完成任务</text>
			</view>
		</view>
		
		<!-- 时间线 -->
		<view class="info-card" v-if="taskInfo">
			<view class="card-title">
				<text class="iconfont icon-time"></text>
				<text class="title-text">进度时间线</text>
			</view>
			
			<view class="timeline">
				<view class="timeline-item" :class="{ done: true }">
					<view class="timeline-dot"></view>
					<view class="timeline-content">
						<text class="timeline-title">任务创建</text>
						<text class="timeline-time">{{ formatTime(taskInfo.created_at) }}</text>
					</view>
				</view>
				
				<view class="timeline-item" :class="{ done: taskInfo.accepted_at }" v-if="taskInfo.status !== 'pending'">
					<view class="timeline-dot"></view>
					<view class="timeline-content">
						<text class="timeline-title">任务接单</text>
						<text class="timeline-time" v-if="taskInfo.accepted_at">{{ formatTime(taskInfo.accepted_at) }}</text>
						<text class="timeline-time pending" v-else>待接单</text>
					</view>
				</view>
				
				<view class="timeline-item" :class="{ done: taskInfo.started_at }" v-if="taskInfo.status !== 'pending' && taskInfo.status !== 'accepted'">
					<view class="timeline-dot"></view>
					<view class="timeline-content">
						<text class="timeline-title">开始生产</text>
						<text class="timeline-time" v-if="taskInfo.started_at">{{ formatTime(taskInfo.started_at) }}</text>
						<text class="timeline-time pending" v-else>待开始</text>
					</view>
				</view>
				
				<view class="timeline-item" :class="{ done: taskInfo.completed_at }" v-if="taskInfo.status === 'completed'">
					<view class="timeline-dot"></view>
					<view class="timeline-content">
						<text class="timeline-title">任务完成</text>
						<text class="timeline-time">{{ formatTime(taskInfo.completed_at) }}</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 底部操作栏 -->
		<view class="bottom-bar" v-if="taskInfo">
			<view class="bar-left" v-if="taskInfo.status === 'in_progress'">
				<button class="bar-btn outline" @click="goToFeedingList">投料记录</button>
				<button class="bar-btn outline" @click="goToMixingList">搅拌记录</button>
			</view>
			
			<view class="bar-right">
				<button 
					class="bar-btn primary" 
					v-if="taskInfo.status === 'pending'"
					:loading="accepting"
					@click="handleAccept"
				>
					一键接单
				</button>
				
				<button 
					class="bar-btn success" 
					v-if="taskInfo.status === 'accepted'"
					@click="handleStart"
				>
					开始生产
				</button>
				
				<button 
					class="bar-btn success" 
					v-if="taskInfo.status === 'in_progress'"
					@click="handleComplete"
				>
					完成任务
				</button>
			</view>
		</view>
	</view>
</template>

<script>
/**
 * 任务详情页面
 * 功能：
 * - 显示任务详细信息
 * - 显示关联配方信息
 * - 任务状态操作（接单、开始、完成）
 * - 进度时间线
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 任务ID
			taskId: null,
			// 任务信息
			taskInfo: null,
			// 操作状态
			accepting: false,
			// 配方材料列表
			formulaMaterials: []
		}
	},
	
	onLoad(options) {
		if (options.id) {
			this.taskId = parseInt(options.id)
			this.loadTaskDetail()
		}
	},
	
	methods: {
		/**
		 * 加载任务详情
		 */
		async loadTaskDetail() {
			uni.showLoading({ title: '加载中...' })
			
			try {
				const res = await api.tasks.getDetail(this.taskId)
				this.taskInfo = res
				
				// 构建配方材料列表
				if (res.formula_info) {
					this.buildFormulaMaterials(res.formula_info)
				}
			} catch (error) {
				console.log('加载任务详情失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 构建配方材料列表
		 */
		buildFormulaMaterials(formula) {
			this.formulaMaterials = [
				{ name: '水泥', value: formula.cement },
				{ name: '水', value: formula.water },
				{ name: '砂子', value: formula.sand },
				{ name: '石子', value: formula.stone }
			]
			
			if (formula.admixture) {
				this.formulaMaterials.push({ name: formula.admixture_type || '外加剂', value: formula.admixture })
			}
			
			if (formula.fly_ash > 0) {
				this.formulaMaterials.push({ name: '粉煤灰', value: formula.fly_ash })
			}
			
			if (formula.mineral_powder > 0) {
				this.formulaMaterials.push({ name: '矿粉', value: formula.mineral_powder })
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
				'pending': '待接单',
				'accepted': '已接单',
				'in_progress': '进行中',
				'completed': '已完成',
				'cancelled': '已取消'
			}
			return statusMap[status] || status
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
		 * 接单
		 */
		async handleAccept() {
			const confirm = await this.showModal('确认接单', '确定要接取此任务吗？')
			if (!confirm) return
			
			this.accepting = true
			
			try {
				await api.tasks.accept(this.taskId)
				
				uni.showToast({
					title: '接单成功',
					icon: 'success'
				})
				
				// 刷新页面
				setTimeout(() => {
					this.loadTaskDetail()
				}, 1000)
			} catch (error) {
				console.log('接单失败:', error)
			} finally {
				this.accepting = false
			}
		},
		
		/**
		 * 开始生产
		 */
		async handleStart() {
			const confirm = await this.showModal('开始生产', '确定要开始此任务的生产吗？')
			if (!confirm) return
			
			try {
				await api.tasks.start(this.taskId)
				
				uni.showToast({
					title: '已开始生产',
					icon: 'success'
				})
				
				setTimeout(() => {
					this.loadTaskDetail()
				}, 1000)
			} catch (error) {
				console.log('开始生产失败:', error)
			}
		},
		
		/**
		 * 完成任务
		 */
		async handleComplete() {
			const confirm = await this.showModal('完成任务', '确定要完成此任务吗？完成后将无法再进行投料和搅拌操作。')
			if (!confirm) return
			
			try {
				await api.tasks.complete(this.taskId)
				
				uni.showToast({
					title: '任务已完成',
					icon: 'success'
				})
				
				setTimeout(() => {
					this.loadTaskDetail()
				}, 1000)
			} catch (error) {
				console.log('完成任务失败:', error)
			}
		},
		
		// ========== 页面跳转 ==========
		
		goToFormulaDetail() {
			if (this.taskInfo.formula_info) {
				uni.navigateTo({
					url: `/pages/formula/formula-detail?id=${this.taskInfo.formula_info.id}`
				})
			}
		},
		
		goToAdjust() {
			uni.navigateTo({
				url: `/pages/formula/formula-adjust?taskId=${this.taskId}&formulaId=${this.taskInfo.formula_info.id}`
			})
		},
		
		goToFeeding() {
			uni.navigateTo({
				url: `/pages/feeding/feeding-add?taskId=${this.taskId}&taskNo=${this.taskInfo.task_no}`
			})
		},
		
		goToMixing() {
			uni.navigateTo({
				url: `/pages/mixing/mixing-add?taskId=${this.taskId}&taskNo=${this.taskInfo.task_no}`
			})
		},
		
		goToFeedingList() {
			uni.navigateTo({
				url: `/pages/feeding/feeding-list?taskId=${this.taskId}`
			})
		},
		
		goToMixingList() {
			uni.navigateTo({
				url: `/pages/mixing/mixing-list?taskId=${this.taskId}`
			})
		}
	}
}
</script>

<style scoped>
/* 任务详情页面样式 */
.task-detail-container {
	min-height: 100vh;
	background: #F5F7FA;
	padding-bottom: 160rpx;
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
	padding: 30rpx;
	background: linear-gradient(90deg, #E6F7FF 0%, #FFFFFF 100%);
	border-bottom: 2rpx solid #F0F0F0;
}

.task-no-box {
	background: #1890FF;
	padding: 12rpx 24rpx;
	border-radius: 12rpx;
}

.task-no {
	font-size: 28rpx;
	color: #FFFFFF;
	font-weight: bold;
}

.status-tag {
	font-size: 26rpx;
	padding: 12rpx 28rpx;
	border-radius: 30rpx;
}

.card-body {
	padding: 30rpx;
}

.info-item {
	display: flex;
	margin-bottom: 24rpx;
}

.info-item:last-child {
	margin-bottom: 0;
}

.info-label {
	width: 160rpx;
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

.info-value.time {
	color: #FA8C16;
}

.info-row {
	display: flex;
	gap: 30rpx;
	margin-bottom: 24rpx;
}

.info-box {
	flex: 1;
	background: #F5F7FA;
	border-radius: 16rpx;
	padding: 24rpx;
	text-align: center;
}

.box-label {
	display: block;
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 12rpx;
}

.box-value {
	display: block;
	font-size: 32rpx;
	color: #333333;
	font-weight: bold;
}

.box-value.highlight {
	color: #1890FF;
}

.time-item {
	padding-top: 24rpx;
	border-top: 2rpx dashed #F0F0F0;
	margin-top: 24rpx;
}

/* 卡片标题 */
.card-title {
	display: flex;
	align-items: center;
	padding: 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.iconfont {
	font-size: 36rpx;
	color: #1890FF;
	margin-right: 16rpx;
}

.title-text {
	font-size: 30rpx;
	color: #333333;
	font-weight: 500;
}

/* 配方信息 */
.formula-info {
	padding: 30rpx;
}

.formula-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 24rpx;
}

.formula-name {
	font-size: 30rpx;
	color: #333333;
	font-weight: 500;
}

.formula-code {
	font-size: 24rpx;
	color: #999999;
	background: #F5F7FA;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
}

.formula-grid {
	display: flex;
	gap: 30rpx;
	margin-bottom: 24rpx;
}

.grid-item {
	flex: 1;
	background: #FAFAFA;
	border-radius: 12rpx;
	padding: 20rpx;
	text-align: center;
}

.grid-label {
	display: block;
	font-size: 24rpx;
	color: #999999;
	margin-bottom: 8rpx;
}

.grid-value {
	display: block;
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
}

/* 材料列表 */
.material-list {
	background: #FAFAFA;
	border-radius: 16rpx;
	padding: 20rpx;
	margin-bottom: 24rpx;
}

.material-item {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 16rpx 0;
	border-bottom: 2rpx solid #F0F0F0;
}

.material-item:last-child {
	border-bottom: none;
}

.material-name {
	font-size: 26rpx;
	color: #666666;
}

.material-qty {
	font-size: 26rpx;
	color: #333333;
	font-weight: 500;
}

/* 配方底部操作 */
.formula-footer {
	display: flex;
	gap: 20rpx;
}

.view-btn,
.adjust-btn {
	flex: 1;
	height: 72rpx;
	line-height: 72rpx;
	font-size: 26rpx;
	border-radius: 36rpx;
	border: none;
}

.view-btn {
	background: #F5F7FA;
	color: #666666;
}

.adjust-btn {
	background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
	color: #FFFFFF;
}

/* 快捷操作 */
.quick-actions {
	display: flex;
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	padding: 30rpx;
	justify-content: space-around;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.action-item {
	display: flex;
	flex-direction: column;
	align-items: center;
}

.action-icon {
	width: 96rpx;
	height: 96rpx;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 12rpx;
}

.bg-blue {
	background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
}

.bg-green {
	background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.bg-orange {
	background: linear-gradient(135deg, #FA8C16 0%, #FFA940 100%);
}

.bg-purple {
	background: linear-gradient(135deg, #722ED1 0%, #9254DE 100%);
}

.bg-success {
	background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.action-icon .iconfont {
	font-size: 44rpx;
	color: #FFFFFF;
	margin: 0;
}

.action-text {
	font-size: 24rpx;
	color: #666666;
}

/* 时间线 */
.timeline {
	padding: 20rpx 30rpx;
}

.timeline-item {
	display: flex;
	position: relative;
	padding-bottom: 40rpx;
}

.timeline-item:last-child {
	padding-bottom: 0;
}

.timeline-item::before {
	content: '';
	position: absolute;
	left: 20rpx;
	top: 40rpx;
	width: 2rpx;
	height: calc(100% - 40rpx);
	background: #E8E8E8;
}

.timeline-item:last-child::before {
	display: none;
}

.timeline-item.done::before {
	background: #1890FF;
}

.timeline-dot {
	width: 40rpx;
	height: 40rpx;
	border-radius: 50%;
	background: #E8E8E8;
	border: 4rpx solid #FFFFFF;
	position: relative;
	z-index: 1;
	flex-shrink: 0;
	margin-right: 20rpx;
}

.timeline-item.done .timeline-dot {
	background: #1890FF;
}

.timeline-content {
	flex: 1;
}

.timeline-title {
	display: block;
	font-size: 28rpx;
	color: #333333;
	margin-bottom: 8rpx;
}

.timeline-time {
	display: block;
	font-size: 24rpx;
	color: #999999;
}

.timeline-time.pending {
	color: #CCCCCC;
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
	justify-content: space-between;
	align-items: center;
	border-top: 2rpx solid #F0F0F0;
	box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.bar-left {
	display: flex;
	gap: 20rpx;
	flex: 1;
}

.bar-right {
	flex: 1;
}

.bar-btn {
	height: 80rpx;
	line-height: 80rpx;
	font-size: 28rpx;
	border-radius: 40rpx;
	border: none;
}

.bar-btn.outline {
	flex: 1;
	background: transparent;
	color: #1890FF;
	border: 2rpx solid #1890FF;
}

.bar-btn.primary {
	width: 100%;
	background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
	color: #FFFFFF;
}

.bar-btn.success {
	width: 100%;
	background: linear-gradient(90deg, #52C41A 0%, #73D13D 100%);
	color: #FFFFFF;
}
</style>
