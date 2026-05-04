<template>
  <view class="order-detail-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">订单详情</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-section" v-if="loading">
      <text>加载中...</text>
    </view>

    <!-- 订单详情内容 -->
    <view v-else-if="orderInfo">
      <!-- 订单状态 -->
      <view class="status-section" :class="orderInfo.status">
        <view class="status-icon">
          <text>{{ getStatusIcon(orderInfo.status) }}</text>
        </view>
        <view class="status-info">
          <text class="status-text">{{ getStatusText(orderInfo.status) }}</text>
          <text class="status-desc" v-if="orderInfo.status === 'PENDING'">
            请在30分钟内完成支付
          </text>
          <text class="status-desc" v-else-if="orderInfo.status === 'PAID'">
            订单已完成，会员卡已激活
          </text>
        </view>
      </view>

      <!-- 商品信息 -->
      <view class="goods-section">
        <view class="section-header">
          <text class="section-title">商品信息</text>
        </view>
        <view class="goods-card">
          <view class="goods-icon" :class="getIconClass(orderInfo.order_type)">
            <text>{{ getOrderTypeIcon(orderInfo.order_type) }}</text>
          </view>
          <view class="goods-info">
            <text class="goods-name">{{ orderInfo.goods_name || getOrderTypeName(orderInfo.order_type) }}</text>
            <view class="goods-spec" v-if="orderInfo.quantity">
              <text>数量：{{ orderInfo.quantity }}</text>
            </view>
          </view>
        </view>
      </view>

      <!-- 订单信息 -->
      <view class="info-section">
        <view class="section-header">
          <text class="section-title">订单信息</text>
        </view>
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">订单编号</text>
            <text class="info-value">{{ orderInfo.order_no }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">创建时间</text>
            <text class="info-value">{{ formatDate(orderInfo.create_time, 'YYYY-MM-DD HH:mm:ss') }}</text>
          </view>
          <view class="info-item" v-if="orderInfo.pay_time">
            <text class="info-label">支付时间</text>
            <text class="info-value">{{ formatDate(orderInfo.pay_time, 'YYYY-MM-DD HH:mm:ss') }}</text>
          </view>
          <view class="info-item" v-if="orderInfo.pay_method">
            <text class="info-label">支付方式</text>
            <text class="info-value">{{ getPayMethodText(orderInfo.pay_method) }}</text>
          </view>
        </view>
      </view>

      <!-- 金额明细 -->
      <view class="price-section">
        <view class="section-header">
          <text class="section-title">金额明细</text>
        </view>
        <view class="price-list">
          <view class="price-item">
            <text class="price-label">商品金额</text>
            <text class="price-value">¥{{ formatAmount(orderInfo.total_amount) }}</text>
          </view>
          <view class="price-item" v-if="orderInfo.discount_amount > 0">
            <text class="price-label">优惠金额</text>
            <text class="price-value discount">-¥{{ formatAmount(orderInfo.discount_amount) }}</text>
          </view>
          <view class="price-item" v-if="orderInfo.promotion_name">
            <text class="price-label">优惠活动</text>
            <text class="price-value promotion">{{ orderInfo.promotion_name }}</text>
          </view>
          <view class="price-item total">
            <text class="price-label">实付金额</text>
            <text class="price-value">¥{{ formatAmount(orderInfo.pay_amount) }}</text>
          </view>
        </view>
      </view>

      <!-- 关联会员卡 -->
      <view class="card-section" v-if="relatedCard">
        <view class="section-header">
          <text class="section-title">关联会员卡</text>
        </view>
        <view class="card-info" @click="goToCardDetail">
          <view class="card-icon">
            <text>💳</text>
          </view>
          <view class="card-detail">
            <text class="card-name">{{ relatedCard.display_name }}</text>
            <text class="card-number">{{ formatCardNumber(relatedCard.card_number) }}</text>
          </view>
          <view class="card-arrow">
            <text>›</text>
          </view>
        </view>
      </view>

      <!-- 订单备注 -->
      <view class="remark-section" v-if="orderInfo.remarks">
        <view class="section-header">
          <text class="section-title">订单备注</text>
        </view>
        <view class="remark-content">
          <text>{{ orderInfo.remarks }}</text>
        </view>
      </view>

      <!-- 底部操作栏 -->
      <view class="footer-section" v-if="orderInfo.status === 'PENDING'">
        <button class="action-btn cancel" @click="handleCancel">
          <text>取消订单</text>
        </button>
        <button class="action-btn pay" :loading="paying" @click="handlePay">
          <text>{{ paying ? '支付中...' : '去支付' }}</text>
        </button>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-section" v-else-if="!loading && !orderInfo">
      <view class="empty-icon">
        <text>📋</text>
      </view>
      <text class="empty-text">订单不存在</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, onLoad } from "vue";
