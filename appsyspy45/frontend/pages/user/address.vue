<template>
  <view class="page">
    <view class="address-list" v-if="addresses.length > 0">
      <view 
        class="address-card" 
        v-for="(addr, index) in addresses" 
        :key="index"
        :class="{ selected: selectedId === addr.id }"
        @click="handleSelect(addr)"
      >
        <view class="address-header">
          <view class="address-user">
            <text class="name">{{ addr.contact_name }}</text>
            <text class="phone">{{ addr.contact_phone }}</text>
          </view>
          <view class="address-tags" v-if="addr.is_default">
            <text class="tag default-tag">默认</text>
          </view>
          <view class="address-tags" v-else-if="addr.tag">
            <text class="tag">{{ addr.tag }}</text>
          </view>
        </view>
        <text class="address-detail">
          {{ addr.province }}{{ addr.city }}{{ addr.district }}{{ addr.detail }}
        </text>
        <view class="address-footer">
          <view class="footer-left" @click.stop="toggleDefault(addr)">
            <view class="checkbox" :class="{ checked: addr.is_default }">
              <text class="check-icon" v-if="addr.is_default">✓</text>
            </view>
            <text class="default-text">设为默认</text>
          </view>
          <view class="footer-right">
            <view class="action-btn" @click.stop="editAddress(addr)">
              <text class="action-icon">✏️</text>
              <text class="action-text">编辑</text>
            </view>
            <view class="action-btn" @click.stop="deleteAddress(addr)">
              <text class="action-icon">🗑️</text>
              <text class="action-text">删除</text>
            </view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="empty-state" v-else>
      <view class="empty-content">
        <text class="empty-icon">📍</text>
        <text class="empty-text">暂无收货地址</text>
      </view>
    </view>
    
    <view class="add-section">
      <view class="add-btn" @click="addAddress">
        <text class="add-icon">+</text>
        <text class="add-text">添加收货地址</text>
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
      addresses: [],
      selectedId: null,
      isSelectMode: false
    }
  },
  
  onLoad(options) {
    this.isSelectMode = options.select === '1'
  },
  
  onShow() {
    this.loadAddresses()
  },
  
  methods: {
    async loadAddresses() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      try {
        const res = await api.get('/user/addresses')
        if (res.code === 200) {
          this.addresses = res.data.list || []
        }
      } catch (e) {
        console.error('加载地址列表失败:', e)
      }
    },
    
    handleSelect(addr) {
      if (!this.isSelectMode) return
      
      const pages = getCurrentPages()
      const prevPage = pages[pages.length - 2]
      
      if (prevPage) {
        prevPage.selectedAddress = addr
        prevPage.$forceUpdate()
      }
      
      uni.navigateBack()
    },
    
    async toggleDefault(addr) {
      if (addr.is_default) return
      
      try {
        const res = await api.put(`/user/addresses/${addr.id}/default`)
        if (res.code === 200) {
          this.addresses.forEach(a => {
            a.is_default = a.id === addr.id
          })
          utils.showToast('设置成功')
        }
      } catch (e) {
        console.error('设置默认地址失败:', e)
      }
    },
    
    editAddress(addr) {
      uni.navigateTo({
        url: `/pages/user/address-edit?id=${addr.id}`
      })
    },
    
    async deleteAddress(addr) {
      const confirmed = await utils.showModal('确定要删除该地址吗？')
      if (!confirmed) return
      
      try {
        const res = await api.del(`/user/addresses/${addr.id}`)
        if (res.code === 200) {
          const index = this.addresses.findIndex(a => a.id === addr.id)
          if (index > -1) {
            this.addresses.splice(index, 1)
          }
          utils.showToast('删除成功')
        }
      } catch (e) {
        console.error('删除地址失败:', e)
      }
    },
    
    addAddress() {
      uni.navigateTo({
        url: '/pages/user/address-edit'
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding-bottom: 140rpx;
}

.address-list {
  padding: 20rpx;
}

.address-card {
  background-color: $white;
  border-radius: $border-radius-md;
  padding: 30rpx;
  margin-bottom: 20rpx;
  border: 2rpx solid transparent;
  
  &.selected {
    border-color: $primary-color;
  }
}

.address-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.address-user {
  flex: 1;
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
  background-color: $bg-color;
  color: $text-secondary;
  font-size: $font-size-xs;
  border-radius: $border-radius-sm;
  
  &.default-tag {
    background-color: rgba($primary-color, 0.1);
    color: $primary-color;
  }
}

.address-detail {
  font-size: $font-size-sm;
  color: $text-secondary;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.address-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 20rpx;
  border-top: 1rpx solid $border-color;
}

.footer-left {
  display: flex;
  align-items: center;
}

.checkbox {
  width: 36rpx;
  height: 36rpx;
  border: 2rpx solid $border-color;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10rpx;
  
  &.checked {
    background-color: $primary-color;
    border-color: $primary-color;
  }
}

.check-icon {
  font-size: 24rpx;
  color: $white;
}

.default-text {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.footer-right {
  display: flex;
  gap: 30rpx;
}

.action-btn {
  display: flex;
  align-items: center;
}

.action-icon {
  font-size: 28rpx;
  margin-right: 6rpx;
}

.action-text {
  font-size: $font-size-sm;
  color: $text-secondary;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 200rpx 0;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: $font-size-base;
  color: $text-secondary;
}

.add-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  background-color: $white;
}

.add-btn {
  height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $primary-color;
  color: $white;
  border-radius: 44rpx;
}

.add-icon {
  font-size: 40rpx;
  margin-right: 10rpx;
}

.add-text {
  font-size: $font-size-lg;
  font-weight: bold;
}
</style>
