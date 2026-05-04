<template>
  <view class="order-pay-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">支付</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 支付金额 -->
    <view class="amount-section">
      <text class="amount-label">支付金额</text>
      <view class="amount-value">
        <text class="amount-symbol">¥</text>
        <text class="amount-number">{{ formatAmount(amount) }}</text>
      </view>
    </view>

    <!-- 支付方式 -->
    <view class="payment-section">
      <view class="section-header">
        <text class="section-title">选择支付方式</text>
      </view>
      <view class="payment-list">
        <view 
          class="payment-item" 
          :class="{ selected: payMethod === 'WECHAT' }"
          @click="payMethod = 'WECHAT'"
        >
          <view class="payment-left">
            <view class="payment-icon wechat">
              <text>💬</text>
            </view>
            <view class="payment-info">
              <text class="payment-name">微信支付</text>
              <text class="payment-desc">安全便捷的支付方式</text>
            </view>
          </view>
          <view class="payment-check" :class="{ selected: payMethod === 'WECHAT' }">
            <text>✓</text>
          </view>
        </view>

        <view 
          class="payment-item" 
          :class="{ selected: payMethod === 'ALIPAY' }"
          @click="payMethod = 'ALIPAY'"
        >
          <view class="payment-left">
            <view class="payment-icon alipay">
              <text>💰</text>
            </view>
            <view class="payment-info">
              <text class="payment-name">支付宝</text>
              <text class="payment-desc">支付宝快捷支付</text>
            </view>
          </view>
          <view class="payment-check" :class="{ selected: payMethod === 'ALIPAY' }">
            <text>✓</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 订单信息 -->
    <view class="order-info-section">
      <view class="section-header">
        <text class="section-title">订单信息</text>
      </view>
      <view class="info-list" v-if="orderInfo">
        <view class="info-item">
          <text class="info-label">订单编号</text>
          <text class="info-value">{{ orderInfo.order_no }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">创建时间</text>
          <text class="info-value">{{ formatDate(orderInfo.create_time, 'YYYY-MM-DD HH:mm') }}</text>
        </view>
        <view class="info-item">
          <text class="info-label">订单金额</text>
          <text class="info-value price">¥{{ formatAmount(orderInfo.total_amount) }}</text>
        </view>
        <view class="info-item" v-if="orderInfo.discount_amount > 0">
          <text class="info-label">优惠金额</text>
          <text class="info-value discount">-¥{{ formatAmount(orderInfo.discount_amount) }}</text>
        </view>
        <view class="info-item total">
          <text class="info-label">应付金额</text>
          <text class="info-value price">¥{{ formatAmount(orderInfo.pay_amount) }}</text>
        </view>
      </view>
    </view>

    <!-- 支付安全提示 -->
    <view class="security-section">
      <view class="security-item">
        <text class="security-icon">🔒</text>
        <text class="security-text">支付安全由平台保护</text>
      </view>
      <view class="security-item">
        <text class="security-icon">🛡️</text>
        <text class="security-text">全程SSL加密传输</text>
      </view>
    </view>

    <!-- 底部支付按钮 -->
    <view class="footer-section">
      <view class="price-summary">
        <text class="price-label">应付：</text>
        <text class="price-symbol">¥</text>
        <text class="price-amount">{{ formatAmount(amount) }}</text>
      </view>
      <button class="pay-btn" :loading="paying" :disabled="paying" @click="handlePay">
        <text>{{ paying ? '支付中...' : '确认支付' }}</text>
      </button>
    </view>

    <!-- 支付结果弹窗 -->
    <view class="result-modal" v-if="showResult">
      <view class="modal-mask" @click="showResult = false"></view>
      <view class="modal-content">
        <view class="result-icon" :class="paySuccess ? 'success' : 'fail'">
          <text>{{ paySuccess ? '✓' : '✕' }}</text>
        </view>
        <text class="result-title">{{ paySuccess ? '支付成功' : '支付失败' }}</text>
        <text class="result-desc">{{ paySuccess ? '您的购买已成功，会员卡已激活' : resultMessage }}</text>
        
        <view class="result-actions">
          <button class="action-btn secondary" v-if="paySuccess" @click="goToCardList">
            <text>查看会员卡</text>
          </button>
          <button class="action-btn primary" v-if="paySuccess" @click="goToOrderList">
            <text>查看订单</text>
          </button>
          <button class="action-btn primary" v-else @click="showResult = false">
            <text>重新支付</text>
          </button>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onLoad } from "vue";
import { order } from "@/api";
import { formatDate, formatAmount, showSuccess, showError } from "@/utils";

const orderId = ref<number | null>(null);
const amount = ref(0);
const payMethod = ref("WECHAT");
const paying = ref(false);
const orderInfo = ref<any>(null);

const showResult = ref(false);
const paySuccess = ref(false);
const resultMessage = ref("");

/**
 * 加载订单信息
 */
async function loadOrderInfo(orderId: number) {
  try {
    const res = await order.getOrderDetail(orderId);
    orderInfo.value = res.data;
  } catch (err) {
    console.error("加载订单信息失败:", err);
  }
}

/**
 * 页面跳转
 */
