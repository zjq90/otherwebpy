<template>
  <view class="orders-container">
    <view class="tabs-header">
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'pending' }"
        @click="switchTab('pending')"
      >
        <text class="tab-text">待接单</text>
        <view v-if="pendingCount > 0" class="tab-badge">{{ pendingCount }}</view>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'accepted' }"
        @click="switchTab('accepted')"
      >
        <text class="tab-text">已接单</text>
      </view>
      <view 
        class="tab-item" 
        :class="{ active: activeTab === 'completed' }"
        @click="switchTab('completed')"
      >
        <text class="tab-text">已完成</text>
      </view>
    </view>

    <scroll-view 
      class="orders-scroll" 
      scroll-y 
      :refresher-enabled="true"
      :refresher-triggered="refreshing"
      @refresherrefresh="onRefresh"
      @scrolltolower="loadMore"
    >
      <view v-if="orders.length === 0 && !loading" class="empty-state">
        <text class="empty-text">暂无订单</text>
      </view>

      <view 
        v-for="order in orders" 
        :key="order.id" 
        class="order-card"
        @click="goToDetail(order.id)"
      >
        <view class="order-header">
          <text class="order-no">{{ order.order_no }}</text>
          <view 
            class="status-tag" 
            :style="{ backgroundColor: getStatusColor(order.status) }"
          >
            <text class="status-text">{{ getStatusText(order.status) }}</text>
          </view>
        </view>

        <view class="order-content">
          <view class="user-info">
            <text class="user-name">{{ order.user_name }}</text>
            <text class="user-phone">{{ order.user_phone }}</text>
          </view>
          <view class="address-row">
            <text class="address-label">地址：</text>
            <text class="address-text">{{ order.address }}</text>
          </view>
          <view class="order-footer">
            <view class="footer-left">
              <text class="weight-text">预估重量：{{ order.estimated_weight || 0 }}kg</text>
            </view>
            <view class="footer-right">
              <text class="time-text">{{ formatTime(order.created_at) }}</text>
            </view>
          </view>
        </view>

        <view v-if="order.status === 'pending'" class="order-actions">
          <button class="action-btn reject" @click.stop="handleReject(order)">拒绝</button>
          <button class="action-btn accept" @click.stop="handleAccept(order)">接单</button>
        </view>

        <view v-if="order.status === 'accepted'" class="order-actions">
          <button class="action-btn process" @click.stop="goToProcess(order)">处理订单</button>
        </view>
      </view>

      <view v-if="loading" class="loading-state">
        <text class="loading-text">加载中...</text>
      </view>
    </scroll-view>

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
import { defineComponent, reactive, ref, onMounted, watch } from 'vue'
import { 
  getPendingOrders, 
  getAcceptedOrders, 
  getCompletedOrders,
  acceptOrder,
  rejectOrder,
  Order,
  getStatusText,
  getStatusColor
} from '@/api/order'

type TabType = 'pending' | 'accepted' | 'completed'

