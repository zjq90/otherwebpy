<template>
    <view class="login-container">
        <!-- 顶部Logo区域 -->
        <view class="logo-section">
            <view class="logo-icon">
                <text class="logo-text">💪</text>
            </view>
            <text class="app-name">健身社交</text>
            <text class="app-slogan">让运动更有动力</text>
        </view>

        <!-- 表单区域 -->
        <view class="form-section">
            <!-- 用户名/邮箱 -->
            <view class="form-item">
                <text class="form-label">账号</text>
                <input 
                    class="form-input" 
                    type="text" 
                    placeholder="请输入用户名或邮箱"
                    v-model="loginForm.username"
                    placeholder-class="placeholder-text"
                />
            </view>

            <!-- 密码 -->
            <view class="form-item">
                <text class="form-label">密码</text>
                <input 
                    class="form-input" 
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="请输入密码"
                    v-model="loginForm.password"
                    placeholder-class="placeholder-text"
                />
                <text 
                    class="eye-icon" 
                    @click="showPassword = !showPassword"
                >
                    {{ showPassword ? '👁️' : '🙈' }}
                </text>
            </view>

            <!-- 登录按钮 -->
            <button 
                class="login-btn" 
                :loading="loading"
                @click="handleLogin"
            >
                登录
            </button>

            <!-- 快速操作 -->
            <view class="quick-actions">
                <text class="action-text" @click="goToRegister">
                    还没有账号？<text class="highlight-text">立即注册</text>
                </text>
            </view>
        </view>

        <!-- 底部提示 -->
        <view class="footer-section">
            <text class="footer-text">测试账号: user1 / 123456</text>
        </view>
    </view>
</template>

<script>
import { authApi } from '@/api/auth'
import { setToken, setUserInfo, navigateToHome } from '@/utils/auth'

export default {
    data() {
        return {
            loginForm: {
                username: '',
                password: ''
            },
            showPassword: false,
            loading: false
        }
    },
    methods: {
        /**
         * 处理登录
         */
        async handleLogin() {
            // 表单验证
            if (!this.loginForm.username.trim()) {
                uni.showToast({
                    title: '请输入用户名或邮箱',
                    icon: 'none'
                })
                return
            }
            
            if (!this.loginForm.password.trim()) {
                uni.showToast({
                    title: '请输入密码',
                    icon: 'none'
                })
                return
            }

            this.loading = true

            try {
                const res = await authApi.login({
                    username: this.loginForm.username,
                    password: this.loginForm.password
                })

                // 保存Token和用户信息
                setToken(res.access_token)
                setUserInfo(res.user)

                uni.showToast({
                    title: '登录成功',
                    icon: 'success'
                })

                // 跳转到首页
                setTimeout(() => {
                    navigateToHome()
                }, 1000)

            } catch (error) {
                console.error('登录失败:', error)
            } finally {
                this.loading = false
            }
        },

        /**
         * 跳转到注册页
         */
        goToRegister() {
            uni.navigateTo({
                url: '/pages/register/register'
            })
        }
    }
}
</script>

<style scoped>
.login-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #E8F5E9 0%, #FFFFFF 100%);
    display: flex;
    flex-direction: column;
    padding: 0 40rpx;
}

/* Logo区域 */
.logo-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 120rpx;
    padding-bottom: 80rpx;
}

.logo-icon {
    width: 160rpx;
    height: 160rpx;
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8rpx 32rpx rgba(76, 175, 80, 0.3);
    margin-bottom: 30rpx;
}

.logo-text {
    font-size: 80rpx;
}

.app-name {
    font-size: 44rpx;
    font-weight: bold;
    color: #333333;
    margin-bottom: 16rpx;
}

.app-slogan {
    font-size: 26rpx;
    color: #666666;
}

/* 表单区域 */
.form-section {
    background: #FFFFFF;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.form-item {
    display: flex;
    align-items: center;
    padding: 24rpx 0;
    border-bottom: 2rpx solid #F5F5F5;
    position: relative;
}

.form-item:last-of-type {
    border-bottom: none;
}

.form-label {
    width: 120rpx;
    font-size: 28rpx;
    color: #333333;
    font-weight: 500;
}

.form-input {
    flex: 1;
    font-size: 28rpx;
    color: #333333;
}

.placeholder-text {
    color: #CCCCCC;
}

.eye-icon {
    font-size: 40rpx;
    padding-left: 20rpx;
}

/* 登录按钮 */
.login-btn {
    width: 100%;
    height: 96rpx;
    line-height: 96rpx;
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    color: #FFFFFF;
    font-size: 32rpx;
    font-weight: 500;
    border-radius: 48rpx;
    margin-top: 50rpx;
    border: none;
    box-shadow: 0 8rpx 24rpx rgba(76, 175, 80, 0.3);
}

.login-btn::after {
    border: none;
}

/* 快速操作 */
.quick-actions {
    display: flex;
    justify-content: center;
    margin-top: 40rpx;
}

.action-text {
    font-size: 26rpx;
    color: #666666;
}

.highlight-text {
    color: #4CAF50;
    font-weight: 500;
}

/* 底部 */
.footer-section {
    flex: 1;
    display: flex;
    align-items: flex-end;
    justify-content: center;
    padding-bottom: 60rpx;
}

.footer-text {
    font-size: 24rpx;
    color: #999999;
}
</style>
