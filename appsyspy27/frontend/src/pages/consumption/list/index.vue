<template>
  <view class="consumption-list-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">消费记录</text>
      <view class="nav-right" @click="goToMonthlyBill">
        <text class="nav-action">月度账单</text>
      </view>
    </view>

    <!-- 类型筛选 -->
    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view 
            class="filter-item" 
            :class="{ active: currentType === '' }"
            @click="currentType = ''; refreshList()"
          >
            <text>全部</text>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentType === 'PURCHASE' }"
            @click="currentType = 'PURCHASE'; refreshList()"
          >
            <text>购卡</text>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentType === 'RENEW' }"
            @click="currentType = 'RENEW'; refreshList()"
          >
            <text>续费</text>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentType === 'USE' }"
            @click="currentType = 'USE'; refreshList()"
          >
            <text>使用</text>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentType === 'DEDUCT' }"
            @click="currentType = 'DEDUCT'; refreshList()"
          >
            <text>扣费</text>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentType === 'REFUND' }"
            @click="currentType = 'REFUND'; refreshList()"
          >
            <text>退款</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 日期筛选 -->
    <view class="date-section">
      <view class="date-picker" @click="showStartPicker = true">
        <text class="date-label">开始日期</text>
        <text class="date-value">{{ startDate || '不限' }}</text>
      </view>
      <text class="date-separator">至</text>
      <view class="date-picker" @click="showEndPicker = true">
        <text class="date-label">结束日期</text>
        <text class="date-value">{{ endDate || '不限' }}</text>
      </view>
      <view class="clear-btn" @click="clearDateFilter" v-if="startDate || endDate">
        <text>清除</text>
      </view>
    </view>

    <!-- 消费记录列表 -->
    <view class="record-list" v-if="!loading && records.length > 0">
      <view 
        class="record-item" 
        v-for="(record, index) in records" 
        :key="record.id"
      >
        <view class="record-left">
          <view class="record-icon" :class="record.record_type">
            <text>{{ getTypeIcon(record.record_type) }}</text>
          </view>
        </view>
        <view class="record-center">
          <view class="record-header">
            <text class="record-title">{{ getTypeText(record.record_type) }}</text>
          </view>
          <text class="record-desc" v-if="record.description">{{ record.description }}</text>
          <view class="record-info">
            <text class="record-time">{{ formatDate(record.create_time, 'YYYY-MM-DD HH:mm') }}</text>
            <text class="record-card" v-if="record.card_name">{{ record.card_name }}</text>
          </view>
        </view>
        <view class="record-right">
          <text class="record-amount" :class="{ income: isIncome(record.record_type) }">
            {{ isIncome(record.record_type) ? '+' : '-' }}{{ formatAmount(record.amount || 0) }}
          </text>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-section" v-if="loading">
      <text>加载中...</text>
    </view>

    <!-- 空状态 -->
    <view class="empty-section" v-else-if="!loading && records.length === 0">
      <view class="empty-icon">
        <text>📊</text>
      </view>
      <text class="empty-text">{{ emptyText }}</text>
    </view>

    <!-- 加载更多 -->
    <view class="load-more" v-if="hasMore && !loading">
      <text>{{ loadingMore ? '加载中...' : '上拉加载更多' }}</text>
    </view>
    <view class="no-more" v-if="!hasMore && records.length > 0">
      <text>没有更多了</text>
    </view>

    <!-- 日期选择器 -->
    <picker 
      mode="date" 
      :value="startDate" 
      :start="minDate" 
      :end="maxDate" 
      @change="onStartDateChange"
      v-model:show="showStartPicker"
    >
      <view style="display: none;"></view>
    </picker>
    <picker 
      mode="date" 
      :value="endDate" 
      :start="minDate" 
      :end="maxDate" 
      @change="onEndDateChange"
      v-model:show="showEndPicker"
    >
      <view style="display: none;"></view>
    </picker>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onLoad, onShow, onPullDownRefresh, onReachBottom } from "vue";
import { consumption } from "@/api";
import { formatDate, formatAmount } from "@/utils";

const cardId = ref<number | null>(null);
const currentType = ref("");
const startDate = ref("");
const endDate = ref("");
const showStartPicker = ref(false);
const showEndPicker = ref(false);

const loading = ref(false);
const loadingMore = ref(false);
const records = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(20);
const hasMore = ref(true);

const today = new Date();
const maxDate = ref(today.toISOString().split('T')[0]);
const minDate = ref("2020-01-01");

const emptyText = computed(() => {
  if (currentType.value) {
    return `暂无${getTypeText(currentType.value)}记录`;
  }
  return "暂无消费记录";
});

/**
 * 获取类型图标
 */
function getTypeIcon(type: string) {
  const map: Record<string, string> = {
    "PURCHASE": "💳",
    "RENEW": "🔄",
    "USE": "✓",
    "DEDUCT": "💰",
    "REFUND": "↩️"
  };
  return map[type] || "📋";
}

/**
 * 获取类型文本
 */
