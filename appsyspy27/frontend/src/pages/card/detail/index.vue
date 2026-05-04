<template>
  <view class="card-detail-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">会员卡详情</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-section" v-if="loading">
      <text>加载中...</text>
    </view>

    <!-- 卡详情内容 -->
    <view v-else-if="cardInfo">
      <!-- 卡面展示 -->
      <view class="card-face-section">
        <view class="card-face" :class="getCardClass(cardInfo.card_category)">
          <view class="card-face-header">
            <text class="card-name">{{ cardInfo.display_name }}</text>
            <view class="card-status" :class="cardInfo.is_valid ? 'valid' : 'invalid'">
              <text>{{ getStatusText(cardInfo) }}</text>
            </view>
          </view>
          
          <view class="card-number">
            <text>{{ formatCardNumber(cardInfo.card_number) }}</text>
          </view>

          <view class="card-main-info">
            <!-- 次卡/课包显示次数 -->
            <view class="info-block" v-if="cardInfo.card_category === 'COUNT' || cardInfo.card_category === 'LESSON'">
              <view class="info-value">
                <text class="value-main">{{ cardInfo.remaining_count }}</text>
                <text class="value-unit">/ {{ cardInfo.total_count }} 次</text>
              </view>
              <text class="info-label">剩余次数</text>
            </view>

            <!-- 时长卡显示时长 -->
            <view class="info-block" v-else-if="cardInfo.card_category === 'DURATION'">
              <view class="info-value">
                <text class="value-main">{{ formatDurationMinutes(cardInfo.remaining_duration) }}</text>
              </view>
              <text class="info-label">剩余时长</text>
            </view>

            <!-- 年卡显示有效期 -->
            <view class="info-block" v-else>
              <view class="info-value">
                <text class="value-main">{{ formatDate(cardInfo.expire_time, 'YYYY-MM-DD') }}</text>
              </view>
              <text class="info-label">有效期至</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 进度条（次卡/课包） -->
      <view class="progress-section" v-if="cardInfo.card_category === 'COUNT' || cardInfo.card_category === 'LESSON'">
        <view class="progress-header">
          <text class="progress-title">使用进度</text>
          <text class="progress-percent">{{ getProgressPercent(cardInfo) }}%</text>
        </view>
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: getProgressPercent(cardInfo) + '%' }"></view>
        </view>
        <view class="progress-desc">
          <text>已使用 {{ cardInfo.total_count - cardInfo.remaining_count }} 次</text>
          <text>剩余 {{ cardInfo.remaining_count }} 次</text>
        </view>
      </view>

      <!-- 卡信息详情 -->
      <view class="info-section">
        <view class="section-header">
          <text class="section-title">卡信息</text>
        </view>
        <view class="info-list">
          <view class="info-item">
            <text class="info-item-label">卡类型</text>
            <text class="info-item-value">{{ getCategoryName(cardInfo.card_category) }}</text>
          </view>
          <view class="info-item">
            <text class="info-item-label">购卡时间</text>
            <text class="info-item-value">{{ formatDate(cardInfo.create_time, 'YYYY-MM-DD HH:mm') }}</text>
          </view>
          <view class="info-item" v-if="cardInfo.card_category !== 'DURATION'">
            <text class="info-item-label">开始时间</text>
            <text class="info-item-value">{{ formatDate(cardInfo.start_time, 'YYYY-MM-DD') }}</text>
          </view>
          <view class="info-item" v-if="cardInfo.card_category !== 'DURATION'">
            <text class="info-item-label">结束时间</text>
            <text class="info-item-value">{{ formatDate(cardInfo.expire_time, 'YYYY-MM-DD') }}</text>
          </view>
          <view class="info-item" v-if="cardInfo.usage_scope">
            <text class="info-item-label">使用范围</text>
            <text class="info-item-value usage">{{ cardInfo.usage_scope }}</text>
          </view>
          <view class="info-item" v-if="cardInfo.remarks">
            <text class="info-item-label">备注</text>
            <text class="info-item-value">{{ cardInfo.remarks }}</text>
          </view>
        </view>
      </view>

      <!-- 使用记录 -->
      <view class="usage-section">
        <view class="section-header">
          <text class="section-title">使用记录</text>
          <text class="section-more" @click="goToUsageRecords">查看全部 ></text>
        </view>
        
        <view class="usage-list" v-if="usageRecords.length > 0">
          <view class="usage-item" v-for="(record, index) in usageRecords.slice(0, 5)" :key="index">
            <view class="usage-type" :class="record.type">
              <text>{{ getUsageTypeText(record.type) }}</text>
            </view>
            <view class="usage-content">
              <text class="usage-desc">{{ record.description || '使用会员卡' }}</text>
              <text class="usage-time">{{ formatDate(record.create_time, 'MM-DD HH:mm') }}</text>
            </view>
            <view class="usage-amount" v-if="record.amount">
              <text class="amount-text">-{{ record.amount }}</text>
            </view>
          </view>
        </view>
        
        <view class="empty-usage" v-else>
          <text>暂无使用记录</text>
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view class="footer-section">
        <view class="footer-actions">
          <button class="action-btn secondary" @click="goToRenew" v-if="cardInfo.is_valid">
            <text>续费</text>
          </button>
          <button class="action-btn primary" @click="goToBuyMore">
            <text>购卡</text>
          </button>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-section" v-else-if="!loading && !cardInfo">
      <view class="empty-icon">
        <text>💳</text>
      </view>
      <text class="empty-text">会员卡不存在</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onLoad } from "vue";
