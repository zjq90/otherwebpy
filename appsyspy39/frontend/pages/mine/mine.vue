<template>
	<view class="mine-container">
		<!-- 用户信息头部 -->
		<view class="user-header">
			<view class="avatar-box">
				<text class="avatar-text">{{ userInfo.real_name ? userInfo.real_name.substring(0, 1) : '用' }}</text>
			</view>
			<view class="user-info">
				<text class="user-name">{{ userInfo.real_name || userInfo.username }}</text>
				<view class="user-meta">
					<view class="role-tag" :class="userInfo.role">
						{{ userInfo.role === 'admin' ? '管理员' : '操作员' }}
					</view>
					<text class="user-phone" v-if="userInfo.phone">{{ userInfo.phone }}</text>
				</view>
			</view>
		</view>
		
		<!-- 功能菜单 -->
		<view class="menu-section">
			<view class="menu-title">功能菜单</view>
			
			<view class="menu-list">
				<view class="menu-item" @click="goToTaskList">
					<view class="menu-icon bg-blue">
						<text class="iconfont icon-task"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">我的任务</text>
						<text class="menu-desc">查看和管理生产任务</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
				
				<view class="menu-item" @click="goToFormulaList">
					<view class="menu-icon bg-green">
						<text class="iconfont icon-formula"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">配合比查询</text>
						<text class="menu-desc">检索标准配合比配方</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
				
				<view class="menu-item" @click="goToFeedingList">
					<view class="menu-icon bg-orange">
						<text class="iconfont icon-feeding"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">投料记录</text>
						<text class="menu-desc">查看投料历史记录</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
				
				<view class="menu-item" @click="goToMixingList">
					<view class="menu-icon bg-purple">
						<text class="iconfont icon-mixing"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">搅拌记录</text>
						<text class="menu-desc">查看搅拌历史记录</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
			</view>
		</view>
		
		<!-- 设置菜单 -->
		<view class="menu-section">
			<view class="menu-title">系统设置</view>
			
			<view class="menu-list">
				<view class="menu-item" @click="goToChangePassword">
					<view class="menu-icon bg-gray">
						<text class="iconfont icon-password"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">修改密码</text>
						<text class="menu-desc">修改登录密码</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
				
				<view class="menu-item" @click="showAbout">
					<view class="menu-icon bg-gray">
						<text class="iconfont icon-about"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">关于我们</text>
						<text class="menu-desc">查看版本信息</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
			</view>
		</view>
		
		<!-- 测试工具（仅管理员可见） -->
		<view class="menu-section" v-if="userInfo.role === 'admin'">
			<view class="menu-title">测试工具</view>
			
			<view class="menu-list">
				<view class="menu-item" @click="generateTestData">
					<view class="menu-icon bg-red">
						<text class="iconfont icon-data"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">生成测试数据</text>
						<text class="menu-desc">一键生成测试数据</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
				
				<view class="menu-item" @click="clearTestData">
					<view class="menu-icon bg-red">
						<text class="iconfont icon-clear"></text>
					</view>
					<view class="menu-content">
						<text class="menu-name">清空测试数据</text>
						<text class="menu-desc">清空所有测试数据</text>
					</view>
					<text class="menu-arrow">›</text>
				</view>
			</view>
		</view>
		
		<!-- 退出登录 -->
		<view class="logout-section">
			<button class="logout-btn" @click="handleLogout">
				退出登录
			</button>
		</view>
		
		<!-- 版本信息 -->
		<view class="version-info">
			<text>混凝土生产管理系统 v1.0.0</text>
		</view>
	</view>
</template>

