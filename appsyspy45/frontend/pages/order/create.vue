<template>
  <view class="page">
    <scroll-view scroll-y class="scroll-content">
      <view class="form-section">
        <view class="section-title">选择衣物类型</view>
        <view class="clothing-grid">
          <view 
            class="type-item" 
            v-for="(item, index) in clothingTypes" 
            :key="index"
            :class="{ active: selectedTypes.includes(item.id) }"
            @click="toggleType(item)"
          >
            <image :src="item.icon" class="type-icon"></image>
            <text class="type-name">{{ item.name }}</text>
            <text class="type-points">{{ item.points }}积分/件</text>
          </view>
        </view>
        
        <view class="quantity-section" v-if="selectedTypes.length > 0">
          <view class="section-title">填写数量</view>
          <view class="quantity-list">
            <view class="quantity-item" v-for="(item, index) in selectedTypes" :key="index">
              <text class="type-label">{{ getTypeName(item) }}</text>
              <view class="quantity-control">
                <view class="btn-minus" @click="decreaseQuantity(item)">-</view>
                <text class="quantity-value">{{ quantities[item] || 0 }}</text>
                <view class="btn-plus" @click="increaseQuantity(item)">+</view>
              </view>
            </view>
          </view>
        </view>
        
        <view class="section-title">选择上门时间</view>
        <view class="time-selector">
          <picker mode="multiSelector" :range="timeRange" :value="timeValue" @change="onTimeChange" @columnchange="onTimeColumnChange">
            <view class="picker-btn">
              <text class="picker-text">{{ selectedDate || '请选择日期' }}</text>
              <text class="picker-text">{{ selectedTimeSlot || '' }}</text>
              <text class="arrow">›</text>
            </view>
          </picker>
        </view>
        
        <view class="section-title">选择回收地址</view>
        <view class="address-section" v-if="selectedAddress">
          <view class="address-card" @click="selectAddress">
            <view class="address-header">
              <text class="name">{{ selectedAddress.contact_name }}</text>
              <text class="phone">{{ selectedAddress.contact_phone }}</text>
            </view>
            <text class="address-text">{{ selectedAddress.province }}{{ selectedAddress.city }}{{ selectedAddress.district }}{{ selectedAddress.detail }}</text>
            <view class="address-tags" v-if="selectedAddress.tag">
              <text class="tag">{{ selectedAddress.tag }}</text>
            </view>
          </view>
        </view>
        <view class="add-address" v-else @click="selectAddress">
          <text class="icon">+</text>
          <text class="text">添加收货地址</text>
        </view>
        
        <view class="section-title">备注信息（选填）</view>
        <view class="remark-section">
          <textarea 
            v-model="form.remark" 
            placeholder="请输入备注信息，如：衣物大概重量、特殊要求等"
            maxlength="200"
          ></textarea>
          <text class="char-count">{{ form.remark.length }}/200</text>
        </view>
      </view>
      
      <view class="estimate-section">
        <view class="estimate-title">预估信息</view>
        <view class="estimate-row">
          <text class="label">预估件数</text>
          <text class="value">{{ totalQuantity }}件</text>
        </view>
        <view class="estimate-row">
          <text class="label">预估积分</text>
          <text class="value highlight">{{ estimatePoints }}积分</text>
        </view>
        <view class="estimate-row">
          <text class="label">预估减碳</text>
          <text class="value highlight">{{ estimateCarbon }}kg</text>
        </view>
      </view>
      
      <view class="bottom-spacer"></view>
    </scroll-view>
    
    <view class="bottom-bar">
      <view class="price-info">
        <text class="label">预估积分：</text>
        <text class="price">{{ estimatePoints }}积分</text>
      </view>
      <view class="submit-btn" :class="{ disabled: !canSubmit }" @click="handleSubmit">
        提交预约
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
      clothingTypes: [],
      selectedTypes: [],
      quantities: {},
      dates: [],
      timeSlots: [],
      timeRange: [[], []],
      timeValue: [0, 0],
      selectedDate: '',
      selectedTimeSlot: '',
      dateValues: [],
      timeSlotValues: [],
      addresses: [],
      selectedAddress: null,
      form: {
        remark: ''
      }
    }
  },
  
  computed: {
    totalQuantity() {
      return Object.values(this.quantities).reduce((sum, qty) => sum + qty, 0)
    },
    
    estimatePoints() {
      let points = 0
      for (const typeId in this.quantities) {
        const qty = this.quantities[typeId]
        const type = this.clothingTypes.find(t => t.id === parseInt(typeId))
        if (type && qty > 0) {
          points += type.points * qty
        }
      }
      return points
    },
    
    estimateCarbon() {
      return (this.estimatePoints * 0.5).toFixed(1)
    },
    
    canSubmit() {
      return this.totalQuantity > 0 && this.selectedDate && this.selectedTimeSlot && this.selectedAddress
    }
  },
  
  onLoad() {
    this.loadData()
  },
  
  onShow() {
    this.loadAddresses()
  },
  
  methods: {
    async loadData() {
      await Promise.all([
        this.loadClothingTypes(),
        this.loadAvailableTimes()
      ])
    },
    
    async loadClothingTypes() {
      try {
        const res = await api.get('/order/clothing-types')
        if (res.code === 200) {
          this.clothingTypes = res.data.list || []
        }
      } catch (e) {
        console.error('加载衣物类型失败:', e)
      }
    },
    
    async loadAvailableTimes() {
      try {
        const res = await api.get('/order/available-times')
        if (res.code === 200) {
          this.dates = res.data.dates || []
          this.timeSlots = res.data.time_slots || []
          
          this.dateValues = this.dates.map(d => d.date)
          this.timeSlotValues = this.timeSlots.map(t => t.slot)
          
          this.timeRange = [
            this.dates.map(d => `${d.date} ${d.label}`),
            this.timeSlots.map(t => t.slot)
          ]
          
          if (this.dates.length > 0) {
            this.selectedDate = this.dates[0].date
          }
          if (this.timeSlots.length > 0) {
            this.selectedTimeSlot = this.timeSlots[0].slot
          }
        }
      } catch (e) {
        console.error('加载可预约时间失败:', e)
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
    
    toggleType(item) {
      const index = this.selectedTypes.indexOf(item.id)
      if (index > -1) {
        this.selectedTypes.splice(index, 1)
        delete this.quantities[item.id]
      } else {
        this.selectedTypes.push(item.id)
        this.quantities[item.id] = 1
      }
    },
    
    getTypeName(typeId) {
      const type = this.clothingTypes.find(t => t.id === typeId)
      return type ? type.name : ''
    },
    
    increaseQuantity(typeId) {
      if (!this.quantities[typeId]) {
        this.quantities[typeId] = 0
      }
      this.quantities[typeId]++
    },
    
    decreaseQuantity(typeId) {
      if (this.quantities[typeId] > 0) {
        this.quantities[typeId]--
        if (this.quantities[typeId] === 0) {
          const index = this.selectedTypes.indexOf(typeId)
          if (index > -1) {
            this.selectedTypes.splice(index, 1)
          }
          delete this.quantities[typeId]
        }
      }
    },
    
    onTimeChange(e) {
      const val = e.detail.value
      this.selectedDate = this.dates[val[0]].date
      this.selectedTimeSlot = this.timeSlots[val[1]].slot
    },
    
    onTimeColumnChange(e) {
      const column = e.detail.column
      const value = e.detail.value
      
      if (column === 0) {
        this.timeValue[0] = value
        this.timeValue[1] = 0
      }
    },
    
    selectAddress() {
      if (!uni.getStorageSync('token')) {
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
    
    async handleSubmit() {
      if (!this.canSubmit) {
        utils.showToast('请完善预约信息')
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
      
      const items = []
      for (const typeId in this.quantities) {
        const qty = this.quantities[typeId]
        if (qty > 0) {
          items.push({
            clothing_type_id: parseInt(typeId),
            quantity: qty,
            quality: 'good'
          })
        }
      }
      
      const orderData = {
        items: items,
        schedule_date: this.selectedDate,
        schedule_time: this.selectedTimeSlot,
        address_id: this.selectedAddress.id,
        remark: this.form.remark
      }
      
      utils.showLoading('提交中...')
      
      try {
        const res = await api.post('/order/create', orderData)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          utils.showToast('预约成功')
          
          setTimeout(() => {
            uni.redirectTo({
              url: `/pages/order/detail?id=${res.data.order_id}`
            })
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('提交预约失败:', e)
      }
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

.form-section {
  padding: 20rpx;
}

.section-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
  margin-bottom: 20rpx;
  margin-top: 20rpx;
}

.clothing-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20rpx;
}

.type-item {
  width: calc(50% - 10rpx);
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2rpx solid transparent;
  box-sizing: border-box;
  
  &.active {
    border-color: $primary-color;
    background-color: rgba($primary-color, 0.05);
  }
}

.type-icon {
  width: 80rpx;
  height: 80rpx;
  margin-bottom: 10rpx;
}

.type-name {
  font-size: $font-size-base;
  color: $text-color;
  font-weight: 500;
}

.type-points {
  font-size: $font-size-sm;
  color: $primary-color;
  margin-top: 6rpx;
}

.quantity-section {
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 20rpx;
  margin-top: 20rpx;
}

.quantity-list {
  margin-top: 10rpx;
}

.quantity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.type-label {
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
}

.quantity-value {
  width: 80rpx;
  text-align: center;
  font-size: $font-size-lg;
  font-weight: bold;
  color: $text-color;
}

.time-selector {
  background-color: $white;
  border-radius: $border-radius-md;
}

.picker-btn {
  display: flex;
  align-items: center;
  padding: 30rpx;
}

.picker-text {
  font-size: $font-size-base;
  color: $text-color;
  margin-right: 20rpx;
}

.arrow {
  margin-left: auto;
  color: $text-muted;
}

.address-card {
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 30rpx;
}

.address-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.name {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
  margin-right: 30rpx;
}

.phone {
  font-size: $font-size-base;
  color: $text-secondary;
}

.address-text {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
}

.address-tags {
  margin-top: 16rpx;
}

.tag {
  display: inline-block;
  padding: 4rpx 16rpx;
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
  font-size: $font-size-xs;
  border-radius: $border-radius-sm;
}

.add-address {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 40rpx;
  border: 2rpx dashed $border-color;
}

.add-address .icon {
  font-size: $font-size-xl;
  color: $primary-color;
  margin-right: 10rpx;
}

.add-address .text {
  font-size: $font-size-base;
  color: $primary-color;
}

.remark-section {
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 20rpx;
  position: relative;
}

.remark-section textarea {
  width: 100%;
  height: 160rpx;
  font-size: $font-size-base;
  color: $text-color;
}

.char-count {
  position: absolute;
  right: 20rpx;
  bottom: 20rpx;
  font-size: $font-size-xs;
  color: $text-muted;
}

.estimate-section {
  background-color: $white;
  margin: 20rpx;
  border-radius: $border-radius-md;
  padding: 30rpx;
}

.estimate-title {
  font-size: $font-size-base;
  font-weight: bold;
  color: $text-color;
  margin-bottom: 20rpx;
}

.estimate-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.estimate-row .label {
  font-size: $font-size-base;
  color: $text-secondary;
}

.estimate-row .value {
  font-size: $font-size-base;
  color: $text-color;
  
  &.highlight {
    color: $primary-color;
    font-weight: bold;
  }
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
  display: flex;
  align-items: baseline;
}

.price-info .label {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.price-info .price {
  font-size: $font-size-xl;
  font-weight: bold;
  color: $primary-color;
}

.submit-btn {
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
    background-color: $border-color;
  }
}

.bottom-spacer {
  height: 180rpx;
}
</style>