import { card, consumption } from "@/api";
import { formatDate, formatDuration } from "@/utils";

const loading = ref(true);
const cardId = ref<number | null>(null);
const cardInfo = ref<any>(null);
const usageRecords = ref<any[]>([]);

/**
 * 获取卡样式类
 */
function getCardClass(category: string) {
  const map: Record<string, string> = {
    "YEAR": "bg-year",
    "COUNT": "bg-count",
    "DURATION": "bg-duration",
    "LESSON": "bg-lesson"
  };
  return map[category] || "bg-default";
}

/**
 * 获取状态文本
 */
function getStatusText(card: any) {
  if (!card.is_valid) {
    if (card.status === "EXPIRED") return "已过期";
    if (card.status === "USED_UP") return "已用完";
    return "已失效";
  }
  return "有效";
}

/**
 * 获取分类名称
 */
function getCategoryName(category: string) {
  const map: Record<string, string> = {
    "YEAR": "年卡",
    "COUNT": "次卡",
    "DURATION": "时长卡",
    "LESSON": "私教课包"
  };
  return map[category] || "会员卡";
}

/**
 * 获取使用类型文本
 */
function getUsageTypeText(type: string) {
  const map: Record<string, string> = {
    "PURCHASE": "购卡",
    "RENEW": "续费",
    "USE": "使用",
    "DEDUCT": "扣费",
    "REFUND": "退款"
  };
  return map[type] || "消费";
}

/**
 * 格式化卡号
 */
function formatCardNumber(number: string) {
  if (!number) return "";
  if (number.length === 12) {
    return `${number.slice(0, 4)} ${number.slice(4, 8)} ${number.slice(8, 12)}`;
  }
  return number;
}

/**
 * 格式化分钟数
 */
function formatDurationMinutes(minutes: number) {
  if (!minutes) return "0分钟";
  return formatDuration(minutes);
}

/**
 * 获取进度百分比
 */
function getProgressPercent(card: any) {
  if (!card || !card.total_count) return 0;
  const used = card.total_count - card.remaining_count;
  const percent = (used / card.total_count) * 100;
  return Math.round(percent);
}

/**
 * 加载会员卡详情
 */
async function loadCardDetail(id: number) {
  loading.value = true;
  try {
    const res = await card.getCardDetail(id);
    cardInfo.value = res.data;
  } catch (err) {
    console.error("加载卡详情失败:", err);
  } finally {
    loading.value = false;
  }
}

/**
 * 加载使用记录
 */
async function loadUsageRecords(cardId: number) {
  try {
    const res = await consumption.getMyRecords({ card_id: cardId, limit: 10 });
    usageRecords.value = res.data?.items || [];
  } catch (err) {
    console.error("加载使用记录失败:", err);
  }
}

/**
 * 页面跳转
 */
function goBack() {
  uni.navigateBack();
}

function goToUsageRecords() {
  uni.navigateTo({ 
    url: `/pages/consumption/list/index?card_id=${cardId.value}` 
  });
}

function goToRenew() {
  if (cardInfo.value) {
    uni.navigateTo({ 
      url: `/pages/order/create/index?card_type_id=${cardInfo.value.card_type_id}&name=${encodeURIComponent(cardInfo.value.display_name)}&price=${cardInfo.value.original_price || 0}&renew=true` 
    });
  }
}

