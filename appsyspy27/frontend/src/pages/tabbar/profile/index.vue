<template>
  <view class="profile-container">
    <!-- 自定义导航栏头部 -->
    <view class="header-section">
      <view class="status-bar"></view>
      <view class="header-content">
        <text class="header-title">我的</text>
        <view class="header-actions">
          <view class="action-btn" @click="goToSetting">
            <text>⚙️</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 用户信息卡片 -->
    <view class="user-card" @click="goToEditProfile">
      <view class="avatar-section">
        <view class="avatar-img" v-if="userInfo?.avatar">
          <image :src="userInfo.avatar" mode="aspectFill" class="avatar" />
        </view>
        <view class="avatar-placeholder" v-else>
          <text class="avatar-text">{{ userInfo?.real_name?.charAt(0) || userInfo?.username?.charAt(0) || '用' }}</text>
        </view>
      </view>
      <view class="user-info">
        <text class="user-name">{{ userInfo?.real_name || userInfo?.username || '用户' }}</text>
        <view class="user-tags">
          <view class="tag-item" v-if="userInfo?.phone">
            <text>📱 已绑定</text>
          </view>
          <view class="tag-item" v-if="userInfo?.wechat_openid">
            <text>💬 微信</text>
          </view>
          <view class="tag-item" v-else>
            <text>👤 未绑定</text>
          </view>
        </view>
      </view>
      <view class="arrow-icon">
        <text>›</text>
      </view>
    </view>

    <!-- 数据统计 -->
    <view class="stats-section">
      <view class="stats-card">
        <view class="stats-item" @click="goToCardList">
          <text class="stats-value">{{ stats.card_count }}</text>
          <text class="stats-label">会员卡</text>
        </view>
        <view class="stats-divider"></view>
        <view class="stats-item" @click="goToOrderList">
          <text class="stats-value">{{ stats.order_count }}</text>
          <text class="stats-label">订单</text>
        </view>
        <view class="stats-divider"></view>
        <view class="stats-item" @click="goToConsumption">
          <text class="stats-value">{{ stats.consumption_count }}</text>
          <text class="stats-label">消费记录</text>
        </view>
      </view>
    </view>

    <!-- 功能菜单 -->
    <view class="menu-section">
      <view class="menu-group">
        <view class="menu-title">我的卡包</view>
        <view class="menu-item" @click="goToCardList">
          <view class="menu-icon">
            <text>💳</text>
          </view>
          <text class="menu-text">我的会员卡</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
        <view class="menu-item" @click="goToCardExpire">
          <view class="menu-icon">
            <text>⏰</text>
          </view>
          <text class="menu-text">即将过期</text>
          <view class="menu-badge" v-if="stats.expire_soon > 0">
            <text>{{ stats.expire_soon }}</text>
          </view>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-title">交易管理</view>
        <view class="menu-item" @click="goToOrderList">
          <view class="menu-icon">
            <text>📋</text>
          </view>
          <text class="menu-text">我的订单</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
        <view class="menu-item" @click="goToConsumption">
          <view class="menu-icon">
            <text>📊</text>
          </view>
          <text class="menu-text">消费记录</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
        <view class="menu-item" @click="goToMonthlyBill">
          <view class="menu-icon">
            <text>📄</text>
          </view>
          <text class="menu-text">月度账单</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-title">账户设置</view>
        <view class="menu-item" @click="goToEditProfile">
          <view class="menu-icon">
            <text>✏️</text>
          </view>
          <text class="menu-text">编辑资料</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
        <view class="menu-item" @click="goToBindPhone">
          <view class="menu-icon">
            <text>📱</text>
          </view>
          <text class="menu-text">绑定手机</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
        <view class="menu-item" @click="goToBindWechat">
          <view class="menu-icon">
            <text>💬</text>
          </view>
          <text class="menu-text">绑定微信</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
      </view>

      <view class="menu-group">
        <view class="menu-title">其他</view>
        <view class="menu-item" @click="goToHelp">
          <view class="menu-icon">
            <text>❓</text>
          </view>
          <text class="menu-text">帮助中心</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
        <view class="menu-item" @click="goToAbout">
          <view class="menu-icon">
            <text>ℹ️</text>
          </view>
          <text class="menu-text">关于我们</text>
          <view class="menu-arrow">
            <text>›</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 退出登录 -->
    <view class="logout-section">
      <button class="logout-btn" @click="handleLogout">退出登录</button>
    </view>

    <!-- 底部安全区域 -->
    <view class="safe-bottom"></view>
  </view>
</template>

<script setup lang="ts">
import { ref, reactive, onShow } from "vue";
import { auth, card, order, consumption } from "@/api";
import { showSuccess, showError, showConfirm } from "@/utils";

const userInfo = ref<any>(null);

const stats = reactive({
  card_count: 0,
  order_count: 0,
  consumption_count: 0,
  expire_soon: 0
});

/**
 * 加载用户信息
 */
async function loadUserInfo() {
  try {
    const res = await auth.getCurrentUser();
    userInfo.value = res.data;
  } catch (err) {
    console.error("加载用户信息失败:", err);
  }
}

/**
 * 加载统计数据
 */
