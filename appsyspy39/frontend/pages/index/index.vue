<template>
	<view class="index-container">
		<!-- 顶部用户信息栏 -->
		<view class="header-section">
			<view class="user-info">
				<view class="avatar">
					<text>{{ userInfo.real_name ? userInfo.real_name.substring(0, 1) : '用' }}</text>
				</view>
				<view class="user-text">
					<text class="user-name">{{ userInfo.real_name || userInfo.username }}</text>
					<text class="user-role">{{ userInfo.role === 'admin' ? '系统管理员' : '生产操作员' }}</text>
				</view>
			</view>
			<view class="header-date">
				<text class="date-text">{{ currentDate }}</text>
				<text class="week-text">{{ currentWeek }}</text>
			</view>
		</view>
		
		<!-- 快捷功能入口 -->
		<view class="quick-actions">
			<view class="action-card" @click="goToTaskList">
				<view class="action-icon bg-blue">
					<text class="iconfont icon-task"></text>
				</view>
				<text class="action-text">任务管理</text>
				<text class="action-badge" v-if="pendingCount > 0">{{ pendingCount }}</text>
			</view>
			
			<view class="action-card" @click="goToFormulaList">
				<view class="action-icon bg-green">
					<text class="iconfont icon-formula"></text>
				</view>
				<text class="action-text">配方查询</text>
			</view>
			
			<view class="action-card" @click="goToFeeding">
				<view class="action-icon bg-orange">
					<text class="iconfont icon-feeding"></text>
				</view>
				<text class="action-text">投料记录</text>
			</view>
			
			<view class="action-card" @click="goToMixing">
				<view class="action-icon bg-purple">
					<text class="iconfont icon-mixing"></text>
				</view>
				<text class="action-text">搅拌记录</text>
			</view>
		</view>
		
		<!-- 待执行任务 -->
		<view class="section">
			<view class="section-header">
				<text class="section-title">待执行任务</text>
				<text class="section-more" @click="goToTaskList">查看全部 ></text>
			</view>
			
			<view class="task-list" v-if="pendingTasks.length > 0">
				<view 
					class="task-item" 
					v-for="(task, index) in pendingTasks" 
					:key="task.id"
					@click="goToTaskDetail(task.id)"
				>
					<view class="task-left">
						<view class="task-no">
							<text class="no-text">{{ task.task_no }}</text>
						</view>
						<view class="task-info">
							<text class="task-project line-1">{{ task.project_name }}</text>
							<view class="task-meta">
								<text class="meta-item">{{ task.concrete_grade }}</text>
								<text class="meta-item">{{ task.quantity }}m³</text>
							</view>
							<text class="task-time">交货时间：{{ formatTime(task.delivery_time) }}</text>
						</view>
					</view>
					<view class="task-right">
						<view class="status-tag" :class="'status-' + task.status">
							{{ getStatusText(task.status) }}
						</view>
						<button 
							class="accept-btn" 
							v-if="task.status === 'pending'"
							:loading="acceptingTaskId === task.id"
							@click.stop="handleAccept(task)"
						>
							接单
						</button>
					</view>
				</view>
			</view>
			
			<view class="empty-state" v-else>
				<text class="empty-icon">📋</text>
				<text class="empty-text">暂无待执行任务</text>
			</view>
		</view>
		
		<!-- 进行中任务统计 -->
		<view class="section" v-if="inProgressTasks.length > 0">
			<view class="section-header">
				<text class="section-title">进行中任务</text>
			</view>
			
			<view class="task-list">
				<view 
					class="task-item in-progress" 
					v-for="(task, index) in inProgressTasks" 
					:key="task.id"
					@click="goToTaskDetail(task.id)"
				>
					<view class="task-left">
						<view class="task-no processing">
							<text class="no-text">{{ task.task_no }}</text>
						</view>
						<view class="task-info">
							<text class="task-project line-1">{{ task.project_name }}</text>
							<view class="task-meta">
								<text class="meta-item">{{ task.concrete_grade }}</text>
								<text class="meta-item">{{ task.quantity }}m³</text>
							</view>
						</view>
					</view>
					<view class="task-right">
						<view class="status-tag status-in_progress">
							进行中
						</view>
						<view class="task-actions">
							<button class="mini-btn" @click.stop="goToFeedingAdd(task)">投料</button>
							<button class="mini-btn outline" @click.stop="goToMixingAdd(task)">搅拌</button>
						</view>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 下拉刷新/上拉加载提示 -->
		<view class="load-more" v-if="loading">
			<text>加载中...</text>
		</view>
	</view>
</template>

