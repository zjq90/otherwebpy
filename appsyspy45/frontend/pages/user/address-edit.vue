<template>
  <view class="page">
    <view class="form-section">
      <view class="form-item">
        <text class="form-label">收货人</text>
        <input 
          v-model="form.contact_name" 
          type="text" 
          placeholder="请输入收货人姓名"
          maxlength="20"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">手机号</text>
        <input 
          v-model="form.contact_phone" 
          type="number" 
          placeholder="请输入手机号"
          maxlength="11"
        />
      </view>
      
      <view class="form-item" @click="selectRegion">
        <text class="form-label">所在地区</text>
        <picker mode="multiSelector" :value="regionValue" :range="regionRange" @change="onRegionChange" @columnchange="onRegionColumnChange">
          <view class="picker-value">
            <text v-if="form.province && form.city && form.district">
              {{ form.province }} {{ form.city }} {{ form.district }}
            </text>
            <text v-else class="placeholder">请选择省市区</text>
            <text class="picker-arrow">›</text>
          </view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="form-label">详细地址</text>
        <textarea 
          v-model="form.detail" 
          placeholder="请输入详细地址，如街道、门牌号等"
          maxlength="200"
        ></textarea>
      </view>
      
      <view class="form-item">
        <text class="form-label">标签</text>
        <view class="tag-list">
          <view 
            class="tag-item" 
            v-for="(tag, index) in tagOptions" 
            :key="index"
            :class="{ active: form.tag === tag }"
            @click="selectTag(tag)"
          >
            {{ tag }}
          </view>
        </view>
      </view>
      
      <view class="form-item" v-if="!isEdit">
        <text class="form-label">设为默认</text>
        <view class="switch-section" @click="form.is_default = !form.is_default">
          <view class="switch-btn" :class="{ active: form.is_default }">
            <view class="switch-dot"></view>
          </view>
        </view>
      </view>
    </view>
    
    <view class="save-section">
      <view class="save-btn" @click="handleSave">保存</view>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

export default {
  data() {
    return {
      isEdit: false,
      addressId: null,
      form: {
        contact_name: '',
        contact_phone: '',
        province: '',
        city: '',
        district: '',
        detail: '',
        tag: '',
        is_default: false
      },
      tagOptions: ['家', '公司', '学校'],
      regionValue: [0, 0, 0],
      regionRange: [['北京市'], ['北京市'], ['朝阳区', '海淀区', '东城区', '西城区', '丰台区', '石景山区']]
    }
  },
  
  onLoad(options) {
    if (options.id) {
      this.isEdit = true
      this.addressId = parseInt(options.id)
      this.loadAddressDetail()
    }
  },
  
  methods: {
    async loadAddressDetail() {
      try {
        const res = await api.get(`/user/addresses/${this.addressId}`)
        if (res.code === 200) {
          this.form = {
            contact_name: res.data.contact_name || '',
            contact_phone: res.data.contact_phone || '',
            province: res.data.province || '',
            city: res.data.city || '',
            district: res.data.district || '',
            detail: res.data.detail || '',
            tag: res.data.tag || '',
            is_default: res.data.is_default || false
          }
        }
      } catch (e) {
        console.error('加载地址详情失败:', e)
      }
    },
    
    selectRegion() {
    },
    
    onRegionChange(e) {
      const val = e.detail.value
      this.regionValue = val
      
      this.form.province = this.regionRange[0][val[0]]
      this.form.city = this.regionRange[1][val[1]]
      this.form.district = this.regionRange[2][val[2]]
    },
    
    onRegionColumnChange(e) {
      const column = e.detail.column
      const value = e.detail.value
      
      if (column === 0) {
        this.regionValue[0] = value
        this.regionValue[1] = 0
        this.regionValue[2] = 0
      } else if (column === 1) {
        this.regionValue[1] = value
        this.regionValue[2] = 0
      }
    },
    
    selectTag(tag) {
      this.form.tag = this.form.tag === tag ? '' : tag
    },
    
    async handleSave() {
      if (!this.form.contact_name) {
        utils.showToast('请输入收货人姓名')
        return
      }
      
      if (!this.form.contact_phone) {
        utils.showToast('请输入手机号')
        return
      }
      
      if (!utils.validatePhone(this.form.contact_phone)) {
        utils.showToast('请输入正确的手机号')
        return
      }
      
      if (!this.form.province || !this.form.city || !this.form.district) {
        utils.showToast('请选择所在地区')
        return
      }
      
      if (!this.form.detail) {
        utils.showToast('请输入详细地址')
        return
      }
      
      utils.showLoading('保存中...')
      
      try {
        let res
        if (this.isEdit) {
          res = await api.put(`/user/addresses/${this.addressId}`, this.form)
        } else {
          res = await api.post('/user/addresses', this.form)
        }
        
        utils.hideLoading()
        
        if (res.code === 200) {
          utils.showToast(this.isEdit ? '修改成功' : '添加成功')
          
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('保存地址失败:', e)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding-bottom: 40rpx;
}

.form-section {
  background-color: $white;
  padding: 0 30rpx;
  margin-bottom: 40rpx;
}

.form-item {
  display: flex;
  align-items: flex-start;
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.form-label {
  width: 180rpx;
  font-size: $font-size-base;
  color: $text-color;
  flex-shrink: 0;
  padding-top: 4rpx;
}

.form-item input,
.form-item textarea {
  flex: 1;
  font-size: $font-size-base;
  color: $text-color;
}

.form-item textarea {
  height: 120rpx;
}

.picker-value {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.picker-value text:first-child {
  font-size: $font-size-base;
  color: $text-color;
}

.placeholder {
  color: $text-muted;
}

.picker-arrow {
  font-size: $font-size-lg;
  color: $text-muted;
}

.tag-list {
  flex: 1;
  display: flex;
  gap: 20rpx;
}

.tag-item {
  padding: 12rpx 40rpx;
  border: 2rpx solid $border-color;
  border-radius: 30rpx;
  font-size: $font-size-sm;
  color: $text-secondary;
  
  &.active {
    border-color: $primary-color;
    background-color: rgba($primary-color, 0.1);
    color: $primary-color;
  }
}

.switch-section {
  display: flex;
  justify-content: flex-end;
  flex: 1;
}

.switch-btn {
  width: 88rpx;
  height: 48rpx;
  background-color: $border-color;
  border-radius: 24rpx;
  position: relative;
  transition: all 0.3s;
  
  &.active {
    background-color: $primary-color;
  }
}

.switch-dot {
  width: 44rpx;
  height: 44rpx;
  background-color: $white;
  border-radius: 50%;
  position: absolute;
  top: 2rpx;
  left: 2rpx;
  transition: all 0.3s;
  box-shadow: 0 2rpx 4rpx rgba(0, 0, 0, 0.1);
  
  .active & {
    left: 42rpx;
  }
}

.save-section {
  padding: 0 30rpx;
}

.save-btn {
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  background-color: $primary-color;
  color: $white;
  font-size: $font-size-lg;
  font-weight: bold;
  border-radius: $border-radius-lg;
}
</style>
