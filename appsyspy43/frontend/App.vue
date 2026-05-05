<script>
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
    // 检查登录状态
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
/* 每个页面公共css */
page {
  background-color: #F5F5F5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 28rpx;
  color: #333333;
  line-height: 1.5;
}

/* 去除默认边距 */
view, text, image {
  box-sizing: border-box;
}

/* 按钮样式 */
.btn-primary {
  background-color: #409EFF;
  color: #FFFFFF;
  border-radius: 8rpx;
  font-size: 32rpx;
  padding: 20rpx 40rpx;
  text-align: center;
}

.btn-primary:active {
  background-color: #66b1ff;
}

.btn-danger {
  background-color: #F56C6C;
  color: #FFFFFF;
  border-radius: 8rpx;
  font-size: 32rpx;
  padding: 20rpx 40rpx;
  text-align: center;
}

.btn-success {
  background-color: #67C23A;
  color: #FFFFFF;
  border-radius: 8rpx;
  font-size: 32rpx;
  padding: 20rpx 40rpx;
  text-align: center;
}

.btn-warning {
  background-color: #E6A23C;
  color: #FFFFFF;
  border-radius: 8rpx;
  font-size: 32rpx;
  padding: 20rpx 40rpx;
  text-align: center;
}

.btn-default {
  background-color: #FFFFFF;
  color: #606266;
  border: 1rpx solid #DCDFE6;
  border-radius: 8rpx;
  font-size: 32rpx;
  padding: 20rpx 40rpx;
  text-align: center;
}

/* 卡片样式 */
.card {
  background-color: #FFFFFF;
  border-radius: 12rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 状态标签样式 */
.status-tag {
  display: inline-flex;
  align-items: center;
  padding: 4rpx 16rpx;
  border-radius: 4rpx;
  font-size: 24rpx;
}

.status-pending {
  background-color: #FEF0F0;
  color: #F56C6C;
}

.status-assigned {
  background-color: #FDF6EC;
  color: #E6A23C;
}

.status-confirmed {
  background-color: #ECF5FF;
  color: #409EFF;
}

.status-departed {
  background-color: #F0F9EB;
  color: #67C23A;
}

.status-arrived {
  background-color: #F4F4F5;
  color: #909399;
}

.status-unloading {
  background-color: #EBEEF5;
  color: #909399;
}

.status-completed {
  background-color: #F0F9EB;
  color: #67C23A;
}

.status-cancelled {
  background-color: #F4F4F5;
  color: #909399;
}

/* 输入框样式 */
.input-group {
  margin-bottom: 24rpx;
}

.input-label {
  display: block;
  font-size: 28rpx;
  color: #606266;
  margin-bottom: 12rpx;
}

.input-field {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background-color: #F5F7FA;
  border: 1rpx solid #DCDFE6;
  border-radius: 8rpx;
  font-size: 30rpx;
  color: #303133;
}

.input-field:focus {
  border-color: #409EFF;
}

/* 分割线 */
.divider {
  height: 1rpx;
  background-color: #EBEEF5;
  margin: 20rpx 0;
}

/* 列表项 */
.list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24rpx;
  background-color: #FFFFFF;
  border-bottom: 1rpx solid #EBEEF5;
}

.list-item:last-child {
  border-bottom: none;
}

/* 图标容器 */
.icon-box {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12rpx;
  margin-right: 20rpx;
}

.icon-primary {
  background-color: #ECF5FF;
  color: #409EFF;
}

.icon-success {
  background-color: #F0F9EB;
  color: #67C23A;
}

.icon-warning {
  background-color: #FDF6EC;
  color: #E6A23C;
}

.icon-danger {
  background-color: #FEF0F0;
  color: #F56C6C;
}
</style>
