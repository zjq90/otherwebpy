<template>
  <view class="login-container">
    <!-- 顶部Logo区域 -->
    <view class="logo-section">
      <view class="logo-icon">
        <text class="logo-text">会员</text>
      </view>
      <text class="app-title">会员管理系统</text>
      <text class="app-subtitle">便捷管理，轻松消费</text>
    </view>

    <!-- 登录表单 -->
    <view class="form-section">
      <view class="form-item">
        <view class="input-wrapper">
          <text class="input-icon">👤</text>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="请输入用户名" 
            class="input-field"
          />
        </view>
      </view>

      <view class="form-item">
        <view class="input-wrapper">
          <text class="input-icon">🔒</text>
          <input 
            v-model="form.password" 
            :password="!showPassword" 
            placeholder="请输入密码" 
            class="input-field"
          />
          <text 
            class="toggle-password" 
            @click="showPassword = !showPassword"
          >
            {{ showPassword ? '🙈' : '👁️' }}
          </text>
        </view>
      </view>

      <button class="login-btn" :loading="loading" @click="handleLogin">
        登录
      </button>

      <view class="other-login">
        <text class="other-title">其他登录方式</text>
        <view class="login-methods">
          <view class="login-method" @click="handleWechatLogin">
            <view class="method-icon wechat-icon">
              <text>💬</text>
            </view>
            <text class="method-text">微信登录</text>
          </view>
        </view>
      </view>

      <view class="register-link">
        <text>还没有账号？</text>
        <text class="link-text" @click="goToRegister">立即注册</text>
      </view>
    </view>

    <!-- 测试账号提示 -->
    <view class="test-account" v-if="showTestAccount">
      <view class="test-header">
        <text class="test-title">测试账号</text>
        <text class="test-close" @click="showTestAccount = false">×</text>
      </view>
      <view class="test-item">
        <text class="test-label">用户名：</text>
        <text class="test-value">testuser1</text>
      </view>
      <view class="test-item">
        <text class="test-label">密码：</text>
        <text class="test-value">123456</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { onLoad } from "@dcloudio/uni-app";
import { auth } from "@/api";
import { showSuccess, showError } from "@/utils";

const form = reactive({
  username: "",
  password: ""
});

const loading = ref(false);
const showPassword = ref(false);
const showTestAccount = ref(true);

onLoad(() => {
  // 检查是否已登录
  if (auth.isLoggedIn()) {
    uni.switchTab({
      url: "/pages/tabbar/home/index"
    });
  }
});

/**
 * 处理登录
 */
async function handleLogin() {
  if (!form.username.trim()) {
    showError("请输入用户名");
    return;
  }
  if (!form.password.trim()) {
    showError("请输入密码");
    return;
  }

  loading.value = true;

  try {
    const res = await auth.login({
      username: form.username.trim(),
      password: form.password.trim()
    });

    // 保存登录状态
    auth.saveLoginState(res.data.access_token, res.data.user);

    showSuccess("登录成功");

    // 跳转到首页
    setTimeout(() => {
      uni.switchTab({
        url: "/pages/tabbar/home/index"
      });
    }, 500);
  } catch (err) {
    console.error("登录失败:", err);
  } finally {
    loading.value = false;
  }
}

/**
 * 微信登录（模拟）
 */
async function handleWechatLogin() {
  // 模拟微信登录，使用随机code
  const mockCode = "mock_wechat_code_" + Date.now();
  
  loading.value = true;

  try {
    const res = await auth.wechatLogin(mockCode);

    // 保存登录状态
    auth.saveLoginState(res.data.access_token, res.data.user);

    showSuccess("微信登录成功");

    setTimeout(() => {
      uni.switchTab({
        url: "/pages/tabbar/home/index"
      });
    }, 500);
  } catch (err) {
    console.error("微信登录失败:", err);
  } finally {
    loading.value = false;
  }
}

/**
 * 跳转到注册页
 */
function goToRegister() {
  uni.navigateTo({
    url: "/pages/register/index"
  });
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  background: linear-gradient(180deg, #4A90D9 0%, #6BA8E0 50%, #F5F5F5 50%);
  padding: 0 40rpx;
  box-sizing: border-box;
}

.logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 100rpx;
  padding-bottom: 80rpx;
}

.logo-icon {
  width: 140rpx;
  height: 140rpx;
  border-radius: 50%;
  background: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  margin-bottom: 30rpx;
}

.logo-text {
  font-size: 48rpx;
  font-weight: bold;
  color: #4A90D9;
}

.app-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 10rpx;
}

.app-subtitle {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.form-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.form-item {
  margin-bottom: 30rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  height: 100rpx;
  background: #F8F9FA;
  border-radius: 16rpx;
  padding: 0 30rpx;
}

.input-icon {
  font-size: 36rpx;
  margin-right: 20rpx;
}

.input-field {
  flex: 1;
  height: 100%;
  font-size: 30rpx;
  color: #333;
}

.toggle-password {
  font-size: 36rpx;
  padding: 10rpx;
}

.login-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  border-radius: 48rpx;
  margin-top: 40rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border: none;
}

.login-btn:active {
  opacity: 0.8;
}

.other-login {
  margin-top: 60rpx;
}

.other-title {
  display: block;
  text-align: center;
  font-size: 26rpx;
  color: #999;
  margin-bottom: 30rpx;
}

.login-methods {
  display: flex;
  justify-content: center;
}

.login-method {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.method-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 16rpx;
}

.wechat-icon {
  background: #07C160;
}

.wechat-icon text {
  font-size: 48rpx;
}

.method-text {
  font-size: 24rpx;
  color: #666;
}

.register-link {
  display: flex;
  justify-content: center;
  margin-top: 60rpx;
  font-size: 28rpx;
  color: #666;
}

.link-text {
  color: #4A90D9;
  margin-left: 10rpx;
}

.test-account {
  background: rgba(74, 144, 217, 0.1);
  border: 2rpx solid rgba(74, 144, 217, 0.3);
  border-radius: 16rpx;
  padding: 24rpx;
  margin-top: 40rpx;
}

.test-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.test-title {
  font-size: 26rpx;
  color: #4A90D9;
  font-weight: bold;
}

.test-close {
  font-size: 36rpx;
  color: #999;
}

.test-item {
  display: flex;
  font-size: 24rpx;
  color: #666;
  margin-bottom: 8rpx;
}

.test-label {
  color: #999;
}

.test-value {
  color: #4A90D9;
  font-family: monospace;
}
</style>
