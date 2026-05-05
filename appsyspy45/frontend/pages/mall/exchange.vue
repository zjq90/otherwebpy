<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-content">
      <view class="product-section" v-if="product">
        <view class="product-card">
          <image :src="product.cover_image || '/static/images/default-product.png'" class="product-image"></image>
          <view class="product-info">
            <text class="product-name">{{ product.name }}</text>
            <view class="product-price">
              <text class="points">{{ product.points_required }}积分</text>
              <text class="cash" v-if="product.cash_required > 0">+¥{{ product.cash_required }}</text>
            </view>
            <text class="product-stock">库存：{{ product.stock }}件</text>
          </view>
        </view>
        
        <view class="quantity-section">
          <text class="quantity-label">兑换数量</text>
          <view class="quantity-control">
            <view class="btn-minus" :class="{ disabled: quantity <= 1 }" @click="decreaseQuantity">-</view>
            <text class="quantity-value">{{ quantity }}</text>
            <view class="btn-plus" :class="{ disabled: quantity >= product.stock }" @click="increaseQuantity">+</view>
          </view>
        </view>
      </view>
      
      <view class="address-section" v-if="selectedAddress">
        <view class="section-header">
          <text class="section-title">收货地址</text>
        </view>
        <view class="address-card" @click="selectAddress">
          <view class="address-header">
            <text class="name">{{ selectedAddress.contact_name }}</text>
            <text class="phone">{{ selectedAddress.contact_phone }}</text>
            <view class="address-tags" v-if="selectedAddress.tag">
              <text class="tag">{{ selectedAddress.tag }}</text>
            </view>
          </view>
          <text class="address-detail">
            {{ selectedAddress.province }}{{ selectedAddress.city }}{{ selectedAddress.district }}{{ selectedAddress.detail }}
          </text>
          <text class="address-arrow">›</text>
        </view>
      </view>
      
      <view class="add-address" v-else @click="selectAddress">
        <text class="add-icon">+</text>
        <text class="add-text">请选择收货地址</text>
      </view>
      
      <view class="order-section">
        <view class="section-header">
          <text class="section-title">订单信息</text>
        </view>
        <view class="order-info-list">
          <view class="info-item">
            <text class="info-label">商品数量</text>
            <text class="info-value">x{{ quantity }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">所需积分</text>
            <text class="info-value highlight">{{ totalPoints }}积分</text>
          </view>
          <view class="info-item" v-if="totalCash > 0">
            <text class="info-label">所需现金</text>
            <text class="info-value highlight">¥{{ totalCash }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">运费</text>
            <text class="info-value free">免运费</text>
          </view>
        </view>
      </view>
      
      <view class="balance-section" v-if="userPoints < totalPoints">
        <view class="balance-warning">
          <text class="warning-icon">⚠️</text>
          <text class="warning-text">积分不足，还差 {{ totalPoints - userPoints }} 积分</text>
        </view>
        <view class="balance-actions">
          <view class="action-btn" @click="goPoints">查看积分</view>
          <view class="action-btn primary" @click="goRecycle">去回收赚积分</view>
        </view>
      </view>
      
      <view class="balance-section" v-else>
        <view class="balance-info">
          <text class="balance-label">可用积分</text>
          <text class="balance-value">{{ userPoints }}积分</text>
        </view>
      </view>
      
      <view class="remark-section">
        <view class="section-header">
          <text class="section-title">备注（选填）</text>
        </view>
        <view class="remark-input">
          <textarea 
            v-model="form.remark" 
            placeholder="请输入备注信息，如：颜色、尺码等特殊要求"
            maxlength="200"
          ></textarea>
          <text class="char-count">{{ form.remark.length }}/200</text>
        </view>
      </view>
      
      <view class="bottom-spacer"></view>
    </scroll-view>
    
    <view class="bottom-bar">
      <view class="price-info">
        <view class="price-row">
          <text class="price-label">共{{ quantity }}件，合计：</text>
          <view class="price-value">
            <text class="points">{{ totalPoints }}积分</text>
            <text class="cash" v-if="totalCash > 0">+¥{{ totalCash }}</text>
          </view>
        </view>
        <view class="price-row" v-if="totalCash > 0">
          <text class="price-tip">（现金部分将在线支付）</text>
        </view>
      </view>
      <view class="exchange-btn" :class="{ disabled: !canExchange }" @click="handleExchange">
        确认兑换
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
      quantity: 1,
      selectedAddress: null,
      userPoints: 0,
      form: {
        remark: ''
      }
    }
  },
  
  computed: {
    totalPoints() {
      if (!this.product) return 0
      return (this.product.points_required || 0) * this.quantity
    },
    
    totalCash() {
      if (!this.product) return 0
      return (this.product.cash_required || 0) * this.quantity
    },
    
    canExchange() {
      if (!this.product) return false
      if (!this.selectedAddress) return false
      if (this.quantity <= 0 || this.quantity > (this.product.stock || 0)) return false
      if (this.userPoints < this.totalPoints) return false
      
      return true
    }
  },
  
  onLoad(options) {
    if (options.product_id) {
      this.productId = parseInt(options.product_id)
      this.loadProductDetail()
    }
    if (options.address_id) {
      this.loadAddressDetail(parseInt(options.address_id))
    }
  },
  
  onShow() {
    this.loadUserPoints()
    this.loadAddresses()
  },
  
  methods: {
    async loadProductDetail() {
      if (!this.productId) return
      
      try {
        const res = await api.get(`/points/products/${this.productId}`)
        if (res.code === 200) {
          this.product = res.data
        }
      } catch (e) {
        console.error('加载商品详情失败:', e)
      }
    },
    
    async loadAddressDetail(addressId) {
      try {
        const res = await api.get(`/user/addresses/${addressId}`)
        if (res.code === 200) {
          this.selectedAddress = res.data
        }
      } catch (e) {
        console.error('加载地址详情失败:', e)
      }
    },
    
    async loadUserPoints() {
      const token = uni.getStorageSync('token')
      if (!token) return
      
      try {
        const res = await api.get('/points/balance')
        if (res.code === 200) {
          this.userPoints = res.data.balance || 0
        }
      } catch (e) {
        console.error('加载积分余额失败:', e)
      }
    },
    
    async loadAddresses() {
      if (this.selectedAddress) return
      
      const token = uni.getStorageSync('token')
      if (!token) return
      
      try {
        const res = await api.get('/user/addresses')
        if (res.code === 200) {
          const addresses = res.data.list || []
          if (addresses.length > 0) {
            const defaultAddr = addresses.find(a => a.is_default)
            this.selectedAddress = defaultAddr || addresses[0]
          }
        }
      } catch (e) {
        console.error('加载地址列表失败:', e)
      }
    },
    
    decreaseQuantity() {
      if (this.quantity > 1) {
        this.quantity--
      }
    },
    
    increaseQuantity() {
      if (this.product && this.quantity < this.product.stock) {
        this.quantity++
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
        if (!this.selectedAddress) {
          utils.showToast('请选择收货地址')
        } else if (this.userPoints < this.totalPoints) {
          utils.showToast('积分不足')
        } else {
          utils.showToast('请完善兑换信息')
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
      
      const confirmed = await utils.showModal(
        `确认兑换 ${this.product?.name} x${this.quantity}？\n将扣除 ${this.totalPoints} 积分${this.totalCash > 0 ? '，支付 ¥' + this.totalCash : ''}`,
        '确认兑换'
      )
      
      if (!confirmed) return
      
      utils.showLoading('兑换中...')
      
      try {
        const exchangeData = {
          product_id: this.productId,
          quantity: this.quantity,
          address_id: this.selectedAddress.id
        }
        
        if (this.form.remark) {
          exchangeData.remark = this.form.remark
        }
        
        const res = await api.post('/points/exchange', exchangeData)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          utils.showToast('兑换成功')
          
          setTimeout(() => {
            uni.redirectTo({
              url: '/pages/mall/orders'
            })
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('兑换失败:', e)
      }
    },
    
    goPoints() {
      uni.navigateTo({
        url: '/pages/points/index'
      })
    },
    
    goRecycle() {
      uni.switchTab({
        url: '/pages/order/create'
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
  height: calc(100vh - 160rpx);
}

.product-section {
  background-color: $white;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.product-card {
  display: flex;
  margin-bottom: 30rpx;
}

.product-image {
  width: 200rpx;
  height: 200rpx;
  border-radius: $border-radius-md;
  margin-right: 20rpx;
}

.product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.product-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.product-price {
  display: flex;
  align-items: baseline;
}

.points {
  font-size: $font-size-lg;
  color: $primary-color;
  font-weight: bold;
}

.cash {
  font-size: $font-size-sm;
  color: $danger-color;
  margin-left: 10rpx;
}

.product-stock {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.quantity-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 30rpx;
  border-top: 1rpx solid $border-color;
}

.quantity-label {
  font-size: $font-size-base;
  color: $text-color;
}

.quantity-control {
  display: flex;
  align-items: center;
}

.btn-minus,
.btn-plus {
  width: 56rpx;
  height: 56rpx;
  background-color: $bg-color;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: $font-size-lg;
  color: $text-secondary;
  
  &.disabled {
    opacity: 0.5;
  }
}

.quantity-value {
  width: 80rpx;
  text-align: center;
  font-size: $font-size-lg;
  font-weight: bold;
  color: $text-color;
}

.address-section,
.order-section,
.balance-section,
.remark-section {
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

.tag {
  padding: 4rpx 16rpx;
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
  font-size: $font-size-xs;
  border-radius: $border-radius-sm;
}

.address-detail {
  flex: 1;
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
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

.order-info-list {
  padding: 20rpx 0;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.info-label {
  font-size: $font-size-base;
  color: $text-secondary;
}

.info-value {
  font-size: $font-size-base;
  color: $text-color;
  
  &.highlight {
    color: $primary-color;
    font-weight: bold;
  }
  
  &.free {
    color: $success-color;
  }
}

.balance-warning {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
}

.warning-icon {
  font-size: 32rpx;
  margin-right: 10rpx;
}

.warning-text {
  font-size: $font-size-sm;
  color: $warning-color;
}

.balance-actions {
  display: flex;
  gap: 20rpx;
  padding-bottom: 30rpx;
}

.action-btn {
  flex: 1;
  height: 72rpx;
  line-height: 72rpx;
  text-align: center;
  background-color: $bg-color;
  color: $text-secondary;
  font-size: $font-size-sm;
  border-radius: 36rpx;
  
  &.primary {
    background-color: $primary-color;
    color: $white;
  }
}

.balance-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx 0;
}

.balance-label {
  font-size: $font-size-base;
  color: $text-secondary;
}

.balance-value {
  font-size: $font-size-lg;
  color: $primary-color;
  font-weight: bold;
}

.remark-input {
  padding: 20rpx 0;
  position: relative;
}

.remark-input textarea {
  width: 100%;
  height: 160rpx;
  font-size: $font-size-base;
  color: $text-color;
}

.char-count {
  position: absolute;
  right: 0;
  bottom: 20rpx;
  font-size: $font-size-xs;
  color: $text-muted;
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

.price-info {
  flex: 1;
}

.price-row {
  display: flex;
  align-items: baseline;
}

.price-label {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.price-value {
  display: flex;
  align-items: baseline;
}

.price-tip {
  font-size: $font-size-xs;
  color: $text-muted;
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
  height: 200rpx;
}
</style>
