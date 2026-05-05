<template>
  <view class="user-center-container">
    <!-- 顶部用户信息卡片 -->
    <view class="user-header">
      <view class="bg-decoration">
        <view class="bg-circle circle-1"></view>
        <view class="bg-circle circle-2"></view>
      </view>
      
      <view class="user-info">
        <view class="user-avatar">
          <text class="avatar-text">{{ avatarText }}</text>
        </view>
        <view class="user-detail">
          <text class="user-name">{{ userInfo.real_name || '用户' }}</text>
          <view class="user-meta">
            <text class="user-role status-tag" :class="roleClass">{{ roleName }}</text>
            <text class="user-phone">{{ userInfo.phone || '未绑定手机号' }}</text>
          </view>
        </view>
        <view class="edit-btn" @click="goToEdit">
          <text>⚙️</text>
        </view>
      </view>
      
      <!-- 统计数据 -->
      <view class="user-stats">
        <view class="stat-item" @click="goToMyTasks">
          <text class="stat-value">{{ statsData.totalTasks }}</text>
          <text class="stat-label">总任务</text>
        </view>
        <view class="stat-item" @click="goToMyTasks('in_progress')">
          <text class="stat-value">{{ statsData.inProgress }}</text>
          <text class="stat-label">进行中</text>
        </view>
        <view class="stat-item" @click="goToMyTasks('completed')">
          <text class="stat-value">{{ statsData.completed }}</text>
          <text class="stat-label">已完成</text>
        </view>
      </view>
    </view>
    
    <!-- 功能菜单列表 -->
    <view class="menu-section">
      <!-- 任务相关 -->
      <view class="menu-group">
        <view class="menu-item" @click="goToMyTasks">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #ECF5FF;">
              <text class="menu-icon">📋</text>
            </view>
            <text class="menu-label">我的任务</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
        
        <view class="menu-item" v-if="isDriver" @click="goToReportLocation">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #F0F9EB;">
              <text class="menu-icon">📍</text>
            </view>
            <text class="menu-label">上报位置</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
        
        <view class="menu-item" v-if="isDriver" @click="goToTrajectory">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #FDF6EC;">
              <text class="menu-icon">🗺️</text>
            </view>
            <text class="menu-label">行驶轨迹</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
      </view>
      
      <!-- 管理功能 -->
      <view class="menu-group" v-if="canManage">
        <view class="menu-item" @click="goToTaskList">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #E6F7FF;">
              <text class="menu-icon">📦</text>
            </view>
            <text class="menu-label">任务管理</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
        
        <view class="menu-item" @click="goToVehicleList">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #FFF7E6;">
              <text class="menu-icon">🚛</text>
            </view>
            <text class="menu-label">车辆管理</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
        
        <view class="menu-item" v-if="isAdmin" @click="goToUserList">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #F6FFED;">
              <text class="menu-icon">👥</text>
            </view>
            <text class="menu-label">用户管理</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
        
        <view class="menu-item" @click="goToVehicleMap">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #FFF1F0;">
              <text class="menu-icon">🗺️</text>
            </view>
            <text class="menu-label">车辆监控</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
      </view>
      
      <!-- 设置相关 -->
      <view class="menu-group">
        <view class="menu-item" @click="goToSettings">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #FFF0F6;">
              <text class="menu-icon">⚙️</text>
            </view>
            <text class="menu-label">设置</text>
          </view>
          <view class="menu-right">
            <text class="menu-arrow">›</text>
          </view>
        </view>
        
        <view class="menu-item" @click="showAbout">
          <view class="menu-left">
            <view class="menu-icon-box" style="background: #F9F0FF;">
              <text class="menu-icon">ℹ️</text>
            </view>
            <text class="menu-label">关于我们</text>
          </view>
          <view class="menu-right">
            <text class="menu-value">v1.0.0</text>
            <text class="menu-arrow">›</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 底部退出按钮 -->
    <view class="logout-section">
      <button class="logout-btn" @click="handleLogout">
        <text>退出登录</text>
      </button>
    </view>
  </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
  data() {
    return {
      userInfo: {},
      statsData: {
        totalTasks: 0,
        inProgress: 0,
        completed: 0
      }
    }
  },
  
  computed: {
    // 头像文本
    avatarText() {
      if (this.userInfo.real_name) {
        return this.userInfo.real_name.charAt(0)
      }
      return '用'
    },
    
    // 角色名称
    roleName() {
      const roleNames = {
        [config.roles.ADMIN]: '管理员',
        [config.roles.DISPATCHER]: '调度员',
        [config.roles.DRIVER]: '司机'
      }
      return roleNames[this.userInfo.role] || '未知角色'
    },
    
    // 角色样式类
    roleClass() {
      const classMap = {
        [config.roles.ADMIN]: 'status-assigned',
        [config.roles.DISPATCHER]: 'status-departed',
        [config.roles.DRIVER]: 'status-pending'
      }
      return classMap[this.userInfo.role] || 'status-cancelled'
    },
    
    // 是否是司机
    isDriver() {
      return this.userInfo.role === config.roles.DRIVER
    },
    
    // 是否是管理员
    isAdmin() {
      return this.userInfo.role === config.roles.ADMIN
    },
    
    // 是否可以管理（管理员或调度员）
    canManage() {
      return this.userInfo.role === config.roles.ADMIN || 
             this.userInfo.role === config.roles.DISPATCHER
    }
  },
  
  onLoad() {
    this.loadUserInfo()
  },
  
  onShow() {
    this.loadUserInfo()
    this.loadStats()
  },
  
  methods: {
    // 加载用户信息
    loadUserInfo() {
      this.userInfo = uni.getStorageSync(config.userInfoKey) || {}
    },
    
    // 加载统计数据
    async loadStats() {
      try {
        const token = uni.getStorageSync(config.tokenKey)
        const res = await uni.request({
          url: `${config.baseUrl}/api/test/system-status`,
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          const data = res[1].data.data
          this.statsData = {
            totalTasks: data.total_tasks || 0,
            inProgress: data.tasks_in_progress || 0,
            completed: data.tasks_completed_today || 0
          }
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
      }
    },
    
    // 跳转到编辑个人信息
    goToEdit() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },
    
    // 跳转到我的任务
    goToMyTasks(filter = 'all') {
      if (this.isDriver) {
        uni.navigateTo({
          url: '/pages/driver/my-tasks'
        })
      } else {
        uni.switchTab({
          url: '/pages/task/task-list'
        })
      }
    },
    
    // 上报位置
    async goToReportLocation() {
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
            url: `${config.baseUrl}/api/locations`,
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
    
    // 跳转到行驶轨迹
    goToTrajectory() {
      uni.navigateTo({
        url: '/pages/map/trajectory'
      })
    },
    
    // 跳转到任务管理
    goToTaskList() {
      uni.switchTab({
        url: '/pages/task/task-list'
      })
    },
    
    // 跳转到车辆管理
    goToVehicleList() {
      uni.navigateTo({
        url: '/pages/vehicle/vehicle-list'
      })
    },
    
    // 跳转到用户管理
    goToUserList() {
      uni.navigateTo({
        url: '/pages/user/user-list'
      })
    },
    
    // 跳转到车辆监控
    goToVehicleMap() {
      uni.switchTab({
        url: '/pages/map/vehicle-map'
      })
    },
    
    // 跳转到设置
    goToSettings() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },
    
    // 显示关于我们
    showAbout() {
      uni.showModal({
        title: '关于运输管理系统',
        content: '版本：1.0.0\n\n运输管理系统（Transport Management System）\n是一款用于车辆调度、任务分配、\n位置监控的综合管理应用。\n\n技术栈：\n后端: Python + FastAPI + SQLite\n前端: uni-app + Vue3',
        showCancel: false,
        confirmText: '知道了'
      })
    },
    
    // 处理退出登录
    handleLogout() {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        confirmText: '退出',
        confirmColor: '#F56C6C',
        success: (res) => {
          if (res.confirm) {
            // 清除本地存储
            uni.removeStorageSync(config.tokenKey)
            uni.removeStorageSync(config.userInfoKey)
            
            // 跳转到登录页
            uni.redirectTo({
              url: '/pages/login/login'
            })
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.user-center-container {
  min-height: 100vh;
  background: #F5F5F5;
  padding-bottom: 40rpx;
}

/* 顶部用户信息区 */
.user-header {
  position: relative;
  padding: 40rpx;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.circle-1 {
  width: 400rpx;
  height: 400rpx;
  top: -100rpx;
  right: -50rpx;
}

.circle-2 {
  width: 300rpx;
  height: 300rpx;
  bottom: -50rpx;
  left: -100rpx;
}

/* 用户信息 */
.user-info {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 40rpx;
}

.user-avatar {
  width: 140rpx;
  height: 140rpx;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 30rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
}

.avatar-text {
  font-size: 56rpx;
  font-weight: bold;
  color: #409EFF;
}

.user-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 40rpx;
  font-weight: bold;
  color: #FFFFFF;
  margin-bottom: 16rpx;
}

.user-meta {
  display: flex;
  flex-direction: column;
  gap: 10rpx;
}

.user-role {
  align-self: flex-start;
}

.user-phone {
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.8);
}

.edit-btn {
  padding: 16rpx;
}

.edit-btn text {
  font-size: 40rpx;
}

/* 统计数据 */
.user-stats {
  position: relative;
  display: flex;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16rpx;
  padding: 30rpx 0;
  backdrop-filter: blur(10rpx);
}

.stat-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1rpx solid rgba(255, 255, 255, 0.2);
}

.stat-item:last-child {
  border-right: none;
}

.stat-value {
  font-size: 48rpx;
  font-weight: bold;
  color: #FFFFFF;
  margin-bottom: 8rpx;
}

.stat-label {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

/* 菜单区域 */
.menu-section {
  padding: 30rpx 20rpx;
}

.menu-group {
  background: #FFFFFF;
  border-radius: 16rpx;
  margin-bottom: 30rpx;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx;
  border-bottom: 1rpx solid #EBEEF5;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-left {
  display: flex;
  align-items: center;
}

.menu-icon-box {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.menu-icon {
  font-size: 40rpx;
}

.menu-label {
  font-size: 30rpx;
  color: #303133;
}

.menu-right {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.menu-value {
  font-size: 26rpx;
  color: #909399;
}

.menu-arrow {
  font-size: 36rpx;
  color: #C0C4CC;
}

/* 退出登录按钮 */
.logout-section {
  padding: 0 40rpx;
  margin-top: 40rpx;
}

.logout-btn {
  width: 100%;
  height: 96rpx;
  background: #FFFFFF;
  border: none;
  border-radius: 12rpx;
}

.logout-btn::after {
  border: none;
}

.logout-btn text {
  font-size: 32rpx;
  color: #F56C6C;
  font-weight: 500;
}
</style>
