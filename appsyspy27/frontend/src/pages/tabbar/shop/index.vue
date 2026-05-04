<template>
  <view class="shop-container">
    <!-- 分类筛选 -->
    <view class="category-section">
      <scroll-view scroll-x class="category-scroll">
        <view class="category-list">
          <view 
            class="category-item" 
            :class="{ active: currentCategory === '' }"
            @click="currentCategory = ''"
          >
            全部
          </view>
          <view 
            class="category-item" 
            :class="{ active: currentCategory === 'YEAR' }"
            @click="currentCategory = 'YEAR'"
          >
            年卡
          </view>
          <view 
            class="category-item" 
            :class="{ active: currentCategory === 'COUNT' }"
            @click="currentCategory = 'COUNT'"
          >
            次卡
          </view>
          <view 
            class="category-item" 
            :class="{ active: currentCategory === 'LESSON' }"
            @click="currentCategory = 'LESSON'"
          >
            课包
          </view>
          <view 
            class="category-item" 
            :class="{ active: currentCategory === 'DURATION' }"
            @click="currentCategory = 'DURATION'"
          >
            时长卡
          </view>
        </view>
      </scroll-view>
    </view>

    <!-- 优惠活动横幅 -->
    <view class="promotion-banner" v-if="promotions.length > 0">
      <view class="banner-content">
        <view class="banner-icon">
          <text>🎉</text>
        </view>
        <view class="banner-info">
          <text class="banner-title">{{ promotions[0].name }}</text>
          <text class="banner-desc">{{ promotions[0].description }}</text>
        </view>
      </view>
    </view>

    <!-- 会员卡列表 -->
    <view class="card-list">
      <view 
        class="card-item" 
        v-for="(card, index) in filteredCards" 
        :key="card.id"
        @click="goToBuy(card)"
      >
        <view class="card-image" :class="getImageClass(card.category)">
          <view class="card-tag">{{ getCategoryName(card.category) }}</view>
          <view class="card-discount" v-if="card.current_price < card.original_price">
            <text>{{ getDiscountPercent(card) }}折</text>
          </view>
        </view>
        <view class="card-content">
          <text class="card-name">{{ card.name }}</text>
          <text class="card-desc">{{ card.description }}</text>
          
          <view class="card-features" v-if="card.valid_days || card.total_count || card.total_duration">
            <view class="feature-item" v-if="card.valid_days">
              <text class="feature-icon">📅</text>
              <text class="feature-text">有效期 {{ card.valid_days }} 天</text>
            </view>
            <view class="feature-item" v-if="card.total_count">
              <text class="feature-icon">🔢</text>
              <text class="feature-text">共 {{ card.total_count }} 次</text>
            </view>
            <view class="feature-item" v-if="card.total_duration">
              <text class="feature-icon">⏱️</text>
              <text class="feature-text">共 {{ formatDuration(card.total_duration) }}</text>
            </view>
          </view>

          <view class="card-usage" v-if="card.usage_scope">
            <text class="usage-label">使用范围：</text>
            <text class="usage-text">{{ card.usage_scope }}</text>
          </view>

          <view class="card-bottom">
            <view class="price-section">
              <text class="price-symbol">¥</text>
              <text class="price-current">{{ card.current_price }}</text>
              <text class="price-original" v-if="card.current_price < card.original_price">
                ¥{{ card.original_price }}
              </text>
            </view>
            <view class="buy-btn">
              <text>立即购买</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 空状态 -->
    <view class="empty-state" v-if="filteredCards.length === 0">
      <view class="empty-icon">
        <text>🛒</text>
      </view>
      <text class="empty-text">暂无商品</text>
    </view>
  </view>
</template>

<script setup lang="ts">
import { ref, computed, onShow } from "vue";
import { card, order } from "@/api";
import { formatDuration } from "@/utils";

const currentCategory = ref("");
const cardTypes = ref<any[]>([]);
const promotions = ref<any[]>([]);

const filteredCards = computed(() => {
  if (!currentCategory.value) {
    return cardTypes.value;
  }
  return cardTypes.value.filter(c => c.category === currentCategory.value);
});

// 获取分类名称
function getCategoryName(category: string) {
  const map: Record<string, string> = {
    "YEAR": "年卡",
    "COUNT": "次卡",
    "DURATION": "时长卡",
    "LESSON": "课包"
  };
  return map[category] || "会员卡";
}

