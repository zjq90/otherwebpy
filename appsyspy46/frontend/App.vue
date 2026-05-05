<script>
export default {
  onLaunch: function() {
    console.log('App Launch')
  },
  onShow: function() {
    console.log('App Show')
  },
  onHide: function() {
    console.log('App Hide')
  }
}
</script>

<style lang="scss">
@import './uni.scss';

page {
  background-color: $bg-color;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 28rpx;
  color: $text-color;
}

.container {
  padding: 20rpx;
  background-color: $bg-color;
  min-height: 100vh;
}

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

.flex-wrap {
  flex-wrap: wrap;
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

.text-secondary {
  color: $text-secondary;
}

.text-muted {
  color: $text-muted;
}

.bg-primary {
  background-color: $primary-color;
}

.bg-success {
  background-color: $success-color;
}

.bg-warning {
  background-color: $warning-color;
}

.bg-danger {
  background-color: $danger-color;
}

.bg-white {
  background-color: #ffffff;
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

.p-10 {
  padding: 10rpx;
}

.p-20 {
  padding: 20rpx;
}

.p-30 {
  padding: 30rpx;
}

.border-radius {
  border-radius: 12rpx;
}

.border-radius-sm {
  border-radius: 8rpx;
}

.border-radius-lg {
  border-radius: 20rpx;
}

.shadow {
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}
</style>
