<template>
  <view class="bill-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">月度账单</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 月份选择 -->
    <view class="month-selector">
      <view class="selector-content">
        <view class="selector-btn" @click="prevMonth">
          <text>‹</text>
        </view>
        <view class="selector-month" @click="showMonthPicker = true">
          <text class="year-text">{{ currentYear }}年</text>
          <text class="month-text">{{ currentMonth }}月</text>
          <text class="arrow">▼</text>
        </view>
        <view class="selector-btn" @click="nextMonth">
          <text>›</text>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-section" v-if="loading">
      <text>加载中...</text>
    </view>

    <!-- 账单内容 -->
    <view v-else-if="billData">
      <!-- 统计概览 -->
      <view class="overview-section">
        <view class="overview-card">
          <view class="overview-item income">
            <view class="overview-header">
              <text class="overview-label">收入</text>
              <text class="overview-icon">📈</text>
            </view>
            <text class="overview-value income">¥{{ formatAmount(billData.total_income || 0) }}</text>
            <text class="overview-count">{{ billData.income_count || 0 }} 笔</text>
          </view>
          <view class="overview-divider"></view>
          <view class="overview-item expense">
            <view class="overview-header">
              <text class="overview-label">支出</text>
              <text class="overview-icon">📉</text>
            </view>
            <text class="overview-value expense">¥{{ formatAmount(billData.total_expense || 0) }}</text>
            <text class="overview-count">{{ billData.expense_count || 0 }} 笔</text>
          </view>
        </view>
        <view class="net-section">
          <text class="net-label">本月收支结余：</text>
          <text class="net-value" :class="{ positive: (billData.total_income || 0) >= (billData.total_expense || 0) }">
            ¥{{ formatAmount((billData.total_income || 0) - (billData.total_expense || 0)) }}
          </text>
        </view>
      </view>

      <!-- 支出分类统计 -->
      <view class="category-section" v-if="billData.category_summary && billData.category_summary.length > 0">
        <view class="section-header">
          <text class="section-title">支出分类</text>
        </view>
        <view class="category-list">
          <view 
            class="category-item" 
            v-for="(item, index) in billData.category_summary" 
            :key="index"
          >
            <view class="category-left">
              <view class="category-icon">
                <text>{{ getCategoryIcon(item.record_type) }}</text>
              </view>
              <view class="category-info">
                <text class="category-name">{{ getCategoryName(item.record_type) }}</text>
                <text class="category-count">{{ item.count }} 笔</text>
              </view>
            </view>
            <view class="category-right">
              <text class="category-amount">¥{{ formatAmount(item.total_amount) }}</text>
              <text class="category-percent">{{ getPercent(item.total_amount, billData.total_expense) }}%</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 消费趋势图表（模拟） -->
      <view class="trend-section" v-if="billData.daily_summary && billData.daily_summary.length > 0">
        <view class="section-header">
          <text class="section-title">每日消费趋势</text>
        </view>
        <view class="trend-chart">
          <view class="chart-item" v-for="(item, index) in chartData" :key="index">
            <view class="chart-bar">
              <view 
                class="bar-fill" 
                :style="{ height: getBarHeight(item.amount, maxAmount) + '%' }"
              ></view>
            </view>
            <text class="chart-label">{{ item.day }}</text>
          </view>
        </view>
      </view>

      <!-- 账单明细 -->
      <view class="detail-section">
        <view class="section-header">
          <text class="section-title">账单明细</text>
          <text class="section-more" @click="goToRecords">查看全部 ></text>
        </view>
        <view class="detail-list" v-if="billData.records && billData.records.length > 0">
          <view 
            class="detail-item" 
            v-for="(record, index) in billData.records.slice(0, 10)" 
            :key="record.id"
          >
            <view class="detail-left">
              <view class="detail-icon" :class="record.record_type">
                <text>{{ getCategoryIcon(record.record_type) }}</text>
              </view>
              <view class="detail-info">
                <text class="detail-title">{{ getCategoryName(record.record_type) }}</text>
                <text class="detail-desc" v-if="record.description">{{ record.description }}</text>
              </view>
            </view>
            <view class="detail-right">
              <text class="detail-amount" :class="{ income: isIncome(record.record_type) }">
                {{ isIncome(record.record_type) ? '+' : '-' }}{{ formatAmount(record.amount || 0) }}
              </text>
              <text class="detail-time">{{ formatDate(record.create_time, 'MM-DD') }}</text>
            </view>
          </view>
        </view>
        <view class="empty-detail" v-else>
          <text>本月暂无账单明细</text>
        </view>
      </view>

      <!-- 导出按钮 -->
      <view class="export-section">
        <button class="export-btn" @click="handleExport">
          <text>📄 导出账单</text>
        </button>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-section" v-else-if="!loading && !billData">
      <view class="empty-icon">
        <text>📄</text>
      </view>
      <text class="empty-text">暂无账单数据</text>
    </view>

    <!-- 月份选择弹窗 -->
    <view class="month-modal" v-if="showMonthPicker">
      <view class="modal-mask" @click="showMonthPicker = false"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">选择月份</text>
          <view class="modal-close" @click="showMonthPicker = false">
            <text>×</text>
          </view>
        </view>
        
        <view class="year-selector">
          <view class="year-btn" @click="prevYear">
            <text>‹</text>
          </view>
          <text class="current-year-text">{{ currentYear }}年</text>
          <view class="year-btn" @click="nextYear">
            <text>›</text>
          </view>
        </view>

        <view class="month-grid">
          <view 
            class="month-cell" 
            :class="{ active: m === currentMonth, disabled: isFutureMonth(m) }"
            v-for="m in 12" 
            :key="m"
            @click="selectMonth(m)"
          >
            <text>{{ m }}月</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onLoad } from "vue";
