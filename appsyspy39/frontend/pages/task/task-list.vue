<template>
	<view class="task-list-container">
		<!-- 搜索和筛选 -->
		<view class="search-section">
			<view class="search-box">
				<text class="iconfont icon-search"></text>
				<input 
					class="search-input" 
					type="text" 
					v-model="searchKeyword" 
					placeholder="搜索任务编号、项目名称"
					placeholder-class="input-placeholder"
					@confirm="handleSearch"
				/>
			</view>
		</view>
		
		<!-- 状态筛选标签 -->
		<view class="filter-tabs">
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === '' }"
				@click="handleFilter('')"
			>
				全部
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === 'pending' }"
				@click="handleFilter('pending')"
			>
				待接
				<text class="tab-badge" v-if="filterCounts.pending > 0">{{ filterCounts.pending }}</text>
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === 'accepted' }"
				@click="handleFilter('accepted')"
			>
				已接
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === 'in_progress' }"
				@click="handleFilter('in_progress')"
			>
				进行中
			</view>
			<view 
				class="tab-item" 
				:class="{ active: currentFilter === 'completed' }"
				@click="handleFilter('completed')"
			>
				已完成
			</view>
		</view>
		
		<!-- 任务列表 -->
		<scroll-view 
			class="task-scroll" 
			scroll-y
			@scrolltolower="loadMore"
			refresher-enabled
			:refresher-triggered="refreshing"
			@refresherrefresh="onRefresh"
		>
			<view class="task-list" v-if="taskList.length > 0">
				<view 
					class="task-card" 
					v-for="(task, index) in taskList" 
					:key="task.id"
					@click="goToDetail(task.id)"
				>
					<!-- 顶部任务号和状态 -->
					<view class="card-header">
						<view class="task-no-box">
							<text class="task-no">{{ task.task_no }}</text>
						</view>
						<view class="status-tag" :class="'status-' + task.status">
							{{ getStatusText(task.status) }}
						</view>
					</view>
					
					<!-- 项目信息 -->
					<view class="card-body">
						<view class="info-row">
							<text class="info-label">项目名称</text>
							<text class="info-value line-1">{{ task.project_name }}</text>
						</view>
						
						<view class="info-row">
							<text class="info-label">混凝土标号</text>
							<text class="info-value highlight">{{ task.concrete_grade }}</text>
						</view>
						
						<view class="info-row">
							<text class="info-label">生产数量</text>
							<text class="info-value">{{ task.quantity }} m³</text>
						</view>
						
						<view class="info-row" v-if="task.operator_name">
							<text class="info-label">接单人</text>
							<text class="info-value">{{ task.operator_name }}</text>
						</view>
						
						<view class="info-row time-row">
							<text class="info-label">交货时间</text>
							<text class="info-value time-text">{{ formatTime(task.delivery_time) }}</text>
						</view>
					</view>
					
					<!-- 操作按钮 -->
					<view class="card-footer" v-if="task.status === 'pending'">
						<button 
							class="action-btn primary"
							:loading="acceptingTaskId === task.id"
							@click.stop="handleAccept(task)"
						>
							一键接单
						</button>
					</view>
					
					<view class="card-footer" v-else-if="task.status === 'accepted'">
						<button 
							class="action-btn success"
							@click.stop="handleStart(task)"
						>
							开始生产
						</button>
					</view>
					
					<view class="card-footer" v-else-if="task.status === 'in_progress'">
						<view class="action-group">
							<button 
								class="action-btn mini"
								@click.stop="goToFeeding(task)"
							>
								投料
							</button>
							<button 
								class="action-btn mini"
								@click.stop="goToMixing(task)"
							>
								搅拌
							</button>
							<button 
								class="action-btn mini outline"
								@click.stop="handleComplete(task)"
							>
								完成
							</button>
						</view>
					</view>
				</view>
			</view>
			
			<!-- 空状态 -->
			<view class="empty-state" v-else-if="!loading && taskList.length === 0">
				<text class="empty-icon">📋</text>
				<text class="empty-text">暂无任务数据</text>
				<text class="empty-tip">下拉刷新试试</text>
			</view>
			
			<!-- 加载更多 -->
			<view class="load-more" v-if="loading && page > 1">
				<text>加载中...</text>
			</view>
			
			<!-- 没有更多 -->
			<view class="no-more" v-if="!hasMore && taskList.length > 0">
				<text>没有更多了</text>
			</view>
		</scroll-view>
	</view>
</template>