function getTypeText(type: string) {
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
 * 判断是否是收入
 */
function isIncome(type: string) {
  return type === "REFUND";
}

/**
 * 刷新列表
 */
function refreshList() {
  page.value = 1;
  hasMore.value = true;
  records.value = [];
  loadRecords(true);
}

/**
 * 加载消费记录
 */
async function loadRecords(refresh: boolean = false) {
  if (refresh) {
    loading.value = true;
  } else {
    loadingMore.value = true;
  }

  try {
    const params: any = {
      page: page.value,
      page_size: pageSize.value
    };

    if (currentType.value) {
      params.record_type = currentType.value;
    }
    if (cardId.value) {
      params.card_id = cardId.value;
    }
    if (startDate.value) {
      params.start_date = startDate.value;
    }
    if (endDate.value) {
      params.end_date = endDate.value;
    }

    const res = await consumption.getMyConsumptions(params);
    const result = res.data;
    const items = result?.items || result || [];

    if (refresh) {
      records.value = items;
    } else {
      records.value.push(...items);
    }

    // 判断是否还有更多
    hasMore.value = items.length >= pageSize.value;
    
    if (hasMore.value) {
      page.value++;
    }
  } catch (err) {
    console.error("加载消费记录失败:", err);
  } finally {
    loading.value = false;
    loadingMore.value = false;
    uni.stopPullDownRefresh();
  }
}

/**
 * 日期选择
 */
function onStartDateChange(e: any) {
  startDate.value = e.detail.value;
  refreshList();
}

function onEndDateChange(e: any) {
  endDate.value = e.detail.value;
  refreshList();
}

/**
 * 清除日期筛选
 */
function clearDateFilter() {
  startDate.value = "";
  endDate.value = "";
  refreshList();
}

/**
 * 页面跳转
 */
function goBack() {
  uni.navigateBack();
}

function goToMonthlyBill() {
  uni.navigateTo({ url: "/pages/consumption/bill/index" });
}

onLoad((options: any) => {
  if (options.card_id) {
    cardId.value = parseInt(options.card_id);
  }
  loadRecords(true);
});

onShow(() => {
  // 页面显示时刷新列表
  loadRecords(true);
});

onPullDownRefresh(() => {
  refreshList();
});

onReachBottom(() => {
  if (hasMore.value && !loadingMore.value) {
    loadRecords();
  }
});
</script>

<style scoped>
.consumption-list-container {
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

.nav-right {
  width: 120rpx;
  text-align: right;
}

.nav-action {
  font-size: 28rpx;
  color: #4A90D9;
}

/* 类型筛选 */
.filter-section {
  background: #fff;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.filter-scroll {
  white-space: nowrap;
}

.filter-list {
  display: inline-flex;
  padding: 0 20rpx;
  gap: 16rpx;
}

.filter-item {
  display: inline-flex;
  height: 64rpx;
  padding: 0 30rpx;
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

/* 日期筛选 */
.date-section {
  display: flex;
  align-items: center;
  background: #fff;
  padding: 20rpx 30rpx;
  margin-bottom: 20rpx;
}

.date-picker {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 0;
  background: #F8F9FA;
  border-radius: 12rpx;
}

.date-label {
  font-size: 22rpx;
  color: #999;
  margin-bottom: 6rpx;
}

.date-value {
  font-size: 26rpx;
  color: #333;
  font-weight: bold;
}

.date-separator {
  width: 60rpx;
  text-align: center;
  font-size: 28rpx;
  color: #999;
}

.clear-btn {
  width: 80rpx;
  text-align: center;
  padding: 16rpx 0;
  margin-left: 16rpx;
}

.clear-btn text {
  font-size: 24rpx;
  color: #999;
}

/* 消费记录列表 */
.record-list {
  padding: 0 30rpx;
}

.record-item {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.record-left {
  margin-right: 24rpx;
}

.record-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.record-icon text {
  font-size: 40rpx;
}

.record-icon.PURCHASE {
  background: rgba(74, 144, 217, 0.1);
}

.record-icon.RENEW {
  background: rgba(82, 196, 26, 0.1);
}

.record-icon.USE {
  background: rgba(250, 173, 20, 0.1);
}

.record-icon.DEDUCT {
  background: rgba(255, 107, 107, 0.1);
}

.record-icon.REFUND {
  background: rgba(82, 196, 26, 0.1);
}

.record-center {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.record-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.record-title {
  font-size: 30rpx;
  color: #333;
  font-weight: bold;
}

.record-desc {
  font-size: 24rpx;
  color: #666;
  margin-bottom: 8rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-info {
  display: flex;
  gap: 20rpx;
}

.record-time {
  font-size: 22rpx;
  color: #999;
}

.record-card {
  font-size: 22rpx;
  color: #4A90D9;
}

.record-right {
  flex-shrink: 0;
}

.record-amount {
  font-size: 32rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.record-amount.income {
  color: #52C41A;
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
  font-size: 120rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

/* 加载更多 */
.load-more,
.no-more {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 30rpx;
  font-size: 26rpx;
  color: #999;
}
</style>
