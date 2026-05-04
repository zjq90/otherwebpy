<template>
  <el-container class="main-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="32" color="#409EFF">
          <OfficeBuilding />
        </el-icon>
        <span>社区管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-sub-menu index="services-menu">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>客户服务</span>
          </template>
          <el-menu-item index="/services">服务请求列表</el-menu-item>
          <el-menu-item index="/services/create">提交服务请求</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="activities-menu">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>社区活动</span>
          </template>
          <el-menu-item index="/activities">活动列表</el-menu-item>
          <el-menu-item index="/my-activities">我的活动</el-menu-item>
          <el-menu-item v-if="userStore.isAdmin" index="/activities/create">创建活动</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.name !== 'Dashboard'">
              {{ currentRoute.meta?.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon :size="20"><User /></el-icon>
              <span>{{ userStore.user?.real_name || userStore.user?.username }}</span>
              <el-tag :type="roleTagType" size="small" class="role-tag">
                {{ roleText }}
              </el-tag>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)

const roleText = computed(() => {
  const role = userStore.user?.role
  const roleMap = {
    admin: '管理员',
    property: '物业人员',
    resident: '业主'
  }
  return roleMap[role] || role
})

const roleTagType = computed(() => {
  const role = userStore.user?.role
  const typeMap = {
    admin: 'danger',
    property: 'warning',
    resident: 'success'
  }
  return typeMap[role] || 'info'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    }).catch(() => {})
  }
}
</script>

<style scoped>
.main-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow-y: auto;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid #3a4a5b;
}

.sidebar-menu {
  border-right: none;
}

.header {
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.role-tag {
  margin-left: 8px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
