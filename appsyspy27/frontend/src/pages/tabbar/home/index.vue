<template>
  <view class="home-container">
    <!-- 自定义导航栏 -->
    <view class="custom-nav">
      <view class="nav-status-bar"></view>
      <view class="nav-content">
        <view class="nav-left">
          <text class="greeting-text">{{ greeting }}</text>
          <text class="user-name" v-if="userInfo">{{ userInfo.real_name || userInfo.username }}</text>
        </view>
        <view class="nav-right">
          <view class="nav-icon" @click="goToNotification">
            <text>🔔</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 搜索栏 -->
    <view class="search-section">
      <view class="search-bar" @click="handleSearch">
        <text class="search-icon">🔍</text>
        <text class="search-placeholder">搜索会员卡、课程</text>
      </view>
    </view>

    <!-- 轮播区域 -->
    <view class="banner-section">
      <swiper class="banner-swiper" indicator-dots autoplay circular interval="3000">
        <swiper-item v-for="(banner, index) in banners" :key="index">
          <view class="banner-item" :style="{ background: banner.bg }">
            <text class="banner-title">{{ banner.title }}</text>
            <text class="banner-subtitle">{{ banner.subtitle }}</text>
          </view>
        </swiper-item>
      </swiper>
    </view>

    <!-- 快捷入口 -->
    <view class="quick-section">
      <view class="quick-item" v-for="(item, index) in quickMenus" :key="index" @click="handleQuickClick(item)">
        <view class="quick-icon" :style="{ background: item.bg }">
          <text>{{ item.icon }}</text>
        </view>
        <text class="quick-text">{{ item.name }}</text>
      </view>
    </view>

    <!-- 我的卡包概览 -->
    <view class="section" v-if="userCards.length > 0">
      <view class="section-header">
        <text class="section-title">我的会员卡</text>
        <text class="section-more" @click="goToCardBag">查看全部 ></text>
      </view>
      <view class="card-preview-list">
        <view 
          class="card-preview-item" 
          v-for="(card, index) in displayCards" 
          :key="card.id"
          @click="goToCardDetail(card.id)"
        >
          <view class="card-preview-bg" :class="getCardClass(card.card_category)">
            <view class="card-preview-top">
              <text class="card-preview-name">{{ card.display_name }}</text>
              <text class="card-preview-status" :class="card.is_valid ? 'valid' : 'invalid'">
                {{ card.is_valid ? '有效' : '已失效' }}
              </text>
            </view>
            <view class="card-preview-info" v-if="card.card_category === 'COUNT' || card.card_category === 'LESSON'">
              <text class="info-label">剩余次数</text>
              <text class="info-value">{{ card.remaining_count }} / {{ card.total_count }}</text>
            </view>
            <view class="card-preview-info" v-else-if="card.card_category === 'DURATION'">
              <text class="info-label">剩余时长</text>
              <text class="info-value">{{ formatDuration(card.remaining_duration) }}</text>
            </view>
            <view class="card-preview-info" v-else>
              <text class="info-label">有效期至</text>
              <text class="info-value">{{ formatDate(card.expire_time, 'MM-DD') }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 推荐会员卡 -->
    <view class="section">
      <view class="section-header">
        <text class="section-title">热门推荐</text>
        <text class="section-more" @click="goToShop">更多 ></text>
      </view>
      <view class="recommend-list">
        <view 
          class="recommend-item" 
          v-for="(item, index) in recommendCards" 
          :key="item.id"
          @click="goToBuy(item)"
        >
          <view class="recommend-image">
            <text class="recommend-category">{{ getCategoryName(item.category) }}</text>
          </view>
          <view class="recommend-content">
            <text class="recommend-name">{{ item.name }}</text>
            <text class="recommend-desc">{{ item.description }}</text>
            <view class="recommend-price">
              <text class="price-current">¥{{ item.current_price }}</text>
              <text class="price-original">¥{{ item.original_price }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 底部安全区域 -->
    <view class="safe-bottom"></view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onShow } from "vue";
import { auth, card } from "@/api";
import { formatDate, formatDuration as formatDurationUtil } from "@/utils";

const greeting = ref("早上好");
const userInfo = ref<any>(null);
const userCards = ref<any[]>([]);
const recommendCards = ref<any[]>([]);

const banners = ref([
  { title: "新会员专享", subtitle: "首次购卡享85折优惠", bg: "linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%)" },
  { title: "限时活动", subtitle: "私教课套餐买30节送5节", bg: "linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%)" },
  { title: "会员日", subtitle: "每周三会员日，全场8折", bg: "linear-gradient(135deg, #52C41A 0%, #73D13D 100%)" }
]);

const quickMenus = ref([
  { name: "卡包", icon: "💳", bg: "linear-gradient(135deg, #4A90D9, #6BA8E0)", path: "/pages/tabbar/card/index" },
  { name: "购卡", icon: "🛒", bg: "linear-gradient(135deg, #FF6B6B, #FF8E8E)", path: "/pages/tabbar/shop/index" },
  { name: "订单", icon: "📋", bg: "linear-gradient(135deg, #FAAD14, #FFC53D)", path: "/pages/order/list/index" },
  { name: "消费记录", icon: "📊", bg: "linear-gradient(135deg, #52C41A, #73D13D)", path: "/pages/consumption/list/index" }
]);

const displayCards = computed(() => userCards.value.slice(0, 3));

// 更新问候语
function updateGreeting() {
  const hour = new Date().getHours();
  if (hour < 6) {
    greeting.value = "夜深了";
  } else if (hour < 12) {
    greeting.value = "早上好";
  } else if (hour < 18) {
    greeting.value = "下午好";
  } else {
    greeting.value = "晚上好";
  }
}

// 获取卡类别名称
function getCategoryName(category: string) {
  const map: Record<string, string> = {
    "YEAR": "年卡",
    "COUNT": "次卡",
    "DURATION": "时长卡",
    "LESSON": "课包"
  };
  return map[category] || "会员卡";
}

// 获取卡样式类
function getCardClass(category: string) {
  const map: Record<string, string> = {
    "YEAR": "card-year",
    "COUNT": "card-count",
    "DURATION": "card-duration",
    "LESSON": "card-lesson"
  };
  return map[category] || "card-default";
}

// 加载用户信息
async function loadUserInfo() {
  try {
    const res = await auth.getCurrentUser();
    userInfo.value = res.data;
  } catch (err) {
    console.error("加载用户信息失败:", err);
  }
}

// 加载用户卡包
async function loadUserCards() {
  try {
    const res = await card.getMyCards({ only_valid: false });
    userCards.value = res.data;
  } catch (err) {
    console.error("加载卡包失败:", err);
  }
}

// 加载推荐卡
async function loadRecommendCards() {
  try {
    const res = await card.getCardTypes({ is_on_sale: true });
    recommendCards.value = res.data.slice(0, 5);
  } catch (err) {
    console.error("加载推荐卡失败:", err);
  }
}

// 检查登录状态
function checkLogin() {
  if (!auth.isLoggedIn()) {
    uni.redirectTo({
      url: "/pages/login/index"
    });
    return false;
  }
  return true;
}

// 快捷入口点击
function handleQuickClick(item: any) {
  uni.navigateTo({ url: item.path });
}

// 页面跳转
function goToNotification() {
  // 通知页面
}

function handleSearch() {
  uni.showToast({ title: "搜索功能开发中", icon: "none" });
}

function goToCardBag() {
  uni.switchTab({ url: "/pages/tabbar/card/index" });
}

function goToCardDetail(id: number) {
  uni.navigateTo({ url: `/pages/card/detail/index?id=${id}` });
}

function goToShop() {
  uni.switchTab({ url: "/pages/tabbar/shop/index" });
}

function goToBuy(item: any) {
  uni.navigateTo({ 
    url: `/pages/order/create/index?card_type_id=${item.id}&name=${encodeURIComponent(item.name)}&price=${item.current_price}` 
  });
}

onShow(() => {
  updateGreeting();
  if (checkLogin()) {
    loadUserInfo();
    loadUserCards();
    loadRecommendCards();
  }
});

onMounted(() => {
  updateGreeting();
});
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #F5F5F5;
}