<script>
/**
 * 任务列表页面
 * 功能：
 * - 任务搜索
 * - 状态筛选
 * - 任务列表展示
 * - 一键接单
 * - 开始/完成生产
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 搜索关键词
			searchKeyword: '',
			// 当前筛选状态
			currentFilter: '',
			// 任务列表
			taskList: [],
			// 分页
			page: 1,
			pageSize: 10,
			hasMore: true,
			// 加载状态
			loading: false,
			refreshing: false,
			// 正在操作的任务ID
			acceptingTaskId: null,
			// 各状态数量统计
			filterCounts: {
				pending: 0
			}
		}
	},
	
	onLoad(options) {
		// 如果有传入的状态参数，设置筛选
		if (options.status) {
			this.currentFilter = options.status
		}
		this.loadData()
	},
	
	onShow() {
		// 页面显示时刷新数据
		if (!this.loading) {
			this.onRefresh()
		}
	},
	
	methods: {
		/**
		 * 加载数据
		 */
		async loadData(isRefresh = false) {
			if (this.loading) return
			
			this.loading = true
			
			try {
				const params = {
					page: this.page,
					page_size: this.pageSize
				}
				
				// 添加筛选条件
				if (this.currentFilter) {
					params.status = this.currentFilter
				}
				
				// 添加搜索关键词
				if (this.searchKeyword.trim()) {
					params.keyword = this.searchKeyword.trim()
				}
				
				const res = await api.tasks.getList(params)
				
				if (res && res.tasks) {
					const newTasks = res.tasks
					
					if (isRefresh) {
						this.taskList = newTasks
					} else {
						this.taskList = [...this.taskList, ...newTasks]
					}
					
					// 判断是否还有更多
					this.hasMore = newTasks.length >= this.pageSize
					
					// 统计待接任务数量（第一次加载时）
					if (isRefresh || this.page === 1) {
						this.updateFilterCounts()
					}
				}
			} catch (error) {
				console.log('加载任务列表失败:', error)
			} finally {
				this.loading = false
				this.refreshing = false
			}
		},
		
		/**
		 * 更新筛选计数
		 */
		async updateFilterCounts() {
			try {
				// 获取所有待接任务数量
				const res = await api.tasks.getList({ status: 'pending', page: 1, page_size: 1 })
				this.filterCounts.pending = res.total || 0
			} catch (error) {
				console.log('获取计数失败:', error)
			}
		},
		
		/**
		 * 下拉刷新
		 */
		async onRefresh() {
			this.refreshing = true
			this.page = 1
			this.hasMore = true
			await this.loadData(true)
		},
		
		/**
		 * 上拉加载更多
		 */
		loadMore() {
			if (this.hasMore && !this.loading) {
				this.page++
				this.loadData()
			}
		},
		
		/**
		 * 搜索
		 */
		handleSearch() {
			this.onRefresh()
		},
		
		/**
		 * 筛选切换
		 * @param {String} status - 筛选状态
		 */
		handleFilter(status) {
			if (this.currentFilter === status) return
			this.currentFilter = status
			this.onRefresh()
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
		async handleAccept(task) {
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
					this.onRefresh()
				}, 1000)
			} catch (error) {
				console.log('接单失败:', error)
			} finally {
				this.acceptingTaskId = null
			}
		},
		
		/**
		 * 开始生产
		 */
		async handleStart(task) {
			const confirm = await this.showModal('开始生产', `确定要开始任务 ${task.task_no} 的生产吗？`)
			if (!confirm) return
			
			try {
				await api.tasks.start(task.id)
				
				uni.showToast({
					title: '已开始生产',
					icon: 'success'
				})
				
				// 刷新列表
				setTimeout(() => {
					this.onRefresh()
				}, 1000)
			} catch (error) {
				console.log('开始生产失败:', error)
			}
		},
		
		/**
		 * 完成任务
		 */
		async handleComplete(task) {
			const confirm = await this.showModal('完成任务', `确定要完成任务 ${task.task_no} 吗？`)
			if (!confirm) return
			
			try {
				await api.tasks.complete(task.id)
				
				uni.showToast({
					title: '任务已完成',
					icon: 'success'
				})
				
				// 刷新列表
				setTimeout(() => {
					this.onRefresh()
				}, 1000)
			} catch (error) {
				console.log('完成任务失败:', error)
			}
		},
		
		// ========== 页面跳转 ==========
		
		goToDetail(taskId) {
			uni.navigateTo({
				url: `/pages/task/task-detail?id=${taskId}`
			})
		},
		
		goToFeeding(task) {
			uni.navigateTo({
				url: `/pages/feeding/feeding-add?taskId=${task.id}&taskNo=${task.task_no}`
			})
		},
		
		goToMixing(task) {
			uni.navigateTo({
				url: `/pages/mixing/mixing-add?taskId=${task.id}&taskNo=${task.task_no}`
			})
		}
	}
}
</script>

