<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
    const token = uni.getStorageSync('token')
    if (!token) {
      uni.reLaunch({
        url: '/pages/login/login'
      })
    }
  },
  onShow: function() {
    console.log('App Show')
  },
  onHide: function() {
    console.log('App Hide')
  }
}
</script>

<style>
@import './uni.scss';

/* 全局样式 */
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: #333;
}

/* 卡片样式 */
.card {
  background: #ffffff;
  border-radius: 16rpx;
  margin: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 按钮样式 */
.btn-primary {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  color: #fff;
  border-radius: 8rpx;
  padding: 20rpx;
  text-align: center;
  font-size: 30rpx;
  font-weight: 500;
}

.btn-primary:active {
  opacity: 0.8;
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
  border-radius: 8rpx;
  padding: 20rpx;
  text-align: center;
  font-size: 30rpx;
}

/* 标签样式 */
.tag {
  display: inline-block;
  padding: 4rpx 16rpx;
  border-radius: 4rpx;
  font-size: 22rpx;
}

.tag-success {
  background: #e8f5e9;
  color: #2e7d32;
}

.tag-warning {
  background: #fff3e0;
  color: #ef6c00;
}

.tag-danger {
  background: #ffebee;
  color: #c62828;
}

.tag-info {
  background: #e3f2fd;
  color: #1565c0;
}

/* 状态标签 */
.status-normal {
  color: #2e7d32;
  background: #e8f5e9;
}

.status-abnormal {
  color: #c62828;
  background: #ffebee;
}

.status-pending {
  color: #ef6c00;
  background: #fff3e0;
}

.status-disabled {
  color: #666;
  background: #f0f0f0;
}

/* 表单样式 */
.form-item {
  padding: 24rpx;
  background: #fff;
  border-bottom: 1rpx solid #eee;
}

.form-label {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 12rpx;
}

.form-input {
  background: #f8f8f8;
  border-radius: 8rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
}

.form-textarea {
  background: #f8f8f8;
  border-radius: 8rpx;
  padding: 20rpx 24rpx;
  font-size: 28rpx;
  height: 160rpx;
}

/* 分割线 */
.divider {
  height: 1rpx;
  background: #eee;
  margin: 20rpx 0;
}

/* 图标大小 */
.icon-small {
  width: 32rpx;
  height: 32rpx;
}

.icon-medium {
  width: 48rpx;
  height: 48rpx;
}

.icon-large {
  width: 64rpx;
  height: 64rpx;
}
</style>
