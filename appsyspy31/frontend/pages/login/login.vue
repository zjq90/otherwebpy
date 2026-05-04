<template>
    <view class="login-container">
        <view class="login-header">
            <view class="logo">
                <text class="logo-text">🏋️</text>
            </view>
            <text class="app-name">健身俱乐部</text>
            <text class="app-desc">智能健身，健康生活</text>
        </view>
        
        <view class="login-form">
            <view class="form-item">
                <text class="form-label">账号</text>
                <input 
                    class="form-input" 
                    type="text" 
                    placeholder="请输入用户名或手机号" 
                    v-model="formData.username"
                    placeholder-class="placeholder"
                />
            </view>
            
            <view class="form-item">
                <text class="form-label">密码</text>
                <input 
                    class="form-input" 
                    type="password" 
                    placeholder="请输入密码" 
                    v-model="formData.password"
                    placeholder-class="placeholder"
                    @confirm="handleLogin"
                />
            </view>
            
            <view class="form-options">
                <view class="remember-me" @click="toggleRemember">
                    <text class="icon" :class="rememberMe ? 'checked' : ''">✓</text>
                    <text class="remember-text">记住密码</text>
                </view>
                <text class="forgot-password">忘记密码？</text>
            </view>
            
            <view class="login-btn" @click="handleLogin" :class="{ 'loading': loading }">
                <text v-if="!loading">登 录</text>
                <text v-else>登录中...</text>
            </view>
            
            <view class="register-link">
                <text class="register-text">还没有账号？</text>
                <text class="register-btn" @click="goToRegister">立即注册</text>
            </view>
        </view>
        
        <view class="quick-login">
            <text class="quick-title">快捷登录测试账号</text>
            <view class="quick-list">
                <view class="quick-item" @click="quickLogin('member')">
                    <view class="quick-avatar member">会</view>
                    <view class="quick-info">
                        <text class="quick-role">会员</text>
                        <text class="quick-account">member1 / 123456</text>
                    </view>
                </view>
                <view class="quick-item" @click="quickLogin('coach')">
                    <view class="quick-avatar coach">教</view>
                    <view class="quick-info">
                        <text class="quick-role">教练</text>
                        <text class="quick-account">coach1 / 123456</text>
                    </view>
                </view>
                <view class="quick-item" @click="quickLogin('admin')">
                    <view class="quick-avatar admin">管</view>
                    <view class="quick-info">
                        <text class="quick-role">管理员</text>
                        <text class="quick-account">admin / admin123</text>
                    </view>
                </view>
            </view>
        </view>
    </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authApi } from '@/utils/api'
import { showLoading, hideLoading, showToast } from '@/utils'

const formData = ref({
    username: '',
    password: ''
})

const loading = ref(false)
const rememberMe = ref(false)

const toggleRemember = () => {
    rememberMe.value = !rememberMe.value
}

const handleLogin = async () => {
    if (!formData.value.username) {
        showToast('请输入用户名或手机号')
        return
    }
    if (!formData.value.password) {
        showToast('请输入密码')
        return
    }
    
    try {
        loading.value = true
        showLoading('登录中...')
        
        const loginData = {
            username: formData.value.username,
            password: formData.value.password
        }
        
        const res = await authApi.login(loginData)
        
        if (res.code === 200) {
            uni.setStorageSync('token', res.data.access_token)
            uni.setStorageSync('userInfo', JSON.stringify(res.data.user))
            
            if (rememberMe.value) {
                uni.setStorageSync('savedUsername', formData.value.username)
                uni.setStorageSync('savedPassword', formData.value.password)
            }
            
            showToast('登录成功', 'success')
            
            setTimeout(() => {
                uni.switchTab({
                    url: '/pages/index/index'
                })
            }, 1000)
        }
    } catch (error) {
        console.error('登录失败:', error)
    } finally {
        loading.value = false
        hideLoading()
    }
}

const quickLogin = (type) => {
    switch (type) {
        case 'member':
            formData.value.username = 'member1'
            formData.value.password = '123456'
            break
        case 'coach':
            formData.value.username = 'coach1'
            formData.value.password = '123456'
            break
        case 'admin':
            formData.value.username = 'admin'
            formData.value.password = 'admin123'
            break
    }
}