import { consumption } from "@/api";
import { formatDate, formatAmount, showSuccess, showError } from "@/utils";

const currentYear = ref(new Date().getFullYear());
const currentMonth = ref(new Date().getMonth() + 1);
const loading = ref(false);
const billData = ref<any>(null);
const showMonthPicker = ref(false);

const today = new Date();
const maxYear = ref(today.getFullYear());
const maxMonth = ref(today.getMonth() + 1);

/**
 * 图表数据
 */
const chartData = computed(() => {
  if (!billData.value?.daily_summary) {
    return [];
  }
  
  // 取最近7天的数据
  const summary = billData.value.daily_summary.slice(-7);
  return summary.map((item: any) => ({
    day: item.day || item.date?.slice(-2) || '',
    amount: item.total_amount || 0
  }));
});

const maxAmount = computed(() => {
  if (chartData.value.length === 0) return 0;
  return Math.max(...chartData.value.map((d: any) => d.amount), 100);
});

/**
 * 获取分类图标
 */
function getCategoryIcon(type: string) {
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
 * 获取分类名称
 */
function getCategoryName(type: string) {
  const map: Record<string, string> = {
    "PURCHASE": "购卡",
    "RENEW": "续费",
    "USE": "使用",
    "DEDUCT": "扣费",
    "REFUND": "退款"
  };
  return map[type] || "其他";
}

/**
 * 判断是否是收入
 */
function isIncome(type: string) {
  return type === "REFUND";
}

/**
 * 计算百分比
 */
function getPercent(amount: number, total: number) {
  if (!total) return 0;
  return ((amount / total) * 100).toFixed(1);
}

/**
 * 计算柱状图高度
 */
function getBarHeight(amount: number, max: number) {
  if (!max) return 0;
  return Math.min((amount / max) * 100, 100);
}

/**
 * 判断是否是未来月份
 */
function isFutureMonth(month: number) {
  if (currentYear.value > maxYear.value) return true;
  if (currentYear.value === maxYear.value && month > maxMonth.value) return true;
  return false;
}

/**
 * 加载账单数据
 */
async function loadBillData() {
  loading.value = true;
  try {
    const res = await consumption.getMonthlyBill(currentYear.value, currentMonth.value);
    billData.value = res.data;
  } catch (err) {
    console.error("加载账单失败:", err);
    billData.value = null;
  } finally {
    loading.value = false;
  }
}

/**
 * 月份导航
 */
function prevMonth() {
  if (currentMonth.value > 1) {
    currentMonth.value--;
  } else {
    currentMonth.value = 12;
    currentYear.value--;
  }
  loadBillData();
}

function nextMonth() {
  // 不能超过当前月份
  if (currentYear.value === maxYear.value && currentMonth.value >= maxMonth.value) {
    return;
  }
  
  if (currentMonth.value < 12) {
    currentMonth.value++;
  } else {
    currentMonth.value = 1;
    currentYear.value++;
  }
  loadBillData();
}

function prevYear() {
  currentYear.value--;
}

function nextYear() {
  if (currentYear.value < maxYear.value) {
    currentYear.value++;
  }
}

function selectMonth(month: number) {
  if (isFutureMonth(month)) return;
  
  currentMonth.value = month;
  showMonthPicker.value = false;
  loadBillData();
}

/**
 * 页面跳转
 */
function goBack() {
  uni.navigateBack();
}

function goToRecords() {
  uni.navigateTo({ 
    url: `/pages/consumption/list/index?start_date=${currentYear}-${currentMonth}-01&end_date=${currentYear}-${currentMonth}-31` 
  });
}

/**
 * 导出账单
 */
function handleExport() {
  showSuccess("账单导出功能开发中");
}

onLoad(() => {
  loadBillData();
});
</script>

<style scoped>
.bill-container {
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

.nav-placeholder {
  width: 60rpx;
}

/* 月份选择 */
.month-selector {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  padding: 30rpx 0;
}

.selector-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40rpx;
}

.selector-btn {
  width: 64rpx;
  height: 64rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.selector-btn text {
  font-size: 32rpx;
  color: #fff;
}

.selector-month {
  display: flex;
  align-items: baseline;
  gap: 8rpx;
}

.year-text {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.8);
}

.month-text {
  font-size: 48rpx;
  font-weight: bold;
  color: #fff;
}

.arrow {
  font-size: 20rpx;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 8rpx;
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

/* 统计概览 */
.overview-section {
  background: #fff;
  margin: 20rpx 30rpx;
  border-radius: 20rpx;
  padding: 30rpx;
}

.overview-card {
  display: flex;
  margin-bottom: 30rpx;
}

.overview-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.overview-item.income {
  align-items: flex-start;
}

.overview-item.expense {
  align-items: flex-end;
}

.overview-header {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.overview-label {
  font-size: 26rpx;
  color: #999;
}

.overview-icon {
  font-size: 28rpx;
  margin-left: 8rpx;
}

.overview-value {
  font-size: 44rpx;
  font-weight: bold;
}

.overview-value.income {
  color: #52C41A;
}

.overview-value.expense {
  color: #FF6B6B;
}

.overview-count {
  font-size: 22rpx;
  color: #999;
  margin-top: 6rpx;
}

.overview-divider {
  width: 2rpx;
  background: #F0F0F0;
  margin: 0 30rpx;
}

.net-section {
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 30rpx;
  border-top: 1rpx solid #F0F0F0;
}

.net-label {
  font-size: 28rpx;
  color: #666;
}

.net-value {
  font-size: 32rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.net-value.positive {
  color: #52C41A;
}

/* 支出分类 */
.category-section {
  background: #fff;
  margin: 0 30rpx 20rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.section-header {
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

.category-list {
  padding: 0 30rpx;
}

.category-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 26rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.category-item:last-child {
  border-bottom: none;
}

.category-left {
  display: flex;
  align-items: center;
}

.category-icon {
  width: 64rpx;
  height: 64rpx;
  background: #F5F5F5;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
}

.category-icon text {
  font-size: 32rpx;
}

.category-info {
  display: flex;
  flex-direction: column;
}

.category-name {
  font-size: 28rpx;
  color: #333;
}

.category-count {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
}

.category-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.category-amount {
  font-size: 30rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.category-percent {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
}

/* 趋势图表 */
.trend-section {
  background: #fff;
  margin: 0 30rpx 20rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.trend-chart {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding: 30rpx;
  height: 280rpx;
}

.chart-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.chart-bar {
  flex: 1;
  width: 40rpx;
  background: #F0F0F0;
  border-radius: 8rpx 8rpx 0 0;
  margin-bottom: 12rpx;
  display: flex;
  align-items: flex-end;
}

.bar-fill {
  width: 100%;
  background: linear-gradient(180deg, #4A90D9 0%, #6BA8E0 100%);
  border-radius: 8rpx 8rpx 0 0;
  transition: height 0.3s ease;
}

.chart-label {
  font-size: 20rpx;
  color: #999;
}

/* 账单明细 */
.detail-section {
  background: #fff;
  margin: 0 30rpx 20rpx;
  border-radius: 20rpx;
  overflow: hidden;
}

.detail-section .section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-list {
  padding: 0 30rpx;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-left {
  display: flex;
  align-items: center;
}

.detail-icon {
  width: 56rpx;
  height: 56rpx;
  background: #F5F5F5;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 16rpx;
}

.detail-icon text {
  font-size: 28rpx;
}

.detail-info {
  display: flex;
  flex-direction: column;
}

.detail-title {
  font-size: 28rpx;
  color: #333;
}

.detail-desc {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300rpx;
}

.detail-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.detail-amount {
  font-size: 28rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.detail-amount.income {
  color: #52C41A;
}

.detail-time {
  font-size: 22rpx;
  color: #999;
  margin-top: 4rpx;
}

.empty-detail {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 60rpx;
  font-size: 26rpx;
  color: #999;
}

/* 导出按钮 */
.export-section {
  padding: 20rpx 30rpx 40rpx;
}

.export-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 30rpx;
  border-radius: 44rpx;
  border: none;
}

.export-btn:active {
  opacity: 0.9;
}

/* 月份选择弹窗 */
.month-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
}

.modal-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
}

.modal-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  border-radius: 40rpx 40rpx 0 0;
  padding-bottom: calc(30rpx + env(safe-area-inset-bottom));
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #F0F0F0;
}

.modal-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
}

.modal-close {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40rpx;
  color: #999;
}

.year-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 60rpx;
  padding: 30rpx;
}

.year-btn {
  width: 56rpx;
  height: 56rpx;
  background: #F5F5F5;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.year-btn text {
  font-size: 28rpx;
  color: #666;
}

.current-year-text {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20rpx;
  padding: 0 30rpx 30rpx;
}

.month-cell {
  height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #F8F9FA;
  border-radius: 16rpx;
  font-size: 28rpx;
  color: #333;
}

.month-cell.active {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
}

.month-cell.disabled {
  color: #CCC;
}
</style>