import { order, card } from "@/api";
import { formatDate, formatAmount, showConfirm, showSuccess } from "@/utils";

const orderId = ref<number | null>(null);
const loading = ref(true);
const paying = ref(false);
const orderInfo = ref<any>(null);
const relatedCard = ref<any>(null);

/**
 * 获取状态图标
 */
function getStatusIcon(status: string) {
  const map: Record<string, string> = {
    "PENDING": "⏳",
    "PAID": "✓",
    "CANCELLED": "✕",
    "EXPIRED": "⏰",
    "REFUNDED": "↩️",
    "FAILED": "✗"
  };
  return map[status] || "📋";
}

/**
 * 获取状态文本
 */
function getStatusText(status: string) {
  const map: Record<string, string> = {
    "PENDING": "待支付",
    "PAID": "支付成功",
    "CANCELLED": "已取消",
    "EXPIRED": "已过期",
    "REFUNDED": "已退款",
    "FAILED": "支付失败"
  };
  return map[status] || "未知状态";
}

/**
 * 获取订单类型图标
 */
function getOrderTypeIcon(type: string) {
  const map: Record<string, string> = {
    "PURCHASE": "💳",
    "RENEW": "🔄",
    "GOODS": "🛍️",
    "SERVICE": "💼"
  };
  return map[type] || "📋";
}

/**
 * 获取订单类型名称
 */
function getOrderTypeName(type: string) {
  const map: Record<string, string> = {
    "PURCHASE": "购买会员卡",
    "RENEW": "续费会员卡",
    "GOODS": "购买商品",
    "SERVICE": "购买服务"
  };
  return map[type] || "订单";
}

/**
 * 获取图标样式类
 */
function getIconClass(type: string) {
  const map: Record<string, string> = {
    "PURCHASE": "type-purchase",
    "RENEW": "type-renew",
    "GOODS": "type-goods",
    "SERVICE": "type-service"
  };
  return map[type] || "type-default";
}

/**
 * 获取支付方式文本
 */
function getPayMethodText(method: string) {
  const map: Record<string, string> = {
    "WECHAT": "微信支付",
    "ALIPAY": "支付宝",
    "BALANCE": "余额支付",
    "CASH": "现金支付"
  };
  return map[method] || "其他支付";
}

/**
 * 格式化卡号
 */
function formatCardNumber(number: string) {
  if (!number) return "";
  if (number.length === 12) {
    return `${number.slice(0, 4)} **** ${number.slice(-4)}`;
  }
  return number;
}

/**
 * 加载订单详情
 */
async function loadOrderDetail(id: number) {
  loading.value = true;
  try {
    const res = await order.getOrderDetail(id);
    orderInfo.value = res.data;
  } catch (err) {
    console.error("加载订单详情失败:", err);
  } finally {
    loading.value = false;
  }
}

/**
 * 页面跳转
 */
function goBack() {
  uni.navigateBack();
}

function goToCardDetail() {
  if (relatedCard.value) {
    uni.navigateTo({ url: `/pages/card/detail/index?id=${relatedCard.value.id}` });
  }
}

/**
 * 取消订单
 */
