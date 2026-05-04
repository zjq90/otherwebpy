<template>
  <view class="order-list-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">我的订单</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 状态筛选 -->
    <view class="filter-section">
      <scroll-view scroll-x class="filter-scroll">
        <view class="filter-list">
          <view 
            class="filter-item" 
            :class="{ active: currentStatus === '' }"
            @click="currentStatus = ''; refreshList()"
          >
            <text>全部</text>
            <view class="filter-badge" v-if="counts.total > 0">
              <text>{{ counts.total }}</text>
            </view>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentStatus === 'PENDING' }"
            @click="currentStatus = 'PENDING'; refreshList()"
          >
            <text>待支付</text>
            <view class="filter-badge" v-if="counts.pending > 0">
              <text>{{ counts.pending }}</text>
            </view>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentStatus === 'PAID' }"
            @click="currentStatus = 'PAID'; refreshList()"
          >
            <text>已支付</text>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentStatus === 'CANCELLED' }"
            @click="currentStatus = 'CANCELLED'; refreshList()"
          >
            <text>已取消</text>
          </view>
          <view 
            class="filter-item" 
            :class="{ active: currentStatus === 'EXPIRED' }"
            @click="currentStatus = 'EXPIRED'; refreshList()"
          >
            <text>已过期</text>
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 订单列表 -->
    <view class="order-list" v-if="!loading && orders.length > 0">
      <view 
        class="order-card" 
        v-for="(order, index) in orders" 
        :key="order.id"
        @click="goToOrderDetail(order.id)"
      >
        <view class="order-header">
          <view class="order-left">
            <text class="order-no">订单号：{{ order.order_no }}</text>
          </view>
          <view class="order-right">
            <text class="order-status" :class="order.status">
              {{ getStatusText(order.status) }}
            </text>
          </view>
        </view>

        <view class="order-content">
          <view class="order-icon" :class="getIconClass(order.order_type)">
            <text>{{ getOrderTypeIcon(order.order_type) }}</text>
          </view>
          <view class="order-info">
            <text class="order-name">{{ order.goods_name || getOrderTypeName(order.order_type) }}</text>
            <view class="order-spec" v-if="order.quantity">
              <text>数量：{{ order.quantity }}</text>
            </view>
            <text class="order-time">{{ formatDate(order.create_time, 'YYYY-MM-DD HH:mm') }}</text>
          </view>
          <view class="order-price">
            <text class="price-symbol">¥</text>
            <text class="price-amount">{{ formatAmount(order.pay_amount || order.total_amount) }}</text>
          </view>
        </view>

        <view class="order-footer" v-if="order.status === 'PENDING'">
          <view class="footer-actions">
            <button class="action-btn cancel" @click.stop="handleCancel(order)">
              <text>取消订单</text>
            </button>
            <button class="action-btn pay" @click.stop="goToPay(order)">
              <text>去支付</text>
            </button>
          </view>
        </view>
      </view>
    </view>

    <!-- 加载状态 -->
    <view class="loading-section" v-if="loading">
      <text>加载中...</text>
    </view>

    <!-- 空状态 -->
    <view class="empty-section" v-else-if="!loading && orders.length === 0">
      <view class="empty-icon">
        <text>📋</text>
      </view>
      <text class="empty-text">{{ emptyText }}</text>
      <button class="empty-btn" @click="goToShop">去逛逛</button>
    </view>

    <!-- 加载更多 -->
    <view class="load-more" v-if="hasMore && !loading">
      <text>{{ loadingMore ? '加载中...' : '上拉加载更多' }}</text>
    </view>
    <view class="no-more" v-if="!hasMore && orders.length > 0">
      <text>没有更多了</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onLoad, onShow, onPullDownRefresh, onReachBottom } from "vue";
import { order } from "@/api";
import { formatDate, formatAmount, showConfirm, showSuccess, showError } from "@/utils";

const currentStatus = ref("");
const loading = ref(false);
const loadingMore = ref(false);
const orders = ref<any[]>([]);
const page = ref(1);
const pageSize = ref(10);
const hasMore = ref(true);

const counts = ref({
  total: 0,
  pending: 0
});

const emptyText = computed(() => {
  if (currentStatus.value === "PENDING") {
    return "暂无待支付订单";
  } else if (currentStatus.value === "PAID") {
    return "暂无已支付订单";
  } else if (currentStatus.value === "CANCELLED") {
    return "暂无已取消订单";
  } else if (currentStatus.value === "EXPIRED") {
    return "暂无已过期订单";
  }
  return "暂无订单";
});

/**
 * 获取状态文本
 */
