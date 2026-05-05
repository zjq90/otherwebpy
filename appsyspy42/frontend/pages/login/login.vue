<template>
    <view class="login-container">
        <view class="status-bar"></view>
        
        <view class="login-header">
            <view class="logo">
                <text class="logo-text">库存管理系统</text>
            </view>
            <text class="subtitle">原材料库存智能管理平台</text>
        </view>
        
        <view class="login-form">
            <view class="form-item">
                <text class="label">用户名</text>
                <input 
                    class="input" 
                    type="text" 
                    placeholder="请输入用户名" 
                    v-model="form.username"
                    placeholder-class="placeholder"
                />
            </view>
            
            <view class="form-item">
                <text class="label">密码</text>
                <input 
                    class="input" 
                    type="password" 
                    placeholder="请输入密码" 
                    v-model="form.password"
                    placeholder-class="placeholder"
                />
            </view>
            
            <button 
                class="login-btn" 
                :loading="loading"
                :disabled="loading"
                @click="handleLogin"
            >
                {{ loading ? '登录中...' : '登 录' }}
            </button>
            
            <view class="quick-login">
                <text class="quick-login-title">快捷登录（测试账号）:</text>
                <view class="quick-btns">
                    <button class="quick-btn" @click="quickLogin('admin')">管理员</button>
                    <button class="quick-btn" @click="quickLogin('purchaser')">采购员</button>
                </view>
            </view>
        </view>
        
        <view class="login-footer">
            <text class="copyright">© 2024 库存管理系统</text>
        </view>
    </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
    data() {
        return {
            form: {
                username: '',
                password: ''
            },
            loading: false
        }
    },
    
    methods: {
        async handleLogin() {
            if (!this.form.username.trim()) {
                uni.showToast({ title: '请输入用户名', icon: 'none' })
                return
            }
            if (!this.form.password.trim()) {
                uni.showToast({ title: '请输入密码', icon: 'none' })
                return
            }
            
            this.loading = true
            
            try {
                const res = await this.$api.login(this.form)
                
                uni.setStorageSync(config.tokenKey, res.token)
                uni.setStorageSync(config.userInfoKey, res.user)
                
                uni.showToast({
                    title: '登录成功',
                    icon: 'success'
                })
                
                setTimeout(() => {
                    uni.switchTab({
                        url: '/pages/index/index'
                    })
                }, 1000)
                
            } catch (err) {
                console.error('登录失败:', err)
            } finally {
                this.loading = false
            }
        },
        
        quickLogin(type) {
            if (type === 'admin') {
                this.form.username = 'admin'
                this.form.password = 'admin123'
            } else {
                this.form.username = 'purchaser'
                this.form.password = 'purchaser123'
            }
        }
    }
}
</script>

<style scoped>
.login-container {
    min-height: 100vh;
    background: linear-gradient(180deg, #1677ff 0%, #4096ff 100%);
    display: flex;
    flex-direction: column;
}

.status-bar {
    height: var(--status-bar-height);
}

.login-header {
    padding: 80rpx 40rpx;
    text-align: center;
}

.logo {
    width: 200rpx;
    height: 200rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    margin: 0 auto 30rpx;
    display: flex;
    align-items: center;
    justify-content: center;
}

.logo-text {
    font-size: 48rpx;
    font-weight: bold;
    color: #fff;
}

.subtitle {
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.8);
}

.login-form {
    flex: 1;
    background: #fff;
    border-radius: 40rpx 40rpx 0 0;
    padding: 60rpx 40rpx;
}

.form-item {
    margin-bottom: 40rpx;
}

.label {
    display: block;
    font-size: 28rpx;
    color: #333;
    margin-bottom: 16rpx;
}

.input {
    width: 100%;
    height: 96rpx;
    background: #f5f5f5;
    border-radius: 16rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
}

.placeholder {
    color: #999;
}

.login-btn {
    width: 100%;
    height: 96rpx;
    background: linear-gradient(90deg, #1677ff 0%, #4096ff 100%);
    border-radius: 48rpx;
    border: none;
    color: #fff;
    font-size: 32rpx;
    font-weight: 500;
    margin-top: 20rpx;
}

.login-btn::after {
    border: none;
}

.quick-login {
    margin-top: 60rpx;
}

.quick-login-title {
    font-size: 26rpx;
    color: #999;
    display: block;
    text-align: center;
    margin-bottom: 24rpx;
}

.quick-btns {
    display: flex;
    justify-content: center;
    gap: 24rpx;
}

.quick-btn {
    width: 200rpx;
    height: 72rpx;
    background: #e6f4ff;
    border-radius: 36rpx;
    border: none;
    color: #1677ff;
    font-size: 26rpx;
}

.quick-btn::after {
    border: none;
}

.login-footer {
    padding: 40rpx;
    text-align: center;
    background: #fff;
}

.copyright {
    font-size: 24rpx;
    color: #999;
}
</style>
