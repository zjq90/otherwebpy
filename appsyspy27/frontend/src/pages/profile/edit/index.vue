<template>
  <view class="edit-profile-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">编辑资料</text>
      <view class="nav-save" @click="handleSave">
        <text>保存</text>
      </view>
    </view>

    <!-- 表单区域 -->
    <view class="form-section">
      <!-- 头像上传 -->
      <view class="avatar-section">
        <text class="section-label">头像</text>
        <view class="avatar-wrapper" @click="chooseAvatar">
          <view class="avatar-preview" v-if="form.avatar">
            <image :src="form.avatar" mode="aspectFill" class="avatar-img" />
          </view>
          <view class="avatar-placeholder" v-else>
            <text>📷</text>
          </view>
          <view class="avatar-change">
            <text>更换</text>
          </view>
        </view>
      </view>

      <!-- 表单列表 -->
      <view class="form-list">
        <view class="form-item">
          <text class="form-label">用户名</text>
          <text class="form-value">{{ form.username }}</text>
        </view>

        <view class="form-item">
          <text class="form-label">真实姓名</text>
          <input 
            v-model="form.real_name" 
            type="text" 
            placeholder="请输入真实姓名" 
            class="form-input"
          />
        </view>

        <view class="form-item">
          <text class="form-label">手机号</text>
          <view class="phone-wrapper">
            <input 
              v-model="form.phone" 
              type="number" 
              placeholder="请输入手机号" 
              class="form-input phone-input"
              maxlength="11"
            />
            <view class="phone-bind" v-if="form.phone && isPhoneBound">
              <text class="bound-text">已绑定</text>
            </view>
            <view class="phone-bind" v-else-if="form.phone">
              <text class="bind-btn" @click.stop="handleBindPhone">去绑定</text>
            </view>
          </view>
        </view>

        <view class="form-item">
          <text class="form-label">邮箱</text>
          <input 
            v-model="form.email" 
            type="text" 
            placeholder="请输入邮箱地址" 
            class="form-input"
          />
        </view>

        <view class="form-item">
          <text class="form-label">微信绑定</text>
          <view class="wechat-wrapper">
            <text class="wechat-status" :class="{ bound: isWechatBound }">
              {{ isWechatBound ? '已绑定微信' : '未绑定微信' }}
            </text>
            <text class="wechat-action" @click="handleBindWechat">
              {{ isWechatBound ? '解绑' : '绑定' }}
            </text>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部保存按钮 -->
    <view class="footer-section">
      <button class="save-btn" :loading="loading" @click="handleSave">
        保存修改
      </button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onLoad, getCurrentInstance } from "vue";
import { auth } from "@/api";
import { showSuccess, showError, showConfirm } from "@/utils";

const loading = ref(false);
const isPhoneBound = ref(false);
const isWechatBound = ref(false);

const form = reactive({
  username: "",
  real_name: "",
  phone: "",
  email: "",
  avatar: ""
});

/**
 * 加载用户信息
 */
async function loadUserInfo() {
  try {
    const res = await auth.getCurrentUser();
    const user = res.data;
    
    form.username = user.username || "";
    form.real_name = user.real_name || "";
    form.phone = user.phone || "";
    form.email = user.email || "";
    form.avatar = user.avatar || "";
    
    isPhoneBound.value = !!user.phone;
    isWechatBound.value = !!user.wechat_openid;
  } catch (err) {
    console.error("加载用户信息失败:", err);
  }
}

/**
 * 返回上一页
 */
function goBack() {
  uni.navigateBack();
}

/**
 * 选择头像
 */
function chooseAvatar() {
  uni.chooseImage({
    count: 1,
    sizeType: ["compressed"],
    sourceType: ["album", "camera"],
    success: (res) => {
      form.avatar = res.tempFilePaths[0];
    }
  });
}

/**
 * 绑定手机
 */
async function handleBindPhone() {
  uni.showToast({ title: "手机绑定功能开发中", icon: "none" });
}

/**
 * 绑定微信
 */