function getStatusText(status: string) {
  const map: Record<string, string> = {
    "PENDING": "待支付",
    "PAID": "已支付",
    "CANCELLED": "已取消",
    "EXPIRED": "已过期",
    "REFUNDED": "已退款",
    "FAILED": "支付失败"
  };
  return map[status] || "未知";
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
 * 刷新列表
 */
function refreshList() {
  page.value = 1;
  hasMore.value = true;
  orders.value = [];
  loadOrders(true);
}

/**
 * 加载订单列表
 */
async function loadOrders(refresh: boolean = false) {
  if (refresh) {
    loading.value = true;
  } else {
    loadingMore.value = true;
  }

  try {
    const res = await order.getMyOrders({
      status: currentStatus.value || undefined,
      page: page.value,
      page_size: pageSize.value
    });

    const result = res.data;
    const items = result?.items || result || [];

    if (refresh) {
      orders.value = items;
    } else {
      orders.value.push(...items);
    }

    // 判断是否还有更多
    hasMore.value = items.length >= pageSize.value;
    
    if (hasMore.value) {
      page.value++;
    }
  } catch (err) {
    console.error("加载订单列表失败:", err);
  } finally {
    loading.value = false;
    loadingMore.value = false;
    uni.stopPullDownRefresh();
  }
}

/**
 * 页面跳转
 */
function goBack() {
  uni.navigateBack();
}

function goToOrderDetail(orderId: number) {
  uni.navigateTo({ url: `/pages/order/detail/index?id=${orderId}` });
}

function goToShop() {
  uni.switchTab({ url: "/pages/tabbar/shop/index" });
}

function goToPay(orderItem: any) {
  uni.navigateTo({
    url: `/pages/order/pay/index?order_id=${orderItem.id}&amount=${orderItem.pay_amount || orderItem.total_amount}`
  });
}

/**
 * 取消订单
 */
async function handleCancel(orderItem: any) {
  try {
    const confirmed = await showConfirm("确定要取消订单吗？", "取消后订单将无法恢复");
    if (confirmed) {
      await order.cancelOrder(orderItem.id);
      showSuccess("已取消订单");
      refreshList();
    }
  } catch (err) {
    console.error("取消订单失败:", err);
  }
}

onLoad(() => {
  loadOrders(true);
});

onShow(() => {
  // 页面显示时刷新订单列表
  loadOrders(true);
});

onPullDownRefresh(() => {
  refreshList();
});

onReachBottom(() => {
  if (hasMore.value && !loadingMore.value) {
    loadOrders();
  }
});
</script>

<style scoped>
.order-list-container {
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

/* 状态筛选 */
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
  align-items: center;
  height: 64rpx;
  padding: 0 30rpx;
  border-radius: 32rpx;
  font-size: 28rpx;
  color: #666;
  background: #F5F5F5;
  position: relative;
}

.filter-item.active {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
}

.filter-badge {
  position: absolute;
  top: -8rpx;
  right: -8rpx;
  min-width: 32rpx;
  height: 32rpx;
  background: #FF4D4F;
  border-radius: 16rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 6rpx;
}

.filter-badge text {
  font-size: 20rpx;
  color: #fff;
}

/* 订单列表 */
.order-list {
  padding: 20rpx 30rpx;
}

.order-card {
  background: #fff;
  border-radius: 20rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #F0F0F0;
}

.order-no {
  font-size: 24rpx;
  color: #999;
}

.order-status {
  font-size: 26rpx;
  font-weight: bold;
}

.order-status.PENDING {
  color: #FAAD14;
}

.order-status.PAID {
  color: #52C41A;
}

.order-status.CANCELLED,
.order-status.EXPIRED,
.order-status.REFUNDED {
  color: #999;
}

.order-status.FAILED {
  color: #FF4D4F;
}

.order-content {
  display: flex;
  align-items: center;
  padding: 30rpx;
}

.order-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 16rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 24rpx;
}

.order-icon text {
  font-size: 48rpx;
}

.order-icon.type-purchase {
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
}

.order-icon.type-renew {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.order-icon.type-goods {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.order-icon.type-service {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.order-icon.type-default {
  background: linear-gradient(135deg, #8C8C8C 0%, #A8A8A8 100%);
}

.order-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.order-name {
  font-size: 30rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 8rpx;
}

.order-spec {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.order-time {
  font-size: 22rpx;
  color: #CCC;
}

.order-price {
  display: flex;
  align-items: baseline;
}

.price-symbol {
  font-size: 24rpx;
  color: #FF6B6B;
  margin-right: 4rpx;
}

.price-amount {
  font-size: 36rpx;
  font-weight: bold;
  color: #FF6B6B;
}

/* 订单底部操作 */
.order-footer {
  padding: 20rpx 30rpx;
  border-top: 1rpx solid #F0F0F0;
  background: #FAFAFA;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 20rpx;
}

.action-btn {
  height: 64rpx;
  padding: 0 36rpx;
  border-radius: 32rpx;
  font-size: 26rpx;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn.cancel {
  background: #F5F5F5;
  color: #666;
}

.action-btn.pay {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: #fff;
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
  margin-bottom: 40rpx;
}

.empty-btn {
  width: 240rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 28rpx;
  border-radius: 40rpx;
  border: none;
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
