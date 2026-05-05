<template>
  <view class="profile-container">
    <!-- 用户信息卡片 -->
    <view class="user-card">
      <view class="user-avatar">
        <text class="avatar-text">{{ userInfo.username ? userInfo.username.charAt(0).toUpperCase() : 'U' }}</text>
      </view>
      <view class="user-info">
        <text class="user-name">{{ userInfo.username || '用户' }}</text>
        <view class="user-role-row">
          <view class="role-tag" :class="userInfo.role">
            <text class="role-text">{{ roleText(userInfo.role) }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 功能列表 -->
    <view class="menu-section">
      <view class="section-title">
        <text class="title-text">数据管理</text>
      </view>
      
      <view class="menu-list">
        <view class="menu-item" @click="goToDataStatistics">
          <view class="menu-icon blue">
            <text class="icon-text">📊</text>
          </view>
          <view class="menu-content">
            <text class="menu-title">数据统计</text>
            <text class="menu-desc">查看质量数据统计报表</text>
          </view>
          <view class="menu-arrow">
            <text class="arrow-text">›</text>
          </view>
        </view>
        
        <view class="menu-item" @click="goToMaterials">
          <view class="menu-icon green">
            <text class="icon-text">📦</text>
          </view>
          <view class="menu-content">
            <text class="menu-title">原材料管理</text>
            <text class="menu-desc">管理原材料基础数据</text>
          </view>
          <view class="menu-arrow">
            <text class="arrow-text">›</text>
          </view>
        </view>
        
        <view class="menu-item" @click="goToProductions">
          <view class="menu-icon orange">
            <text class="icon-text">🏭</text>
          </view>
          <view class="menu-content">
            <text class="menu-title">生产记录</text>
            <text class="menu-desc">查看所有生产批次记录</text>
          </view>
          <view class="menu-arrow">
            <text class="arrow-text">›</text>
          </view>
        </view>
      </view>
    </view>
    
    <view class="menu-section">
      <view class="section-title">
        <text class="title-text">系统设置</text>
      </view>
      
      <view class="menu-list">
        <view class="menu-item" @click="goToTestData">
          <view class="menu-icon purple">
            <text class="icon-text">🧪</text>
          </view>
          <view class="menu-content">
            <text class="menu-title">测试数据</text>
            <text class="menu-desc">生成和管理测试数据</text>
          </view>
          <view class="menu-arrow">
            <text class="arrow-text">›</text>
          </view>
        </view>
        
        <view class="menu-item" @click="goToSetting">
          <view class="menu-icon gray">
            <text class="icon-text">⚙️</text>
          </view>
          <view class="menu-content">
            <text class="menu-title">设置</text>
            <text class="menu-desc">系统和个人设置</text>
          </view>
          <view class="menu-arrow">
            <text class="arrow-text">›</text>
          </view>
        </view>
        
        <view class="menu-item" @click="showAbout">
          <view class="menu-icon blue">
            <text class="icon-text">ℹ️</text>
          </view>
          <view class="menu-content">
            <text class="menu-title">关于</text>
            <text class="menu-desc">版本信息 v1.0.0</text>
          </view>
          <view class="menu-arrow">
            <text class="arrow-text">›</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 退出登录 -->
    <view class="logout-section">
      <view class="logout-btn" @click="logout">
        <text class="logout-text">退出登录</text>
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      userInfo: {
        username: '',
        role: ''
      }
    }
  },
  onShow() {
    this.loadUserInfo()
  },
  methods: {
    async loadUserInfo() {
      try {
        const res = await request.get('/api/auth/me')
        
        if (res.code === 200) {
          this.userInfo = res.data
        }
      } catch (err) {
        console.error('获取用户信息失败:', err)
        // 使用本地存储的用户信息
        const token = uni.getStorageSync('token')
        if (token) {
          this.userInfo = {
            username: '测试用户',
            role: '管理员'
          }
        }
      }
    },
    
    roleText(role) {
      const roleMap = {
        'admin': '管理员',
        'inspector': '质量检测员',
        'manager': '生产经理'
      }
      return roleMap[role] || role
    },
    
    goToDataStatistics() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },
    
    goToMaterials() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },
    
    goToProductions() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },
    
    goToTestData() {
      uni.showModal({
        title: '生成测试数据',
        content: '确定要生成测试数据吗？这将在后端创建测试用户、原材料、检验记录等数据。',
        success: (res) => {
          if (res.confirm) {
            this.generateTestData()
          }
        }
      })
    },
    
    async generateTestData() {
      uni.showLoading({
        title: '生成中...'
      })
      
      try {
        // 调用后端生成测试数据的接口
        // 注意：这里需要后端提供对应的API
        // 目前后端的test_data.py是一个独立脚本，需要运行它来生成数据
        
        uni.hideLoading()
        uni.showModal({
          title: '提示',
          content: '请在后端运行 python test_data.py 来生成测试数据。\n\n操作步骤：\n1. 打开终端，进入 backend 目录\n2. 运行命令: python test_data.py\n3. 等待执行完成后刷新数据',
          showCancel: false
        })
      } catch (err) {
        uni.hideLoading()
        console.error('生成测试数据失败:', err)
        uni.showToast({
          title: '生成失败',
          icon: 'none'
        })
      }
    },
    
    goToSetting() {
      uni.showToast({
        title: '功能开发中',
        icon: 'none'
      })
    },
    
    showAbout() {
      uni.showModal({
        title: '关于',
        content: '混凝土质量追溯系统 v1.0.0\n\n技术栈：\n- 后端: Python + FastAPI + SQLite\n- 前端: uni-app + Vue.js\n\n功能模块：\n- 原材料检验录入\n- 生产质量追溯\n- 质量异常预警',
        showCancel: false
      })
    },
    
    logout() {
      uni.showModal({
        title: '确认退出',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            // 清除本地存储
            uni.removeStorageSync('token')
            uni.removeStorageSync('userInfo')
            uni.removeStorageSync('traceHistory')
            
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
.profile-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

/* 用户卡片 */
.user-card {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  padding: 40rpx 32rpx;
  display: flex;
  align-items: center;
}

.user-avatar {
  width: 120rpx;
  height: 120rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.avatar-text {
  font-size: 48rpx;
  font-weight: 600;
  color: #fff;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-size: 36rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 12rpx;
}

.user-role-row {
  display: flex;
}

.role-tag {
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
  background: rgba(255, 255, 255, 0.2);
}

.role-text {
  font-size: 24rpx;
  color: #fff;
}

/* 菜单区域 */
.menu-section {
  margin-top: 20rpx;
  background: #fff;
}

.section-title {
  padding: 24rpx 24rpx 12rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.title-text {
  font-size: 26rpx;
  color: #999;
}

.menu-list {
  padding: 0 24rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-icon {
  width: 72rpx;
  height: 72rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.menu-icon.blue {
  background: #e3f2fd;
}

.menu-icon.green {
  background: #e8f5e9;
}

.menu-icon.orange {
  background: #fff3e0;
}

.menu-icon.purple {
  background: #f3e5f5;
}

.menu-icon.gray {
  background: #f5f5f5;
}

.icon-text {
  font-size: 36rpx;
}

.menu-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.menu-title {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 6rpx;
}

.menu-desc {
  font-size: 24rpx;
  color: #999;
}

.menu-arrow {
  padding: 0 8rpx;
}

.arrow-text {
  font-size: 40rpx;
  color: #ccc;
}

/* 退出登录 */
.logout-section {
  padding: 40rpx 24rpx;
}

.logout-btn {
  width: 100%;
  height: 88rpx;
  background: #fff;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2rpx solid #e0e0e0;
}

.logout-text {
  font-size: 30rpx;
  color: #e53935;
}
</style>
