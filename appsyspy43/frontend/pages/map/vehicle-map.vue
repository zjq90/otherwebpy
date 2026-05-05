<template>
  <view class="map-container">
    <!-- 顶部筛选栏 -->
    <view class="filter-bar">
      <view class="filter-item" :class="{ active: currentFilter === 'all' }" @click="setFilter('all')">
      <text>全部车辆</text>
    </view>
    <view class="filter-item" :class="{ active: currentFilter === 'idle' }" @click="setFilter('idle')">
      <text>空闲</text>
    </view>
    <view class="filter-item" :class="{ active: currentFilter === 'transit' }" @click="setFilter('transit')">
      <text>运输中</text>
    </view>
    </view>
    
    <!-- 地图区域 -->
    <view class="map-wrapper">
      <map 
        id="vehicleMap"
        class="map"
        :longitude="centerLongitude"
        :latitude="centerLatitude"
        :scale="mapScale"
        :markers="markers"
        :show-location="true"
        :enable-zoom="true"
        :enable-scroll="true"
        :enable-rotate="true"
        @markertap="onMarkerTap"
        @callouttap="onCalloutTap"
      ></map>
      
      <!-- 地图操作按钮 -->
      <view class="map-controls">
        <view class="control-btn" @click="zoomIn">
          <text class="control-icon">+</text>
        </view>
        <view class="control-btn" @click="zoomOut">
          <text class="control-icon">-</text>
        </view>
        <view class="control-btn" @click="locateMe">
          <text class="control-icon">📍</text>
        </view>
        <view class="control-btn" @click="refreshMap">
          <text class="control-icon">🔄</text>
        </view>
      </view>
    </view>
    
    <!-- 车辆列表展示 -->
    <view class="vehicle-list-panel" v-if="selectedVehicle">
      <view class="panel-header">
        <text class="panel-title">车辆详情</text>
        <view class="close-btn" @click="selectedVehicle = null">
          <text>×</text>
        </view>
      </view>
      <view class="vehicle-detail">
        <view class="detail-row">
          <text class="detail-label">车牌号：</text>
          <text class="detail-value">{{ selectedVehicle.plate_number }}</text>
        </view>
        <view class="detail-row">
          <text class="detail-label">车辆名称：</text>
          <text class="detail-value">{{ selectedVehicle.vehicle_name || '-' }}</text>
        </view>
        <view class="detail-row">
          <text class="detail-label">状态：</text>
          <text class="status-tag" :class="getVehicleStatusClass(selectedVehicle.status)">
            {{ getVehicleStatusText(selectedVehicle.status) }}
          </text>
        </view>
        <view class="detail-row">
          <text class="detail-label">当前位置：</text>
          <text class="detail-value">{{ selectedVehicle.current_address || '位置未知' }}</text>
        </view>
        <view class="detail-row" v-if="selectedVehicle.driver">
          <text class="detail-label">司机：</text>
          <text class="detail-value">{{ selectedVehicle.driver.real_name || '-' }}</text>
        </view>
        <view class="detail-row" v-if="selectedVehicle.current_task">
          <text class="detail-label">当前任务：</text>
          <text class="detail-value">{{ selectedVehicle.current_task.task_no || '-' }}</text>
        </view>
      </view>
      <view class="panel-actions">
        <view class="action-btn" @click="viewTrajectory">
          <text class="action-text">查看轨迹</text>
        </view>
        <view class="action-btn primary" @click="callDriver">
          <text class="action-text">联系司机</text>
        </view>
      </view>
    </view>
    
    <!-- 底部车辆列表 -->
    <view class="bottom-vehicle-list" v-if="!selectedVehicle && filteredVehicles.length > 0">
      <scroll-view scroll-x class="vehicle-scroll">
        <view class="vehicle-cards">
          <view 
            class="vehicle-card" 
            v-for="(item, index) in filteredVehicles" 
            :key="index"
            @click="selectVehicle(item)"
          >
            <view class="card-header">
              <text class="card-plate">{{ item.plate_number }}</text>
              <text class="status-tag" :class="getVehicleStatusClass(item.status)">
                {{ getVehicleStatusText(item.status) }}
              </text>
            </view>
            <view class="card-body">
              <text class="card-location">{{ item.current_address || '位置未知' }}</text>
            </view>
            <view class="card-footer" v-if="item.driver">
              <text class="card-driver">司机: {{ item.driver.real_name || '-' }}</text>
            </view>
          </view>
        </view>
      </scroll-view>
    </view>
  </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
  data() {
    return {
      centerLongitude: 116.397428,
      centerLatitude: 39.90923,
      mapScale: 13,
      currentFilter: 'all',
      vehicles: [],
      filteredVehicles: [],
      markers: [],
      selectedVehicle: null,
      mapContext: null
    }
  },
  
  onLoad() {
    this.initMap()
    this.loadVehicles()
  },
  
  onShow() {
    this.loadVehicles()
  },
  
  onReady() {
    this.mapContext = uni.createMapContext('vehicleMap', this)
  },
  
  methods: {
    // 初始化地图
    initMap() {
      // 获取当前位置
      uni.getLocation({
        type: 'gcj02',
        success: (res) => {
          this.centerLongitude = res.longitude
          this.centerLatitude = res.latitude
        }
      })
    },
    
    // 加载车辆数据
    async loadVehicles() {
      try {
        const token = uni.getStorageSync(config.tokenKey)
        const res = await uni.request({
          url: config.baseUrl + '/api/vehicles/with-location',
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          this.vehicles = res[1].data.data || []
          this.applyFilter()
          this.updateMarkers()
          
          // 调整地图中心点
          if (this.vehicles.length > 0) {
            const firstVehicle = this.vehicles[0]
            if (firstVehicle.current_longitude && firstVehicle.current_latitude) {
              this.centerLongitude = firstVehicle.current_longitude
              this.centerLatitude = firstVehicle.current_latitude
            }
          }
        }
      } catch (error) {
        console.error('加载车辆数据失败:', error)
      }
    },
    
    // 应用筛选条件
    applyFilter() {
      if (this.currentFilter === 'all') {
        this.filteredVehicles = this.vehicles
      } else if (this.currentFilter === 'idle') {
        this.filteredVehicles = this.vehicles.filter(v => v.status === 'idle')
      } else if (this.currentFilter === 'transit') {
        this.filteredVehicles = this.vehicles.filter(v => v.status === 'in_transit')
      }
    },
    
    // 设置筛选条件
    setFilter(filter) {
      this.currentFilter = filter
      this.applyFilter()
      this.updateMarkers()
    },
    
    // 更新地图标记点
    updateMarkers() {
      this.markers = this.filteredVehicles.map((vehicle, index) => {
        let iconPath = '/static/icons/truck-idle.png'
        let color = '#909399'
        
        if (vehicle.status === 'in_transit') {
          iconPath = '/static/icons/truck-transit.png'
          color = '#67C23A'
        } else if (vehicle.status === 'maintenance') {
          iconPath = '/static/icons/truck-maintenance.png'
          color = '#E6A23C'
        }
        
        return {
          id: vehicle.id,
          latitude: vehicle.current_latitude || this.centerLatitude + index * 0.01,
          longitude: vehicle.current_longitude || this.centerLongitude + index * 0.01,
          width: 40,
          height: 40,
          iconPath: iconPath,
          callout: {
            content: `${vehicle.plate_number}\n${this.getVehicleStatusText(vehicle.status)}`,
            color: '#FFFFFF',
            bgColor: color,
            fontSize: 12,
            borderRadius: 4,
            padding: 8,
            display: 'ALWAYS',
            textAlign: 'center'
          },
          label: {
            content: vehicle.plate_number,
            color: color,
            fontSize: 10,
            anchorX: -20,
            anchorY: -30
          }
        }
      })
    },
    
    // 获取车辆状态样式类
    getVehicleStatusClass(status) {
      const statusClassMap = {
        [config.vehicleStatus.IDLE]: 'status-pending',
        [config.vehicleStatus.IN_TRANSIT]: 'status-departed',
        [config.vehicleStatus.MAINTENANCE]: 'status-assigned',
        [config.vehicleStatus.DISABLED]: 'status-cancelled'
      }
      return statusClassMap[status] || 'status-cancelled'
    },
    
    // 获取车辆状态文本
    getVehicleStatusText(status) {
      return config.vehicleStatusText[status] || '未知状态'
    },
    
    // 标记点点击事件
    onMarkerTap(e) {
      const markerId = e.detail.markerId
      const vehicle = this.vehicles.find(v => v.id === markerId)
      if (vehicle) {
        this.selectedVehicle = vehicle
      }
    },
    
    // 气泡点击事件
    onCalloutTap(e) {
      const markerId = e.detail.markerId
      const vehicle = this.vehicles.find(v => v.id === markerId)
      if (vehicle) {
        this.selectedVehicle = vehicle
      }
    },
    
    // 选择车辆
    selectVehicle(vehicle) {
      this.selectedVehicle = vehicle
      
      // 移动地图到车辆位置
      if (vehicle.current_latitude && vehicle.current_longitude) {
        this.mapContext.moveToLocation({
          latitude: vehicle.current_latitude,
          longitude: vehicle.current_longitude
        })
      }
    },
    
    // 放大地图
    zoomIn() {
      this.mapScale = Math.min(this.mapScale + 1, 20)
    },
    
    // 缩小地图
    zoomOut() {
      this.mapScale = Math.max(this.mapScale - 1, 3)
    },
    
    // 定位到当前位置
    locateMe() {
      this.mapContext.moveToLocation()
    },
    
    // 刷新地图
    refreshMap() {
      uni.showLoading({ title: '刷新中...' })
      this.loadVehicles().then(() => {
        uni.hideLoading()
        uni.showToast({ title: '刷新成功', icon: 'success' })
      })
    },
    
    // 查看轨迹
    viewTrajectory() {
      if (this.selectedVehicle) {
        uni.navigateTo({
          url: `/pages/map/trajectory?vehicle_id=${this.selectedVehicle.id}`
        })
      }
    },
    
    // 联系司机
    callDriver() {
      if (this.selectedVehicle && this.selectedVehicle.driver) {
        uni.makePhoneCall({
          phoneNumber: this.selectedVehicle.driver.phone || '10086'
        })
      } else {
        uni.showToast({ title: '暂无司机联系方式', icon: 'none' })
      }
    }
  }
}
</script>

