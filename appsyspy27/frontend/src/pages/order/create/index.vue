<template>
  <view class="order-create-container">
    <!-- 头部导航 -->
    <view class="nav-header">
      <view class="nav-back" @click="goBack">
        <text>‹</text>
      </view>
      <text class="nav-title">确认订单</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 商品信息 -->
    <view class="goods-section">
      <view class="section-header">
        <text class="section-title">购买商品</text>
      </view>
      <view class="goods-card" :class="getCardClass(cardCategory)">
        <view class="goods-info">
          <view class="goods-icon">
            <text>{{ getCategoryIcon(cardCategory) }}</text>
          </view>
          <view class="goods-detail">
            <text class="goods-name">{{ cardName }}</text>
            <text class="goods-category">{{ getCategoryName(cardCategory) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 数量选择 -->
    <view class="quantity-section">
      <view class="section-header">
        <text class="section-title">购买数量</text>
      </view>
      <view class="quantity-wrapper">
        <view class="quantity-control">
          <view class="control-btn" @click="decreaseQuantity" :class="{ disabled: quantity <= 1 }">
            <text>−</text>
          </view>
          <text class="quantity-value">{{ quantity }}</text>
          <view class="control-btn" @click="increaseQuantity">
            <text>+</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 优惠选择 -->
    <view class="promotion-section" v-if="promotions.length > 0">
      <view class="section-header">
        <text class="section-title">优惠活动</text>
      </view>
      <view class="promotion-list">
        <view 
          class="promotion-item" 
          v-for="(promotion, index) in promotions" 
          :key="promotion.id"
          :class="{ selected: selectedPromotion?.id === promotion.id }"
          @click="selectPromotion(promotion)"
        >
          <view class="promotion-left">
            <view class="promotion-tag">
              <text>{{ getPromotionType(promotion.promotion_type) }}</text>
            </view>
            <view class="promotion-info">
              <text class="promotion-name">{{ promotion.name }}</text>
              <text class="promotion-desc">{{ promotion.description }}</text>
              <view class="promotion-time">
                <text>{{ formatDate(promotion.start_time, 'MM-DD') }} - {{ formatDate(promotion.end_time, 'MM-DD') }}</text>
              </view>
            </view>
          </view>
          <view class="promotion-check">
            <text v-if="selectedPromotion?.id === promotion.id">✓</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 支付方式 -->
    <view class="payment-section">
      <view class="section-header">
        <text class="section-title">支付方式</text>
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
              <text class="payment-desc">推荐使用</text>
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
              <text class="payment-desc">安全便捷</text>
            </view>
          </view>
          <view class="payment-check" :class="{ selected: payMethod === 'ALIPAY' }">
            <text>✓</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 电子合同 -->
    <view class="contract-section">
      <view class="contract-content" @click="toggleContract">
        <view class="contract-checkbox" :class="{ checked: agreeContract }" @click.stop="agreeContract = !agreeContract">
          <text v-if="agreeContract">✓</text>
        </view>
        <text class="contract-text">我已阅读并同意</text>
        <text class="contract-link" @click.stop="viewContract">《电子服务协议》</text>
      </view>
    </view>

    <!-- 底部结算栏 -->
    <view class="footer-section">
      <view class="footer-left">
        <view class="price-summary">
          <text class="price-label">合计：</text>
          <text class="price-symbol">¥</text>
          <text class="price-amount">{{ formatAmount(totalAmount) }}</text>
        </view>
        <view class="price-discount" v-if="discountAmount > 0">
          <text>优惠：-¥{{ formatAmount(discountAmount) }}</text>
        </view>
      </view>
      <button class="submit-btn" :loading="loading" :disabled="!canSubmit" @click="handleSubmit">
        <text>{{ canSubmit ? '确认支付' : (agreeContract ? '请选择支付方式' : '请同意协议') }}</text>
      </button>
    </view>

    <!-- 电子合同弹窗 -->
    <view class="contract-modal" v-if="showContractModal">
      <view class="modal-mask" @click="showContractModal = false"></view>
      <view class="modal-content">
        <view class="modal-header">
          <text class="modal-title">电子服务协议</text>
          <view class="modal-close" @click="showContractModal = false">
            <text>×</text>
          </view>
        </view>
        <scroll-view scroll-y class="modal-body">
          <view class="contract-text-content">
            <text class="contract-paragraph">
              1. 服务内容
              
              本协议是您与会员管理系统平台（以下简称"平台"）之间关于购买和使用会员卡服务的电子服务协议。平台为您提供各类会员卡购买、续费、使用等服务。
            </text>
            <text class="contract-paragraph">
              2. 用户权利与义务
              
              您有权按照会员卡的使用规则享受相应的服务；您有义务妥善保管自己的账户信息，不得将账户转让给他人使用；您有义务按时支付相关费用。
            </text>
            <text class="contract-paragraph">
              3. 平台权利与义务
              
              平台有权根据业务需要调整服务内容和价格；平台有义务保障您的账户安全；平台有义务按照协议约定提供服务。
            </text>
            <text class="contract-paragraph">
              4. 退款规则
              
              会员卡一经购买并激活使用，除法律法规另有规定外，原则上不予退款。如因特殊情况需要退款，请联系客服处理。
            </text>
            <text class="contract-paragraph">
              5. 协议终止
              
              您可以随时停止使用平台服务；平台有权在您违反协议规定时终止提供服务；服务期限届满且未续费的，协议自动终止。
            </text>
          </view>
        </scroll-view>
        <view class="modal-footer">
          <button class="modal-btn" @click="handleAgreeContract">
            <text>我已阅读并同意</text>
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

const loading = ref(false);
const cardTypeId = ref<number | null>(null);
const cardName = ref("");
const cardCategory = ref("");
const originalPrice = ref(0);
const isRenew = ref(false);

const quantity = ref(1);
const payMethod = ref("WECHAT");
const agreeContract = ref(false);
const selectedPromotion = ref<any>(null);
const promotions = ref<any[]>([]);
const showContractModal = ref(false);

const canSubmit = computed(() => {
  return agreeContract.value && !!payMethod.value;
});

const totalAmount = computed(() => {
  const baseAmount = originalPrice.value * quantity.value;
  if (selectedPromotion.value) {
    if (selectedPromotion.value.promotion_type === "DISCOUNT") {
      return baseAmount * (selectedPromotion.value.discount_value / 100);
    } else if (selectedPromotion.value.promotion_type === "DEDUCTION") {
      return Math.max(0, baseAmount - selectedPromotion.value.discount_value);
    }
  }
  return baseAmount;
});

const discountAmount = computed(() => {
  const baseAmount = originalPrice.value * quantity.value;
  return baseAmount - totalAmount.value;
});

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
 * 获取分类图标
 */
function getCategoryIcon(category: string) {
  const map: Record<string, string> = {
    "YEAR": "📅",
    "COUNT": "🔢",
    "DURATION": "⏱️",
    "LESSON": "📚"
  };
  return map[category] || "💳";
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
 * 获取优惠类型
 */
function getPromotionType(type: string) {
  const map: Record<string, string> = {
    "DISCOUNT": "折扣",
    "DEDUCTION": "满减",
    "GIFT": "赠送"
  };
  return map[type] || "优惠";
}

/**
 * 数量控制
 */
function increaseQuantity() {
  if (quantity.value < 99) {
    quantity.value++;
  }
}

function decreaseQuantity() {
  if (quantity.value > 1) {
    quantity.value--;
  }
}

/**
 * 选择优惠
 */
function selectPromotion(promotion: any) {
  if (selectedPromotion.value?.id === promotion.id) {
    selectedPromotion.value = null;
  } else {
    selectedPromotion.value = promotion;
  }
}

/**
 * 加载优惠活动
 */
async function loadPromotions() {
  try {
    const res = await order.getPromotions(true);
    promotions.value = res.data || [];
  } catch (err) {
    console.error("加载优惠活动失败:", err);
  }
}

/**
 * 协议相关
 */
function toggleContract() {
  showContractModal.value = true;
}

function viewContract() {
  showContractModal.value = true;
}

function handleAgreeContract() {
  agreeContract.value = true;
  showContractModal.value = false;
}

/**
 * 页面跳转
 */
function goBack() {
  uni.navigateBack();
}

/**
 * 提交订单
 */
async function handleSubmit() {
  if (!canSubmit.value) {
    if (!agreeContract.value) {
      showError("请先阅读并同意服务协议");
    } else if (!payMethod.value) {
      showError("请选择支付方式");
    }
    return;
  }

  if (!cardTypeId.value) {
    showError("缺少必要参数");
    return;
  }

  loading.value = true;

  try {
    // 创建订单
    const orderRes = await order.createOrder({
      order_type: isRenew.value ? "RENEW" : "PURCHASE",
      card_type_id: cardTypeId.value,
      quantity: quantity.value,
      promotion_id: selectedPromotion.value?.id
    });

    const newOrder = orderRes.data;

    showSuccess("订单创建成功");

    // 跳转到支付页面
    setTimeout(() => {
      uni.redirectTo({
        url: `/pages/order/pay/index?order_id=${newOrder.id}&amount=${totalAmount.value}&pay_method=${payMethod.value}`
      });
    }, 500);
  } catch (err) {
    console.error("创建订单失败:", err);
  } finally {
    loading.value = false;
  }
}

onLoad((options: any) => {
  if (options.card_type_id) {
    cardTypeId.value = parseInt(options.card_type_id);
  }
  if (options.name) {
    cardName.value = decodeURIComponent(options.name);
  }
  if (options.price) {
    originalPrice.value = parseFloat(options.price);
  }
  if (options.category) {
    cardCategory.value = options.category;
  }
  if (options.renew) {
    isRenew.value = true;
  }

  loadPromotions();
});
</script>

<style scoped>
.order-create-container {
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

/* 通用区块 */
.goods-section,
.quantity-section,
.promotion-section,
.payment-section {
  background: #fff;
  margin: 20rpx 30rpx;
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
  padding: 30rpx;
  margin: 30rpx;
  border-radius: 16rpx;
}

.goods-card.bg-year {
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
}

.goods-card.bg-count {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.goods-card.bg-duration {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.goods-card.bg-lesson {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.goods-card.bg-default {
  background: linear-gradient(135deg, #8C8C8C 0%, #A8A8A8 100%);
}

.goods-info {
  display: flex;
  align-items: center;
}

.goods-icon {
  width: 80rpx;
  height: 80rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
}

.goods-icon text {
  font-size: 40rpx;
}

.goods-detail {
  display: flex;
  flex-direction: column;
}

.goods-name {
  font-size: 32rpx;
  font-weight: bold;
  color: #fff;
  margin-bottom: 8rpx;
}

.goods-category {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

/* 数量选择 */
.quantity-wrapper {
  padding: 30rpx;
  display: flex;
  justify-content: center;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 30rpx;
}

.control-btn {
  width: 64rpx;
  height: 64rpx;
  background: #F5F5F5;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 40rpx;
  color: #333;
}

.control-btn.disabled {
  opacity: 0.5;
}

.quantity-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #333;
  min-width: 60rpx;
  text-align: center;
}

/* 优惠活动 */
.promotion-list {
  padding: 0 30rpx;
}

.promotion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #F0F0F0;
}

.promotion-item:last-child {
  border-bottom: none;
}

.promotion-item.selected {
  background: rgba(74, 144, 217, 0.05);
}

.promotion-left {
  display: flex;
  align-items: flex-start;
  flex: 1;
}

.promotion-tag {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  color: #fff;
  font-size: 22rpx;
  padding: 6rpx 12rpx;
  border-radius: 4rpx;
  margin-right: 16rpx;
  flex-shrink: 0;
}

.promotion-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.promotion-name {
  font-size: 28rpx;
  color: #333;
  font-weight: bold;
  margin-bottom: 6rpx;
}

.promotion-desc {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 4rpx;
}

.promotion-time {
  font-size: 20rpx;
  color: #CCC;
}

.promotion-check {
  width: 48rpx;
  height: 48rpx;
  border: 2rpx solid #E8E8E8;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-left: 20rpx;
}

.promotion-check text {
  font-size: 24rpx;
  color: #fff;
}

.promotion-item.selected .promotion-check {
  background: #4A90D9;
  border-color: #4A90D9;
}

/* 支付方式 */
.payment-list {
  padding: 0 30rpx;
}

.payment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 26rpx 0;
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
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20rpx;
}

.payment-icon text {
  font-size: 40rpx;
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
  font-size: 22rpx;
  color: #999;
}

.payment-check {
  width: 40rpx;
  height: 40rpx;
  border: 2rpx solid #E8E8E8;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.payment-check text {
  font-size: 20rpx;
  color: #fff;
}

.payment-check.selected {
  background: #4A90D9;
  border-color: #4A90D9;
}

/* 电子合同 */
.contract-section {
  padding: 20rpx 30rpx;
}

.contract-content {
  display: flex;
  align-items: center;
  font-size: 24rpx;
}

.contract-checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid #E8E8E8;
  border-radius: 6rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 12rpx;
}

.contract-checkbox.checked {
  background: #4A90D9;
  border-color: #4A90D9;
}

.contract-checkbox text {
  font-size: 24rpx;
  color: #fff;
}

.contract-text {
  color: #666;
}

.contract-link {
  color: #4A90D9;
}

/* 底部结算栏 */
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

.footer-left {
  display: flex;
  flex-direction: column;
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
  font-size: 40rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.price-discount {
  font-size: 22rpx;
  color: #52C41A;
  margin-top: 4rpx;
}

.submit-btn {
  min-width: 240rpx;
  height: 88rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 30rpx;
  font-weight: bold;
  border-radius: 44rpx;
  border: none;
}

.submit-btn:disabled {
  opacity: 0.6;
}

/* 合同弹窗 */
.contract-modal {
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
  width: 80%;
  max-height: 80vh;
  background: #fff;
  border-radius: 20rpx;
  overflow: hidden;
  display: flex;
  flex-direction: column;
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

.modal-body {
  flex: 1;
  max-height: 50vh;
  padding: 30rpx;
}

.contract-text-content {
  display: flex;
  flex-direction: column;
}

.contract-paragraph {
  font-size: 26rpx;
  color: #666;
  line-height: 1.8;
  margin-bottom: 30rpx;
  white-space: pre-line;
}

.modal-footer {
  padding: 24rpx 30rpx;
  border-top: 1rpx solid #F0F0F0;
}

.modal-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 30rpx;
  font-weight: bold;
  border-radius: 44rpx;
  border: none;
}
</style>