<script>
/**
 * 我的页面
 * 功能：
 * - 显示用户信息
 * - 功能菜单入口
 * - 系统设置
 * - 退出登录
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 用户信息
			userInfo: {}
		}
	},
	
	onLoad() {
		this.getUserInfo()
	},
	
	onShow() {
		this.getUserInfo()
	},
	
	methods: {
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
		 * 显示关于
		 */
		showAbout() {
			uni.showModal({
				title: '关于我们',
				content: '混凝土生产管理系统 v1.0.0\n\n技术栈：\n后端：Python + FastAPI + SQLite\n前端：uniapp\n\n功能模块：\n- 任务接收与确认\n- 配方调用与微调\n- 投料监控与预警\n- 搅拌过程记录',
				showCancel: false
			})
		},
		
		/**
		 * 生成测试数据
		 */
		async generateTestData() {
			const confirm = await this.showModal('生成测试数据', '确定要生成测试数据吗？这将添加测试用户、配方、任务等数据。')
			if (!confirm) return
			
			uni.showLoading({ title: '生成中...' })
			
			try {
				await api.test.generateData()
				
				uni.showToast({
					title: '生成成功',
					icon: 'success'
				})
			} catch (error) {
				console.log('生成测试数据失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 清空测试数据
		 */
		async clearTestData() {
			const confirm = await this.showModal('清空数据', '确定要清空所有测试数据吗？此操作不可恢复！')
			if (!confirm) return
			
			const confirm2 = await this.showModal('再次确认', '真的要清空所有数据吗？')
			if (!confirm2) return
			
			uni.showLoading({ title: '清空中...' })
			
			try {
				await api.test.clearData()
				
				uni.showToast({
					title: '清空成功',
					icon: 'success'
				})
			} catch (error) {
				console.log('清空数据失败:', error)
			} finally {
				uni.hideLoading()
			}
		},
		
		/**
		 * 退出登录
		 */
		async handleLogout() {
			const confirm = await this.showModal('退出登录', '确定要退出登录吗？')
			if (!confirm) return
			
			// 清除本地存储
			uni.removeStorageSync('token')
			uni.removeStorageSync('userInfo')
			
			uni.showToast({
				title: '已退出登录',
				icon: 'success'
			})
			
			// 跳转到登录页
			setTimeout(() => {
				uni.redirectTo({
					url: '/pages/login/login'
				})
			}, 1000)
		},
		
		// ========== 页面跳转 ==========
		
		goToTaskList() {
			uni.switchTab({
				url: '/pages/task/task-list'
			})
		},
		
		goToFormulaList() {
			uni.switchTab({
				url: '/pages/formula/formula-list'
			})
		},
		
		goToFeedingList() {
			uni.navigateTo({
				url: '/pages/feeding/feeding-list'
			})
		},
		
		goToMixingList() {
			uni.navigateTo({
				url: '/pages/mixing/mixing-list'
			})
		},
		
		goToChangePassword() {
			uni.showToast({
				title: '功能开发中',
				icon: 'none'
			})
		}
	}
}
</script>

<style scoped>
/* 我的页面样式 */
.mine-container {
	min-height: 100vh;
	background: #F5F7FA;
	padding-bottom: 60rpx;
}

/* 用户头部 */
.user-header {
	display: flex;
	align-items: center;
	background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
	padding: 60rpx 40rpx;
	padding-top: calc(60rpx + env(safe-area-inset-top));
}

.avatar-box {
	width: 140rpx;
	height: 140rpx;
	background: rgba(255, 255, 255, 0.2);
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 30rpx;
	border: 6rpx solid rgba(255, 255, 255, 0.3);
}

.avatar-text {
	font-size: 60rpx;
	color: #FFFFFF;
	font-weight: bold;
}

.user-info {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.user-name {
	font-size: 40rpx;
	color: #FFFFFF;
	font-weight: bold;
	margin-bottom: 16rpx;
}

.user-meta {
	display: flex;
	align-items: center;
	flex-wrap: wrap;
	gap: 16rpx;
}

.role-tag {
	font-size: 24rpx;
	padding: 6rpx 16rpx;
	border-radius: 8rpx;
}

.role-tag.admin {
	background: rgba(255, 255, 255, 0.3);
	color: #FFFFFF;
}

.role-tag.operator {
	background: rgba(255, 255, 255, 0.2);
	color: #FFFFFF;
}

.user-phone {
	font-size: 26rpx;
	color: rgba(255, 255, 255, 0.9);
}

/* 菜单区块 */
.menu-section {
	background: #FFFFFF;
	margin: 20rpx 30rpx;
	border-radius: 20rpx;
	overflow: hidden;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.03);
}

.menu-title {
	font-size: 26rpx;
	color: #999999;
	padding: 24rpx 30rpx;
	background: #FAFAFA;
	border-bottom: 2rpx solid #F0F0F0;
}

.menu-list {
	padding: 0 30rpx;
}

.menu-item {
	display: flex;
	align-items: center;
	padding: 30rpx 0;
	border-bottom: 2rpx solid #F5F5F5;
}

.menu-item:last-child {
	border-bottom: none;
}

.menu-icon {
	width: 80rpx;
	height: 80rpx;
	border-radius: 16rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	margin-right: 24rpx;
	flex-shrink: 0;
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

.bg-gray {
	background: linear-gradient(135deg, #8C8C8C 0%, #BFBFBF 100%);
}

.bg-red {
	background: linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%);
}

.iconfont {
	font-size: 40rpx;
	color: #FFFFFF;
}

.menu-content {
	flex: 1;
	display: flex;
	flex-direction: column;
}

.menu-name {
	font-size: 30rpx;
	color: #333333;
	margin-bottom: 6rpx;
}

.menu-desc {
	font-size: 24rpx;
	color: #999999;
}

.menu-arrow {
	font-size: 36rpx;
	color: #CCCCCC;
	flex-shrink: 0;
}

/* 退出登录 */
.logout-section {
	padding: 40rpx 30rpx;
}

.logout-btn {
	width: 100%;
	height: 88rpx;
	line-height: 88rpx;
	background: #FFFFFF;
	color: #FF4D4F;
	font-size: 30rpx;
	border-radius: 44rpx;
	border: none;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

/* 版本信息 */
.version-info {
	text-align: center;
	padding: 30rpx;
}

.version-info text {
	font-size: 24rpx;
	color: #CCCCCC;
}
</style>