<script>
/**
 * 首页
 * 功能：
 * - 显示用户信息和日期
 * - 快捷功能入口
 * - 待执行任务列表（支持一键接单）
 * - 进行中任务列表
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 用户信息
			userInfo: {},
			// 当前日期
			currentDate: '',
			currentWeek: '',
			// 待执行任务
			pendingTasks: [],
			// 进行中任务
			inProgressTasks: [],
			// 待接任务数量
			pendingCount: 0,
			// 加载状态
			loading: false,
			// 正在接单的任务ID
			acceptingTaskId: null
		}
	},
	
	onLoad() {
		// 初始化日期
		this.initDate()
		// 获取用户信息
		this.getUserInfo()
	},
	
	onShow() {
		// 页面显示时刷新任务列表
		this.loadData()
	},
	
	onPullDownRefresh() {
		// 下拉刷新
		this.loadData().finally(() => {
			uni.stopPullDownRefresh()
		})
	},
	
	methods: {
		/**
		 * 初始化日期
		 */
		initDate() {
			const now = new Date()
			const year = now.getFullYear()
			const month = String(now.getMonth() + 1).padStart(2, '0')
			const day = String(now.getDate()).padStart(2, '0')
			const weeks = ['星期日', '星期一', '星期二', '星期三', '星期四', '星期五', '星期六']
			
			this.currentDate = `${year}年${month}月${day}日`
			this.currentWeek = weeks[now.getDay()]
		},
		
		/**
		 * 获取用户信息
		 */
		getUserInfo() {
			const userInfo = uni.getStorageSync('userInfo')
			if (userInfo) {
				this.userInfo = userInfo
			}
		},
		
		/**
		 * 加载数据
		 */
		async loadData() {
			this.loading = true
			
			try {
				// 获取待执行任务
				const res = await api.tasks.getPending({ page: 1, page_size: 20 })
				
				if (res && res.tasks) {
					// 分类：待接、已接、进行中
					this.pendingTasks = res.tasks.filter(t => t.status === 'pending')
					this.inProgressTasks = res.tasks.filter(t => 
						t.status === 'accepted' || t.status === 'in_progress'
					)
					this.pendingCount = this.pendingTasks.length
				}
			} catch (error) {
				console.log('加载任务失败:', error)
			} finally {
				this.loading = false
			}
		},
		
		/**
		 * 格式化时间
		 * @param {String} time - 时间字符串
		 */
		formatTime(time) {
			if (!time) return ''
			const date = new Date(time)
			const month = String(date.getMonth() + 1).padStart(2, '0')
			const day = String(date.getDate()).padStart(2, '0')
			const hour = String(date.getHours()).padStart(2, '0')
			const minute = String(date.getMinutes()).padStart(2, '0')
			return `${month}-${day} ${hour}:${minute}`
		},
		
		/**
		 * 获取状态文本
		 * @param {String} status - 状态值
		 */
		getStatusText(status) {
			const statusMap = {
				'pending': '待接',
				'accepted': '已接',
				'in_progress': '进行中',
				'completed': '已完成',
				'cancelled': '已取消'
			}
			return statusMap[status] || status
		},
		
		/**
		 * 处理接单
		 * @param {Object} task - 任务对象
		 */
		async handleAccept(task) {
			// 确认接单
			const confirm = await this.showModal('确认接单', `确定要接取任务 ${task.task_no} 吗？`)
			if (!confirm) return
			
			this.acceptingTaskId = task.id
			
			try {
				await api.tasks.accept(task.id)
				
				uni.showToast({
					title: '接单成功',
					icon: 'success'
				})
				
				// 刷新列表
				setTimeout(() => {
					this.loadData()
				}, 1000)
			} catch (error) {
				console.log('接单失败:', error)
			} finally {
				this.acceptingTaskId = null
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
		
		// ========== 页面跳转 ==========
		
		goToTaskList() {
			uni.navigateTo({
				url: '/pages/task/task-list'
			})
		},
		
		goToTaskDetail(taskId) {
			uni.navigateTo({
				url: `/pages/task/task-detail?id=${taskId}`
			})
		},
		
		goToFormulaList() {
			uni.navigateTo({
				url: '/pages/formula/formula-list'
			})
		},
		
		goToFeeding() {
			uni.navigateTo({
				url: '/pages/feeding/feeding-list'
			})
		},
		
		goToMixing() {
			uni.navigateTo({
				url: '/pages/mixing/mixing-list'
			})
		},
		
		goToFeedingAdd(task) {
			uni.navigateTo({
				url: `/pages/feeding/feeding-add?taskId=${task.id}&taskNo=${task.task_no}`
			})
		},
		
		goToMixingAdd(task) {
			uni.navigateTo({
				url: `/pages/mixing/mixing-add?taskId=${task.id}&taskNo=${task.task_no}`
			})
		}
	}
}
</script>

