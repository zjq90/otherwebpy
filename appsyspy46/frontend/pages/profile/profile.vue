<template>
  <view class="profile-container">
    <scroll-view class="profile-scroll" scroll-y>
      <view class="profile-header">
        <view class="avatar-section">
          <view class="avatar">
            <text class="avatar-text">{{ userInitial }}</text>
          </view>
          <view class="user-info">
            <text class="user-name">{{ userInfo?.real_name || userInfo?.username || '未登录' }}</text>
            <text class="user-phone">{{ userInfo?.phone || '未绑定手机号' }}</text>
          </view>
        </view>
      </view>

      <view class="stats-section">
        <view class="stats-card">
          <text class="stats-value">{{ stats?.total_orders || 0 }}</text>
          <text class="stats-label">完成订单</text>
        </view>
        <view class="stats-card">
          <text class="stats-value">{{ stats?.total_weight?.toFixed(1) || '0.0' }}</text>
          <text class="stats-label">回收重量(kg)</text>
        </view>
        <view class="stats-card">
          <text class="stats-value">¥{{ stats?.total_income?.toFixed(2) || '0.00' }}</text>
          <text class="stats-label">累计收益</text>
        </view>
      </view>

      <view class="today-stats" v-if="stats">
        <view class="today-header">
          <text class="today-title">今日业绩</text>
        </view>
        <view class="today-body">
          <view class="today-item">
            <text class="today-label">今日订单</text>
            <text class="today-value">{{ stats.today_orders || 0 }} 单</text>
          </view>
          <view class="today-item">
            <text class="today-label">今日重量</text>
            <text class="today-value">{{ stats.today_weight?.toFixed(1) || '0.0' }} kg</text>
          </view>
          <view class="today-item">
            <text class="today-label">今日收益</text>
            <text class="today-value">¥{{ stats.today_income?.toFixed(2) || '0.00' }}</text>
          </view>
        </view>
      </view>

      <view class="menu-section">
        <view class="menu-header">
          <text class="menu-title">常用功能</text>
        </view>
        
        <view class="menu-list">
          <view class="menu-item" @click="goToWithdrawal">
            <view class="menu-icon withdraw">
              <text class="icon-text">💰</text>
            </view>
            <view class="menu-content">
              <text class="menu-name">申请提现</text>
              <text class="menu-desc">将收益提现到银行卡</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-text">›</text>
            </view>
          </view>

          <view class="menu-item" @click="goToWithdrawalHistory">
            <view class="menu-icon history">
              <text class="icon-text">📋</text>
            </view>
            <view class="menu-content">
              <text class="menu-name">提现记录</text>
              <text class="menu-desc">查看历史提现记录</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-text">›</text>
            </view>
          </view>
        </view>
      </view>

      <view class="menu-section">
        <view class="menu-header">
          <text class="menu-title">账户设置</text>
        </view>
        
        <view class="menu-list">
          <view class="menu-item" @click="goToEditProfile">
            <view class="menu-icon profile">
              <text class="icon-text">👤</text>
            </view>
            <view class="menu-content">
              <text class="menu-name">个人信息</text>
              <text class="menu-desc">修改个人资料</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-text">›</text>
            </view>
          </view>

          <view class="menu-item" @click="showAbout">
            <view class="menu-icon about">
              <text class="icon-text">ℹ️</text>
            </view>
            <view class="menu-content">
              <text class="menu-name">关于我们</text>
              <text class="menu-desc">版本 v1.0.0</text>
            </view>
            <view class="menu-arrow">
              <text class="arrow-text">›</text>
            </view>
          </view>

          <view class="menu-item logout" @click="handleLogout">
            <view class="menu-icon logout">
              <text class="icon-text">🚪</text>
            </view>
            <view class="menu-content">
              <text class="menu-name">退出登录</text>
              <text class="menu-desc">安全退出当前账户</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue'
import { getProfile, getStats, UserStats } from '@/api/user'
import { getUserInfo, clearLoginInfo, isLoggedIn } from '@/api/auth'

interface UserInfo {
  id: number
  username: string
  real_name?: string
  phone?: string
  avatar?: string
  total_orders: number
  total_weight: number
  total_income: number
}

