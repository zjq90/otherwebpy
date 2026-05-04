<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <el-aside width="220px" class="app-aside">
        <div class="logo">
          <el-icon :size="32" color="#409EFF"><OfficeBuilding /></el-icon>
          <span class="logo-text">物业管理系统</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="app-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <el-sub-menu index="security">
            <template #title>
              <el-icon><PoliceCar /></el-icon>
              <span>秩序维护管理</span>
            </template>
            <el-menu-item index="/security/personnel">安保人员管理</el-menu-item>
            <el-menu-item index="/security/schedule">安保排班管理</el-menu-item>
            <el-menu-item index="/security/patrol-route">巡逻路线管理</el-menu-item>
            <el-menu-item index="/security/patrol-record">巡逻记录管理</el-menu-item>
            <el-menu-item index="/security/monitor">监控设备管理</el-menu-item>
            <el-menu-item index="/security/vehicle">车辆出入登记</el-menu-item>
            <el-menu-item index="/security/visitor">外来人员管理</el-menu-item>
            <el-menu-item index="/security/emergency">突发事件上报</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="environment">
            <template #title>
              <el-icon><Sunny /></el-icon>
              <span>环境保洁与绿化养护</span>
            </template>
            <el-menu-item index="/environment/cleaning-area">保洁区域管理</el-menu-item>
            <el-menu-item index="/environment/cleaning-record">清洁记录管理</el-menu-item>
            <el-menu-item index="/environment/green-plant">绿化植物管理</el-menu-item>
            <el-menu-item index="/environment/maintenance-plan">养护计划管理</el-menu-item>
            <el-menu-item index="/environment/maintenance-record">养护记录管理</el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="app-header">
          <div class="header-title">
            {{ currentRouteTitle }}
          </div>
          <div class="header-user">
            <el-dropdown>
              <span class="user-info">
                <el-icon><UserFilled /></el-icon>
                <span>管理员</span>
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
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()

const activeMenu = computed(() => route.path)

const routeTitles = {
  '/dashboard': '系统首页',
  '/security/personnel': '安保人员管理',
  '/security/schedule': '安保排班管理',
  '/security/patrol-route': '巡逻路线管理',
  '/security/patrol-record': '巡逻记录管理',
  '/security/monitor': '监控设备管理',
  '/security/vehicle': '车辆出入登记',
  '/security/visitor': '外来人员管理',
  '/security/emergency': '突发事件上报',
  '/environment/cleaning-area': '保洁区域管理',
  '/environment/cleaning-record': '清洁记录管理',
  '/environment/green-plant': '绿化植物管理',
  '/environment/maintenance-plan': '养护计划管理',
  '/environment/maintenance-record': '养护记录管理'
}

const currentRouteTitle = computed(() => {
  return routeTitles[route.path] || '物业管理系统'
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
  width: 100%;
}

.app-container {
  height: 100%;
}

.app-aside {
  background-color: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 0 20px;
  border-bottom: 1px solid #3a4a5c;
}

.logo-text {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.app-menu {
  border-right: none;
}

.app-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.header-user {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
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
