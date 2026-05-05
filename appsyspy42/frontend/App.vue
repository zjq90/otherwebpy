<script>
export default {
    onLaunch: function() {
        console.log('App Launch')
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
page {
    background-color: #f5f5f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
    font-size: 28rpx;
    color: #333;
}

.container {
    padding: 20rpx;
}

.card {
    background-color: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 16rpx;
}

.card-content {
    font-size: 28rpx;
    color: #666;
    line-height: 1.6;
}

.row-between {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.row-center {
    display: flex;
    justify-content: center;
    align-items: center;
}

.col-center {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.text-primary {
    color: #1677ff;
}

.text-success {
    color: #52c41a;
}

.text-warning {
    color: #faad14;
}

.text-danger {
    color: #ff4d4f;
}

.text-muted {
    color: #999;
}

.btn {
    height: 88rpx;
    line-height: 88rpx;
    text-align: center;
    border-radius: 44rpx;
    font-size: 30rpx;
    font-weight: 500;
}

.btn-primary {
    background-color: #1677ff;
    color: #fff;
}

.btn-primary:active {
    background-color: #0958d9;
}

.btn-success {
    background-color: #52c41a;
    color: #fff;
}

.btn-warning {
    background-color: #faad14;
    color: #fff;
}

.btn-danger {
    background-color: #ff4d4f;
    color: #fff;
}

.btn-outline {
    background-color: #fff;
    color: #1677ff;
    border: 2rpx solid #1677ff;
}

.tag {
    display: inline-block;
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
    font-size: 24rpx;
}

.tag-primary {
    background-color: #e6f4ff;
    color: #1677ff;
}

.tag-success {
    background-color: #f6ffed;
    color: #52c41a;
}

.tag-warning {
    background-color: #fffbe6;
    color: #faad14;
}

.tag-danger {
    background-color: #fff2f0;
    color: #ff4d4f;
}

.divider {
    height: 1rpx;
    background-color: #f0f0f0;
    margin: 20rpx 0;
}

.empty-state {
    padding: 100rpx 0;
    text-align: center;
    color: #999;
}

.empty-state image {
    width: 200rpx;
    height: 200rpx;
    margin-bottom: 20rpx;
}

.loading-state {
    padding: 60rpx 0;
    text-align: center;
}

.status-bar {
    height: var(--status-bar-height);
    width: 100%;
}
</style>