<style scoped>
.map-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #F5F5F5;
}

/* 筛选栏 */
.filter-bar {
  display: flex;
  padding: 20rpx;
  background: #FFFFFF;
  gap: 20rpx;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.05);
}

.filter-item {
  flex: 1;
  padding: 16rpx 32rpx;
  background: #F5F7FA;
  border-radius: 8rpx;
  text-align: center;
}

.filter-item text {
  font-size: 26rpx;
  color: #606266;
}

.filter-item.active {
  background: #409EFF;
}

.filter-item.active text {
  color: #FFFFFF;
}

/* 地图区域 */
.map-wrapper {
  flex: 1;
  position: relative;
}

.map {
  width: 100%;
  height: 100%;
}

/* 地图控制按钮 */
.map-controls {
  position: absolute;
  right: 20rpx;
  top: 20rpx;
  display: flex;
  flex-direction: column;
  gap: 20rpx;
  z-index: 100;
}

.control-btn {
  width: 80rpx;
  height: 80rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.15);
}

.control-icon {
  font-size: 36rpx;
}

/* 车辆详情面板 */
.vehicle-list-panel {
  position: absolute;
  left: 20rpx;
  right: 20rpx;
  bottom: 20rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  box-shadow: 0 8rpx 32rpx rgba(0, 0, 0, 0.15);
  z-index: 200;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #EBEEF5;
}

