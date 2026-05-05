<template>
	<view class="login-container">
		<!-- 顶部Logo区域 -->
		<view class="login-header">
			<view class="logo-box">
				<text class="logo-text">混</text>
			</view>
			<text class="app-title">混凝土生产管理系统</text>
			<text class="app-subtitle">Concrete Production Management</text>
		</view>
		
		<!-- 登录表单 -->
		<view class="login-form">
			<view class="form-item">
				<view class="form-label">
					<text class="iconfont icon-user"></text>
					<text>用户名</text>
				</view>
				<input 
					class="form-input" 
					type="text" 
					v-model="form.username" 
					placeholder="请输入用户名"
					placeholder-class="input-placeholder"
				/>
			</view>
			
			<view class="form-item">
				<view class="form-label">
					<text class="iconfont icon-lock"></text>
					<text>密码</text>
				</view>
				<input 
					class="form-input" 
					:type="showPassword ? 'text' : 'password'" 
					v-model="form.password" 
					placeholder="请输入密码"
					placeholder-class="input-placeholder"
				/>
				<text 
					class="password-toggle" 
					@click="showPassword = !showPassword"
				>
					{{ showPassword ? '隐藏' : '显示' }}
				</text>
			</view>
			
			<!-- 登录按钮 -->
			<button 
				class="login-btn" 
				:disabled="loading"
				@click="handleLogin"
			>
				<text v-if="loading">登录中...</text>
				<text v-else>登 录</text>
			</button>
			
			<!-- 测试账号提示 -->
			<view class="test-accounts" v-if="testAccounts.length > 0">
				<text class="test-title">测试账号：</text>
				<view class="test-list">
					<view 
						class="test-item" 
						v-for="(item, index) in testAccounts" 
						:key="index"
						@click="quickLogin(item)"
					>
						<text class="test-role">{{ item.role === 'admin' ? '管理员' : '操作员' }}</text>
						<text class="test-user">{{ item.username }} / {{ item.password }}</text>
					</view>
				</view>
			</view>
		</view>
		
		<!-- 底部版权信息 -->
		<view class="login-footer">
			<text class="copyright">© 2024 混凝土生产管理系统 v1.0.0</text>
		</view>
	</view>
</template>

<script>
/**
 * 登录页面
 * 功能：
 * - 用户登录（用户名/密码）
 * - 记住密码（可选）
 * - 测试账号快捷登录
 * - Token存储和用户信息存储
 */
import api from '@/utils/api.js'

export default {
	data() {
		return {
			// 表单数据
			form: {
				username: '',
				password: ''
			},
			// 是否显示密码
			showPassword: false,
			// 登录加载状态
			loading: false,
			// 测试账号列表
			testAccounts: []
		}
	},
	
	onLoad() {
		// 页面加载时获取测试账号信息
		this.getTestAccounts()
	},
	
	methods: {
		/**
		 * 获取测试账号信息
		 */
		async getTestAccounts() {
			try {
				const res = await api.auth.getTestUsers()
				if (res && res.test_accounts) {
					this.testAccounts = res.test_accounts
				}
			} catch (error) {
				console.log('获取测试账号失败:', error)
			}
		},
		
		/**
		 * 快捷登录（点击测试账号）
		 * @param {Object} account - 账号信息
		 */
		quickLogin(account) {
			this.form.username = account.username
			this.form.password = account.password
		},
		
		/**
		 * 处理登录
		 */
		async handleLogin() {
			// 表单验证
			if (!this.form.username.trim()) {
				uni.showToast({
					title: '请输入用户名',
					icon: 'none'
				})
				return
			}
			
			if (!this.form.password.trim()) {
				uni.showToast({
					title: '请输入密码',
					icon: 'none'
				})
				return
			}
			
			// 开始登录
			this.loading = true
			
			try {
				const res = await api.auth.login(this.form.username, this.form.password)
				
				// 登录成功
				if (res.access_token) {
					// 存储Token和用户信息
					uni.setStorageSync('token', res.access_token)
					uni.setStorageSync('userInfo', res.user)
					
					uni.showToast({
						title: '登录成功',
						icon: 'success'
					})
					
					// 延迟跳转，让用户看到成功提示
					setTimeout(() => {
						uni.switchTab({
							url: '/pages/index/index'
						})
					}, 1000)
				}
			} catch (error) {
				console.log('登录失败:', error)
				// 错误提示已经在request封装中处理
			} finally {
				this.loading = false
			}
		}
	}
}
</script>

