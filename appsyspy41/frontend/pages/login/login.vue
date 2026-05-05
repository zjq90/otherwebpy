<template>
	<view class="login-container">
		<view class="login-header">
			<view class="logo">
				<text class="logo-text">设备管理系统</text>
			</view>
			<view class="subtitle">
				<text>设备监控 · 保养管理 · 故障报修</text>
			</view>
		</view>
		
		<view class="login-form">
			<view class="form-item">
				<view class="form-label">
					<text>用户名</text>
				</view>
				<input 
					class="form-input" 
					type="text" 
					placeholder="请输入用户名"
					v-model="formData.username"
					:disabled="loading"
				/>
			</view>
			
			<view class="form-item">
				<view class="form-label">
					<text>密码</text>
				</view>
				<input 
					class="form-input" 
					type="password" 
					placeholder="请输入密码"
					v-model="formData.password"
					:disabled="loading"
					@confirm="handleLogin"
				/>
			</view>
			
			<view class="form-tips">
				<text class="tips-text">测试账号: admin / 123456</text>
			</view>
			
			<button 
				class="login-btn btn btn-primary" 
				:class="{ 'btn-disabled': loading }"
				:disabled="loading"
				@click="handleLogin"
			>
				<text v-if="!loading">登录</text>
				<text v-else>登录中...</text>
			</button>
		</view>
		
		<view class="login-footer">
			<text class="footer-text">版本 1.0.0</text>
		</view>
	</view>
</template>

<script>
import api from '@/api/index.js'
import utils from '@/utils/index.js'

export default {
	data() {
		return {
			loading: false,
			formData: {
				username: '',
				password: ''
			}
		}
	},
	
	onLoad() {
		// 检查是否已登录
		const userInfo = utils.getCurrentUser()
		if (userInfo) {
			uni.reLaunch({
				url: '/pages/index/index'
			})
		}
	},
	
	methods: {
		/**
		 * 处理登录
		 */
		async handleLogin() {
			// 验证表单
			if (!this.formData.username.trim()) {
				utils.showError('请输入用户名')
				return
			}
			if (!this.formData.password.trim()) {
				utils.showError('请输入密码')
				return
			}
			
			this.loading = true
			
			try {
				const res = await api.auth.login(
					this.formData.username.trim(),
					this.formData.password.trim()
				)
				
				if (res.code === 200) {
					// 保存用户信息
					utils.setCurrentUser(res.data.user)
					
					utils.showSuccess('登录成功')
					
					// 延迟跳转，让用户看到提示
					setTimeout(() => {
						uni.reLaunch({
							url: '/pages/index/index'
						})
					}, 1000)
				}
			} catch (err) {
				console.error('登录失败:', err)
			} finally {
				this.loading = false
			}
		}
	}
}
</script>

<style scoped>
.login-container {
	min-height: 100vh;
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
	display: flex;
	flex-direction: column;
	padding: 80rpx 48rpx;
}

.login-header {
	text-align: center;
	margin-bottom: 80rpx;
	padding-top: 60rpx;
}

.logo {
	margin-bottom: 24rpx;
}

.logo-text {
	font-size: 56rpx;
	font-weight: bold;
	color: #fff;
}

.subtitle text {
	font-size: 28rpx;
	color: rgba(255, 255, 255, 0.8);
}

.login-form {
	background-color: #fff;
	border-radius: 24rpx;
	padding: 48rpx;
	box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.1);
}

.form-item {
	margin-bottom: 32rpx;
}

.form-item:last-child {
	margin-bottom: 0;
}

.form-label {
	margin-bottom: 16rpx;
}

.form-label text {
	font-size: 28rpx;
	color: #333;
	font-weight: 500;
}

.form-input {
	width: 100%;
	height: 88rpx;
	padding: 0 24rpx;
	font-size: 30rpx;
	background-color: #f5f5f5;
	border-radius: 12rpx;
	border: 2rpx solid transparent;
}

.form-input:focus {
	border-color: #1677ff;
	background-color: #fff;
}

.form-tips {
	margin-bottom: 48rpx;
	text-align: center;
}

.tips-text {
	font-size: 24rpx;
	color: #999;
}

.login-btn {
	width: 100%;
	height: 96rpx;
	border-radius: 12rpx;
	font-size: 32rpx;
	font-weight: 500;
}

.login-btn:not(.btn-disabled) {
	background: linear-gradient(135deg, #1677ff 0%, #40a9ff 100%);
}

.btn-disabled {
	background-color: #d9d9d9 !important;
	opacity: 0.7;
}

.login-footer {
	margin-top: auto;
	text-align: center;
	padding-top: 48rpx;
}

.footer-text {
	font-size: 24rpx;
	color: rgba(255, 255, 255, 0.6);
}
</style>