export default defineComponent({
  setup() {
    const activeTab = ref<TabType>('pending')
    const orders = ref<Order[]>([])
    const loading = ref(false)
    const refreshing = ref(false)
    const page = ref(1)
    const pageSize = ref(10)
    const hasMore = ref(true)
    const pendingCount = ref(0)

    const showRejectPopup = ref(false)
    const rejectReason = ref('')
    const currentOrder = ref<Order | null>(null)

    const fetchOrders = async (isRefresh: boolean = false) => {
      if (isRefresh) {
        page.value = 1
        hasMore.value = true
        refreshing.value = true
      }

      if (!hasMore.value || loading.value) return
      loading.value = true

      try {
        let result
        switch (activeTab.value) {
          case 'pending':
            result = await getPendingOrders(page.value, pageSize.value)
            pendingCount.value = result.total
            break
          case 'accepted':
            result = await getAcceptedOrders(page.value, pageSize.value)
            break
          case 'completed':
            result = await getCompletedOrders(page.value, pageSize.value)
            break
        }

        if (isRefresh) {
          orders.value = result.orders
        } else {
          orders.value = [...orders.value, ...result.orders]
        }

        hasMore.value = orders.value.length < result.total
        page.value++
      } catch (error) {
        console.error('获取订单列表失败:', error)
        uni.showToast({ title: '获取数据失败', icon: 'none' })
      } finally {
        loading.value = false
        refreshing.value = false
      }
    }

    const switchTab = (tab: TabType) => {
      if (activeTab.value !== tab) {
        activeTab.value = tab
        orders.value = []
        fetchOrders(true)
      }
    }

    const onRefresh = () => {
      fetchOrders(true)
    }

    const loadMore = () => {
      if (hasMore.value && !loading.value) {
        fetchOrders(false)
      }
    }

    const handleAccept = async (order: Order) => {
      uni.showModal({
        title: '提示',
        content: '确认接取此订单？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await acceptOrder({ order_id: order.id })
              uni.showToast({ title: '接单成功', icon: 'success' })
              fetchOrders(true)
            } catch (error) {
              console.error('接单失败:', error)
            }
          }
        }
      })
    }

    const handleReject = (order: Order) => {
      currentOrder.value = order
      rejectReason.value = ''
      showRejectPopup.value = true
    }

    const submitReject = async () => {
      if (!rejectReason.value.trim()) {
        uni.showToast({ title: '请输入拒绝原因', icon: 'none' })
        return
      }
      if (!currentOrder.value) return

      try {
        await rejectOrder({
          order_id: currentOrder.value.id,
          reject_reason: rejectReason.value
        })
        uni.showToast({ title: '已拒绝', icon: 'success' })
        showRejectPopup.value = false
        fetchOrders(true)
      } catch (error) {
        console.error('拒绝订单失败:', error)
      }
    }

    const goToDetail = (orderId: number) => {
      uni.navigateTo({ 
        url: `/pages/order-detail/order-detail?id=${orderId}` 
      })
    }

    const goToProcess = (order: Order) => {
      uni.navigateTo({ 
        url: `/pages/order-process/order-process?id=${order.id}` 
      })
    }

    const formatTime = (time: string) => {
      if (!time) return ''
      const date = new Date(time)
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hour = String(date.getHours()).padStart(2, '0')
      const minute = String(date.getMinutes()).padStart(2, '0')
      return `${month}-${day} ${hour}:${minute}`
    }

    watch(activeTab, () => {
      fetchOrders(true)
    })

    onMounted(() => {
      fetchOrders(true)
    })

    return {
      activeTab,
      orders,
      loading,
      refreshing,
      pendingCount,
      showRejectPopup,
      rejectReason,
      getStatusText,
      getStatusColor,
      switchTab,
      onRefresh,
      loadMore,
      handleAccept,
      handleReject,
      submitReject,
      goToDetail,
      goToProcess,
      formatTime
    }
  }
})
</script>

<style lang="scss" scoped>
.orders-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.tabs-header {
  display: flex;
  background-color: #ffffff;
  padding: 0 20rpx;
  border-bottom: 1rpx solid #e4e7ed;
}

.tab-item {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 96rpx;
  position: relative;
}

.tab-text {
  font-size: 28rpx;
  color: #606266;
}

.tab-item.active .tab-text {
  color: #2979ff;
  font-weight: 500;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60rpx;
  height: 4rpx;
  background-color: #2979ff;
  border-radius: 2rpx;
}

.tab-badge {
  position: absolute;
  top: 20rpx;
  right: 40rpx;
  min-width: 32rpx;
  height: 32rpx;
  background-color: #f56c6c;
  border-radius: 16rpx;
  font-size: 20rpx;
  color: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8rpx;
}

.orders-scroll {
  flex: 1;
  padding: 20rpx;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 400rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
}

.order-card {
  background-color: #ffffff;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.04);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.order-no {
  font-size: 26rpx;
  color: #909399;
}

.status-tag {
  padding: 6rpx 16rpx;
  border-radius: 8rpx;
}

.status-text {
  font-size: 24rpx;
  color: #ffffff;
}

.order-content {
  margin-bottom: 20rpx;
}

.user-info {
  display: flex;
  align-items: center;
  margin-bottom: 12rpx;
}

.user-name {
  font-size: 32rpx;
  font-weight: 500;
  color: #303133;
  margin-right: 20rpx;
}

.user-phone {
  font-size: 28rpx;
  color: #606266;
}

.address-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16rpx;
}

.address-label {
  font-size: 26rpx;
  color: #909399;
  flex-shrink: 0;
}

.address-text {
  font-size: 26rpx;
  color: #606266;
  flex: 1;
  line-height: 1.6;
}

.order-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.weight-text {
  font-size: 24rpx;
  color: #909399;
}

.time-text {
  font-size: 24rpx;
  color: #c0c4cc;
}

.order-actions {
  display: flex;
  gap: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.action-btn {
  flex: 1;
  height: 72rpx;
  border-radius: 36rpx;
  font-size: 28rpx;
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

.loading-state {
  text-align: center;
  padding: 30rpx;
}

.loading-text {
  font-size: 26rpx;
  color: #909399;
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
