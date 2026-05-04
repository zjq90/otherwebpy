/**
 * 根组件
 * 包含应用布局和导航菜单
 */
<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="32"><OfficeBuilding /></el-icon>
        <span class="logo-text">物业综合管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        
        <el-sub-menu index="equipment">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>工程维保管理</span>
          </template>
          <el-menu-item index="/equipment/list">
            <el-icon><Grid /></el-icon>
            <span>设备台账</span>
          </el-menu-item>
          <el-menu-item index="/equipment/inspection">
            <el-icon><Calendar /></el-icon>
            <span>巡检计划</span>
          </el-menu-item>
          <el-menu-item index="/equipment/maintenance">
            <el-icon><Setting /></el-icon>
            <span>保养计划</span>
          </el-menu-item>
          <el-menu-item index="/equipment/fault">
            <el-icon><Warning /></el-icon>
            <span>故障维修</span>
          </el-menu-item>
          <el-menu-item index="/equipment/statistics">
            <el-icon><DataLine /></el-icon>
            <span>费用统计</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="decoration">
          <template #title>
            <el-icon><House /></el-icon>
            <span>装修管理</span>
          </template>
          <el-menu-item index="/decoration/application">
            <el-icon><Document /></el-icon>
            <span>装修申请</span>
          </el-menu-item>
          <el-menu-item index="/decoration/deposit">
            <el-icon><Money /></el-icon>
            <span>押金管理</span>
          </el-menu-item>
          <el-menu-item index="/decoration/inspection">
            <el-icon><View /></el-icon>
            <span>装修巡检</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="contract">
          <template #title>
            <el-icon><Notebook /></el-icon>
            <span>合同与供应商管理</span>
          </template>
          <el-menu-item index="/contract/supplier">
            <el-icon><User /></el-icon>
            <span>供应商管理</span>
          </el-menu-item>
          <el-menu-item index="/contract/list">
            <el-icon><Document /></el-icon>
            <span>合同管理</span>
          </el-menu-item>
          <el-menu-item index="/contract/payment">
            <el-icon><Money /></el-icon>
            <span>付款记录</span>
          </el-menu-item>
          <el-menu-item index="/contract/evaluation">
            <el-icon><Star /></el-icon>
            <span>服务质量评估</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <!-- 主内容区 -->
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentPageTitle">{{ currentPageTitle }}</el-breadcrumb-item>
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
                <el-dropdown-item>个人设置</el-dropdown-item>
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

// 当前激活的菜单
const activeMenu = computed(() => {
  return route.path
})

// 页面标题映射
const pageTitleMap = {
  '/': '首页',
  '/equipment/list': '设备台账',
  '/equipment/inspection': '巡检计划',
  '/equipment/maintenance': '保养计划',
  '/equipment/fault': '故障维修',
  '/equipment/statistics': '费用统计',
  '/decoration/application': '装修申请',
  '/decoration/deposit': '押金管理',
  '/decoration/inspection': '装修巡检',
  '/contract/supplier': '供应商管理',
  '/contract/list': '合同管理',
  '/contract/payment': '付款记录',
  '/contract/evaluation': '服务质量评估'
}

const currentPageTitle = computed(() => {
  return pageTitleMap[route.path] || ''
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-container {
  height: 100%;
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
  background-color: #2b3a4a;
  color: #fff;
  padding: 0 15px;
}

.logo-text {
  margin-left: 10px;
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
}

.el-menu {
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
  flex: 1;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  color: #606266;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}

.page-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  min-height: calc(100vh - 140px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.search-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-label {
  white-space: nowrap;
  color: #606266;
}

.table-container {
  margin-top: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-form {
  width: 500px;
}

.form-item {
  margin-bottom: 18px;
}
</style>