// 获取图片样式类
function getImageClass(category: string) {
  const map: Record<string, string> = {
    "YEAR": "img-year",
    "COUNT": "img-count",
    "DURATION": "img-duration",
    "LESSON": "img-lesson"
  };
  return map[category] || "img-default";
}

// 计算折扣
function getDiscountPercent(card: any) {
  if (!card.original_price || !card.current_price) return "";
  const percent = (card.current_price / card.original_price) * 10;
  return percent.toFixed(1);
}

// 加载卡类型
async function loadCardTypes() {
  try {
    const res = await card.getCardTypes({ is_on_sale: true });
    cardTypes.value = res.data;
  } catch (err) {
    console.error("加载卡类型失败:", err);
  }
}

// 加载优惠活动
async function loadPromotions() {
  try {
    const res = await order.getPromotions(true);
    promotions.value = res.data;
  } catch (err) {
    console.error("加载优惠活动失败:", err);
  }
}

// 页面跳转
function goToBuy(card: any) {
  uni.navigateTo({ 
    url: `/pages/order/create/index?card_type_id=${card.id}&name=${encodeURIComponent(card.name)}&price=${card.current_price}&category=${card.category}` 
  });
}

onShow(() => {
  loadCardTypes();
  loadPromotions();
});
</script>

<style scoped>
.shop-container {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 40rpx;
}

/* 分类筛选 */
.category-section {
  background: #fff;
  padding: 20rpx 0;
}

.category-scroll {
  white-space: nowrap;
}

.category-list {
  display: inline-flex;
  padding: 0 20rpx;
  gap: 16rpx;
}

.category-item {
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

.category-item.active {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
}

/* 优惠横幅 */
.promotion-banner {
  margin: 20rpx 30rpx;
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
  border-radius: 16rpx;
  padding: 24rpx 30rpx;
}

.banner-content {
  display: flex;
  align-items: center;
}

.banner-icon {
  width: 80rpx;
  height: 80rpx;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 48rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  margin-right: 20rpx;
}

.banner-info {
  display: flex;
  flex-direction: column;
}

.banner-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #fff;
}

.banner-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 6rpx;
}

/* 会员卡列表 */
.card-list {
  padding: 20rpx 30rpx;
}

.card-item {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
  margin-bottom: 30rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.card-image {
  height: 200rpx;
  display: flex;
  position: relative;
  align-items: center;
  justify-content: center;
}

.img-year {
  background: linear-gradient(135deg, #4A90D9 0%, #6BA8E0 100%);
}

.img-count {
  background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
}

.img-duration {
  background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
}

.img-lesson {
  background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
}

.img-default {
  background: linear-gradient(135deg, #8C8C8C 0%, #A8A8A8 100%);
}

.card-tag {
  position: absolute;
  top: 20rpx;
  left: 20rpx;
  background: rgba(255, 255, 255, 0.3);
  color: #fff;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.card-discount {
  position: absolute;
  top: 20rpx;
  right: 20rpx;
  background: #FF4D4F;
  color: #fff;
  font-size: 22rpx;
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.card-content {
  padding: 24rpx;
}

.card-name {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #333;
  margin-bottom: 12rpx;
}

.card-desc {
  display: block;
  font-size: 24rpx;
  color: #999;
  margin-bottom: 20rpx;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-features {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.feature-item {
  display: flex;
  align-items: center;
  font-size: 24rpx;
  color: #666;
}

.feature-icon {
  margin-right: 8rpx;
}

.card-usage {
  display: flex;
  margin-bottom: 20rpx;
}

.usage-label {
  font-size: 24rpx;
  color: #999;
  flex-shrink: 0;
}

.usage-text {
  font-size: 24rpx;
  color: #666;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1rpx solid #F0F0F0;
}

.price-section {
  display: flex;
  align-items: baseline;
}

.price-symbol {
  font-size: 24rpx;
  color: #FF6B6B;
  margin-right: 4rpx;
}

.price-current {
  font-size: 36rpx;
  font-weight: bold;
  color: #FF6B6B;
}

.price-original {
  font-size: 22rpx;
  color: #999;
  text-decoration: line-through;
  margin-left: 12rpx;
}

.buy-btn {
  background: linear-gradient(135deg, #4A90D9 0%, #357ABD 100%);
  color: #fff;
  font-size: 26rpx;
  padding: 16rpx 40rpx;
  border-radius: 32rpx;
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
}
</style>
