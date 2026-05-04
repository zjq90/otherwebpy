<script setup>
import { onLaunch, onShow, onHide } from '@dcloudio/uni-app'

onLaunch(() => {
    console.log('App Launch')
    const token = uni.getStorageSync('token')
    if (token) {
        console.log('用户已登录')
    }
})

onShow(() => {
    console.log('App Show')
})

onHide(() => {
    console.log('App Hide')
})
</script>

<style lang="scss">
@import './uni.scss';

page {
    background-color: $bg-color;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    font-size: 28rpx;
    color: $text-color;
    min-height: 100vh;
}

.container {
    padding: 30rpx;
}

.card {
    background-color: #ffffff;
    border-radius: 16rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
    padding: 30rpx;
    margin-bottom: 20rpx;
}

.btn-primary {
    background: linear-gradient(135deg, $primary-color 0%, $secondary-color 100%);
    color: #ffffff;
    border: none;
    border-radius: 50rpx;
    padding: 24rpx 48rpx;
    font-size: 30rpx;
    font-weight: 500;
    text-align: center;
    
    &:active {
        opacity: 0.9;
    }
}

.btn-secondary {
    background-color: #ffffff;
    color: $primary-color;
    border: 2rpx solid $primary-color;
    border-radius: 50rpx;
    padding: 24rpx 48rpx;
    font-size: 30rpx;
    font-weight: 500;
    text-align: center;
    
    &:active {
        opacity: 0.9;
    }
}

.text-primary {
    color: $primary-color;
}

.text-secondary {
    color: $text-secondary;
}

.text-danger {
    color: $danger-color;
}

.text-success {
    color: $success-color;
}

.text-warning {
    color: $warning-color;
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

.flex-1 {
    flex: 1;
}

.text-center {
    text-align: center;
}

.text-ellipsis {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.text-ellipsis-2 {
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
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
</style>
