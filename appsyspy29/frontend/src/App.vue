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
page {
  background-color: #f5f5f5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
  font-size: 28rpx;
  color: #333;
}

/* 容器 */
.container {
  padding: 20rpx;
  box-sizing: border-box;
}

/* 卡片样式 */
.card {
  background-color: #fff;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 按钮样式 */
.btn-primary {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: #fff;
  border: none;
  border-radius: 8rpx;
  padding: 20rpx 40rpx;
  font-size: 30rpx;
  font-weight: 500;
}

.btn-primary:active {
  opacity: 0.8;
}

.btn-default {
  background-color: #fff;
  color: #606266;
  border: 1rpx solid #dcdfe6;
  border-radius: 8rpx;
  padding: 20rpx 40rpx;
  font-size: 30rpx;
}

/* 表单样式 */
.form-item {
  margin-bottom: 30rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #606266;
  margin-bottom: 12rpx;
}

.form-input {
  width: 100%;
  height: 80rpx;
  padding: 0 20rpx;
  background-color: #f5f7fa;
  border-radius: 8rpx;
  font-size: 30rpx;
  color: #333;
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  height: 200rpx;
  padding: 20rpx;
  background-color: #f5f7fa;
  border-radius: 8rpx;
  font-size: 30rpx;
  color: #333;
  box-sizing: border-box;
}

/* 统计数据样式 */
.stats-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10rpx;
}

.stats-item {
  width: 50%;
  padding: 0 10rpx;
  margin-bottom: 20rpx;
  box-sizing: border-box;
}

.stats-card {
  background-color: #fff;
  border-radius: 12rpx;
  padding: 24rpx;
  text-align: center;
}

.stats-value {
  font-size: 40rpx;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8rpx;
}

.stats-label {
  font-size: 24rpx;
  color: #909399;
}

/* 进度条样式 */
.progress-bar {
  width: 100%;
  height: 16rpx;
  background-color: #ebeef5;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF, #66b1ff);
  border-radius: 8rpx;
  transition: width 0.3s ease;
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 40rpx;
}

.empty-icon {
  width: 120rpx;
  height: 120rpx;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
}

/* 加载样式 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40rpx;
}

/* 分割线 */
.divider {
  height: 1rpx;
  background-color: #ebeef5;
  margin: 20rpx 0;
}

/* flex布局工具类 */
.flex {
  display: flex;
}

.flex-column {
  flex-direction: column;
}

.flex-center {
  justify-content: center;
  align-items: center;
}

.flex-between {
  justify-content: space-between;
}

.flex-around {
  justify-content: space-around;
}

.flex-1 {
  flex: 1;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.text-primary {
  color: #409EFF;
}

.text-success {
  color: #67c23a;
}

.text-warning {
  color: #e6a23c;
}

.text-danger {
  color: #f56c6c;
}

.text-secondary {
  color: #909399;
}

.font-bold {
  font-weight: 600;
}

.mb-10 {
  margin-bottom: 20rpx;
}

.mb-20 {
  margin-bottom: 40rpx;
}

.mt-10 {
  margin-top: 20rpx;
}

.p-10 {
  padding: 20rpx;
}
</style>