<style scoped>
/* 登录页面样式 */
.login-container {
	min-height: 100vh;
	display: flex;
	flex-direction: column;
	background: linear-gradient(180deg, #1890FF 0%, #40A9FF 50%, #F5F7FA 50%, #F5F7FA 100%);
}

/* 顶部Logo区域 */
.login-header {
	display: flex;
	flex-direction: column;
	align-items: center;
	padding: 100rpx 0 80rpx;
}

.logo-box {
	width: 160rpx;
	height: 160rpx;
	background: #FFFFFF;
	border-radius: 50%;
	display: flex;
	align-items: center;
	justify-content: center;
	box-shadow: 0 8rpx 32rpx rgba(24, 144, 255, 0.3);
	margin-bottom: 30rpx;
}

.logo-text {
	font-size: 80rpx;
	font-weight: bold;
	color: #1890FF;
}

.app-title {
	font-size: 36rpx;
	font-weight: bold;
	color: #FFFFFF;
	margin-bottom: 10rpx;
}

.app-subtitle {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.8);
}

/* 登录表单 */
.login-form {
	flex: 1;
	padding: 0 40rpx;
}

.form-item {
	background: #FFFFFF;
	border-radius: 16rpx;
	padding: 30rpx;
	margin-bottom: 30rpx;
	position: relative;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.form-label {
	display: flex;
	align-items: center;
	margin-bottom: 20rpx;
	font-size: 28rpx;
	color: #666666;
}

.iconfont {
	margin-right: 10rpx;
	font-size: 32rpx;
	color: #1890FF;
}

.form-input {
	font-size: 32rpx;
	color: #333333;
	height: 60rpx;
}

.input-placeholder {
	color: #CCCCCC;
}

.password-toggle {
	position: absolute;
	right: 30rpx;
	bottom: 30rpx;
	font-size: 26rpx;
	color: #1890FF;
}

/* 登录按钮 */
.login-btn {
	width: 100%;
	height: 96rpx;
	background: linear-gradient(90deg, #1890FF 0%, #40A9FF 100%);
	border-radius: 48rpx;
	display: flex;
	align-items: center;
	justify-content: center;
	font-size: 32rpx;
	color: #FFFFFF;
	font-weight: bold;
	border: none;
	margin-top: 20rpx;
	box-shadow: 0 8rpx 24rpx rgba(24, 144, 255, 0.3);
}

.login-btn[disabled] {
	opacity: 0.6;
}

/* 测试账号 */
.test-accounts {
	margin-top: 40rpx;
	padding: 30rpx;
	background: #FFFFFF;
	border-radius: 16rpx;
	box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.test-title {
	font-size: 26rpx;
	color: #999999;
	margin-bottom: 20rpx;
	display: block;
}

.test-list {
	display: flex;
	flex-wrap: wrap;
	gap: 20rpx;
}

.test-item {
	flex: 1;
	min-width: 45%;
	padding: 20rpx;
	background: #F5F7FA;
	border-radius: 12rpx;
	border: 2rpx solid #E8E8E8;
}

.test-role {
	display: block;
	font-size: 24rpx;
	color: #1890FF;
	font-weight: bold;
	margin-bottom: 8rpx;
}

.test-user {
	display: block;
	font-size: 22rpx;
	color: #666666;
}

/* 底部版权 */
.login-footer {
	padding: 40rpx;
	text-align: center;
}

.copyright {
	font-size: 24rpx;
	color: #999999;
}
</style>
