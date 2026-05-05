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
page {
  background-color: #F5F7FA;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  font-size: 28rpx;
  color: #333333;
}

.container {
  padding: 20rpx;
}

.card {
  background-color: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.card-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F2329;
  margin-bottom: 16rpx;
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

.text-secondary {
  color: #666666;
}

.text-muted {
  color: #999999;
}

.btn-primary {
  background-color: #1890FF;
  color: #FFFFFF;
  border: none;
  border-radius: 8rpx;
  padding: 20rpx 32rpx;
  font-size: 28rpx;
}

.btn-outline {
  background-color: #FFFFFF;
  color: #1890FF;
  border: 2rpx solid #1890FF;
  border-radius: 8rpx;
  padding: 18rpx 32rpx;
  font-size: 28rpx;
}

.row {
  display: flex;
  flex-direction: row;
}

.col {
  flex: 1;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.mt-10 {
  margin-top: 20rpx;
}

.mb-10 {
  margin-bottom: 20rpx;
}

.p-10 {
  padding: 20rpx;
}

.divider {
  height: 1rpx;
  background-color: #EEEEEE;
  margin: 20rpx 0;
}

.stat-card {
  background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
  border-radius: 16rpx;
  padding: 24rpx;
  color: #FFFFFF;
  margin-bottom: 20rpx;
}

.stat-card.success {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.stat-card.warning {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.stat-card.danger {
  background: linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%);
}

.stat-value {
  font-size: 48rpx;
  font-weight: 600;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 26rpx;
  opacity: 0.9;
}
</style>
