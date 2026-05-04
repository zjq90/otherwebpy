<template>
  <el-container class="app-container">
    <el-aside width="220px" class="app-aside">
      <div class="logo">
        <el-icon size="28"><DishDot /></el-icon>
        <span class="logo-text">会员管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="aside-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-sub-menu index="cards">
          <template #title>
            <el-icon><CreditCard /></el-icon>
            <span>卡项管理</span>
          </template>
          <el-menu-item index="/cards/types">卡类型管理</el-menu-item>
          <el-menu-item index="/cards/list">卡项列表</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="courses">
          <template #title>
            <el-icon><VideoCamera /></el-icon>
            <span>课程管理</span>
          </template>
          <el-menu-item index="/courses/types">课程类型管理</el-menu-item>
          <el-menu-item index="/courses/list">课程列表</el-menu-item>
          <el-menu-item index="/courses/schedules">课程排期</el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/venues">
          <el-icon><OfficeBuilding /></el-icon>
          <span>场地管理</span>
        </el-menu-item>
        
        <el-menu-item index="/members/list">
          <el-icon><User /></el-icon>
          <span>会员管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.name !== 'Home'">
              {{ currentRoute.meta?.title || currentRoute.name }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="username">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeMenu = computed(() => {
  return route.path
})

const currentRoute = computed(() => {
  return route
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  width: 100%;
  height: 100%;
}

.app-container {
  height: 100%;
}

.app-aside {
  background-color: #304156;
  transition: width 0.3s;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background-color: #263445;
  color: #fff;
}

.logo-text {
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap;
}

.aside-menu {
  border-right: none;
  height: calc(100% - 60px);
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  padding: 0 20px;
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

.username {
  color: #606266;
  font-size: 14px;
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.page-header {
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.page-desc {
  font-size: 14px;
  color: #909399;
}

.search-bar {
  margin-bottom: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
}

.table-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
}

.form-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 30px;
}

.status-tag-active {
  background-color: #e1f3d8;
  color: #67c23a;
}

.status-tag-inactive {
  background-color: #f4f4f5;
  color: #909399;
}
</style>
