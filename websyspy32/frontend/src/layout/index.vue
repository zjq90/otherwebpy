<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="sidebar">
      <div class="logo-container">
        <h2 v-show="!isCollapse" class="logo-title">库存管理系统</h2>
        <el-icon v-show="isCollapse" class="logo-icon"><Box /></el-icon>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/inventory">
          <el-icon><Box /></el-icon>
          <template #title>动态库存</template>
        </el-menu-item>
        <el-menu-item index="/production">
          <el-icon><TrendCharts /></el-icon>
          <template #title>物料需求预测</template>
        </el-menu-item>
        <el-menu-item index="/suppliers">
          <el-icon><User /></el-icon>
          <template #title>供应商管理</template>
        </el-menu-item>
        <el-menu-item index="/settlements">
          <el-icon><Money /></el-icon>
          <template #title>结算管理</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-icon" @click="toggleCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tag type="warning" v-if="lowInventoryCount > 0" effect="dark" class="alert-tag">
            <el-icon><Warning /></el-icon>
            {{ lowInventoryCount }} 个低库存预警
          </el-tag>
          <el-dropdown>
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
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
      
      <el-main class="main">
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
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { siloApi } from '@/api'

const route = useRoute()
const isCollapse = ref(false)
const lowInventoryCount = ref(0)

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
  const titles = {
    '/dashboard': '仪表盘',
    '/inventory': '动态库存',
    '/production': '物料需求预测',
    '/suppliers': '供应商管理',
    '/settlements': '结算管理'
  }
  return titles[route.path] || '首页'
})

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const fetchLowInventory = async () => {
  try {
    const res = await siloApi.getLowInventory()
    lowInventoryCount.value = res.data.length
  } catch (error) {
    console.error('获取低库存预警失败:', error)
  }
}

onMounted(() => {
  fetchLowInventory()
})
</script>

<style scoped>
.layout-container {
  height: 100%;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}

.logo-container {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 16px;
  background-color: #2b3a4a;
}

.logo-title {
  color: #fff;
  font-size: 18px;
  font-weight: 600;
  white-space: nowrap;
}

.logo-icon {
  font-size: 32px;
  color: #409EFF;
}

.el-menu {
  border-right: none;
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-icon {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.collapse-icon:hover {
  color: #409EFF;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.alert-tag {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  color: #606266;
}

.main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
