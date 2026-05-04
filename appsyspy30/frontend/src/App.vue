<script>
/**
 * 主应用组件
 */
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
        /**
         * 检查登录状态
         */
        checkLoginStatus() {
            const token = uni.getStorageSync('token')
            const userInfo = uni.getStorageSync('userInfo')
            
            if (token && userInfo) {
                // 已登录
                console.log('用户已登录')
            } else {
                // 未登录，跳转到登录页
                console.log('用户未登录')
            }
        }
    }
}
</script>

<style>
/* 全局样式 */
page {
    background-color: #f5f5f5;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    font-size: 28rpx;
    color: #333333;
}

/* 通用容器 */
.container {
    padding: 20rpx;
    background-color: #ffffff;
    border-radius: 16rpx;
    margin: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

/* 弹性布局 */
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

.flex-align-center {
    align-items: center;
}

/* 文字对齐 */
.text-center {
    text-align: center;
}

.text-right {
    text-align: right;
}

/* 文字颜色 */
.text-primary {
    color: #4CAF50;
}

.text-secondary {
    color: #666666;
}

.text-muted {
    color: #999999;
}

.text-danger {
    color: #f44336;
}

/* 背景色 */
.bg-white {
    background-color: #ffffff;
}

.bg-gray {
    background-color: #f5f5f5;
}

/* 边框 */
.border-bottom {
    border-bottom: 1rpx solid #eeeeee;
}

/* 间距 */
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

/* 圆角 */
.round {
    border-radius: 50%;
}

.radius-8 {
    border-radius: 8rpx;
}

.radius-16 {
    border-radius: 16rpx;
}

/* 按钮样式 */
.btn-primary {
    background-color: #4CAF50;
    color: #ffffff;
    border: none;
    border-radius: 8rpx;
    padding: 20rpx 40rpx;
    font-size: 28rpx;
}

.btn-primary:active {
    background-color: #43A047;
}

.btn-outline {
    background-color: #ffffff;
    color: #4CAF50;
    border: 2rpx solid #4CAF50;
    border-radius: 8rpx;
    padding: 20rpx 40rpx;
    font-size: 28rpx;
}

/* 表单样式 */
.form-item {
    display: flex;
    align-items: center;
    padding: 20rpx 30rpx;
    background-color: #ffffff;
    border-bottom: 1rpx solid #f0f0f0;
}

.form-label {
    width: 160rpx;
    font-size: 28rpx;
    color: #333333;
}

.form-input {
    flex: 1;
    font-size: 28rpx;
    color: #333333;
}

/* 头像样式 */
.avatar {
    width: 80rpx;
    height: 80rpx;
    border-radius: 50%;
    background-color: #e0e0e0;
}

.avatar-small {
    width: 60rpx;
    height: 60rpx;
    border-radius: 50%;
    background-color: #e0e0e0;
}

.avatar-large {
    width: 120rpx;
    height: 120rpx;
    border-radius: 50%;
    background-color: #e0e0e0;
}

/* 空状态 */
.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 100rpx 0;
}

.empty-icon {
    width: 160rpx;
    height: 160rpx;
    margin-bottom: 20rpx;
}

.empty-text {
    font-size: 28rpx;
    color: #999999;
}

/* 加载状态 */
.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 40rpx 0;
}

/* 标签样式 */
.tag {
    display: inline-flex;
    align-items: center;
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
    font-size: 22rpx;
}

.tag-primary {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4CAF50;
}

.tag-warning {
    background-color: rgba(255, 152, 0, 0.1);
    color: #FF9800;
}

.tag-info {
    background-color: rgba(33, 150, 243, 0.1);
    color: #2196F3;
}
</style>
