<template>
  <!-- 主应用组件 -->
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="32"><Gym /></el-icon>
        <span>健身房管理系统</span>
      </div>
      
      <!-- 导航菜单 -->
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <!-- 工作台 -->
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>工作台</span>
        </el-menu-item>
        
        <!-- 会员管理 -->
        <el-sub-menu index="members-group">
          <template #title>
            <el-icon><User /></el-icon>
            <span>会员管理</span>
          </template>
          <el-menu-item index="/members">会员列表</el-menu-item>
        </el-sub-menu>
        
        <!-- 签到管理 -->
        <el-sub-menu index="checkin-group">
          <template #title>
            <el-icon><Timer /></el-icon>
            <span>签到管理</span>
          </template>
          <el-menu-item index="/checkin">签到验证</el-menu-item>
          <el-menu-item index="/checkin/records">签到记录</el-menu-item>
        </el-sub-menu>
        
        <!-- 储物柜管理 -->
        <el-sub-menu index="locker-group">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>储物柜管理</span>
          </template>
          <el-menu-item index="/lockers">储物柜列表</el-menu-item>
          <el-menu-item index="/lockers/usage">使用记录</el-menu-item>
        </el-sub-menu>
        
        <!-- 收银管理 -->
        <el-sub-menu index="cashier-group">
          <template #title>
            <el-icon><Money /></el-icon>
            <span>收银管理</span>
          </template>
          <el-menu-item index="/cashier">收银台</el-menu-item>
          <el-menu-item index="/cashier/products">商品管理</el-menu-item>
          <el-menu-item index="/cashier/coupons">优惠券管理</el-menu-item>
          <el-menu-item index="/cashier/orders">订单管理</el-menu-item>
          <el-menu-item index="/cashier/reconcile">流水对账</el-menu-item>
        </el-sub-menu>
        
        <!-- 测试中心 -->
        <el-menu-item index="/test">
          <el-icon><Tools /></el-icon>
          <span>测试中心</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <!-- 顶部栏 -->
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute?.meta?.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-text class="system-time">{{ currentTime }}</el-text>
          <el-dropdown>
            <span class="user-info">
              <el-icon :size="20"><UserFilled /></el-icon>
              <span>管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <!-- 内容区域 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import dayjs from 'dayjs'

const route = useRoute()

// 当前激活的菜单项
const activeMenu = computed(() => route.path)

// 当前路由信息
const currentRoute = computed(() => route)

// 当前时间
const currentTime = ref('')
let timeInterval = null

// 更新时间
const updateTime = () => {
  currentTime.value = dayjs().format('YYYY-MM-DD HH:mm:ss')
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.app-container {
  height: 100vh;
  width: 100%;
}

/* 侧边栏样式 */
.sidebar {
  background-color: #304156;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #3a4a5c;
}

.el-menu {
  border-right: none;
}

/* 头部样式 */
.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.system-time {
  color: #909399;
  font-size: 14px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
}

/* 内容区域样式 */
.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 页面卡片样式 */
.page-card {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 20px;
}

/* 表格操作按钮 */
.action-buttons {
  display: flex;
  gap: 10px;
}

/* 状态标签样式 */
.status-tag {
  margin-right: 5px;
}
</style>