<style scoped>
/* 任务列表页面样式 */
.task-list-container {
	height: 100vh;
	display: flex;
	flex-direction: column;
	background: #F5F7FA;
}

/* 搜索区域 */
.search-section {
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	border-bottom: 2rpx solid #F0F0F0;
}

.search-box {
	display: flex;
	align-items: center;
	background: #F5F7FA;
	border-radius: 40rpx;
	padding: 16rpx 30rpx;
}

.icon-search {
	font-size: 32rpx;
	color: #999999;
	margin-right: 16rpx;
}

.search-input {
	flex: 1;
	font-size: 28rpx;
	color: #333333;
}

.input-placeholder {
	color: #CCCCCC;
}

/* 筛选标签 */
.filter-tabs {
	display: flex;
	background: #FFFFFF;
	padding: 20rpx 30rpx;
	gap: 24rpx;
	overflow-x: auto;
	border-bottom: 2rpx solid #F0F0F0;
}

.tab-item {
	flex-shrink: 0;
	font-size: 28rpx;
	color: #666666;
	padding: 12rpx 24rpx;
	border-radius: 30rpx;
	position: relative;
}

.tab-item.active {
	background: #E6F7FF;
	color: #1890FF;
	font-weight: 500;
}

.tab-badge {
	position: absolute;
	top: 4rpx;
	right: 4rpx;
	min-width: 28rpx;
	height: 28rpx;
	background: #FF4D4F;
	border-radius: 14rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 18rpx;
	color: #FFFFFF;
	padding: 0 6rpx;
}

/* 滚动区域 */
.task-scroll {
	flex: 1;
}

.task-list {
	padding: 20rpx 30rpx;
	display: flex;
	flex-direction: column;
	gap: 24rpx;
}

/* 任务卡片 */
.task-card {
	background: #FFFFFF;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.card-header {
	display: flex;
	justify-content: space-between;
	align-items: center;
	padding: 24rpx 30rpx;
	background: linear-gradient(90deg, #FAFAFA 0%, #FFFFFF 100%);
	border-bottom: 2rpx solid #F5F5F5;
}

.task-no-box {
	background: #E6F7FF;
	padding: 8rpx 20rpx;
	border-radius: 8rpx;
}

.task-no {
	font-size: 26rpx;
	color: #1890FF;
	font-weight: 500;
}

.status-tag {
	font-size: 24rpx;
	padding: 8rpx 20rpx;
	border-radius: 20rpx;
}

/* 卡片主体 */
.card-body {
	padding: 24rpx 30rpx;
}

.info-row {
	display: flex;
	margin-bottom: 16rpx;
}

.info-row:last-child {
	margin-bottom: 0;
}

.info-label {
	width: 160rpx;
	font-size: 26rpx;
	color: #999999;
	flex-shrink: 0;
}

.info-value {
	flex: 1;
	font-size: 26rpx;
	color: #333333;
}

.info-value.highlight {
	color: #1890FF;
	font-weight: 500;
}

.time-row {
	padding-top: 16rpx;
	border-top: 2rpx dashed #F0F0F0;
	margin-top: 16rpx;
}

.time-text {
	color: #FA8C16;
}

/* 卡片底部操作 */
.card-footer {
	padding: 20rpx 30rpx;
	border-top: 2rpx solid #F5F5F5;
}

.action-btn {
	width: 100%;
	height: 80rpx;
	line-height: 80rpx;
	border-radius: 40rpx;
	font-size: 28rpx;
	border: none;
}

.action-btn.primary {
	background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
	color: #FFFFFF;
}

.action-btn.success {
	background: linear-gradient(90deg, #52C41A 0%, #73D13D 100%);
	color: #FFFFFF;
}

.action-group {
	display: flex;
	gap: 20rpx;
}

.action-btn.mini {
	flex: 1;
	height: 64rpx;
	line-height: 64rpx;
	font-size: 26rpx;
	background: #1890FF;
	color: #FFFFFF;
}

.action-btn.mini.outline {
	background: transparent;
	color: #52C41A;
	border: 2rpx solid #52C41A;
}

/* 空状态 */
.empty-state {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 120rpx 0;
}

.empty-icon {
	font-size: 100rpx;
	margin-bottom: 30rpx;
}

.empty-text {
	font-size: 30rpx;
	color: #666666;
	margin-bottom: 12rpx;
}

.empty-tip {
	font-size: 24rpx;
	color: #999999;
}

/* 加载状态 */
.load-more,
.no-more {
	text-align: center;
	padding: 40rpx;
	font-size: 26rpx;
	color: #999999;
}
</style>
