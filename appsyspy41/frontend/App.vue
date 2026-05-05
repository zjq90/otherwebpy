<script>
	export default {
		onLaunch: function() {
			console.log('App Launch')
			// 检查用户登录状态
			this.checkLoginStatus()
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		methods: {
			checkLoginStatus() {
				const userInfo = uni.getStorageSync('userInfo')
				if (!userInfo) {
					// 未登录，跳转到登录页
					uni.reLaunch({
						url: '/pages/login/login'
					})
				}
			}
		}
	}
</script>

<style>
	/* 全局样式 */
	* {
		margin: 0;
		padding: 0;
		box-sizing: border-box;
	}
	
	page {
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
		font-size: 28rpx;
		color: #333;
		background-color: #f5f5f5;
	}
	
	/* 通用容器 */
	.container {
		padding: 24rpx;
		background-color: #f5f5f5;
		min-height: 100vh;
	}
	
	/* 卡片样式 */
	.card {
		background-color: #fff;
		border-radius: 16rpx;
		padding: 24rpx;
		margin-bottom: 24rpx;
		box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
	}
	
	/* 状态标签样式 */
	.status-tag {
		display: inline-block;
		padding: 4rpx 16rpx;
		border-radius: 8rpx;
		font-size: 24rpx;
	}
	
	.status-normal {
		background-color: #e6f7ff;
		color: #1890ff;
	}
	
	.status-warning {
		background-color: #fffbe6;
		color: #faad14;
	}
	
	.status-fault {
		background-color: #fff2f0;
		color: #ff4d4f;
	}
	
	.status-pending {
		background-color: #f0f0f0;
		color: #666;
	}
	
	.status-processing {
		background-color: #e6fffb;
		color: #13c2c2;
	}
	
	.status-completed {
		background-color: #f6ffed;
		color: #52c41a;
	}
	
	.status-overdue {
		background-color: #fff2f0;
		color: #ff4d4f;
	}
	
	/* 优先级标签 */
	.priority-high {
		background-color: #fff2f0;
		color: #ff4d4f;
	}
	
	.priority-medium {
		background-color: #fffbe6;
		color: #faad14;
	}
	
	.priority-low {
		background-color: #f6ffed;
		color: #52c41a;
	}
	
	/* 按钮样式 */
	.btn {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 88rpx;
		border-radius: 8rpx;
		font-size: 32rpx;
		font-weight: 500;
	}
	
	.btn-primary {
		background-color: #1677ff;
		color: #fff;
	}
	
	.btn-danger {
		background-color: #ff4d4f;
		color: #fff;
	}
	
	.btn-success {
		background-color: #52c41a;
		color: #fff;
	}
	
	.btn-default {
		background-color: #fff;
		color: #333;
		border: 1rpx solid #d9d9d9;
	}
	
	/* 表单样式 */
	.form-item {
		padding: 24rpx 0;
		border-bottom: 1rpx solid #f0f0f0;
	}
	
	.form-item:last-child {
		border-bottom: none;
	}
	
	.form-label {
		display: block;
		font-size: 28rpx;
		color: #666;
		margin-bottom: 16rpx;
	}
	
	.form-input {
		width: 100%;
		height: 80rpx;
		padding: 0 24rpx;
		font-size: 30rpx;
		background-color: #fafafa;
		border-radius: 8rpx;
		border: none;
	}
	
	.form-textarea {
		width: 100%;
		min-height: 200rpx;
		padding: 24rpx;
		font-size: 30rpx;
		background-color: #fafafa;
		border-radius: 8rpx;
		border: none;
		line-height: 1.6;
	}
	
	/* 空数据样式 */
	.empty-state {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 100rpx 0;
	}
	
	.empty-state-icon {
		font-size: 120rpx;
		color: #d9d9d9;
		margin-bottom: 24rpx;
	}
	
	.empty-state-text {
		font-size: 28rpx;
		color: #999;
	}
	
	/* 加载中样式 */
	.loading {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 50rpx 0;
	}
	
	/* 分隔线 */
	.divider {
		height: 1rpx;
		background-color: #f0f0f0;
		margin: 24rpx 0;
	}
</style>
