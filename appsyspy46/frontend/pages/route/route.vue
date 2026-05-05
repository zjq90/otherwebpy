<template>
  <view class="route-container">
    <view class="route-header">
      <text class="header-title">上门路线规划</text>
      <text class="header-subtitle">共 {{ orders.length }} 个待上门订单</text>
    </view>

    <scroll-view class="route-scroll" scroll-y>
      <view v-if="loading" class="loading-state">
        <text class="loading-text">加载中...</text>
      </view>

      <view v-else-if="orders.length === 0" class="empty-state">
        <text class="empty-icon">🚗</text>
        <text class="empty-text">暂无待上门的订单</text>
        <text class="empty-hint">接单后会在这里显示待上门的订单</text>
      </view>

      <view v-else class="route-content">
        <view class="route-summary">
          <view class="summary-item">
            <text class="summary-value">{{ orders.length }}</text>
            <text class="summary-label">待上门</text>
          </view>
          <view class="summary-item">
            <text class="summary-value">{{ totalWeight }}</text>
            <text class="summary-label">总重量(kg)</text>
          </view>
          <view class="summary-item">
            <text class="summary-value">{{ totalDistance }}</text>
            <text class="summary-label">预估距离(km)</text>
          </view>
        </view>

        <view class="route-plan" v-if="optimizedRoute.length > 0">
          <view class="plan-header">
            <view class="plan-dot start"></view>
            <text class="plan-title">当前位置</text>
          </view>
          
          <view 
            v-for="(point, index) in optimizedRoute" 
            :key="point.order_id"
            class="plan-item"
          >
            <view class="plan-connector">
              <view class="connector-line"></view>
              <view class="connector-dot" :class="{ isLast: index === optimizedRoute.length - 1 }">
                <text class="dot-number">{{ index + 1 }}</text>
              </view>
            </view>
            <view class="plan-info">
              <view class="info-header">
                <text class="info-user">{{ point.user_name }}</text>
                <text class="info-weight">{{ point.estimated_weight || 0 }}kg</text>
              </view>
              <text class="info-address">{{ point.address }}</text>
              <view class="info-footer">
                <text class="info-phone" @click="callPhone(point.user_phone)">
                  📞 {{ point.user_phone }}
                </text>
                <button class="info-btn" @click="goToProcess(point.order_id)">
                  处理
                </button>
              </view>
            </view>
          </view>
        </view>

        <view class="order-list">
          <view class="list-header">
            <text class="list-title">订单列表</text>
            <view class="sort-info">
              <text class="sort-text">按路线排序</text>
            </view>
          </view>
          
          <view 
            v-for="(order, index) in optimizedRoute" 
            :key="order.order_id"
            class="order-card"
          >
            <view class="card-order">
              <text class="order-sort">{{ index + 1 }}</text>
            </view>
            <view class="card-content">
              <view class="content-header">
                <text class="content-user">{{ order.user_name }}</text>
                <text class="content-phone" @click="callPhone(order.user_phone)">{{ order.user_phone }}</text>
              </view>
              <text class="content-address">{{ order.address }}</text>
              <view class="content-footer">
                <text class="content-weight">预估：{{ order.estimated_weight || 0 }}kg</text>
                <button class="content-btn" @click="goToProcess(order.order_id)">
                  处理订单
                </button>
              </view>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>

    <view v-if="orders.length > 0" class="bottom-actions">
      <button class="action-btn navigate" @click="startNavigation">
        开始导航
      </button>
    </view>
  </view>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { getAcceptedOrders, Order } from '@/api/order'

interface RoutePoint {
  order_id: number
  user_name: string
  user_phone: string
  address: string
  estimated_weight: number
  latitude?: number
  longitude?: number
}

export default defineComponent({
  setup() {
    const orders = ref<Order[]>([])
    const loading = ref(true)
    const currentLocation = ref<{ lat: number; lng: number } | null>(null)

    const totalWeight = computed(() => {
      return orders.value.reduce((sum, o) => sum + (o.estimated_weight || 0), 0).toFixed(1)
    })

    const totalDistance = computed(() => {
      const count = orders.value.length
      if (count <= 1) return '0'
      return (count * 2).toFixed(1)
    })

    const optimizedRoute = computed<RoutePoint[]>(() => {
      return orders.value.map((order) => ({
        order_id: order.id,
        user_name: order.user_name,
        user_phone: order.user_phone,
        address: order.address,
        estimated_weight: order.estimated_weight || 0,
        latitude: order.latitude,
        longitude: order.longitude
      }))
    })

    const fetchAcceptedOrders = async () => {
      loading.value = true
      try {
        const result = await getAcceptedOrders(1, 100)
        orders.value = result.orders || []
      } catch (error) {
        console.error('获取已接单列表失败:', error)
        uni.showToast({ title: '获取数据失败', icon: 'none' })
      } finally {
        loading.value = false
      }
    }

    const goToProcess = (orderId: number) => {
      uni.navigateTo({ 
        url: `/pages/order-process/order-process?id=${orderId}` 
      })
    }

    const callPhone = (phone: string) => {
      uni.makePhoneCall({ phoneNumber: phone })
    }

    const startNavigation = () => {
      if (optimizedRoute.value.length === 0) {
        uni.showToast({ title: '没有待导航的订单', icon: 'none' })
        return
      }

      const firstPoint = optimizedRoute.value[0]
      uni.showToast({ 
        title: '正在打开地图...', 
        icon: 'loading' 
      })

      if (firstPoint.latitude && firstPoint.longitude) {
        uni.openLocation({
          latitude: firstPoint.latitude,
          longitude: firstPoint.longitude,
          name: firstPoint.user_name,
          address: firstPoint.address,
          success: () => {
            console.log('打开地图成功')
          },
          fail: (err) => {
            console.error('打开地图失败:', err)
            uni.showToast({ title: '无法打开地图', icon: 'none' })
          }
        })
      } else {
        uni.showModal({
          title: '提示',
          content: '该订单没有位置信息，建议先联系用户确认地址',
          showCancel: false
        })
      }
    }

    onMounted(() => {
      fetchAcceptedOrders()
    })

    return {
      orders,
      loading,
      totalWeight,
      totalDistance,
      optimizedRoute,
      goToProcess,
      callPhone,
      startNavigation
    }
  }
})
</script>