const goToRegister = () => {
    uni.navigateTo({
        url: '/pages/register/register'
    })
}

onMounted(() => {
    const savedUsername = uni.getStorageSync('savedUsername')
    const savedPassword = uni.getStorageSync('savedPassword')
    
    if (savedUsername && savedPassword) {
        formData.value.username = savedUsername
        formData.value.password = savedPassword
        rememberMe.value = true
    }
})
</script>

<style lang="scss" scoped>
.login-container {
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 60rpx 40rpx;
    box-sizing: border-box;
}

.login-header {
    text-align: center;
    margin-bottom: 80rpx;
    padding-top: 40rpx;
}

.logo {
    width: 160rpx;
    height: 160rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 30rpx;
}

.logo-text {
    font-size: 80rpx;
}

.app-name {
    font-size: 44rpx;
    font-weight: bold;
    color: #ffffff;
    margin-bottom: 10rpx;
    display: block;
}

.app-desc {
    font-size: 26rpx;
    color: rgba(255, 255, 255, 0.8);
}

.login-form {
    background: #ffffff;
    border-radius: 24rpx;
    padding: 50rpx 40rpx;
    margin-bottom: 40rpx;
}

.form-item {
    margin-bottom: 40rpx;
}

.form-label {
    font-size: 28rpx;
    color: #333333;
    font-weight: 500;
    margin-bottom: 15rpx;
    display: block;
}

.form-input {
    width: 100%;
    height: 88rpx;
    background: #f5f7fa;
    border-radius: 12rpx;
    padding: 0 30rpx;
    font-size: 28rpx;
    color: #333333;
    box-sizing: border-box;
}

.placeholder {
    color: #999999;
}

.form-options {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 50rpx;
}

.remember-me {
    display: flex;
    align-items: center;
}

.icon {
    width: 36rpx;
    height: 36rpx;
    border: 2rpx solid #ddd;
    border-radius: 6rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22rpx;
    color: transparent;
    margin-right: 12rpx;
}

.icon.checked {
    background: $primary-color;
    border-color: $primary-color;
    color: #ffffff;
}

.remember-text {
    font-size: 26rpx;
    color: #666666;
}

.forgot-password {
    font-size: 26rpx;
    color: $primary-color;
}

.login-btn {
    width: 100%;
    height: 96rpx;
    background: linear-gradient(135deg, $primary-color 0%, $secondary-color 100%);
    border-radius: 48rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8rpx 20rpx rgba(102, 126, 234, 0.3);
}

.login-btn text {
    font-size: 32rpx;
    font-weight: 500;
    color: #ffffff;
}

.register-link {
    text-align: center;
    margin-top: 40rpx;
}

.register-text {
    font-size: 26rpx;
    color: #999999;
}

.register-btn {
    font-size: 26rpx;
    color: $primary-color;
    margin-left: 10rpx;
}

.quick-login {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 24rpx;
    padding: 40rpx;
}

.quick-title {
    font-size: 28rpx;
    color: #666666;
    margin-bottom: 30rpx;
    display: block;
}

.quick-list {
    display: flex;
    flex-wrap: wrap;
    gap: 20rpx;
}

.quick-item {
    display: flex;
    align-items: center;
    background: #f5f7fa;
    border-radius: 16rpx;
    padding: 20rpx 25rpx;
    flex: 1;
    min-width: calc(50% - 10rpx);
}

.quick-avatar {
    width: 64rpx;
    height: 64rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28rpx;
    font-weight: bold;
    color: #ffffff;
    margin-right: 20rpx;
}

.quick-avatar.member {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.quick-avatar.coach {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.quick-avatar.admin {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.quick-info {
    display: flex;
    flex-direction: column;
}

.quick-role {
    font-size: 26rpx;
    color: #333333;
    font-weight: 500;
}

.quick-account {
    font-size: 22rpx;
    color: #999999;
    margin-top: 6rpx;
}
</style>
