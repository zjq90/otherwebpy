<template>
    <view class="login-container">
        <!-- 顶部状态栏占位 -->
        <view class="status-bar-placeholder"></view>
        
        <!-- Logo区域 -->
        <view class="logo-section">
            <view class="logo-icon">
                <text class="logo-text">管</text>
            </view>
            <text class="app-name">多角色管理系统</text>
            <text class="app-desc">高效、安全、便捷的业务管理平台</text>
        </view>

        <!-- 登录方式切换 -->
        <view class="login-tabs">
            <view 
                class="tab-item" 
                :class="{ active: loginType === 'password' }"
                @click="loginType = 'password'"
            >
                账号密码登录
            </view>
            <view 
                class="tab-item" 
                :class="{ active: loginType === 'phone' }"
                @click="loginType = 'phone'"
            >
                手机号登录
            </view>
        </view>

        <!-- 登录表单 -->
        <view class="login-form">
            <!-- 账号密码登录表单 -->
            <view v-if="loginType === 'password'" class="form-content">
                <view class="input-group">
                    <text class="input-label">用户名</text>
                    <input 
                        class="input-field" 
                        type="text" 
                        placeholder="请输入用户名"
                        v-model="form.username"
                    />
                </view>
                <view class="input-group">
                    <text class="input-label">密码</text>
                    <input 
                        class="input-field" 
                        type="password" 
                        placeholder="请输入密码"
                        v-model="form.password"
                    />
                </view>
            </view>

            <!-- 手机号登录表单 -->
            <view v-else class="form-content">
                <view class="input-group">
                    <text class="input-label">手机号</text>
                    <input 
                        class="input-field" 
                        type="number" 
                        placeholder="请输入手机号"
                        maxlength="11"
                        v-model="form.phone"
                    />
                </view>
                <view class="input-group code-group">
                    <view class="code-input-wrapper">
                        <text class="input-label">验证码</text>
                        <input 
                            class="input-field code-input" 
                            type="number" 
                            placeholder="请输入验证码"
                            maxlength="6"
                            v-model="form.code"
                        />
                    </view>
                    <view 
                        class="send-code-btn" 
                        :class="{ disabled: countdown > 0 }"
                        @click="sendCode"
                    >
                        {{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}
                    </view>
                </view>
            </view>

            <!-- 登录按钮 -->
            <view class="login-btn-wrapper">
                <view 
                    class="btn-primary login-btn" 
                    :class="{ disabled: isLoading }"
                    @click="handleLogin"
                >
                    {{ isLoading ? '登录中...' : '登 录' }}
                </view>
            </view>

            <!-- 测试账号提示 -->
            <view class="test-account-tip">
                <text class="tip-text">测试账号：</text>
                <text class="tip-text">admin / admin123 (管理员)</text>
                <text class="tip-text">operator1 / 123456 (操作员)</text>
            </view>
        </view>

        <!-- 底部版权 -->
        <view class="footer">
            <text class="copyright">© 2026 多角色管理系统 v1.0.0</text>
        </view>
    </view>
</template>

<script>
import { loginWithPassword, loginWithPhone, sendCode as sendCodeApi } from '@/api/auth.js'

export default {
    data() {
        return {
            loginType: 'password', // password: 账号密码登录, phone: 手机号登录
            form: {
                username: '',
                password: '',
                phone: '',
                code: ''
            },
            isLoading: false,
            countdown: 0
        }
    },
    methods: {
        // 发送验证码
        async sendCode() {
            if (this.countdown > 0) return
            
            if (!this.form.phone || this.form.phone.length !== 11) {
                uni.showToast({
                    title: '请输入正确的手机号',
                    icon: 'none'
                })
                return
            }

            try {
                const res = await sendCodeApi(this.form.phone)
                uni.showToast({
                    title: `验证码已发送: ${res.data?.code || '开发环境已显示'}`,
                    icon: 'none'
                })
                
                // 开始倒计时
                this.countdown = 60
                const timer = setInterval(() => {
                    this.countdown--
                    if (this.countdown <= 0) {
                        clearInterval(timer)
                    }
                }, 1000)
            } catch (err) {
                console.error('发送验证码失败:', err)
            }
        },

        // 处理登录
        async handleLogin() {
            if (this.isLoading) return

            // 表单验证
            if (this.loginType === 'password') {
                if (!this.form.username) {
                    uni.showToast({ title: '请输入用户名', icon: 'none' })
                    return
                }
                if (!this.form.password) {
                    uni.showToast({ title: '请输入密码', icon: 'none' })
                    return
                }
            } else {
                if (!this.form.phone || this.form.phone.length !== 11) {
                    uni.showToast({ title: '请输入正确的手机号', icon: 'none' })
                    return
                }
                if (!this.form.code) {
                    uni.showToast({ title: '请输入验证码', icon: 'none' })
                    return
                }
            }

            this.isLoading = true

            try {
                let loginRes
                
                if (this.loginType === 'password') {
                    loginRes = await loginWithPassword(this.form.username, this.form.password)
                } else {
                    loginRes = await loginWithPhone(this.form.phone, this.form.code)
                }

                // 保存登录信息
                uni.setStorageSync('token', loginRes.access_token)
                uni.setStorageSync('userInfo', loginRes.user)

                // 跳转到对应页面
                if (loginRes.is_first_login) {
                    uni.redirectTo({
                        url: '/pages/real-name-verify/real-name-verify'
                    })
                } else {
                    uni.switchTab({
                        url: '/pages/tabbar/index/index'
                    })
                }

                uni.showToast({
                    title: '登录成功',
                    icon: 'success'
                })

            } catch (err) {
                console.error('登录失败:', err)
            } finally {
                this.isLoading = false
            }
        }
    }
}
</script>

<style scoped>
.login-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #1890ff 0%, #40a9ff 50%, #f5f5f5 50%, #f5f5f5 100%);
    display: flex;
    flex-direction: column;
    padding: 0 40rpx;
}

