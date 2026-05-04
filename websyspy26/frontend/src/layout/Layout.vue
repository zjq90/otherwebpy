<template>
  <div class="layout-container">
    <!-- 侧边栏 -->
    <div class="layout-sidebar">
      <div class="sidebar-logo">
        <el-icon size="24"><User /></el-icon>
        <span style="margin-left: 8px">会员管理系统</span>
      </div>
      <div class="sidebar-menu">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="sidebar-menu-item"
          :class="{ active: isActive(item.path) }"
          @click="navigateTo(item.path)"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </div>
      </div>
    </div>

    <!-- 顶部导航 -->
    <div class="layout-header">
      <div style="font-size: 16px; color: #303133">
        {{ currentPageTitle }}
      </div>
      <div style="display: flex; align-items: center; gap: 15px">
        <el-text type="info">管理员</el-text>
        <el-avatar :size="32" style="background-color: #409eff">
          <el-icon><User /></el-icon>
        </el-avatar>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="layout-main">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  HomeFilled, 
  User, 
  Present, 
  Bell, 
  Tools 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 菜单项
const menuItems = [
  { path: '/dashboard', title: '系统首页', icon: 'HomeFilled' },
  { path: '/members', title: '会员管理', icon: 'User' },
  { path: '/promotions', title: '促销活动', icon: 'Present' },
  { path: '/reminders', title: '续费提醒', icon: 'Bell' },
  { path: '/test', title: '测试工具', icon: 'Tools' }
]

// 当前页面标题
const currentPageTitle = computed(() => {
  return route.meta?.title || '系统首页'
})

// 检查是否激活
const isActive = (path) => {
  if (path === '/dashboard') {
    return route.path === '/dashboard'
  }
  return route.path.startsWith(path)
}

// 导航
const navigateTo = (path) => {
  router.push(path)
}
</script>