async function handleCancel() {
  if (!orderInfo.value) return;

  try {
    const confirmed = await showConfirm("确定要取消订单吗？", "取消后订单将无法恢复");
    if (confirmed) {
      await order.cancelOrder(orderInfo.value.id);
      showSuccess("已取消订单");
      // 刷新订单信息
      loadOrderDetail(orderId.value!);
    }
  } catch (err) {
    console.error("取消订单失败:", err);
  }
}

/**
 * 去支付
 */
function handlePay() {
  if (!orderInfo.value) return;

  uni.navigateTo({
    url: `/pages/order/pay/index?order_id=${orderInfo.value.id}&amount=${orderInfo.value.pay_amount}`
  });
}

onLoad((options: any) => {
  if (options.id) {
    orderId.value = parseInt(options.id);
    loadOrderDetail(orderId.value);
  }
});
</script>

<style scoped>
.order-detail-container {
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
  font-size: 120rpx;
  margin-bottom: 30rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #999;
}

/* 状态区域 */
.status-section {
  padding: 40rpx 30rpx;
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.status-section.PENDING {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.status-section.PAID {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.status-section.CANCELLED,
.status-section.EXPIRED,
.status-section.REFUNDED {
  background: linear-gradient(135deg, #8C8C8C 0%, #A8A8A8 100%);
}

.status-section.FAILED {
  background: linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%);
}

.status-icon {
  width: 96rpx;
  height: 96rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 24rpx;
}

.status-icon text {
  font-size: 48rpx;
  color: #fff;
}

.status-info {
  display: flex;
  flex-direction: column;
}

.status-text {
  font-size: 36rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8rpx;
}

.status-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
}

/* 通用区块 */
.goods-section,
.info-section,
.price-section,
.card-section,
.remark-section {
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

/* 商品信息 */
.goods-card {
  display: flex;
  align-items: center;
  padding: 30rpx;
}

.goods-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 16rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 24rpx;
}

.goods-icon text {
  font-size: 48rpx;
}

.goods-icon.type-purchase {
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
}

.goods-icon.type-renew {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.goods-icon.type-goods {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.goods-icon.type-service {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.goods-icon.type-default {
  background: linear-gradient(135deg, #8C8C8C 0%, #A8A8A8 100%);
}

.goods-info {
  display: flex;
  flex-direction: column;
}

.goods-name {
  font-size: 32rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 12rpx;
}

.goods-spec {
  font-size: 26rpx;
  color: #999;
}

/* 信息列表 */
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

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 28rpx;
  color: #666;
}

.info-value {
  font-size: 28rpx;
  color: #333;
  font-family: monospace;
}

/* 价格列表 */
.price-list {
  padding: 0 30rpx;
}

.price-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
}

.price-item.total {
  padding-top: 30rpx;
  border-top: 1rpx solid #F0F0F0;
}

.price-label {
  font-size: 28rpx;
  color: #666;
}

.price-value {
  font-size: 28rpx;
  color: #333;
}

.price-value.discount {
  color: #52C41A;
}

.price-value.promotion {
  color: #FF6B6B;
}

.price-item.total .price-label {
  font-weight: bold;
  color: #333;
}

.price-item.total .price-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #FF6B6B;
}

/* 关联会员卡 */
.card-info {
  display: flex;
  align-items: center;
  padding: 30rpx;
}

.card-icon {
  width: 72rpx;
  height: 72rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
}

.card-icon text {
  font-size: 36rpx;
  color: #fff;
}

.card-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-name {
  font-size: 30rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 6rpx;
}

.card-number {
  font-size: 24rpx;
  color: #999;
  font-family: monospace;
}

.card-arrow {
  font-size: 40rpx;
  color: #CCC;
}

/* 订单备注 */
.remark-content {
  padding: 30rpx;
  font-size: 28rpx;
  color: #666;
  line-height: 1.6;
}

/* 底部操作栏 */
.footer-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  display: flex;
  justify-content: flex-end;
  gap: 20rpx;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
  min-width: 200rpx;
  height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.action-btn.cancel {
  background: #F5F5F5;
  color: #666;
}

.action-btn.pay {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: #fff;
}
</style>