async function handleBindWechat() {
  if (isWechatBound.value) {
    try {
      const confirmed = await showConfirm("确定要解绑微信吗？");
      if (confirmed) {
        uni.showToast({ title: "解绑功能开发中", icon: "none" });
      }
    } catch (err) {
      console.error("解绑微信失败:", err);
    }
  } else {
    uni.showToast({ title: "微信绑定功能开发中", icon: "none" });
  }
}

/**
 * 保存修改
 */
async function handleSave() {
  const updateData: any = {};
  
  if (form.real_name && form.real_name.trim()) {
    updateData.real_name = form.real_name.trim();
  }
  if (form.email && form.email.trim()) {
    updateData.email = form.email.trim();
  }
  if (form.phone && form.phone.trim()) {
    updateData.phone = form.phone.trim();
  }
  if (form.avatar) {
    updateData.avatar = form.avatar;
  }

  if (Object.keys(updateData).length === 0) {
    showError("没有需要保存的修改");
    return;
  }

  loading.value = true;

  try {
    const res = await auth.updateCurrentUser(updateData);
    
    // 更新本地缓存的用户信息
    const localUser = auth.getLocalUserInfo();
    if (localUser) {
      Object.assign(localUser, updateData);
      auth.saveLoginState(
        uni.getStorageSync("token"),
        localUser
      );
    }

    showSuccess("保存成功");
    
    setTimeout(() => {
      uni.navigateBack();
    }, 500);
  } catch (err) {
    console.error("保存失败:", err);
  } finally {
    loading.value = false;
  }
}

onLoad(() => {
  loadUserInfo();
});
</script>

<style scoped>
.edit-profile-container {
  min-height: 100vh;
  background: #F5F5F5;
}

/* 头部导航 */
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
  font-size: 48rpx;
  color: #333;
}

.nav-title {
  font-size: 34rpx;
  font-weight: bold;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.nav-save {
  width: 100rpx;
  text-align: right;
}

.nav-save text {
  font-size: 30rpx;
  color: #4A90D9;
}

/* 表单区域 */
.form-section {
  padding: 30rpx;
}

/* 头像区域 */
.avatar-section {
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.section-label {
  display: block;
  font-size: 28rpx;
  color: #999;
  margin-bottom: 20rpx;
}

.avatar-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.avatar-preview,
.avatar-placeholder {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-img {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-placeholder text {
  font-size: 64rpx;
}

.avatar-change {
  position: absolute;
  right: 20rpx;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  padding: 8rpx 24rpx;
  border-radius: 20rpx;
}

.avatar-change text {
  font-size: 22rpx;
  color: #fff;
}

/* 表单列表 */
.form-list {
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #F0F0F0;
}

.form-item:last-child {
  border-bottom: none;
}

.form-label {
  width: 160rpx;
  font-size: 30rpx;
  color: #333;
  flex-shrink: 0;
}

.form-value {
  flex: 1;
  font-size: 30rpx;
  color: #999;
  text-align: right;
}

.form-input {
  flex: 1;
  font-size: 30rpx;
  color: #333;
  text-align: right;
}

.phone-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.phone-input {
  text-align: right;
  margin-right: 16rpx;
}

.phone-bind {
  flex-shrink: 0;
}

.bound-text {
  font-size: 24rpx;
  color: #52C41A;
  background: rgba(82, 196, 26, 0.1);
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.bind-btn {
  font-size: 24rpx;
  color: #4A90D9;
}

/* 微信绑定 */
.wechat-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.wechat-status {
  font-size: 28rpx;
  color: #999;
  margin-right: 20rpx;
}

.wechat-status.bound {
  color: #07C160;
}

.wechat-action {
  font-size: 28rpx;
  color: #4A90D9;
}

/* 底部区域 */
.footer-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 30rpx;
  background: #fff;
  padding-bottom: calc(30rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.save-btn {
  width: 100%;
  height: 96rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  border-radius: 48rpx;
  border: none;
}

.save-btn:active {
  opacity: 0.8;
}
</style>
