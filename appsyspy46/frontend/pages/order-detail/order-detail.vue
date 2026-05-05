<template>
  <view class="detail-container">
    <scroll-view class="detail-scroll" scroll-y>
      <view v-if="loading" class="loading-state">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="order" class="detail-content">
        <view class="status-section">
          <view 
            class="status-badge"
            :style="{ backgroundColor: getStatusColor(order.status) }"
          >
            <text class="status-text">{{ getStatusText(order.status) }}</text>
          </view>
          <text class="order-no-text">订单号：{{ order.order_no }}</text>
        </view>

        <view class="section">
          <view class="section-header">
            <view class="section-dot"></view>
            <text class="section-title">用户信息</text>
          </view>
          <view class="section-body">
            <view class="info-row">
              <text class="info-label">姓名</text>
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
            <text class="section-title">衣物信息</text>
          </view>
          <view class="section-body">
            <view v-if="order.clothing_types" class="info-row">
              <text class="info-label">衣物类型</text>
              <text class="info-value">{{ order.clothing_types }}</text>
            </view>
            <view class="info-row">
              <text class="info-label">预估重量</text>
              <text class="info-value">{{ order.estimated_weight || 0 }}kg</text>
            </view>
            <view v-if="order.actual_weight" class="info-row">
              <text class="info-label">实际重量</text>
              <text class="info-value">{{ order.actual_weight }}kg</text>
            </view>
            <view v-if="order.estimated_quantity" class="info-row">
              <text class="info-label">预估数量</text>
              <text class="info-value">{{ order.estimated_quantity }}件</text>
            </view>
            <view v-if="order.actual_quantity" class="info-row">
              <text class="info-label">实际数量</text>
              <text class="info-value">{{ order.actual_quantity }}件</text>
            </view>
            <view v-if="order.description" class="info-row">
              <text class="info-label">备注</text>
              <text class="info-value">{{ order.description }}</text>
            </view>
          </view>
        </view>

        <view v-if="order.recycle_photos" class="section">
          <view class="section-header">
            <view class="section-dot"></view>
            <text class="section-title">回收照片</text>
          </view>
          <view class="section-body">
            <view class="photo-grid">
              <image 
                v-for="(photo, index) in photoList" 
                :key="index"
                :src="photo"
                class="photo-item"
                mode="aspectFill"
                @click="previewPhoto(photo)"
              ></image>
            </view>
          </view>
        </view>

        <view class="section">
          <view class="section-header">
            <view class="section-dot"></view>
            <text class="section-title">订单信息</text>
          </view>
          <view class="section-body">
            <view class="info-row">
              <text class="info-label">创建时间</text>
              <text class="info-value">{{ formatTime(order.created_at) }}</text>
            </view>
            <view v-if="order.accepted_at" class="info-row">
              <text class="info-label">接单时间</text>
              <text class="info-value">{{ formatTime(order.accepted_at) }}</text>
            </view>
            <view v-if="order.completed_at" class="info-row">
              <text class="info-label">完成时间</text>
              <text class="info-value">{{ formatTime(order.completed_at) }}</text>
            </view>
            <view v-if="order.total_amount" class="info-row amount">
              <text class="info-label">结算金额</text>
              <text class="info-value">¥{{ order.total_amount.toFixed(2) }}</text>
            </view>
          </view>
        </view>

        <view v-if="order.reject_reason" class="section">
          <view class="section-header">
            <view class="section-dot" style="background-color: #f56c6c;"></view>
            <text class="section-title">拒绝原因</text>
          </view>
          <view class="section-body">
            <text class="reject-text">{{ order.reject_reason }}</text>
          </view>
        </view>
      </view>
    </scroll-view>

    <view v-if="order && order.status === 'pending'" class="bottom-actions">
      <button class="action-btn reject" @click="handleReject">拒绝</button>
      <button class="action-btn accept" @click="handleAccept">接单</button>
    </view>

    <view v-if="order && order.status === 'accepted'" class="bottom-actions">
      <button class="action-btn process" @click="goToProcess">处理订单</button>
    </view>

    <view v-if="showRejectPopup" class="popup-mask" @click="showRejectPopup = false">
      <view class="popup-content" @click.stop>
        <text class="popup-title">拒绝原因</text>
        <textarea 
          class="reject-textarea" 
          v-model="rejectReason"
          placeholder="请输入拒绝原因"
          :maxlength="200"
        ></textarea>
        <view class="popup-actions">
          <button class="popup-btn cancel" @click="showRejectPopup = false">取消</button>
          <button class="popup-btn confirm" @click="submitReject">确认拒绝</button>
        </view>
      </view>
    </view>
  </view>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { getOrderDetail, acceptOrder, rejectOrder, Order, getStatusText, getStatusColor } from '@/api/order'