async function loadStats() {
  try {
    const [cardRes, orderRes, consumptionRes] = await Promise.all([
      card.getMyCards({ only_valid: true }),
      order.getMyOrders({ limit: 1 }),
      consumption.getMyRecords({ limit: 1 })
    ]);

    stats.card_count = cardRes.data.length;
    stats.order_count = orderRes.data?.total || 0;
    stats.consumption_count = consumptionRes.data?.total || 0;

    const expireSoonCount = cardRes.data.filter((c: any) => {
      if (!c.is_valid) return false;
      const expireTime = new Date(c.expire_time);
      const now = new Date();
      const diffDays = Math.ceil((expireTime.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
      return diffDays <= 7 && diffDays >= 0;
    }).length;
    stats.expire_soon = expireSoonCount;
  } catch (err) {
    console.error("加载统计数据失败:", err);
  }
}

/**
 * 检查登录状态
 */
function checkLogin() {
  if (!auth.isLoggedIn()) {
    uni.redirectTo({
      url: "/pages/login/index"
    });
    return false;
  }
  return true;
}

/**
 * 页面跳转
 */
function goToEditProfile() {
  uni.navigateTo({ url: "/pages/profile/edit/index" });
}

function goToSetting() {
  uni.showToast({ title: "设置功能开发中", icon: "none" });
}

function goToCardList() {
  uni.switchTab({ url: "/pages/tabbar/card/index" });
}

function goToCardExpire() {
  uni.showToast({ title: "即将过期功能开发中", icon: "none" });
}

function goToOrderList() {
  uni.navigateTo({ url: "/pages/order/list/index" });
}

function goToConsumption() {
  uni.navigateTo({ url: "/pages/consumption/list/index" });
}

function goToMonthlyBill() {
  uni.navigateTo({ url: "/pages/consumption/bill/index" });
}

function goToBindPhone() {
  uni.showToast({ title: "绑定手机功能开发中", icon: "none" });
}

function goToBindWechat() {
  uni.showToast({ title: "绑定微信功能开发中", icon: "none" });
}

function goToHelp() {
  uni.showToast({ title: "帮助中心功能开发中", icon: "none" });
}

function goToAbout() {
  uni.showToast({ title: "关于我们功能开发中", icon: "none" });
}

/**
 * 退出登录
 */
async function handleLogout() {
  try {
    const confirmed = await showConfirm("确定要退出登录吗？");
    if (confirmed) {
      auth.clearLoginState();
      showSuccess("已退出登录");
      setTimeout(() => {
        uni.redirectTo({
          url: "/pages/login/index"
        });
      }, 500);
    }
  } catch (err) {
    console.error("退出登录失败:", err);
  }
}

onShow(() => {
  if (checkLogin()) {
    loadUserInfo();
    loadStats();
  }
});
</script>

<style scoped>
.profile-container {
  min-height: 100vh;
  background: #F5F5F5;
}

/* 头部区域 */
.header-section {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
}

.status-bar {
  height: var(--status-bar-height);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 88rpx;
  padding: 0 30rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
}

.header-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40rpx;
}

/* 用户卡片 */
.user-card {
  display: flex;
  align-items: center;
  background: #fff;
  margin: 20rpx 30rpx;
  padding: 30rpx;
  border-radius: 20rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.avatar-section {
  margin-right: 24rpx;
}

.avatar-img {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  overflow: hidden;
}

.avatar {
  width: 100%;
  height: 100%;
}

.avatar-placeholder {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.avatar-text {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
}

.user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 12rpx;
}

.user-tags {
  display: flex;
  gap: 16rpx;
}

.tag-item {
  font-size: 22rpx;
  color: #666;
  background: #F5F5F5;
  padding: 6rpx 16rpx;
  border-radius: 20rpx;
}

.arrow-icon {
  font-size: 48rpx;
  color: #CCC;
  margin-left: 16rpx;
}

/* 统计区域 */
.stats-section {
  padding: 0 30rpx;
  margin-bottom: 20rpx;
}

.stats-card {
  display: flex;
  background: #fff;
  border-radius: 20rpx;
  padding: 30rpx 0;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.stats-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stats-value {
  font-size: 48rpx;
  font-weight: bold;
  color: #4A90D9;
  margin-bottom: 8rpx;
}

.stats-label {
  font-size: 24rpx;
  color: #999;
}

.stats-divider {
  width: 2rpx;
  height: 80rpx;
  background: #F0F0F0;
  align-self: center;
}

/* 菜单区域 */
.menu-section {
  padding: 0 30rpx;
}

.menu-group {
  background: #fff;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.menu-title {
  font-size: 24rpx;
  color: #999;
  padding: 24rpx 30rpx 16rpx;
  background: #FAFAFA;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #F0F0F0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40rpx;
  margin-right: 20rpx;
}

.menu-text {
  flex: 1;
  font-size: 30rpx;
  color: #333;
}

.menu-badge {
  background: #FF4D4F;
  color: #fff;
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 20rpx;
  margin-right: 12rpx;
}

.menu-arrow {
  font-size: 36rpx;
  color: #CCC;
}

/* 退出登录 */
.logout-section {
  padding: 40rpx 30rpx;
}

.logout-btn {
  width: 100%;
  height: 96rpx;
  background: #fff;
  color: #FF4D4F;
  font-size: 32rpx;
  font-weight: bold;
  border-radius: 48rpx;
  border: none;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.logout-btn:active {
  opacity: 0.8;
}

/* 底部安全区域 */
.safe-bottom {
  height: 40rpx;
}
</style>
