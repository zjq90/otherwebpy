<script>
	/**
	 * 应用入口文件
	 * 处理全局生命周期和全局变量
	 */
	export default {
		onLaunch: function() {
			console.log('App Launch')
			// 检查登录状态
			this.checkLoginStatus()
		},
		onShow: function() {
			console.log('App Show')
		},
		onHide: function() {
			console.log('App Hide')
		},
		methods: {
			/**
			 * 检查登录状态
			 * 如果未登录，跳转到登录页
			 */
			checkLoginStatus() {
				const token = uni.getStorageSync('token')
				const userInfo = uni.getStorageSync('userInfo')
				
				if (!token || !userInfo) {
					// 未登录，跳转到登录页
					uni.redirectTo({
						url: '/pages/login/login'
					})
				}
			}
		}
	}
</script>

<style>
	/* 全局样式 */
	/* 每个页面公共css */
	page {
		background-color: #F5F7FA;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
		font-size: 28rpx;
		color: #333333;
	}
	
	/* 清除默认边距 */
	view, text, scroll-view, swiper, swiper-item, movable-view, cover-view, cover-image {
		box-sizing: border-box;
	}
	
	/* 常用工具类 */
	.flex {
		display: flex;
	}
	
	.flex-column {
		flex-direction: column;
	}
	
	.flex-between {
		justify-content: space-between;
	}
	
	.flex-center {
		justify-content: center;
		align-items: center;
	}
	
	.flex-wrap {
		flex-wrap: wrap;
	}
	
	.flex-1 {
		flex: 1;
	}
	
	.align-center {
		align-items: center;
	}
	
	.text-center {
		text-align: center;
	}
	
	.text-right {
		text-align: right;
	}
	
	.text-primary {
		color: #1890FF;
	}
	
	.text-success {
		color: #52C41A;
	}
	
	.text-warning {
		color: #FAAD14;
	}
	
	.text-danger {
		color: #FF4D4F;
	}
	
	.text-gray {
		color: #999999;
	}
	
	.text-light-gray {
		color: #CCCCCC;
	}
	
	.text-bold {
		font-weight: bold;
	}
	
	.bg-white {
		background-color: #FFFFFF;
	}
	
	.bg-primary {
		background-color: #1890FF;
	}
	
	.p-20 {
		padding: 20rpx;
	}
	
	.p-30 {
		padding: 30rpx;
	}
	
	.m-20 {
		margin: 20rpx;
	}
	
	.mb-20 {
		margin-bottom: 20rpx;
	}
	
	.mt-20 {
		margin-top: 20rpx;
	}
	
	.mr-20 {
		margin-right: 20rpx;
	}
	
	.ml-20 {
		margin-left: 20rpx;
	}
	
	.radius-8 {
		border-radius: 16rpx;
	}
	
	.radius-12 {
		border-radius: 24rpx;
	}
	
	.shadow {
		box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
	}
	
	.line-1 {
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
	}
	
	.line-2 {
		display: -webkit-box;
		-webkit-box-orient: vertical;
		-webkit-line-clamp: 2;
		overflow: hidden;
	}
	
	/* 状态标签样式 */
	.status-tag {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 4rpx 16rpx;
		border-radius: 8rpx;
		font-size: 24rpx;
	}
	
	.status-pending {
		background-color: #FFF7E6;
		color: #FA8C16;
	}
	
	.status-accepted {
		background-color: #E6F7FF;
		color: #1890FF;
	}
	
	.status-in_progress {
		background-color: #F6FFED;
		color: #52C41A;
	}
	
	.status-completed {
		background-color: #F0F0F0;
		color: #666666;
	}
	
	.status-cancelled {
		background-color: #FFF1F0;
		color: #FF4D4F;
	}
	
	/* 预警标签 */
	.warning-tag {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 4rpx 16rpx;
		border-radius: 8rpx;
		font-size: 24rpx;
	}
	
	.warning-normal {
		background-color: #F6FFED;
		color: #52C41A;
	}
	
	.warning-warning {
		background-color: #FFF7E6;
		color: #FA8C16;
	}
	
	.warning-critical {
		background-color: #FFF1F0;
		color: #FF4D4F;
	}
</style>