function goBack() {
  if (showResult.value) {
    showResult.value = false;
  } else {
    uni.navigateBack();
  }
}

function goToCardList() {
  showResult.value = false;
  uni.switchTab({ url: "/pages/tabbar/card/index" });
}

function goToOrderList() {
  showResult.value = false;
  uni.redirectTo({ url: "/pages/order/list/index" });
}

/**
 * 处理支付
 */
async function handlePay() {
  if (!orderId.value) {
    showError("缺少订单信息");
    return;
  }

  paying.value = true;

  try {
    // 调用支付接口
    const res = await order.payOrder({
      order_id: orderId.value,
      pay_method: payMethod.value
    });

    // 支付成功
    paySuccess.value = true;
    resultMessage.value = "";
    showSuccess("支付成功");

    // 显示结果弹窗
    showResult.value = true;
  } catch (err: any) {
    console.error("支付失败:", err);
    paySuccess.value = false;
    resultMessage.value = err.message || "支付失败，请稍后重试";
    showResult.value = true;
  } finally {
    paying.value = false;
  }
}

onLoad((options: any) => {
  if (options.order_id) {
    orderId.value = parseInt(options.order_id);
    loadOrderInfo(orderId.value);
  }
  if (options.amount) {
    amount.value = parseFloat(options.amount);
  }
  if (options.pay_method) {
    payMethod.value = options.pay_method;
  }
});
</script>

<style scoped>
.order-pay-container {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 140rpx;
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

/* 支付金额 */
.amount-section {
  background: #fff;
  padding: 60rpx 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20rpx;
}

.amount-label {
  font-size: 28rpx;
  color: #999;
  margin-bottom: 20rpx;
}

.amount-value {
  display: flex;
  align-items: baseline;
}

.amount-symbol {
  font-size: 40rpx;
  color: #FF6B6B;
  margin-right: 8rpx;
}

.amount-number {
  font-size: 72rpx;
  font-weight: bold;
  color: #FF6B6B;
}

/* 通用区块 */
.payment-section,
.order-info-section {
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

/* 支付方式 */
.payment-list {
  padding: 0 30rpx;
}

.payment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.payment-item:last-child {
  border-bottom: none;
}

.payment-left {
  display: flex;
  align-items: center;
}

.payment-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 24rpx;
}

.payment-icon text {
  font-size: 48rpx;
}

.payment-icon.wechat {
  background: #07C160;
}

.payment-icon.alipay {
  background: #1677FF;
}

.payment-info {
  display: flex;
  flex-direction: column;
}

.payment-name {
  font-size: 30rpx;
  color: #333;
  font-weight: bold;
}

.payment-desc {
  font-size: 24rpx;
  color: #999;
  margin-top: 6rpx;
}

.payment-check {
  width: 44rpx;
  height: 44rpx;
  border: 2rpx solid #E8E8E8;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.payment-check text {
  font-size: 24rpx;
  color: #fff;
}

.payment-check.selected {
  background: #4A90D9;
  border-color: #4A90D9;
}

/* 订单信息 */
.info-list {
  padding: 0 30rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 26rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.info-item:last-child,
.info-item.total {
  border-bottom: none;
}

.info-item.total {
  padding-top: 30rpx;
  border-top: 1rpx solid #F0F0F0;
}

.info-label {
  font-size: 28rpx;
  color: #666;
}

.info-value {
  font-size: 28rpx;
  color: #333;
}

.info-value.price {
  font-weight: bold;
  color: #FF6B6B;
}

.info-value.discount {
  color: #52C41A;
}

/* 安全提示 */
.security-section {
  display: flex;
  justify-content: center;
  gap: 60rpx;
  padding: 40rpx 0;
}

.security-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.security-icon {
  font-size: 28rpx;
}

.security-text {
  font-size: 24rpx;
  color: #999;
}

/* 底部支付按钮 */
.footer-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.price-summary {
  display: flex;
  align-items: baseline;
}

.price-label {
  font-size: 28rpx;
  color: #333;
}

.price-symbol {
  font-size: 24rpx;
  color: #FF6B6B;
  margin-left: 8rpx;
}

.price-amount {
  font-size: 44rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.pay-btn {
  min-width: 280rpx;
  height: 96rpx;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: #fff;
  font-size: 32rpx;
  font-weight: bold;
  border-radius: 48rpx;
  border: none;
}

.pay-btn:disabled {
  opacity: 0.7;
}

/* 结果弹窗 */
.result-modal {
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
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 75%;
  background: #fff;
  border-radius: 24rpx;
  padding: 60rpx 40rpx 40rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.result-icon {
  width: 120rpx;
  height: 120rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 30rpx;
}

.result-icon.success {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.result-icon.fail {
  background: linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%);
}

.result-icon text {
  font-size: 64rpx;
  color: #fff;
  font-weight: bold;
}

.result-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 16rpx;
}

.result-desc {
  font-size: 26rpx;
  color: #999;
  text-align: center;
  margin-bottom: 40rpx;
}

.result-actions {
  display: flex;
  gap: 20rpx;
  width: 100%;
}

.action-btn {
  flex: 1;
  height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.action-btn.secondary {
  background: #F5F5F5;
  color: #666;
}

.action-btn.primary {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
}
</style>
