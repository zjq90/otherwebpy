<template>
  <view class="index-container">
    <!-- 顶部状态栏占位 -->
    <view class="status-bar-placeholder"></view>
    
    <!-- 顶部欢迎栏 -->
    <view class="welcome-bar">
      <view class="welcome-info">
        <text class="welcome-text">您好，{{ userInfo.real_name || '用户' }}</text>
        <text class="welcome-role">{{ roleName }}</text>
      </view>
      <view class="welcome-avatar">
        <text class="avatar-text">{{ (userInfo.real_name || '用').charAt(0) }}</text>
      </view>
    </view>
    
    <!-- 数据统计卡片 -->
    <view class="stats-section">
      <view class="stats-card" v-for="(item, index) in statsList" :key="index" @click="handleStatClick(item)">
        <view class="stat-icon" :style="{ background: item.bgColor }">
          <text>{{ item.icon }}</text>
        </view>
        <view class="stat-info">
          <text class="stat-value">{{ item.value }}</text>
          <text class="stat-label">{{ item.label }}</text>
        </view>
      </view>
    </view>
    
    <!-- 快捷功能入口 -->
    <view class="quick-section">
      <view class="section-title">
        <text class="title-text">快捷功能</text>
      </view>
      <view class="quick-grid">
        <view 
          class="quick-item" 
          v-for="(item, index) in quickMenuList" 
          :key="index"
          @click="handleQuickClick(item)"
        >
          <view class="quick-icon" :style="{ background: item.bgColor }">
            <text>{{ item.icon }}</text>
          </view>
          <text class="quick-label">{{ item.label }}</text>
        </view>
      </view>
    </view>
    
    <!-- 待办任务 -->
    <view class="todo-section">
      <view class="section-title flex-between">
        <text class="title-text">待办任务</text>
        <text class="title-more" @click="goToTaskList">查看全部 ></text>
      </view>
      <view class="todo-list" v-if="todoList.length > 0">
        <view 
          class="todo-item card" 
          v-for="(item, index) in todoList" 
          :key="index"
          @click="goToTaskDetail(item.id)"
        >
          <view class="todo-header">
            <text class="todo-no">{{ item.task_no }}</text>
            <text class="status-tag" :class="getStatusClass(item.status)">
              {{ getStatusText(item.status) }}
            </text>
          </view>
          <view class="todo-content">
            <view class="todo-row">
              <text class="todo-label">货物：</text>
              <text class="todo-value">{{ item.cargo_name || '-' }}</text>
            </view>
            <view class="todo-row">
              <text class="todo-label">目的地：</text>
              <text class="todo-value">{{ item.unloading_address || '-' }}</text>
            </view>
          </view>
        </view>
      </view>
      <view class="empty-state" v-else>
        <text class="empty-icon">📋</text>
        <text class="empty-text">暂无待办任务</text>
      </view>
    </view>
    
    <!-- 车辆状态 -->
    <view class="vehicle-section" v-if="showVehicleSection">
      <view class="section-title flex-between">
        <text class="title-text">车辆状态</text>
        <text class="title-more" @click="goToVehicleList">查看全部 ></text>
      </view>
      <view class="vehicle-list">
        <view 
          class="vehicle-item card" 
          v-for="(item, index) in vehicleList" 
          :key="index"
          @click="goToVehicleMap"
        >
          <view class="vehicle-icon" :class="getVehicleStatusClass(item.status)">
            <text>🚛</text>
          </view>
          <view class="vehicle-info">
            <view class="vehicle-row">
              <text class="vehicle-plate">{{ item.plate_number }}</text>
              <text class="status-tag" :class="getVehicleStatusClass(item.status)">
                {{ getVehicleStatusText(item.status) }}
              </text>
            </view>
            <view class="vehicle-row">
              <text class="vehicle-location">{{ item.current_address || '位置未知' }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
  data() {
    return {
      userInfo: {},
      roleName: '',
      statsList: [
        { icon: '📦', value: 0, label: '待分配任务', key: 'pending', bgColor: '#FEF0F0' },
        { icon: '🚚', value: 0, label: '运输中', key: 'transit', bgColor: '#ECF5FF' },
        { icon: '✅', value: 0, label: '今日完成', key: 'today', bgColor: '#F0F9EB' },
        { icon: '🚛', value: 0, label: '空闲车辆', key: 'idle', bgColor: '#FDF6EC' }
      ],
      quickMenuList: [],
      todoList: [],
      vehicleList: [],
      showVehicleSection: true
    }
  },
  
  onLoad() {
    this.initPage()
  },
  
  onShow() {
    this.loadData()
  },
  
  methods: {
    // 初始化页面
    initPage() {
      this.userInfo = uni.getStorageSync(config.userInfoKey) || {}
      this.roleName = this.getRoleName(this.userInfo.role)
      this.initQuickMenu()
    },
    
    // 初始化快捷菜单
    initQuickMenu() {
      const role = this.userInfo.role
      
      // 默认菜单
      const defaultMenus = [
        { icon: '📋', label: '运输任务', path: '/pages/task/task-list', bgColor: '#ECF5FF' }
      ]
      
      // 根据角色配置菜单
      if (role === config.roles.ADMIN) {
        this.quickMenuList = [
          { icon: '👥', label: '用户管理', path: '/pages/user/user-list', bgColor: '#ECF5FF' },
          { icon: '🚛', label: '车辆管理', path: '/pages/vehicle/vehicle-list', bgColor: '#F0F9EB' },
          { icon: '📋', label: '任务管理', path: '/pages/task/task-list', bgColor: '#FDF6EC' },
          { icon: '🗺️', label: '车辆监控', path: '/pages/map/vehicle-map', bgColor: '#FEF0F0' }
        ]
      } else if (role === config.roles.DISPATCHER) {
        this.quickMenuList = [
          { icon: '➕', label: '创建任务', path: '/pages/task/task-create', bgColor: '#F0F9EB' },
          { icon: '📋', label: '任务管理', path: '/pages/task/task-list', bgColor: '#ECF5FF' },
          { icon: '🗺️', label: '车辆监控', path: '/pages/map/vehicle-map', bgColor: '#FDF6EC' },
          { icon: '🚛', label: '车辆列表', path: '/pages/vehicle/vehicle-list', bgColor: '#FEF0F0' }
        ]
      } else if (role === config.roles.DRIVER) {
        this.quickMenuList = [
          { icon: '📋', label: '我的任务', path: '/pages/driver/my-tasks', bgColor: '#ECF5FF' },
          { icon: '📍', label: '上报位置', path: '', action: 'reportLocation', bgColor: '#F0F9EB' },
          { icon: '🗺️', label: '行驶轨迹', path: '/pages/map/trajectory', bgColor: '#FDF6EC' }
        ]
        this.showVehicleSection = false
      }
    },
    
    // 加载数据
    async loadData() {
      await Promise.all([
        this.loadStats(),
        this.loadTodoTasks(),
        this.loadVehicles()
      ])
    },
    
    // 加载统计数据
    async loadStats() {
      try {
        const token = uni.getStorageSync(config.tokenKey)
        const res = await uni.request({
          url: config.baseUrl + '/api/test/system-status',
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          const data = res[1].data.data
          this.statsList[0].value = data.tasks_pending || 0
          this.statsList[1].value = data.tasks_in_progress || 0
          this.statsList[2].value = data.tasks_completed_today || 0
          this.statsList[3].value = data.vehicles_idle || 0
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    
    // 加载待办任务
    async loadTodoTasks() {
      try {
        const token = uni.getStorageSync(config.tokenKey)
        const role = this.userInfo.role
        
        let url = config.baseUrl + '/api/tasks?page=1&size=5'
        
        // 司机只看自己的任务
        if (role === config.roles.DRIVER) {
          url += '&status=assigned,confirmed,departed,arrived,unloading'
        }
        
        const res = await uni.request({
          url: url,
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          this.todoList = res[1].data.data.items || []
        }
      } catch (error) {
        console.error('加载待办任务失败:', error)
      }
    },
    
    // 加载车辆列表
    async loadVehicles() {
      try {
        if (!this.showVehicleSection) return
        
        const token = uni.getStorageSync(config.tokenKey)
        const res = await uni.request({
          url: config.baseUrl + '/api/vehicles/with-location?page=1&size=5',
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          this.vehicleList = res[1].data.data || []
        }
      } catch (error) {
        console.error('加载车辆列表失败:', error)
      }
    },
    
    // 获取角色名称
    getRoleName(role) {
      const roleNames = {
        [config.roles.ADMIN]: '管理员',
        [config.roles.DISPATCHER]: '调度员',
        [config.roles.DRIVER]: '司机'
      }
      return roleNames[role] || '未知角色'
    },
    
    // 获取任务状态样式类
    getStatusClass(status) {
      return `status-${status}`
    },
    
    // 获取任务状态文本
    getStatusText(status) {
      return config.taskStatusText[status] || '未知状态'
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
    
    // 统计卡片点击
    handleStatClick(item) {
      uni.navigateTo({
        url: '/pages/task/task-list'
      })
    },
    
    // 快捷功能点击
    handleQuickClick(item) {
      if (item.action === 'reportLocation') {
        this.reportLocation()
      } else if (item.path) {
        uni.navigateTo({
          url: item.path
        })
      }
    },
    
    // 上报位置
    async reportLocation() {
      uni.showLoading({ title: '获取位置中...' })
      
      try {
        const locationRes = await uni.getLocation({
          type: 'gcj02',
          isHighAccuracy: true
        })
        
        if (locationRes[1].errMsg === 'getLocation:ok') {
          const { latitude, longitude, address } = locationRes[1]
          
          const token = uni.getStorageSync(config.tokenKey)
          const res = await uni.request({
            url: config.baseUrl + '/api/locations',
            method: 'POST',
            header: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            data: {
              latitude: latitude,
              longitude: longitude,
              address: address || ''
            }
          })
          
          if (res[1].statusCode === 200 && res[1].data.code === 200) {
            uni.showToast({
              title: '位置上报成功',
              icon: 'success'
            })
          } else {
            uni.showToast({
              title: res[1].data?.message || '上报失败',
              icon: 'none'
            })
          }
        }
      } catch (error) {
        console.error('上报位置失败:', error)
        uni.showToast({
          title: '获取位置失败',
          icon: 'none'
        })
      } finally {
        uni.hideLoading()
      }
    },
    
    // 跳转到任务列表
    goToTaskList() {
      uni.switchTab({
        url: '/pages/task/task-list'
      })
    },
    
    // 跳转到任务详情
    goToTaskDetail(id) {
      uni.navigateTo({
        url: `/pages/task/task-detail?id=${id}`
      })
    },
    
    // 跳转到车辆列表
    goToVehicleList() {
      uni.navigateTo({
        url: '/pages/vehicle/vehicle-list'
      })
    },
    
    // 跳转到车辆地图
    goToVehicleMap() {
      uni.switchTab({
        url: '/pages/map/vehicle-map'
      })
    }
  }
}
</script>

<style scoped>
.index-container {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 40rpx;
}

.status-bar-placeholder {
  height: var(--status-bar-height);
  background: #409EFF;
}

/* 欢迎栏 */
.welcome-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 40rpx;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  border-radius: 0 0 32rpx 32rpx;
}

.welcome-info {
  display: flex;
  flex-direction: column;
}

.welcome-text {
  font-size: 36rpx;
  font-weight: bold;
  color: #FFFFFF;
  margin-bottom: 8rpx;
}

.welcome-role {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.welcome-avatar {
  width: 96rpx;
  height: 96rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-text {
  font-size: 40rpx;
  font-weight: bold;
  color: #FFFFFF;
}

/* 统计卡片 */
.stats-section {
  display: flex;
  flex-wrap: wrap;
  padding: 30rpx 20rpx;
  gap: 20rpx;
  margin-top: -40rpx;
}

.stats-card {
  flex: 1;
  min-width: 320rpx;
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 30rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 88rpx;
  height: 88rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.stat-icon text {
  font-size: 44rpx;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 48rpx;
  font-weight: bold;
  color: #303133;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 26rpx;
  color: #909399;
}

/* 通用标题 */
.section-title {
  padding: 30rpx 40rpx 20rpx;
}

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-text {
  font-size: 32rpx;
  font-weight: bold;
  color: #303133;
}

.title-more {
  font-size: 26rpx;
  color: #909399;
}

/* 快捷功能 */
.quick-section {
  margin-bottom: 20rpx;
}

.quick-grid {
  display: flex;
  flex-wrap: wrap;
  padding: 0 20rpx;
  gap: 20rpx;
}

.quick-item {
  width: calc(50% - 30rpx);
  background: #FFFFFF;
  border-radius: 16rpx;
  padding: 30rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.quick-icon {
  width: 96rpx;
  height: 96rpx;
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20rpx;
}

.quick-icon text {
  font-size: 48rpx;
}

.quick-label {
  font-size: 28rpx;
  color: #303133;
  font-weight: 500;
}

/* 待办任务 */
.todo-section {
  padding: 0 20rpx;
}

.todo-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.todo-item {
  margin-bottom: 0;
}

.todo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.todo-no {
  font-size: 28rpx;
  font-weight: bold;
  color: #303133;
}

.todo-content {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.todo-row {
  display: flex;
  align-items: flex-start;
}

.todo-label {
  font-size: 26rpx;
  color: #909399;
  width: 100rpx;
  flex-shrink: 0;
}

.todo-value {
  font-size: 26rpx;
  color: #606266;
  flex: 1;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60rpx 0;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
}

/* 车辆状态 */
.vehicle-section {
  padding: 0 20rpx;
  margin-top: 20rpx;
}

.vehicle-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.vehicle-item {
  display: flex;
  align-items: center;
  margin-bottom: 0;
}

.vehicle-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.vehicle-icon.status-pending {
  background: #FEF0F0;
}

.vehicle-icon.status-departed {
  background: #F0F9EB;
}

.vehicle-icon.status-assigned {
  background: #FDF6EC;
}

.vehicle-icon.status-cancelled {
  background: #F4F4F5;
}

.vehicle-icon text {
  font-size: 40rpx;
}

.vehicle-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.vehicle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.vehicle-plate {
  font-size: 30rpx;
  font-weight: bold;
  color: #303133;
}

.vehicle-location {
  font-size: 24rpx;
  color: #909399;
}
</style>