/* 自定义导航栏 */
.custom-nav {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
}

.nav-status-bar {
  height: var(--status-bar-height);
}

.nav-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 88rpx;
  padding: 0 30rpx;
}

.nav-left {
  display: flex;
  flex-direction: column;
}

.greeting-text {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.user-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
  margin-top: 4rpx;
}

.nav-right {
  display: flex;
}

.nav-icon {
  width: 64rpx;
  height: 64rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40rpx;
}

/* 搜索栏 */
.search-section {
  padding: 20rpx 30rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
}

.search-bar {
  display: flex;
  align-items: center;
  height: 80rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 40rpx;
  padding: 0 30rpx;
}

.search-icon {
  font-size: 32rpx;
  margin-right: 16rpx;
}

.search-placeholder {
  font-size: 28rpx;
  color: #999;
}

/* 轮播图 */
.banner-section {
  padding: 20rpx 30rpx;
}

.banner-swiper {
  height: 280rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.banner-item {
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 50rpx;
  border-radius: 20rpx;
}

.banner-title {
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 10rpx;
}

.banner-subtitle {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 快捷入口 */
.quick-section {
  display: flex;
  justify-content: space-around;
  padding: 20rpx 30rpx;
  background: #fff;
  margin: 0 30rpx 20rpx;
  border-radius: 16rpx;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.quick-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 48rpx;
  margin-bottom: 12rpx;
}

.quick-text {
  font-size: 24rpx;
  color: #333;
}

/* 通用区块 */
.section {
  background: #fff;
  margin: 0 30rpx 20rpx;
  border-radius: 16rpx;
  padding: 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.section-more {
  font-size: 26rpx;
  color: #999;
}

/* 卡包预览 */
.card-preview-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.card-preview-item {
  border-radius: 16rpx;
  overflow: hidden;
}

.card-preview-bg {
  padding: 30rpx;
  border-radius: 16rpx;
}

.card-year {
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
}

.card-count {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.card-duration {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.card-lesson {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.card-default {
  background: linear-gradient(135deg, #8C8C8C 0%, #A8A8A8 100%);
}

.card-preview-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-preview-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
}

.card-preview-status {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.card-preview-status.valid {
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.card-preview-status.invalid {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.card-preview-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.info-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #fff;
}

/* 推荐列表 */
.recommend-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.recommend-item {
  display: flex;
  background: #F8F9FA;
  border-radius: 12rpx;
  overflow: hidden;
}

.recommend-image {
  width: 160rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
  display: flex;
  justify-content: center;
  align-items: center;
}

.recommend-category {
  font-size: 24rpx;
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.recommend-content {
  flex: 1;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.recommend-name {
  font-size: 28rpx;
  font-weight: bold;
  color: #333;
}

.recommend-desc {
  font-size: 22rpx;
  color: #999;
  margin-top: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-price {
  display: flex;
  align-items: baseline;
  margin-top: 8rpx;
}

.price-current {
  font-size: 32rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.price-original {
  font-size: 22rpx;
  color: #999;
  text-decoration: line-through;
  margin-left: 12rpx;
}

/* 底部安全区域 */
.safe-bottom {
  height: 40rpx;
}
</style>
