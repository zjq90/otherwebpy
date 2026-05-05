<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
    const token = uni.getStorageSync('token')
    if (token) {
      this.globalData.hasLogin = true
    }
  },
  onShow: function() {
    console.log('App Show')
  },
  onHide: function() {
    console.log('App Hide')
  },
  globalData: {
    hasLogin: false,
    userInfo: null,
    baseUrl: 'http://localhost:8000/api/v1'
  }
}
</script>

<style lang="scss">
@import './uni.scss';

page {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: $bg-color;
  font-size: $font-size-base;
  color: $text-color;
  min-height: 100vh;
}

.container {
  padding: 20rpx;
}

.flex {
  display: flex;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

.flex-between {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.flex-column {
  display: flex;
  flex-direction: column;
}

.text-center {
  text-align: center;
}

.text-primary {
  color: $primary-color;
}

.text-success {
  color: $success-color;
}

.text-warning {
  color: $warning-color;
}

.text-danger {
  color: $danger-color;
}

.text-muted {
  color: $text-secondary;
}

.mt-10 {
  margin-top: 10rpx;
}

.mt-20 {
  margin-top: 20rpx;
}

.mt-30 {
  margin-top: 30rpx;
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

.p-20 {
  padding: 20rpx;
}

.p-30 {
  padding: 30rpx;
}

.card {
  background-color: $white;
  border-radius: $border-radius-lg;
  padding: 30rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.btn {
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  border-radius: $border-radius-md;
  font-size: $font-size-lg;
  font-weight: 500;
}

.btn-primary {
  background-color: $primary-color;
  color: $white;
}

.btn-primary:active {
    background-color: #388E3C;
  }

.btn-outline {
  background-color: transparent;
  border: 2rpx solid $primary-color;
  color: $primary-color;
}

.btn-outline:active {
  background-color: rgba($primary-color, 0.1);
}

.btn-danger {
  background-color: $danger-color;
  color: $white;
}

.btn-danger:active {
    background-color: #C62828;
  }

.btn-small {
  height: 60rpx;
  line-height: 60rpx;
  font-size: $font-size-sm;
  padding: 0 30rpx;
  display: inline-block;
}

.input-group {
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 0 30rpx;
  margin-bottom: 20rpx;
}

.input-item {
  display: flex;
  align-items: center;
  height: 100rpx;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.input-item .label {
  width: 160rpx;
  font-size: $font-size-base;
  color: $text-color;
}

.input-item input {
  flex: 1;
  height: 100%;
  font-size: $font-size-base;
}

.input-item .code-btn {
  padding: 0 20rpx;
  height: 60rpx;
  line-height: 60rpx;
  font-size: $font-size-sm;
  color: $primary-color;
  background-color: rgba($primary-color, 0.1);
  border-radius: $border-radius-sm;
}

.input-item .code-btn.disabled {
  color: $text-muted;
  background-color: $bg-color;
}

.tips {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 0;
}

.empty-state image {
  width: 240rpx;
  height: 240rpx;
  margin-bottom: 30rpx;
}

.empty-state .text {
  font-size: $font-size-base;
  color: $text-secondary;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
  font-size: $font-size-sm;
}

.status-pending {
  background-color: #FFF3E0;
  color: $warning-color;
}

.status-progress {
  background-color: #E3F2FD;
  color: $primary-color;
}

.status-completed {
  background-color: #E8F5E9;
  color: $success-color;
}

.status-cancelled {
  background-color: #F5F5F5;
  color: $text-secondary;
}

.divider {
  height: 1rpx;
  background-color: $border-color;
  margin: 20rpx 0;
}

.tag {
  display: inline-block;
  padding: 4rpx 16rpx;
  font-size: $font-size-sm;
  border-radius: $border-radius-sm;
  margin-right: 10rpx;
  margin-bottom: 10rpx;
}

.tag-primary {
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
}

.tag-success {
  background-color: rgba($success-color, 0.1);
  color: $success-color;
}

.tag-warning {
  background-color: rgba($warning-color, 0.1);
  color: $warning-color;
}

.tag-outline {
  background-color: transparent;
  border: 1rpx solid $border-color;
  color: $text-secondary;
}

.tag-outline.active {
  border-color: $primary-color;
  color: $primary-color;
  background-color: rgba($primary-color, 0.05);
}
</style>