function goToBuyMore() {
  uni.switchTab({ url: "/pages/tabbar/shop/index" });
}

onLoad((options: any) => {
  if (options.id) {
    cardId.value = parseInt(options.id);
    loadCardDetail(cardId.value);
    loadUsageRecords(cardId.value);
  }
});
</script>

<style scoped>
.card-detail-container {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 120rpx;
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
  position: sticky;
  top: 0;
  z-index: 100;
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

.nav-placeholder {
  width: 60rpx;
}

/* 加载状态 */
.loading-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 100rpx;
  font-size: 28rpx;
  color: #999;
}

/* 空状态 */
.empty-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 120rpx 0;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

/* 卡面展示 */
.card-face-section {
  padding: 30rpx;
}

.card-face {
  padding: 40rpx;
  border-radius: 24rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
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

.card-face-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30rpx;
}

.card-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #fff;
}

.card-status {
  font-size: 22rpx;
  padding: 6rpx 20rpx;
  border-radius: 20rpx;
}

.card-status.valid {
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.card-status.invalid {
  background: rgba(0, 0, 0, 0.2);
  color: rgba(255, 255, 255, 0.8);
}

.card-number {
  font-size: 32rpx;
  color: rgba(255, 255, 255, 0.8);
  font-family: monospace;
  margin-bottom: 30rpx;
  letter-spacing: 4rpx;
}

.card-main-info {
  display: flex;
  flex-direction: column;
}

.info-block {
  display: flex;
  flex-direction: column;
}

.info-value {
  display: flex;
  align-items: baseline;
}

.value-main {
  font-size: 56rpx;
  font-weight: bold;
  color: #fff;
}

.value-unit {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-left: 8rpx;
}

.info-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 8rpx;
}

/* 进度条 */
.progress-section {
  background: #fff;
  margin: 0 30rpx 20rpx;
  padding: 30rpx;
  border-radius: 20rpx;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.progress-title {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
}

.progress-percent {
  font-size: 28rpx;
  color: #4A90D9;
  font-weight: bold;
}

.progress-bar {
  height: 16rpx;
  background: #F0F0F0;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4A90D9 0%, #6BA8E0 100%);
  border-radius: 8rpx;
  transition: width 0.3s ease;
}

.progress-desc {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
  font-size: 24rpx;
  color: #999;
}

/* 信息区域 */
.info-section {
  background: #fff;
  margin: 0 30rpx 20rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #F0F0F0;
}

.section-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #333;
}

.section-more {
  font-size: 26rpx;
  color: #4A90D9;
}

.info-list {
  padding: 0 30rpx;
}

.info-item {
  display: flex;
  padding: 26rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item-label {
  width: 180rpx;
  font-size: 28rpx;
  color: #999;
  flex-shrink: 0;
}

.info-item-value {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.info-item-value.usage {
  text-align: left;
  word-break: break-all;
}

/* 使用记录 */
.usage-section {
  background: #fff;
  margin: 0 30rpx 20rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.usage-list {
  padding: 0 30rpx;
}

.usage-item {
  display: flex;
  align-items: center;
  padding: 26rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.usage-item:last-child {
  border-bottom: none;
}

.usage-type {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.usage-type text {
  font-size: 20rpx;
  color: #fff;
}

.usage-type.PURCHASE {
  background: #52C41A;
}

.usage-type.USE,
.usage-type.DEDUCT {
  background: #FF6B6B;
}

.usage-type.RENEW {
  background: #4A90D9;
}

.usage-type.REFUND {
  background: #FAAD14;
}

.usage-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.usage-desc {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 6rpx;
}

.usage-time {
  font-size: 22rpx;
  color: #999;
}

.usage-amount {
  flex-shrink: 0;
}

.amount-text {
  font-size: 28rpx;
  color: #FF6B6B;
  font-weight: bold;
}

.empty-usage {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60rpx;
  font-size: 28rpx;
  color: #999;
}

/* 底部操作栏 */
.footer-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.footer-actions {
  display: flex;
  gap: 20rpx;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 44rpx;
  font-size: 30rpx;
  font-weight: bold;
  border: none;
}

.action-btn.secondary {
  background: #F5F5F5;
  color: #333;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
}
</style>
