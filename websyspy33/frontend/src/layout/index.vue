<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h2>混凝土质量管理系统</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-sub-menu index="supplier">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>供应商管理</span>
          </template>
          <el-menu-item index="/suppliers">
            <span>供应商列表</span>
          </el-menu-item>
          <el-menu-item index="/supplier-ratings">
            <span>供应商评级</span>
          </el-menu-item>
          <el-menu-item index="/settlement-orders">
            <span>结算单管理</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="material">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>原材料管理</span>
          </template>
          <el-menu-item index="/raw-materials">
            <span>原材料列表</span>
          </el-menu-item>
          <el-menu-item index="/material-inspections">
            <span>原材料检验</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="production">
          <template #title>
            <el-icon><Timer /></el-icon>
            <span>生产管理</span>
          </template>
          <el-menu-item index="/mix-designs">
            <span>配比设计</span>
          </el-menu-item>
          <el-menu-item index="/production/batches">
            <span>生产批次</span>
          </el-menu-item>
          <el-menu-item index="/production/records">
            <span>生产记录</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="quality">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>质量管理</span>
          </template>
          <el-menu-item index="/test-blocks">
            <span>试块管理</span>
          </el-menu-item>
          <el-menu-item index="/strength-tests">
            <span>强度检测</span>
          </el-menu-item>
          <el-menu-item index="/quality-reports">
            <span>质量报告</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentRoute.meta?.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-icon><User /></el-icon>
              管理员
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
      
      <el-main class="main-content">
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

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #263445;
}

.logo h2 {
  color: #fff;
  font-size: 16px;
  margin: 0;
  font-weight: 500;
}

:deep(.el-menu) {
  border-right: none;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-right .user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
