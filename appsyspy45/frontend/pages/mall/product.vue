<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-content">
      <view class="product-section">
        <swiper class="product-swiper" indicator-dots autoplay circular>
          <swiper-item v-for="(img, index) in productImages" :key="index">
            <image :src="img" class="product-image" mode="aspectFill"></image>
          </swiper-item>
        </swiper>
      </view>
      
      <view class="info-section">
        <view class="price-row">
          <view class="points-price">
            <text class="points-label">积分</text>
            <text class="points-value">{{ product?.points_required || 0 }}</text>
          </view>
          <view class="cash-price" v-if="product?.cash_required > 0">
            <text class="plus">+</text>
            <text class="cash-symbol">¥</text>
            <text class="cash-value">{{ product?.cash_required || 0 }}</text>
          </view>
          <view class="original-price" v-if="product?.original_price > 0">
            <text class="original-text">原价 ¥{{ product?.original_price }}</text>
          </view>
        </view>
        
        <view class="product-name">{{ product?.name || '' }}</view>
        
        <view class="product-tags" v-if="productTags.length > 0">
          <text class="tag" v-for="(tag, index) in productTags" :key="index">{{ tag }}</text>
        </view>
        
        <view class="product-meta">
          <view class="meta-item">
            <text class="meta-label">库存</text>
            <text class="meta-value">{{ product?.stock || 0 }}件</text>
          </view>
          <view class="meta-item">
            <text class="meta-label">已兑</text>
            <text class="meta-value">{{ product?.sales_count || 0 }}件</text>
          </view>
          <view class="meta-item">
            <text class="meta-label">免运费</text>
          </view>
        </view>
      </view>
      
      <view class="address-section" v-if="addresses.length > 0">
        <view class="section-header">
          <text class="section-title">收货地址</text>
        </view>
        <view class="address-card" @click="selectAddress">
          <view class="address-header">
            <text class="name">{{ selectedAddress?.contact_name || '' }}</text>
            <text class="phone">{{ selectedAddress?.contact_phone || '' }}</text>
            <view class="address-tags" v-if="selectedAddress?.tag">
              <text class="tag">{{ selectedAddress?.tag }}</text>
            </view>
          </view>
          <text class="address-detail">
            {{ selectedAddress?.province }}{{ selectedAddress?.city }}{{ selectedAddress?.district }}{{ selectedAddress?.detail }}
          </text>
          <text class="address-arrow">›</text>
        </view>
      </view>
      
      <view class="add-address" v-else @click="selectAddress">
        <text class="add-icon">+</text>
        <text class="add-text">添加收货地址</text>
      </view>
      
      <view class="spec-section" v-if="productSpecs.length > 0">
        <view class="section-header">
          <text class="section-title">规格参数</text>
        </view>
        <view class="spec-list">
          <view class="spec-item" v-for="(spec, index) in productSpecs" :key="index">
            <text class="spec-label">{{ spec.label }}</text>
            <text class="spec-value">{{ spec.value }}</text>
          </view>
        </view>
      </view>
      
      <view class="desc-section">
        <view class="section-header">
          <text class="section-title">商品详情</text>
        </view>
        <view class="desc-content">
          <text class="desc-text">{{ product?.description || '暂无商品详情' }}</text>
        </view>
      </view>
      
      <view class="exchange-rules">
        <view class="section-header">
          <text class="section-title">兑换规则</text>
        </view>
        <view class="rules-list">
          <view class="rule-item">
            <text class="rule-dot">•</text>
            <text class="rule-text">积分不足时，可使用积分加现金的方式兑换</text>
          </view>
          <view class="rule-item">
            <text class="rule-dot">•</text>
            <text class="rule-text">兑换商品将在3-5个工作日内发货</text>
          </view>
          <view class="rule-item">
            <text class="rule-dot">•</text>
            <text class="rule-text">所有兑换商品均包邮配送</text>
          </view>
          <view class="rule-item">
            <text class="rule-dot">•</text>
            <text class="rule-text">如有问题请联系客服</text>
          </view>
        </view>
      </view>
      
      <view class="bottom-spacer"></view>
    </scroll-view>
    
    <view class="bottom-bar">
      <view class="bottom-actions">
        <view class="action-item" @click="goOrders">
          <text class="action-icon">📦</text>
          <text class="action-text">兑换订单</text>
        </view>
        <view class="action-item" @click="goCustomerService">
          <text class="action-icon">💬</text>
          <text class="action-text">客服</text>
        </view>
      </view>
      <view class="exchange-btn" :class="{ disabled: !canExchange }" @click="handleExchange">
        立即兑换
      </view>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

