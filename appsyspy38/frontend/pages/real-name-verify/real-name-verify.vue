<template>
    <view class="verify-container">
        <view class="status-bar-placeholder"></view>
        
        <!-- 顶部导航 -->
        <view class="header">
            <text class="header-title">实名认证</text>
        </view>

        <!-- 说明区域 -->
        <view class="info-section">
            <view class="info-icon">
                <text class="icon-text">!</text>
            </view>
            <view class="info-text">
                <text class="info-title">首次登录需要完成实名认证</text>
                <text class="info-desc">实名认证是保障您账户安全的必要步骤，请如实填写您的真实姓名和身份证号码</text>
            </view>
        </view>

        <!-- 表单区域 -->
        <view class="form-section">
            <view class="input-group">
                <text class="input-label">真实姓名</text>
                <input 
                    class="input-field" 
                    type="text" 
                    placeholder="请输入您的真实姓名"
                    v-model="form.realName"
                />
            </view>

            <view class="input-group">
                <text class="input-label">身份证号码</text>
                <input 
                    class="input-field" 
                    type="text" 
                    placeholder="请输入18位身份证号码"
                    maxlength="18"
                    v-model="form.idCard"
                />
            </view>

            <view class="input-group">
                <text class="input-label">确认身份证号码</text>
                <input 
                    class="input-field" 
                    type="text" 
                    placeholder="请再次输入身份证号码"
                    maxlength="18"
                    v-model="form.confirmIdCard"
                />
            </view>
        </view>

        <!-- 协议勾选 -->
        <view class="agreement-section">
            <view 
                class="checkbox" 
                :class="{ checked: agreed }"
                @click="agreed = !agreed"
            >
                <text v-if="agreed" class="check-icon">✓</text>
            </view>
            <text class="agreement-text">
                我已阅读并同意
                <text class="agreement-link">《用户协议》</text>
                和
                <text class="agreement-link">《隐私政策》</text>
            </text>
        </view>

        <!-- 提交按钮 -->
        <view class="submit-section">
            <view 
                class="btn-primary submit-btn" 
                :class="{ disabled: isLoading || !agreed }"
                @click="handleSubmit"
            >
                {{ isLoading ? '提交中...' : '完成认证' }}
            </view>
        </view>

        <!-- 跳过按钮（仅开发测试用） -->
        <view class="skip-section">
            <text class="skip-text" @click="handleSkip">跳过（仅开发测试）</text>
        </view>
    </view>
</template>

<script>
import { realNameVerify } from '@/api/auth.js'

export default {
    data() {
        return {
            form: {
                realName: '',
                idCard: '',
                confirmIdCard: ''
            },
            agreed: false,
            isLoading: false
        }
    },
    methods: {
        // 简单的身份证号验证
        validateIdCard(idCard) {
            const reg = /(^\d{18}$)|(^\d{17}(\d|X|x)$)/
            return reg.test(idCard)
        },

        // 提交实名认证
        async handleSubmit() {
            if (this.isLoading) return
            if (!this.agreed) {
                uni.showToast({
                    title: '请先同意用户协议',
                    icon: 'none'
                })
                return
            }

            // 表单验证
            if (!this.form.realName) {
                uni.showToast({ title: '请输入真实姓名', icon: 'none' })
                return
            }
            if (!this.form.idCard) {
                uni.showToast({ title: '请输入身份证号码', icon: 'none' })
                return
            }
            if (!this.validateIdCard(this.form.idCard)) {
                uni.showToast({ title: '请输入正确的身份证号码', icon: 'none' })
                return
            }
            if (this.form.idCard !== this.form.confirmIdCard) {
                uni.showToast({ title: '两次输入的身份证号码不一致', icon: 'none' })
                return
            }

            this.isLoading = true

            try {
                const res = await realNameVerify(this.form.realName, this.form.idCard)
                
                // 更新本地存储的用户信息
                const userInfo = uni.getStorageSync('userInfo')
                userInfo.real_name = this.form.realName
                userInfo.id_card = this.form.idCard
                userInfo.is_verified = true
                userInfo.is_first_login = false
                uni.setStorageSync('userInfo', userInfo)

                uni.showToast({
                    title: '认证成功',
                    icon: 'success'
                })

                setTimeout(() => {
                    uni.switchTab({
                        url: '/pages/tabbar/index/index'
                    })
                }, 1500)

            } catch (err) {
                console.error('实名认证失败:', err)
            } finally {
                this.isLoading = false
            }
        },

        // 跳过认证（仅开发测试用）
        handleSkip() {
            uni.showModal({
                title: '提示',
                content: '确定要跳过实名认证吗？部分功能可能无法使用。',
                success: (res) => {
                    if (res.confirm) {
                        const userInfo = uni.getStorageSync('userInfo')
                        userInfo.is_first_login = false
                        uni.setStorageSync('userInfo', userInfo)
                        
                        uni.switchTab({
                            url: '/pages/tabbar/index/index'
                        })
                    }
                }
            })
        }
    }
}
</script>

<style scoped>
.verify-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding: 0 40rpx;
}

.status-bar-placeholder {
    height: var(--status-bar-height);
}

.header {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32rpx 0;
    position: relative;
}

.header-title {
    font-size: 34rpx;
    font-weight: 600;
    color: #333333;
}

.info-section {
    display: flex;
    background: #e6f7ff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 32rpx;
}

.info-icon {
    width: 48rpx;
    height: 48rpx;
    background: #1890ff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16rpx;
    flex-shrink: 0;
}

.icon-text {
    font-size: 28rpx;
    color: #ffffff;
    font-weight: bold;
}

.info-text {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.info-title {
    font-size: 28rpx;
    color: #1890ff;
    font-weight: 500;
    margin-bottom: 8rpx;
}

.info-desc {
    font-size: 24rpx;
    color: #666666;
    line-height: 1.6;
}

.form-section {
    background: #ffffff;
    border-radius: 16rpx;
    padding: 32rpx;
    margin-bottom: 32rpx;
}

.input-group {
    margin-bottom: 32rpx;
}

.input-group:last-child {
    margin-bottom: 0;
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
    background: #f5f5f5;
    border-radius: 12rpx;
    padding: 0 24rpx;
    font-size: 30rpx;
    color: #333333;
}

.agreement-section {
    display: flex;
    align-items: flex-start;
    padding: 0 8rpx;
    margin-bottom: 48rpx;
}

.checkbox {
    width: 36rpx;
    height: 36rpx;
    border: 2rpx solid #d9d9d9;
    border-radius: 8rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16rpx;
    margin-top: 4rpx;
    flex-shrink: 0;
}

.checkbox.checked {
    background: #1890ff;
    border-color: #1890ff;
}

.check-icon {
    font-size: 24rpx;
    color: #ffffff;
}

.agreement-text {
    font-size: 26rpx;
    color: #666666;
    line-height: 1.6;
}

.agreement-link {
    color: #1890ff;
}

.submit-section {
    margin-bottom: 32rpx;
}

.submit-btn {
    width: 100%;
    padding: 28rpx 0;
    font-size: 32rpx;
    font-weight: 500;
}

.submit-btn.disabled {
    opacity: 0.6;
}

.skip-section {
    text-align: center;
    padding: 20rpx;
}

.skip-text {
    font-size: 24rpx;
    color: #999999;
}
</style>
