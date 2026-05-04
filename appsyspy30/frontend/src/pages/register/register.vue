<template>
    <view class="register-container">
        <!-- 自定义导航栏 -->
        <view class="custom-nav">
            <view class="nav-back" @click="goBack">
                <text class="back-icon">‹</text>
            </view>
            <text class="nav-title">注册账号</text>
            <view class="nav-placeholder"></view>
        </view>

        <!-- 表单区域 -->
        <view class="form-section">
            <!-- 用户名 -->
            <view class="form-item">
                <text class="form-label">用户名</text>
                <input 
                    class="form-input" 
                    type="text" 
                    placeholder="3-50个字符"
                    v-model="registerForm.username"
                    placeholder-class="placeholder-text"
                />
            </view>

            <!-- 邮箱 -->
            <view class="form-item">
                <text class="form-label">邮箱</text>
                <input 
                    class="form-input" 
                    type="text" 
                    placeholder="请输入邮箱地址"
                    v-model="registerForm.email"
                    placeholder-class="placeholder-text"
                />
            </view>

            <!-- 昵称 -->
            <view class="form-item">
                <text class="form-label">昵称</text>
                <input 
                    class="form-input" 
                    type="text" 
                    placeholder="请输入昵称（可选）"
                    v-model="registerForm.nickname"
                    placeholder-class="placeholder-text"
                />
            </view>

            <!-- 密码 -->
            <view class="form-item">
                <text class="form-label">密码</text>
                <input 
                    class="form-input" 
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="至少6个字符"
                    v-model="registerForm.password"
                    placeholder-class="placeholder-text"
                />
                <text 
                    class="eye-icon" 
                    @click="showPassword = !showPassword"
                >
                    {{ showPassword ? '👁️' : '🙈' }}
                </text>
            </view>

            <!-- 确认密码 -->
            <view class="form-item">
                <text class="form-label">确认密码</text>
                <input 
                    class="form-input" 
                    :type="showConfirmPassword ? 'text' : 'password'"
                    placeholder="请再次输入密码"
                    v-model="confirmPassword"
                    placeholder-class="placeholder-text"
                />
                <text 
                    class="eye-icon" 
                    @click="showConfirmPassword = !showConfirmPassword"
                >
                    {{ showConfirmPassword ? '👁️' : '🙈' }}
                </text>
            </view>

            <!-- 邀请码 -->
            <view class="form-item">
                <text class="form-label">邀请码</text>
                <input 
                    class="form-input" 
                    type="text" 
                    placeholder="邀请码（可选）"
                    v-model="registerForm.invite_code"
                    placeholder-class="placeholder-text"
                />
            </view>

            <!-- 注册按钮 -->
            <button 
                class="register-btn" 
                :loading="loading"
                @click="handleRegister"
            >
                注册
            </button>

            <!-- 登录链接 -->
            <view class="login-link">
                <text class="link-text" @click="goToLogin">
                    已有账号？<text class="highlight-text">立即登录</text>
                </text>
            </view>
        </view>
    </view>
</template>

<script>
import { authApi } from '@/api/auth'
import { setToken, setUserInfo, navigateToHome } from '@/utils/auth'

export default {
    data() {
        return {
            registerForm: {
                username: '',
                email: '',
                nickname: '',
                password: '',
                invite_code: ''
            },
            confirmPassword: '',
            showPassword: false,
            showConfirmPassword: false,
            loading: false
        }
    },
    methods: {
        /**
         * 返回上一页
         */
        goBack() {
            uni.navigateBack()
        },

        /**
         * 跳转到登录页
         */
        goToLogin() {
            uni.navigateBack()
        },

        /**
         * 处理注册
         */
        async handleRegister() {
            // 表单验证
            if (!this.registerForm.username.trim()) {
                uni.showToast({
                    title: '请输入用户名',
                    icon: 'none'
                })
                return
            }

            if (this.registerForm.username.length < 3) {
                uni.showToast({
                    title: '用户名至少3个字符',
                    icon: 'none'
                })
                return
            }

            if (!this.registerForm.email.trim()) {
                uni.showToast({
                    title: '请输入邮箱',
                    icon: 'none'
                })
                return
            }

            // 简单的邮箱格式验证
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
            if (!emailRegex.test(this.registerForm.email)) {
                uni.showToast({
                    title: '请输入正确的邮箱格式',
                    icon: 'none'
                })
                return
            }

            if (!this.registerForm.password.trim()) {
                uni.showToast({
                    title: '请输入密码',
                    icon: 'none'
                })
                return
            }

            if (this.registerForm.password.length < 6) {
                uni.showToast({
                    title: '密码至少6个字符',
                    icon: 'none'
                })
                return
            }

            if (this.registerForm.password !== this.confirmPassword) {
                uni.showToast({
                    title: '两次密码输入不一致',
                    icon: 'none'
                })
                return
            }

            this.loading = true

            try {
                const res = await authApi.register(this.registerForm)

                // 保存Token和用户信息
                setToken(res.access_token)
                setUserInfo(res.user)

                uni.showToast({
                    title: '注册成功',
                    icon: 'success'
                })

                // 跳转到首页
                setTimeout(() => {
                    navigateToHome()
                }, 1000)

            } catch (error) {
                console.error('注册失败:', error)
            } finally {
                this.loading = false
            }
        }
    }
}
</script>

<style scoped>
.register-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #E8F5E9 0%, #FFFFFF 100%);
}

/* 自定义导航栏 */
.custom-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 88rpx;
    padding-top: var(--status-bar-height);
    background: #FFFFFF;
    position: sticky;
    top: 0;
    z-index: 100;
}

.nav-back {
    width: 88rpx;
    height: 88rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.back-icon {
    font-size: 48rpx;
    color: #333333;
    font-weight: bold;
}

.nav-title {
    font-size: 34rpx;
    font-weight: 500;
    color: #333333;
}

.nav-placeholder {
    width: 88rpx;
}

/* 表单区域 */
.form-section {
    padding: 40rpx;
}

.form-item {
    display: flex;
    align-items: center;
    padding: 28rpx 0;
    border-bottom: 2rpx solid #F5F5F5;
    position: relative;
}

.form-item:last-of-type {
    border-bottom: none;
}

.form-label {
    width: 160rpx;
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

/* 注册按钮 */
.register-btn {
    width: 100%;
    height: 96rpx;
    line-height: 96rpx;
    background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
    color: #FFFFFF;
    font-size: 32rpx;
    font-weight: 500;
    border-radius: 48rpx;
    margin-top: 60rpx;
    border: none;
    box-shadow: 0 8rpx 24rpx rgba(76, 175, 80, 0.3);
}

.register-btn::after {
    border: none;
}

/* 登录链接 */
.login-link {
    display: flex;
    justify-content: center;
    margin-top: 40rpx;
}

.link-text {
    font-size: 26rpx;
    color: #666666;
}

.highlight-text {
    color: #4CAF50;
    font-weight: 500;
}
</style>
