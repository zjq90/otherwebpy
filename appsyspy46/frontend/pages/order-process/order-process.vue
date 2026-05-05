<template>
  <view class="process-container">
    <scroll-view class="process-scroll" scroll-y>
      <view v-if="loading" class="loading-state">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="order" class="process-content">
        <view class="section">
          <view class="section-header">
            <view class="section-dot"></view>
            <text class="section-title">订单信息</text>
          </view>
          <view class="section-body">
            <view class="info-row">
              <text class="info-label">订单号</text>
              <text class="info-value">{{ order.order_no }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">用户</text>
              <text class="info-value">{{ order.user_name }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">电话</text>
              <text class="info-value" @click="callPhone(order.user_phone)">{{ order.user_phone }}</text>
            </view>
            <view class="info-row address">
              <text class="info-label">地址</text>
              <text class="info-value">{{ order.address }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <view class="section-dot"></view>
            <text class="section-title">预估信息</text>
          </view>
          <view class="section-body">
            <view class="info-row">
              <text class="info-label">预估重量</text>
              <text class="info-value">{{ order.estimated_weight || 0 }}kg</text>
            </view>
            <view class="info-row">
              <text class="info-label">预估数量</text>
              <text class="info-value">{{ order.estimated_quantity || 0 }}件</text>
            </view>
            <view v-if="order.clothing_types" class="info-row">
              <text class="info-label">衣物类型</text>
              <text class="info-value">{{ order.clothing_types }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <view class="section-dot" style="background-color: #07c160;"></view>
            <text class="section-title">实际信息</text>
          </view>
          <view class="section-body">
            <view class="input-item">
              <text class="input-label">实际重量 (kg) <text class="required">*</text></text>
              <input 
                class="input-field"
                v-model="formData.actual_weight"
                type="number"
                placeholder="请输入实际重量"
              />
            </view>

            <view class="input-item">
              <text class="input-label">实际数量 (件)</text>
              <input 
                class="input-field"
                v-model="formData.actual_quantity"
                type="number"
                placeholder="请输入实际数量（可选）"
              />
            </view>

            <view class="input-item">
              <text class="input-label">回收单价 (元/kg)</text>
              <input 
                class="input-field"
                v-model="formData.unit_price"
                type="number"
                placeholder="默认1.5元/kg"
              />
            </view>

            <view v-if="estimatedAmount > 0" class="amount-preview">
              <text class="amount-label">预估结算金额</text>
              <text class="amount-value">¥{{ estimatedAmount.toFixed(2) }}</text>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <view class="section-dot" style="background-color: #ff976a;"></view>
            <text class="section-title">回收照片</text>
          </view>
          <view class="section-body">
            <view class="photo-upload-area">
              <view 
                v-for="(photo, index) in photoList" 
                :key="index"
                class="photo-item"
              >
                <image :src="photo" class="photo-img" mode="aspectFill"></image>
                <view class="photo-delete" @click="deletePhoto(index)">
                  <text class="delete-icon">×</text>
                </view>
              </view>
              <view 
                v-if="photoList.length < 9" 
                class="photo-add-btn"
                @click="chooseImage"
              >
                <text class="add-icon">+</text>
                <text class="add-text">添加照片</text>
              </view>
            </view>
            <text class="photo-hint">最多上传9张照片，点击图片可预览</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <view class="bottom-actions">
      <button 
        class="submit-btn" 
        :disabled="!canSubmit || submitting"
        :loading="submitting"
        @click="submitComplete"
      >
        {{ submitting ? '提交中...' : '确认完成回收' }}
      </button>
    </view>
  </view>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { getOrderDetail, completeOrder, Order } from '@/api/order'

export default defineComponent({
  setup() {
    const orderId = ref<number>(0)
    const order = ref<Order | null>(null)
    const loading = ref(true)
    const submitting = ref(false)

    const formData = ref({
      actual_weight: '',
      actual_quantity: '',
      unit_price: '1.5'
    })

    const photoList = ref<string[]>([])

    const canSubmit = computed(() => {
      const weight = parseFloat(formData.value.actual_weight)
      return weight > 0
    })

    const estimatedAmount = computed(() => {
      const weight = parseFloat(formData.value.actual_weight) || 0
      const price = parseFloat(formData.value.unit_price) || 0
      return weight * price
    })

    const fetchOrderDetail = async () => {
      if (!orderId.value) return
      loading.value = true
      try {
        order.value = await getOrderDetail(orderId.value)
        if (order.value.unit_price > 0) {
          formData.value.unit_price = order.value.unit_price.toString()
        }
      } catch (error) {
        console.error('获取订单详情失败:', error)
        uni.showToast({ title: '获取订单详情失败', icon: 'none' })
      } finally {
        loading.value = false
      }
    }

    const chooseImage = () => {
      uni.chooseImage({
        count: 9 - photoList.value.length,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const tempFilePaths = res.tempFilePaths
          photoList.value = [...photoList.value, ...tempFilePaths]
        }
      })
    }

    const deletePhoto = (index: number) => {
      photoList.value.splice(index, 1)
    }

    const uploadPhotos = async (): Promise<string[]> => {
      if (photoList.value.length === 0) return []
      
      const uploadPromises = photoList.value.map((filePath) => {
        return new Promise<string>((resolve, reject) => {
          uni.uploadFile({
            url: 'http://localhost:8000/api/upload',
            filePath: filePath,
            name: 'file',
            success: (res) => {
              if (res.statusCode === 200) {
                try {
                  const data = JSON.parse(res.data)
                  resolve(data.url || '')
                } catch {
                  resolve('')
                }
              } else {
                reject(new Error('上传失败'))
              }
            },
            fail: (err) => {
              reject(err)
            }
          })
        })
      })

      try {
        const results = await Promise.all(uploadPromises)
        return results.filter(url => url)
      } catch (error) {
        console.error('上传照片失败:', error)
        return []
      }
    }

    const submitComplete = async () => {
      if (!canSubmit.value) {
        uni.showToast({ title: '请输入实际重量', icon: 'none' })
        return
      }

      submitting.value = true
      try {
        const uploadedUrls = await uploadPhotos()
        
        await completeOrder({
          order_id: orderId.value,
          actual_weight: parseFloat(formData.value.actual_weight),
          actual_quantity: formData.value.actual_quantity ? parseInt(formData.value.actual_quantity) : undefined,
          unit_price: parseFloat(formData.value.unit_price) || 1.5,
          recycle_photos: uploadedUrls.join(',')
        })

        uni.showToast({ title: '回收完成', icon: 'success' })
        setTimeout(() => {
          uni.switchTab({ url: '/pages/orders/orders' })
        }, 1500)
      } catch (error) {
        console.error('完成订单失败:', error)
        uni.showToast({ title: '提交失败，请重试', icon: 'none' })
      } finally {
        submitting.value = false
      }
    }

    const callPhone = (phone: string) => {
      uni.makePhoneCall({ phoneNumber: phone })
    }

    onMounted(() => {
      const pages = getCurrentPages()
      const currentPage = pages[pages.length - 1]
      const id = (currentPage as any).options?.id
      if (id) {
        orderId.value = Number(id)
        fetchOrderDetail()
      }
    })

    return {
      order,
      loading,
      submitting,
      formData,
      photoList,
      canSubmit,
      estimatedAmount,
      chooseImage,
      deletePhoto,
      submitComplete,
      callPhone
    }
  }
})
</script>

<style lang="scss" scoped>
.process-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.process-scroll {
  flex: 1;
  padding-bottom: 140rpx;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #909399;
}

.process-content {
  padding: 20rpx;
}

.section {
  background-color: #ffffff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  overflow: hidden;
}

.section-header {
  display: flex;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.section-dot {
  width: 8rpx;
  height: 28rpx;
  background-color: #2979ff;
  border-radius: 4rpx;
  margin-right: 16rpx;
}

.section-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #303133;
}

.section-body {
  padding: 20rpx 30rpx;
}

.info-row {
  display: flex;
  padding: 12rpx 0;
}

.info-row.address {
  align-items: flex-start;
}

.info-label {
  width: 160rpx;
  font-size: 26rpx;
  color: #909399;
  flex-shrink: 0;
}

.info-value {
  flex: 1;
  font-size: 26rpx;
  color: #303133;
  line-height: 1.6;
}

.input-item {
  margin-bottom: 30rpx;
}

.input-label {
  display: block;
  font-size: 26rpx;
  color: #606266;
  margin-bottom: 12rpx;
}

.required {
  color: #f56c6c;
}

.input-field {
  width: 100%;
  height: 80rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  padding: 0 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.amount-preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx;
  background: linear-gradient(90deg, rgba(7, 193, 96, 0.1) 0%, rgba(7, 193, 96, 0.05) 100%);
  border-radius: 12rpx;
  margin-top: 20rpx;
}

.amount-label {
  font-size: 26rpx;
  color: #606266;
}

.amount-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #07c160;
}

.photo-upload-area {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.photo-item {
  position: relative;
  width: 200rpx;
  height: 200rpx;
}

.photo-img {
  width: 100%;
  height: 100%;
  border-radius: 12rpx;
}

.photo-delete {
  position: absolute;
  top: -16rpx;
  right: -16rpx;
  width: 40rpx;
  height: 40rpx;
  background-color: rgba(0, 0, 0, 0.6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-icon {
  font-size: 32rpx;
  color: #ffffff;
  line-height: 1;
}

.photo-add-btn {
  width: 200rpx;
  height: 200rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  border: 2rpx dashed #dcdfe6;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.add-icon {
  font-size: 60rpx;
  color: #c0c4cc;
  line-height: 1;
}

.add-text {
  font-size: 24rpx;
  color: #909399;
  margin-top: 8rpx;
}

.photo-hint {
  display: block;
  font-size: 22rpx;
  color: #c0c4cc;
  margin-top: 16rpx;
}

.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #ffffff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(90deg, #07c160 0%, #05a652 100%);
  border-radius: 44rpx;
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 500;
  border: none;
}

.submit-btn[disabled] {
  background: #c0c4cc;
  color: #ffffff;
}
</style>