export default defineComponent({
  setup() {
    const userInfo = ref<UserInfo | null>(null)
    const stats = ref<UserStats | null>(null)
    const loading = ref(false)

    const userInitial = computed(() => {
      if (userInfo.value?.real_name) {
        return userInfo.value.real_name.charAt(0)
      }
      if (userInfo.value?.username) {
        return userInfo.value.username.charAt(0)
      }
      return '?'
    })

    const fetchProfile = async () => {
      if (!isLoggedIn()) {
        uni.navigateTo({ url: '/pages/login/login' })
        return
      }

      loading.value = true
      try {
        const [profileData, statsData] = await Promise.all([
          getProfile(),
          getStats()
        ])
        userInfo.value = profileData as UserInfo
        stats.value = statsData
      } catch (error) {
        console.error('获取个人信息失败:', error)
        const localUserInfo = getUserInfo()
        if (localUserInfo) {
          userInfo.value = {
            id: localUserInfo.id,
            username: localUserInfo.username,
            real_name: localUserInfo.real_name,
            phone: localUserInfo.phone,
            total_orders: localUserInfo.total_orders || 0,
            total_weight: localUserInfo.total_weight || 0,
            total_income: localUserInfo.total_income || 0
          }
        }
      } finally {
        loading.value = false
      }
    }

    const goToWithdrawal = () => {
      uni.navigateTo({ url: '/pages/withdrawal/withdrawal' })
    }

    const goToWithdrawalHistory = () => {
      uni.showToast({ title: '功能开发中', icon: 'none' })
    }

    const goToEditProfile = () => {
      uni.showToast({ title: '功能开发中', icon: 'none' })
    }

    const showAbout = () => {
      uni.showModal({
        title: '关于衣回收',
        content: '旧衣物回收系统 - 回收人员端\n版本: v1.0.0\n\n环保回收，共建美好家园。',
        showCancel: false
      })
    }

    const handleLogout = () => {
      uni.showModal({
        title: '提示',
        content: '确定要退出登录吗？',
        success: (res) => {
          if (res.confirm) {
            clearLoginInfo()
            uni.reLaunch({ url: '/pages/login/login' })
          }
        }
      })
    }

    onMounted(() => {
      fetchProfile()
    })

    return {
      userInfo,
      stats,
      loading,
      userInitial,
      goToWithdrawal,
      goToWithdrawalHistory,
      goToEditProfile,
      showAbout,
      handleLogout
    }
  }
})
</script>

<style lang="scss" scoped>
.profile-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.profile-scroll {
  flex: 1;
}

.profile-header {
  background: linear-gradient(135deg, #2979ff 0%, #1976d2 100%);
  padding: 40rpx 30rpx;
  padding-bottom: 60rpx;
}

.avatar-section {
  display: flex;
  align-items: center;
}

.avatar {
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #ffffff 0%, #e3f2fd 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.15);
}

.avatar-text {
  font-size: 48rpx;
  font-weight: bold;
  color: #2979ff;
}

.user-info {
  margin-left: 24rpx;
}

.user-name {
  display: block;
  font-size: 36rpx;
  font-weight: bold;
  color: #ffffff;
}

.user-phone {
  display: block;
  font-size: 26rpx;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 8rpx;
}

.stats-section {
  background-color: #ffffff;
  margin: -40rpx 20rpx 20rpx;
  border-radius: 16rpx;
  padding: 30rpx;
  display: flex;
  justify-content: space-around;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.05);
}

.stats-card {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stats-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #2979ff;
}

.stats-label {
  font-size: 24rpx;
  color: #909399;
  margin-top: 8rpx;
}

.today-stats {
  background-color: #ffffff;
  margin: 0 20rpx 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.today-header {
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.today-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #303133;
}

.today-body {
  padding: 20rpx 30rpx;
}

.today-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16rpx 0;
}

.today-label {
  font-size: 26rpx;
  color: #606266;
}

.today-value {
  font-size: 26rpx;
  color: #2979ff;
  font-weight: 500;
}

.menu-section {
  background-color: #ffffff;
  margin: 0 20rpx 20rpx;
  border-radius: 16rpx;
  overflow: hidden;
}

.menu-header {
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-title {
  font-size: 28rpx;
  font-weight: 500;
  color: #303133;
}

.menu-list {
  padding: 0 10rpx;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 24rpx 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.menu-item:last-child {
  border-bottom: none;
}

.menu-item.logout {
  opacity: 0.8;
}

.menu-icon {
  width: 80rpx;
  height: 80rpx;
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.menu-icon.withdraw {
  background-color: rgba(7, 193, 96, 0.1);
}

.menu-icon.history {
  background-color: rgba(41, 121, 255, 0.1);
}

.menu-icon.profile {
  background-color: rgba(255, 151, 106, 0.1);
}

.menu-icon.about {
  background-color: rgba(144, 147, 153, 0.1);
}

.menu-icon.logout {
  background-color: rgba(245, 108, 108, 0.1);
}

.icon-text {
  font-size: 36rpx;
}

.menu-content {
  flex: 1;
}

.menu-name {
  display: block;
  font-size: 28rpx;
  color: #303133;
  font-weight: 500;
}

.menu-desc {
  display: block;
  font-size: 24rpx;
  color: #909399;
  margin-top: 4rpx;
}

.menu-arrow {
  margin-left: 20rpx;
}

.arrow-text {
  font-size: 40rpx;
  color: #c0c4cc;
}
</style>