export default defineComponent({
  setup() {
    const orderId = ref<number>(0)
    const order = ref<Order | null>(null)
    const loading = ref(true)
    const showRejectPopup = ref(false)
    const rejectReason = ref('')

    const photoList = computed(() => {
      if (!order.value?.recycle_photos) return []
      return order.value.recycle_photos.split(',').filter(p => p)
    })

    const fetchOrderDetail = async () => {
      if (!orderId.value) return
      loading.value = true
      try {
        order.value = await getOrderDetail(orderId.value)
      } catch (error) {
        console.error('获取订单详情失败:', error)
        uni.showToast({ title: '获取订单详情失败', icon: 'none' })
      } finally {
        loading.value = false
      }
    }

    const handleAccept = () => {
      uni.showModal({
        title: '提示',
        content: '确认接取此订单？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await acceptOrder({ order_id: orderId.value })
              uni.showToast({ title: '接单成功', icon: 'success' })
              fetchOrderDetail()
            } catch (error) {
              console.error('接单失败:', error)
            }
          }
        }
      })
    }

    const handleReject = () => {
      rejectReason.value = ''
      showRejectPopup.value = true
    }

    const submitReject = async () => {
      if (!rejectReason.value.trim()) {
        uni.showToast({ title: '请输入拒绝原因', icon: 'none' })
        return
      }

      try {
        await rejectOrder({
          order_id: orderId.value,
          reject_reason: rejectReason.value
        })
        uni.showToast({ title: '已拒绝', icon: 'success' })
        showRejectPopup.value = false
        fetchOrderDetail()
      } catch (error) {
        console.error('拒绝订单失败:', error)
      }
    }

    const goToProcess = () => {
      uni.redirectTo({ 
        url: `/pages/order-process/order-process?id=${orderId.value}` 
      })
    }

    const callPhone = (phone: string) => {
      uni.makePhoneCall({ phoneNumber: phone })
    }

    const previewPhoto = (photo: string) => {
      uni.previewImage({
        current: photo,
        urls: photoList.value
      })
    }

    const formatTime = (time: string) => {
      if (!time) return ''
      const date = new Date(time)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hour = String(date.getHours()).padStart(2, '0')
      const minute = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hour}:${minute}`
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
      photoList,
      showRejectPopup,
      rejectReason,
      getStatusText,
      getStatusColor,
      handleAccept,
      handleReject,
      submitReject,
      goToProcess,
      callPhone,
      previewPhoto,
      formatTime
    }
  }
})
</script>

<style lang="scss" scoped>
.detail-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.detail-scroll {
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

.detail-content {
  padding: 20rpx;
}

.status-section {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.status-badge {
  padding: 12rpx 32rpx;
  border-radius: 24rpx;
  margin-bottom: 16rpx;
}

.status-text {
  font-size: 28rpx;
  color: #ffffff;
}

.order-no-text {
  font-size: 24rpx;
  color: #909399;
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

.info-row.amount .info-value {
  color: #f56c6c;
  font-size: 32rpx;
  font-weight: 500;
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

.photo-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.photo-item {
  width: 200rpx;
  height: 200rpx;
  border-radius: 12rpx;
  background-color: #f5f7fa;
}

.reject-text {
  font-size: 26rpx;
  color: #f56c6c;
  line-height: 1.6;
}

.bottom-actions {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: #ffffff;
  padding: 20rpx 30rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  display: flex;
  gap: 20rpx;
  box-shadow: 0 -4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 44rpx;
  font-size: 30rpx;
  border: none;
}

.action-btn.reject {
  background-color: #f5f7fa;
  color: #606266;
}

.action-btn.accept {
  background-color: #2979ff;
  color: #ffffff;
}

.action-btn.process {
  background-color: #07c160;
  color: #ffffff;
}

.popup-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.popup-content {
  width: 600rpx;
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 40rpx;
}

.popup-title {
  display: block;
  font-size: 32rpx;
  font-weight: 500;
  color: #303133;
  text-align: center;
  margin-bottom: 30rpx;
}

.reject-textarea {
  width: 100%;
  height: 200rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  padding: 20rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.popup-actions {
  display: flex;
  gap: 20rpx;
  margin-top: 40rpx;
}

.popup-btn {
  flex: 1;
  height: 80rpx;
  border-radius: 40rpx;
  font-size: 28rpx;
  border: none;
}

.popup-btn.cancel {
  background-color: #f5f7fa;
  color: #606266;
}

.popup-btn.confirm {
  background-color: #f56c6c;
  color: #ffffff;
}
</style>
