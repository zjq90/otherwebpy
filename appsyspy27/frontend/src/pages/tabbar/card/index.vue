<template>
  <view class="card-container">
    <!-- 状态筛选 -->
    <view class="filter-section">
      <view 
        class="filter-item" 
        :class="{ active: currentFilter === 'all' }"
        @click="currentFilter = 'all'"
      >
        全部
      </view>
      <view 
        class="filter-item" 
        :class="{ active: currentFilter === 'valid' }"
        @click="currentFilter = 'valid'"
      >
        有效
      </view>
      <view 
        class="filter-item" 
        :class="{ active: currentFilter === 'expired' }"
        @click="currentFilter = 'expired'"
      >
        已过期
      </view>
    </view>

    <!-- 卡包列表 -->
    <view class="card-list" v-if="filteredCards.length > 0">
      <view 
        class="card-item" 
        v-for="(card, index) in filteredCards" 
        :key="card.id"
        @click="goToCardDetail(card.id)"
      >
        <view class="card-bg" :class="getCardClass(card.card_category)">
          <view class="card-top">
            <view class="card-header">
              <text class="card-name">{{ card.display_name }}</text>
              <text class="card-status" :class="card.is_valid ? 'status-valid' : 'status-invalid'">
                {{ getStatusText(card) }}
              </text>
            </view>
            <view class="card-number">
              卡号：{{ card.card_number }}
            </view>
          </view>

          <view class="card-info">
            <!-- 次卡/课包显示次数 -->
            <view class="info-item" v-if="card.card_category === 'COUNT' || card.card_category === 'LESSON'">
              <view class="info-value">
                <text class="value-main">{{ card.remaining_count }}</text>
                <text class="value-unit">/ {{ card.total_count }} 次</text>
              </view>
              <text class="info-label">剩余次数</text>
            </view>

            <!-- 时长卡显示时长 -->
            <view class="info-item" v-else-if="card.card_category === 'DURATION'">
              <view class="info-value">
                <text class="value-main">{{ formatDurationMinutes(card.remaining_duration) }}</text>
              </view>
              <text class="info-label">剩余时长</text>
            </view>

            <!-- 年卡显示有效期 -->
            <view class="info-item" v-else>
              <view class="info-value">
                <text class="value-main">{{ formatDate(card.expire_time, 'YYYY-MM-DD') }}</text>
              </view>
              <text class="info-label">有效期至</text>
            </view>
          </view>

          <!-- 进度条（次卡/课包） -->
          <view class="progress-section" v-if="card.card_category === 'COUNT' || card.card_category === 'LESSON'">
            <view class="progress-bar">
              <view class="progress-fill" :style="{ width: getProgressWidth(card) }"></view>
            </view>
            <view class="progress-text">
              <text>已使用 {{ card.total_count - card.remaining_count }} 次</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text>💳</text>
      </view>
      <text class="empty-text">{{ emptyText }}</text>
      <button class="empty-btn" @click="goToShop">去购卡</button>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onShow } from "vue";
import { card, auth } from "@/api";
import { formatDate, formatDuration } from "@/utils";

const currentFilter = ref("all");
const userCards = ref<any[]>([]);

const emptyText = computed(() => {
  if (currentFilter.value === "valid") {
    return "暂无有效会员卡";
  } else if (currentFilter.value === "expired") {
    return "暂无已过期会员卡";
  }
  return "暂无会员卡";
});

const filteredCards = computed(() => {
  if (currentFilter.value === "valid") {
    return userCards.value.filter(c => c.is_valid);
  } else if (currentFilter.value === "expired") {
    return userCards.value.filter(c => !c.is_valid);
  }
  return userCards.value;
});

// 获取卡样式类
function getCardClass(category: string) {
  const map: Record<string, string> = {
    "YEAR": "bg-year",
    "COUNT": "bg-count",
    "DURATION": "bg-duration",
    "LESSON": "bg-lesson"
  };
  return map[category] || "bg-default";
}

// 获取状态文本
function getStatusText(card: any) {
  if (!card.is_valid) {
    if (card.status === "EXPIRED") return "已过期";
    if (card.status === "USED_UP") return "已用完";
    return "已失效";
  }
  return "有效";
}

// 获取进度条宽度
function getProgressWidth(card: any) {
  if (!card.total_count) return "0%";
  const used = card.total_count - card.remaining_count;
  const percent = (used / card.total_count) * 100;
  return `${percent}%`;
}

// 格式化分钟数
function formatDurationMinutes(minutes: number) {
  if (!minutes) return "0分钟";
  return formatDuration(minutes);
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

// 页面跳转
function goToCardDetail(id: number) {
  uni.navigateTo({ url: `/pages/card/detail/index?id=${id}` });
}

function goToShop() {
  uni.switchTab({ url: "/pages/tabbar/shop/index" });
}

onShow(() => {
  if (checkLogin()) {
    loadUserCards();
  }
});
</script>

<style scoped>
.card-container {
  min-height: 100vh;
  background: #F5F5F5;
}

/* 筛选栏 */
.filter-section {
  display: flex;
  background: #fff;
  padding: 20rpx 30rpx;
  gap: 20rpx;
}

.filter-item {
  flex: 1;
  height: 64rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 32rpx;
  font-size: 28rpx;
  color: #666;
  background: #F5F5F5;
}

.filter-item.active {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
}

/* 卡包列表 */
.card-list {
  padding: 20rpx 30rpx;
}

.card-item {
  margin-bottom: 30rpx;
}

.card-bg {
  padding: 30rpx;
  border-radius: 20rpx;
}

.bg-year {
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
}

.bg-count {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.bg-duration {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.bg-lesson {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.bg-default {
  background: linear-gradient(135deg, #8C8C8C 0%, #A8A8A8 100%);
}

.card-top {
  margin-bottom: 30rpx;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.card-name {
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
}

.card-status {
  font-size: 22rpx;
  padding: 4rpx 16rpx;
  border-radius: 20rpx;
}

.status-valid {
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.status-invalid {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.card-number {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
  font-family: monospace;
}

.card-info {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-value {
  display: flex;
  align-items: baseline;
}

.value-main {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
}

.value-unit {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 8rpx;
}

.info-label {
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 8rpx;
}

/* 进度条 */
.progress-section {
  margin-top: 24rpx;
  padding-top: 24rpx;
  border-top: 1rpx solid rgba(255, 255, 255, 0.2);
}

.progress-bar {
  height: 12rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #fff;
  border-radius: 6rpx;
  transition: width 0.3s ease;
}

.progress-text {
  margin-top: 12rpx;
  font-size: 22rpx;
  color: rgba(255, 255, 255, 0.7);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  width: 160rpx;
  height: 160rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 80rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 40rpx;
}

.empty-btn {
  width: 240rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 28rpx;
  border-radius: 40rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border: none;
}
</style>