.status-bar-placeholder {
    height: var(--status-bar-height);
}

.logo-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 60rpx;
    padding-bottom: 80rpx;
}

.logo-icon {
    width: 160rpx;
    height: 160rpx;
    background: #ffffff;
    border-radius: 32rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8rpx 32rpx rgba(24, 144, 255, 0.3);
    margin-bottom: 32rpx;
}

.logo-text {
    font-size: 72rpx;
    font-weight: bold;
    color: #1890ff;
}

.app-name {
    font-size: 36rpx;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 16rpx;
}

.app-desc {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
}

.login-tabs {
    display: flex;
    background: #ffffff;
    border-radius: 16rpx;
    padding: 8rpx;
    margin-bottom: 32rpx;
}

.tab-item {
    flex: 1;
    text-align: center;
    padding: 20rpx 0;
    font-size: 28rpx;
    color: #666666;
    border-radius: 12rpx;
    transition: all 0.3s;
}

.tab-item.active {
    background: #1890ff;
    color: #ffffff;
    font-weight: 500;
}

.login-form {
    background: #ffffff;
    border-radius: 24rpx;
    padding: 40rpx;
    box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.form-content {
    margin-bottom: 40rpx;
}

.input-group {
    margin-bottom: 32rpx;
}

.input-label {
    display: block;
    font-size: 26rpx;
    color: #666666;
    margin-bottom: 12rpx;
}

.input-field {
    width: 100%;
    height: 88rpx;
    background: #f5f5f5;
    border-radius: 12rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
    color: #333333;
}

.code-group {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}

.code-input-wrapper {
    flex: 1;
    margin-right: 24rpx;
}

.code-input {
    width: 100%;
}

.send-code-btn {
    width: 240rpx;
    height: 88rpx;
    background: #e6f7ff;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26rpx;
    color: #1890ff;
}

.send-code-btn.disabled {
    background: #f5f5f5;
    color: #999999;
}

.login-btn-wrapper {
    margin-top: 40rpx;
}

.login-btn {
    width: 100%;
    padding: 28rpx 0;
    font-size: 32rpx;
    font-weight: 500;
}

.login-btn.disabled {
    opacity: 0.6;
}

.test-account-tip {
    margin-top: 40rpx;
    padding: 24rpx;
    background: #fffbe6;
    border-radius: 12rpx;
}

.tip-text {
    display: block;
    font-size: 22rpx;
    color: #faad14;
    line-height: 1.8;
}

.footer {
    margin-top: auto;
    padding: 40rpx 0;
    text-align: center;
}

.copyright {
    font-size: 22rpx;
    color: #999999;
}
</style>
