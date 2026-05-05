<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="layout-aside">
      <div class="logo">
        <el-icon size="28"><Truck /></el-icon>
        <span>混凝土生产管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="layout-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><Monitor /></el-icon>
          <span>监控面板</span>
        </el-menu-item>
        <el-sub-menu index="formula">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>配方管理</span>
          </template>
          <el-menu-item index="/formulas">配方列表</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="production">
          <template #title>
            <el-icon><Calendar /></el-icon>
            <span>生产管理</span>
          </template>
          <el-menu-item index="/plans">生产计划</el-menu-item>
          <el-menu-item index="/orders">生产任务</el-menu-item>
          <el-menu-item index="/resources">资源管理</el-menu-item>
        </el-sub-menu>
        <el-sub-menu index="monitoring">
          <template #title>
            <el-icon><View /></el-icon>
            <span>实时监控</span>
          </template>
          <el-menu-item index="/monitoring">生产监控</el-menu-item>
          <el-menu-item index="/logs">生产日志</el-menu-item>
          <el-menu-item index="/alerts">预警管理</el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/test">
          <el-icon><Tools /></el-icon>
          <span>测试功能</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.meta?.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tooltip content="刷新数据" placement="bottom">
            <el-button type="text" @click="handleRefresh">
              <el-icon size="20"><Refresh /></el-icon>
            </el-button>
          </el-tooltip>
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">管理员</span>
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
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)

const handleRefresh = () => {
  router.go(0)
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.layout-aside {
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
  font-size: 16px;
  font-weight: bold;
  border-bottom: 1px solid #3a4a5f;
}

.layout-menu {
  border-right: none;
}

.layout-header {
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

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  color: #606266;
  font-size: 14px;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