<style scoped>
/* 首页样式 */
.index-container {
	min-height: 100vh;
	background: #F5F7FA;
	padding-bottom: 40rpx;
}

/* 顶部信息栏 */
.header-section {
	background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
	padding: 40rpx 30rpx;
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
}

.user-info {
	display: flex;
	align-items: center;
}

.avatar {
	width: 100rpx;
	height: 100rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
}

.avatar text {
	font-size: 44rpx;
	color: #FFFFFF;
	font-weight: bold;
}

.user-text {
	display: flex;
	flex-direction: column;
}

.user-name {
	font-size: 36rpx;
	color: #FFFFFF;
	font-weight: bold;
	margin-bottom: 8rpx;
}

.user-role {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

.header-date {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
}

.date-text {
	font-size: 28rpx;
	color: #FFFFFF;
	margin-bottom: 8rpx;
}

.week-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

/* 快捷功能入口 */
.quick-actions {
	display: flex;
	flex-wrap: wrap;
	padding: 30rpx;
	margin-top: -40rpx;
}

.action-card {
	width: 25%;
	display: flex;
	flex-direction: column;
	align-items: center;
	position: relative;
}

.action-icon {
	width: 100rpx;
	height: 100rpx;
	border-radius: 24rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-bottom: 16rpx;
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

.iconfont {
	font-size: 48rpx;
	color: #FFFFFF;
}

.action-text {
	font-size: 24rpx;
	color: #333333;
}

.action-badge {
	position: absolute;
	top: 0;
	right: 20rpx;
	min-width: 36rpx;
	height: 36rpx;
	background: #FF4D4F;
	border-radius: 18rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 20rpx;
	color: #FFFFFF;
	padding: 0 8rpx;
}

/* 通用区块 */
.section {
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	padding: 30rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.section-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: 30rpx;
}

.section-title {
	font-size: 32rpx;
	font-weight: bold;
	color: #333333;
}

.section-more {
	font-size: 26rpx;
	color: #1890FF;
}

/* 任务列表 */
.task-list {
	display: flex;
	flex-direction: column;
	gap: 20rpx;
}

.task-item {
	display: flex;
	justify-content: space-between;
	align-items: flex-start;
	padding: 24rpx;
	background: #FAFAFA;
	border-radius: 16rpx;
	border: 2rpx solid #F0F0F0;
}

.task-item.in-progress {
	background: #F6FFED;
	border-color: #B7EB8F;
}

.task-left {
	display: flex;
	flex: 1;
	min-width: 0;
}

.task-no {
	width: 80rpx;
	height: 80rpx;
	background: #E6F7FF;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 20rpx;
	flex-shrink: 0;
}

.task-no.processing {
	background: #B7EB8F;
}

.no-text {
	font-size: 22rpx;
	color: #1890FF;
	font-weight: bold;
	word-break: break-all;
	text-align: center;
}

.task-info {
	flex: 1;
	min-width: 0;
	display: flex;
	flex-direction: column;
}

.task-project {
	font-size: 28rpx;
	color: #333333;
	font-weight: 500;
	margin-bottom: 12rpx;
}

.task-meta {
	display: flex;
	gap: 20rpx;
	margin-bottom: 8rpx;
}

.meta-item {
	font-size: 24rpx;
	color: #666666;
	background: #FFFFFF;
	padding: 4rpx 12rpx;
	border-radius: 8rpx;
}

.task-time {
	font-size: 22rpx;
	color: #999999;
}

.task-right {
	display: flex;
	flex-direction: column;
	align-items: flex-end;
	flex-shrink: 0;
	margin-left: 20rpx;
}

.status-tag {
	font-size: 22rpx;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
	margin-bottom: 16rpx;
}

.accept-btn {
	height: 56rpx;
	line-height: 56rpx;
	background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
	color: #FFFFFF;
	font-size: 24rpx;
	border-radius: 28rpx;
	padding: 0 24rpx;
	border: none;
}

.task-actions {
	display: flex;
	gap: 12rpx;
}

.mini-btn {
	height: 48rpx;
	line-height: 48rpx;
	background: #1890FF;
	color: #FFFFFF;
	font-size: 22rpx;
	border-radius: 24rpx;
	padding: 0 16rpx;
	border: none;
}

.mini-btn.outline {
	background: transparent;
	color: #1890FF;
	border: 2rpx solid #1890FF;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 60rpx 0;
}

.empty-icon {
	font-size: 80rpx;
	margin-bottom: 20rpx;
}

.empty-text {
	font-size: 28rpx;
	color: #999999;
}

/* 加载更多 */
.load-more {
	text-align: center;
	padding: 30rpx;
	font-size: 26rpx;
	color: #999999;
}
</style>