<style lang="scss" scoped>
.route-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.route-header {
  background: linear-gradient(90deg, #2979ff 0%, #1976d2 100%);
  padding: 30rpx;
  padding-bottom: 40rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #ffffff;
  display: block;
}

.header-subtitle {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8rpx;
  display: block;
}

.route-scroll {
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 100rpx 40rpx;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 32rpx;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12rpx;
}

.empty-hint {
  font-size: 26rpx;
  color: #909399;
}

.route-content {
  padding: 20rpx;
}

.route-summary {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  display: flex;
  justify-content: space-around;
  margin-bottom: 20rpx;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-value {
  font-size: 40rpx;
  font-weight: bold;
  color: #2979ff;
}

.summary-label {
  font-size: 24rpx;
  color: #909399;
  margin-top: 8rpx;
}

.route-plan {
  background-color: #ffffff;
  border-radius: 16rpx;
  padding: 30rpx;
  margin-bottom: 20rpx;
}

.plan-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.plan-dot {
  width: 24rpx;
  height: 24rpx;
  border-radius: 50%;
  margin-right: 16rpx;
}

.plan-dot.start {
  background-color: #07c160;
}

.plan-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #303133;
}

.plan-item {
  display: flex;
  margin-left: 11rpx;
  padding: 20rpx 0;
}

.plan-connector {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 20rpx;
}

.connector-line {
  width: 2rpx;
  flex: 1;
  background-color: #2979ff;
}

.connector-dot {
  width: 48rpx;
  height: 48rpx;
  background-color: #2979ff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.connector-dot.isLast {
  background-color: #f56c6c;
}

.dot-number {
  font-size: 24rpx;
  color: #ffffff;
  font-weight: bold;
}

.plan-info {
  flex: 1;
  padding: 16rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
}

.info-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8rpx;
}

.info-user {
  font-size: 30rpx;
  font-weight: 500;
  color: #303133;
}

.info-weight {
  font-size: 26rpx;
  color: #2979ff;
  font-weight: 500;
}

.info-address {
  font-size: 24rpx;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12rpx;
}

.info-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-phone {
  font-size: 24rpx;
  color: #2979ff;
}

.info-btn {
  width: 140rpx;
  height: 56rpx;
  background-color: #2979ff;
  border-radius: 28rpx;
  font-size: 24rpx;
  color: #ffffff;
  border: none;
  margin: 0;
  padding: 0;
}

.order-list {
  background-color: #ffffff;
  border-radius: 16rpx;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.list-title {
  font-size: 30rpx;
  font-weight: 500;
  color: #303133;
}

.sort-text {
  font-size: 24rpx;
  color: #909399;
}

.order-card {
  display: flex;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.order-card:last-child {
  border-bottom: none;
}

.card-order {
  width: 60rpx;
  height: 60rpx;
  background: linear-gradient(135deg, #2979ff 0%, #1976d2 100%);
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
  flex-shrink: 0;
}

.order-sort {
  font-size: 28rpx;
  font-weight: bold;
  color: #ffffff;
}

.card-content {
  flex: 1;
}

.content-header {
  display: flex;
  align-items: center;
  margin-bottom: 8rpx;
}

.content-user {
  font-size: 30rpx;
  font-weight: 500;
  color: #303133;
  margin-right: 20rpx;
}

.content-phone {
  font-size: 26rpx;
  color: #606266;
}

.content-address {
  font-size: 24rpx;
  color: #606266;
  line-height: 1.5;
  margin-bottom: 12rpx;
}

.content-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-weight {
  font-size: 24rpx;
  color: #909399;
}

.content-btn {
  width: 160rpx;
  height: 56rpx;
  background-color: #07c160;
  border-radius: 28rpx;
  font-size: 24rpx;
  color: #ffffff;
  border: none;
  margin: 0;
  padding: 0;
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

.action-btn {
  width: 100%;
  height: 88rpx;
  background: linear-gradient(90deg, #2979ff 0%, #1976d2 100%);
  border-radius: 44rpx;
  color: #ffffff;
  font-size: 30rpx;
  font-weight: 500;
  border: none;
}
</style>