export default {
  data() {
    return {
      productId: null,
      product: null,
      productImages: [],
      productTags: [],
      productSpecs: [],
      addresses: [],
      selectedAddress: null,
      pointsBalance: 0
    }
  },
  
  computed: {
    canExchange() {
      if (!this.product) return false
      if (this.product.stock <= 0) return false
      
      const pointsNeeded = this.product.points_required || 0
      const cashNeeded = this.product.cash_required || 0
      
      if (cashNeeded > 0) {
        return this.pointsBalance >= pointsNeeded && this.selectedAddress
      }
      
      return this.pointsBalance >= pointsNeeded && this.selectedAddress
    }
  },
  
  onLoad(options) {
    if (options.id) {
      this.productId = parseInt(options.id)
      this.loadProductDetail()
    }
  },
  
  onShow() {
    this.loadPointsBalance()
    this.loadAddresses()
  },
  
  methods: {
    async loadProductDetail() {
      if (!this.productId) return
      
      try {
        const res = await api.get(`/points/products/${this.productId}`)
        if (res.code === 200) {
          this.product = res.data
          this.productImages = [res.data.cover_image || '/static/images/default-product.png']
          
          this.productTags = []
          if (res.data.is_free_shipping) {
            this.productTags.push('包邮')
          }
          if (res.data.cash_required > 0) {
            this.productTags.push('积分+现金')
          }
          
          this.productSpecs = []
          if (res.data.specifications) {
            try {
              const specs = JSON.parse(res.data.specifications)
              this.productSpecs = Object.keys(specs).map(key => ({
                label: key,
                value: specs[key]
              }))
            } catch (e) {
              console.error('解析规格参数失败:', e)
            }
          }
        }
      } catch (e) {
        console.error('加载商品详情失败:', e)
      }
    },
    
    async loadPointsBalance() {
      const token = uni.getStorageSync('token')
      if (!token) return
      
      try {
        const res = await api.get('/points/balance')
        if (res.code === 200) {
          this.pointsBalance = res.data.balance || 0
        }
      } catch (e) {
        console.error('加载积分余额失败:', e)
      }
    },
    
    async loadAddresses() {
      const token = uni.getStorageSync('token')
      if (!token) return
      
      try {
        const res = await api.get('/user/addresses')
        if (res.code === 200) {
          this.addresses = res.data.list || []
          
          if (this.addresses.length > 0 && !this.selectedAddress) {
            const defaultAddr = this.addresses.find(a => a.is_default)
            this.selectedAddress = defaultAddr || this.addresses[0]
          }
        }
      } catch (e) {
        console.error('加载地址失败:', e)
      }
    },
    
    selectAddress() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      uni.navigateTo({
        url: '/pages/user/address?select=1'
      })
    },
    
    async handleExchange() {
      if (!this.canExchange) {
        if (this.product?.stock <= 0) {
          utils.showToast('商品库存不足')
        } else if (!this.selectedAddress) {
          utils.showToast('请选择收货地址')
        } else if (this.pointsBalance < (this.product?.points_required || 0)) {
          utils.showToast('积分不足')
        }
        return
      }
      
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      uni.navigateTo({
        url: `/pages/mall/exchange?product_id=${this.productId}&address_id=${this.selectedAddress?.id}`
      })
    },
    
    goOrders() {
      uni.navigateTo({
        url: '/pages/mall/orders'
      })
    },
    
    goCustomerService() {
      uni.navigateTo({
        url: '/pages/chat/list'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
}

.scroll-content {
  height: calc(100vh - 120rpx);
}

.product-section {
  background-color: $white;
}

.product-swiper {
  height: 600rpx;
}

.product-image {
  width: 100%;
  height: 100%;
}

.info-section {
  background-color: $white;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.price-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 20rpx;
}

.points-price {
  display: flex;
  align-items: baseline;
}

.points-label {
  font-size: $font-size-sm;
  color: $primary-color;
  margin-right: 6rpx;
}

.points-value {
  font-size: 48rpx;
  font-weight: bold;
  color: $primary-color;
}

.cash-price {
  display: flex;
  align-items: baseline;
  margin-left: 20rpx;
}

.plus {
  font-size: $font-size-base;
  color: $text-secondary;
  margin-right: 6rpx;
}

.cash-symbol {
  font-size: $font-size-sm;
  color: $danger-color;
}

.cash-value {
  font-size: 36rpx;
  font-weight: bold;
  color: $danger-color;
}

.original-price {
  margin-left: 20rpx;
}

.original-text {
  font-size: $font-size-sm;
  color: $text-muted;
  text-decoration: line-through;
}

.product-name {
  font-size: $font-size-lg;
  font-weight: bold;
  color: $text-color;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.product-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.tag {
  padding: 6rpx 16rpx;
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
  font-size: $font-size-xs;
  border-radius: $border-radius-sm;
}

.product-meta {
  display: flex;
  padding-top: 20rpx;
  border-top: 1rpx solid $border-color;
}

.meta-item {
  margin-right: 40rpx;
  display: flex;
  align-items: center;
}

.meta-label {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.meta-value {
  font-size: $font-size-sm;
  color: $text-color;
  margin-left: 6rpx;
}

.address-section,
.spec-section,
.desc-section,
.exchange-rules {
  background-color: $white;
  margin-bottom: 20rpx;
  padding: 0 30rpx;
}

.section-header {
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
}

.section-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
}

.address-card {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
}

.address-header {
  display: flex;
  align-items: center;
  margin-bottom: 10rpx;
}

.name {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
  margin-right: 20rpx;
}

.phone {
  font-size: $font-size-base;
  color: $text-secondary;
}

.address-tags {
  margin-left: 20rpx;
}

.address-detail {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
  flex: 1;
}

.address-arrow {
  font-size: $font-size-lg;
  color: $text-muted;
  margin-left: 20rpx;
}

.add-address {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $white;
  margin-bottom: 20rpx;
  padding: 40rpx;
  border: 2rpx dashed $border-color;
}

.add-icon {
  font-size: $font-size-xl;
  color: $primary-color;
  margin-right: 10rpx;
}

.add-text {
  font-size: $font-size-base;
  color: $primary-color;
}

.spec-list {
  padding: 20rpx 0;
}

.spec-item {
  display: flex;
  padding: 16rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.spec-label {
  width: 160rpx;
  font-size: $font-size-sm;
  color: $text-secondary;
}

.spec-value {
  flex: 1;
  font-size: $font-size-sm;
  color: $text-color;
}

.desc-content {
  padding: 30rpx 0;
}

.desc-text {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.8;
}

.rules-list {
  padding: 20rpx 0;
}

.rule-item {
  display: flex;
  align-items: flex-start;
  padding: 12rpx 0;
}

.rule-dot {
  font-size: $font-size-sm;
  color: $text-muted;
  margin-right: 10rpx;
}

.rule-text {
  flex: 1;
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: $white;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.bottom-actions {
  display: flex;
  gap: 30rpx;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.action-icon {
  font-size: 36rpx;
}

.action-text {
  font-size: $font-size-xs;
  color: $text-secondary;
  margin-top: 6rpx;
}

.exchange-btn {
  width: 280rpx;
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  background-color: $primary-color;
  color: $white;
  font-size: $font-size-lg;
  font-weight: bold;
  border-radius: 44rpx;
  
  &.disabled {
    background-color: $text-muted;
  }
}

.bottom-spacer {
  height: 180rpx;
}
</style>
