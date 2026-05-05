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
            
            if (token && userInfo) {
                if (userInfo.is_first_login) {
                    uni.redirectTo({
                        url: '/pages/real-name-verify/real-name-verify'
                    })
                } else {
                    uni.switchTab({
                        url: '/pages/tabbar/index/index'
                    })
                }
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
    color: #333333;
}

/* 容器样式 */
.container {
    padding: 20rpx;
}

/* 卡片样式 */
.card {
    background-color: #ffffff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 主按钮样式 */
.btn-primary {
    background-color: #1890ff;
    color: #ffffff;
    border-radius: 8rpx;
    text-align: center;
    padding: 24rpx;
    font-size: 32rpx;
    font-weight: 500;
}

.btn-primary:active {
    background-color: #096dd9;
}

/* 次要按钮样式 */
.btn-secondary {
    background-color: #ffffff;
    color: #1890ff;
    border: 2rpx solid #1890ff;
    border-radius: 8rpx;
    text-align: center;
    padding: 24rpx;
    font-size: 32rpx;
    font-weight: 500;
}

/* 危险按钮样式 */
.btn-danger {
    background-color: #ff4d4f;
    color: #ffffff;
    border-radius: 8rpx;
    text-align: center;
    padding: 24rpx;
    font-size: 32rpx;
    font-weight: 500;
}

/* 输入框样式 */
.input-group {
    margin-bottom: 32rpx;
}

.input-label {
    display: block;
    font-size: 28rpx;
    color: #666666;
    margin-bottom: 12rpx;
}

.input-field {
    width: 100%;
    height: 88rpx;
    background-color: #f5f5f5;
    border-radius: 8rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
    color: #333333;
}

/* 状态标签样式 */
.status-tag {
    display: inline-block;
    padding: 8rpx 20rpx;
    border-radius: 20rpx;
    font-size: 24rpx;
}

.status-pending {
    background-color: #fff7e6;
    color: #fa8c16;
}

.status-executing,
.status-in-transit {
    background-color: #e6f7ff;
    color: #1890ff;
}

.status-completed {
    background-color: #f6ffed;
    color: #52c41a;
}

.status-qualified {
    background-color: #f6ffed;
    color: #52c41a;
}

.status-unqualified {
    background-color: #fff1f0;
    color: #ff4d4f;
}

.status-approved {
    background-color: #f6ffed;
    color: #52c41a;
}

.status-rejected {
    background-color: #fff1f0;
    color: #ff4d4f;
}

.status-idle {
    background-color: #f0f0f0;
    color: #8c8c8c;
}

.status-busy {
    background-color: #e6f7ff;
    color: #1890ff;
}

.status-maintenance {
    background-color: #fffbe6;
    color: #faad14;
}

.status-low {
    background-color: #e6f7ff;
    color: #1890ff;
}

.status-medium {
    background-color: #fff7e6;
    color: #fa8c16;
}

.status-high {
    background-color: #fff1f0;
    color: #ff4d4f;
}

/* 分割线样式 */
.divider {
    height: 1rpx;
    background-color: #e8e8e8;
    margin: 20rpx 0;
}

/* 空状态样式 */
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
    color: #999999;
}

/* 加载中样式 */
.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60rpx 0;
}
</style>
