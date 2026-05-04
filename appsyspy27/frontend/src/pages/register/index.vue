<template>
  <view class="register-container">
    <!-- 顶部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>←</text>
      </view>
      <text class="nav-title">注册账号</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 表单区域 -->
    <view class="form-section">
      <view class="form-item">
        <text class="form-label">用户名</text>
        <view class="input-wrapper">
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="请输入用户名（2-50字符）" 
            class="input-field"
          />
        </view>
      </view>

      <view class="form-item">
        <text class="form-label">密码</text>
        <view class="input-wrapper">
          <input 
            v-model="form.password" 
            :password="!showPassword" 
            placeholder="请输入密码（6-100字符）" 
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

      <view class="form-item">
        <text class="form-label">确认密码</text>
        <view class="input-wrapper">
          <input 
            v-model="form.confirmPassword" 
            :password="!showConfirmPassword" 
            placeholder="请再次输入密码" 
            class="input-field"
          />
          <text 
            class="toggle-password" 
            @click="showConfirmPassword = !showConfirmPassword"
          >
            {{ showConfirmPassword ? '🙈' : '👁️' }}
          </text>
        </view>
      </view>

      <view class="form-item">
        <text class="form-label">真实姓名（可选）</text>
        <view class="input-wrapper">
          <input 
            v-model="form.realName" 
            type="text" 
            placeholder="请输入真实姓名" 
            class="input-field"
          />
        </view>
      </view>

      <view class="form-item">
        <text class="form-label">手机号（可选）</text>
        <view class="input-wrapper">
          <input 
            v-model="form.phone" 
            type="number" 
            placeholder="请输入手机号" 
            class="input-field"
            maxlength="11"
          />
        </view>
      </view>

      <button class="register-btn" :loading="loading" @click="handleRegister">
        注册
      </button>

      <view class="login-link">
        <text>已有账号？</text>
        <text class="link-text" @click="goToLogin">立即登录</text>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { auth } from "@/api";
import { showSuccess, showError } from "@/utils";

const form = reactive({
  username: "",
  password: "",
  confirmPassword: "",
  realName: "",
  phone: ""
});

const loading = ref(false);
const showPassword = ref(false);
const showConfirmPassword = ref(false);

/**
 * 返回上一页
 */
function goBack() {
  uni.navigateBack();
}

/**
 * 跳转到登录页
 */
function goToLogin() {
  uni.navigateBack();
}

/**
 * 处理注册
 */
async function handleRegister() {
  // 验证表单
  if (!form.username.trim()) {
    showError("请输入用户名");
    return;
  }
  if (form.username.length < 2 || form.username.length > 50) {
    showError("用户名长度为2-50字符");
    return;
  }
  if (!form.password.trim()) {
    showError("请输入密码");
    return;
  }
  if (form.password.length < 6 || form.password.length > 100) {
    showError("密码长度为6-100字符");
    return;
  }
  if (form.password !== form.confirmPassword) {
    showError("两次输入的密码不一致");
    return;
  }

  loading.value = true;

  try {
    const res = await auth.register({
      username: form.username.trim(),
      password: form.password.trim(),
      real_name: form.realName.trim() || undefined,
      phone: form.phone.trim() || undefined
    });

    // 保存登录状态
    auth.saveLoginState(res.data.access_token, res.data.user);

    showSuccess("注册成功");

    // 跳转到首页
    setTimeout(() => {
      uni.switchTab({
        url: "/pages/tabbar/home/index"
      });
    }, 500);
  } catch (err) {
    console.error("注册失败:", err);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: #F5F5F5;
}

.nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 88rpx;
  background: #fff;
  padding: 0 30rpx;
  box-sizing: border-box;
  border-bottom: 1rpx solid #F0F0F0;
}

.nav-back {
  width: 60rpx;
  height: 60rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  color: #333;
}

.nav-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.nav-placeholder {
  width: 60rpx;
}

.form-section {
  padding: 40rpx;
}

.form-item {
  margin-bottom: 40rpx;
}

.form-label {
  display: block;
  font-size: 28rpx;
  color: #333;
  margin-bottom: 16rpx;
}

.input-wrapper {
  display: flex;
  align-items: center;
  height: 96rpx;
  background: #fff;
  border-radius: 16rpx;
  padding: 0 30rpx;
  border: 2rpx solid #E8E8E8;
}

.input-wrapper:focus-within {
  border-color: #4A90D9;
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

.register-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  border-radius: 48rpx;
  margin-top: 60rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border: none;
}

.register-btn:active {
  opacity: 0.8;
}

.login-link {
  display: flex;
  justify-content: center;
  margin-top: 40rpx;
  font-size: 28rpx;
  color: #666;
}

.link-text {
  color: #4A90D9;
  margin-left: 10rpx;
}
</style>
