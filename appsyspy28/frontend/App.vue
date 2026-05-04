<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
    const token = uni.getStorageSync('token')
    if (token) {
      console.log('已登录，token存在')
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
page {
  background-color: #f3f4f6;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 28rpx;
  color: #1f2937;
}

.container {
  padding: 20rpx;
  box-sizing: border-box;
}

.card {
  background-color: #ffffff;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 20rpx;
  overflow: hidden;
}

.card-header {
  padding: 24rpx;
  border-bottom: 1rpx solid #f3f4f6;
}

.card-body {
  padding: 24rpx;
}

.card-footer {
  padding: 24rpx;
  border-top: 1rpx solid #f3f4f6;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.btn {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  padding: 16rpx 32rpx;
  border-radius: 8rpx;
  font-size: 28rpx;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-primary {
  background-color: #2563eb;
  color: #ffffff;
}

.btn-primary:active {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #6b7280;
  color: #ffffff;
}

.btn-success {
  background-color: #10b981;
  color: #ffffff;
}

.btn-danger {
  background-color: #ef4444;
  color: #ffffff;
}

.btn-outline {
  background-color: transparent;
  border: 2rpx solid #2563eb;
  color: #2563eb;
}

.btn-sm {
  padding: 10rpx 20rpx;
  font-size: 24rpx;
}

.btn-lg {
  padding: 24rpx 48rpx;
  font-size: 32rpx;
}

.btn-block {
  width: 100%;
}

.btn:disabled {
  opacity: 0.6;
  pointer-events: none;
}

.text-primary {
  color: #2563eb;
}

.text-success {
  color: #10b981;
}

.text-warning {
  color: #f59e0b;
}

.text-danger {
  color: #ef4444;
}

.text-secondary {
  color: #6b7280;
}

.text-muted {
  color: #9ca3af;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.flex {
  display: flex;
}

.flex-column {
  flex-direction: column;
}

.flex-wrap {
  flex-wrap: wrap;
}

.justify-center {
  justify-content: center;
}

.justify-between {
  justify-content: space-between;
}

.justify-around {
  justify-content: space-around;
}

.items-center {
  align-items: center;
}

.flex-1 {
  flex: 1;
}

.gap-10 {
  gap: 10rpx;
}

.gap-20 {
  gap: 20rpx;
}

.p-10 {
  padding: 10rpx;
}

.p-20 {
  padding: 20rpx;
}

.p-30 {
  padding: 30rpx;
}

.m-10 {
  margin: 10rpx;
}

.m-20 {
  margin: 20rpx;
}

.mb-10 {
  margin-bottom: 10rpx;
}

.mb-20 {
  margin-bottom: 20rpx;
}

.mb-30 {
  margin-bottom: 30rpx;
}

.mt-10 {
  margin-top: 10rpx;
}

.mt-20 {
  margin-top: 20rpx;
}

.font-bold {
  font-weight: bold;
}

.font-medium {
  font-weight: 500;
}

.text-sm {
  font-size: 24rpx;
}

.text-base {
  font-size: 28rpx;
}

.text-lg {
  font-size: 32rpx;
}

.text-xl {
  font-size: 36rpx;
}

.text-2xl {
  font-size: 44rpx;
}

.rounded {
  border-radius: 8rpx;
}

.rounded-lg {
  border-radius: 16rpx;
}

.rounded-full {
  border-radius: 9999rpx;
}

.divider {
  height: 1rpx;
  background-color: #e5e7eb;
  margin: 20rpx 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 100rpx 40rpx;
  color: #9ca3af;
}

.empty-state .icon {
  font-size: 120rpx;
  margin-bottom: 20rpx;
}

.empty-state .text {
  font-size: 28rpx;
}

.badge {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  font-size: 20rpx;
  font-weight: 500;
}

.badge-primary {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.badge-success {
  background-color: #d1fae5;
  color: #047857;
}

.badge-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-danger {
  background-color: #fee2e2;
  color: #b91c1c;
}

.badge-secondary {
  background-color: #f3f4f6;
  color: #4b5563;
}

.tag {
  display: inline-block;
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
  font-size: 22rpx;
  margin-right: 10rpx;
  margin-bottom: 10rpx;
}

.tag-blue {
  background-color: #dbeafe;
  color: #1d4ed8;
}

.tag-green {
  background-color: #d1fae5;
  color: #047857;
}

.tag-yellow {
  background-color: #fef3c7;
  color: #92400e;
}

.tag-purple {
  background-color: #ede9fe;
  color: #6d28d9;
}
</style>