.panel-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #303133;
}

.close-btn {
  width: 50rpx;
  height: 50rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #F5F7FA;
  border-radius: 50%;
}

.close-btn text {
  font-size: 36rpx;
  color: #909399;
}

.vehicle-detail {
  padding: 24rpx 30rpx;
}

.detail-row {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 26rpx;
  color: #909399;
  width: 140rpx;
  flex-shrink: 0;
}

.detail-value {
  font-size: 26rpx;
  color: #606266;
  flex: 1;
}

.panel-actions {
  display: flex;
  padding: 20rpx 30rpx;
  gap: 20rpx;
  border-top: 1rpx solid #EBEEF5;
}

.action-btn {
  flex: 1;
  padding: 24rpx;
  background: #F5F7FA;
  border-radius: 12rpx;
  text-align: center;
}

.action-btn.primary {
  background: #409EFF;
}

.action-btn.primary .action-text {
  color: #FFFFFF;
}

.action-text {
  font-size: 28rpx;
  color: #606266;
}

/* 底部车辆列表 */
.bottom-vehicle-list {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20rpx;
  background: linear-gradient(to top, rgba(0,0,0,0.3), transparent);
  z-index: 100;
}

.vehicle-scroll {
  white-space: nowrap;
}

.vehicle-cards {
  display: inline-flex;
  gap: 20rpx;
}

.vehicle-card {
  width: 320rpx;
  background: #FFFFFF;
  border-radius: 12rpx;
  padding: 20rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.card-plate {
  font-size: 28rpx;
  font-weight: bold;
  color: #303133;
}

.card-body {
  margin-bottom: 12rpx;
}

.card-location {
  font-size: 24rpx;
  color: #909399;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-footer {
  padding-top: 12rpx;
  border-top: 1rpx solid #EBEEF5;
}

.card-driver {
  font-size: 24rpx;
  color: #606266;
}
</style>
