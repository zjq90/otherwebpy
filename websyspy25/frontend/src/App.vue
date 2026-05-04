<template>
  <el-config-provider :locale="zhCn">
    <el-container class="app-container">
      <!-- 侧边栏 -->
      <el-aside width="220px" class="sidebar">
        <div class="logo">
          <el-icon :size="30" color="#409EFF"><Dumbbell /></el-icon>
          <span class="logo-text">私教管理系统</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
          router
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <span>首页概览</span>
          </el-menu-item>
          
          <el-sub-menu index="coach">
            <template #title>
              <el-icon><UserFilled /></el-icon>
              <span>教练档案</span>
            </template>
            <el-menu-item index="/coach/list">教练列表</el-menu-item>
            <el-menu-item index="/coach/schedule">排班管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="member">
            <template #title>
              <el-icon><Team /></el-icon>
              <span>会员管理</span>
            </template>
            <el-menu-item index="/member/list">会员列表</el-menu-item>
            <el-menu-item index="/member/packages">课程包管理</el-menu-item>
          </el-sub-menu>
          
          <el-sub-menu index="lesson">
            <template #title>
              <el-icon><Calendar /></el-icon>
              <span>私教课管理</span>
            </template>
            <el-menu-item index="/lesson/records">课时记录</el-menu-item>
            <el-menu-item index="/lesson/makeup">补课管理</el-menu-item>
            <el-menu-item index="/lesson/freeze">冻结管理</el-menu-item>
          </el-sub-menu>
          
          <el-menu-item index="/performance">
            <el-icon><TrendCharts /></el-icon>
            <span>业绩追踪</span>
          </el-menu-item>
          
          <el-menu-item index="/test">
            <el-icon><Tools /></el-icon>
            <span>测试工具</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      
      <!-- 主内容区 -->
      <el-container>
        <el-header class="header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item v-if="breadcrumbName">{{ breadcrumbName }}</el-breadcrumb-item>
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
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const route = useRoute()

// 当前激活的菜单项
const activeMenu = computed(() => route.path)

// 面包屑名称
const breadcrumbName = computed(() => {
  const nameMap = {
    '/coach/list': '教练列表',
    '/coach/schedule': '排班管理',
    '/member/list': '会员列表',
    '/member/packages': '课程包管理',
    '/lesson/records': '课时记录',
    '/lesson/makeup': '补课管理',
    '/lesson/freeze': '冻结管理',
    '/performance': '业绩追踪',
    '/test': '测试工具'
  }
  return nameMap[route.path] || ''
})
</script>

<style lang="scss">
.app-container {
  height: 100vh;
  width: 100%;
}

.sidebar {
  background-color: #304156;
  transition: width 0.3s;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 15px;
    background-color: #2b3a4a;
    
    .logo-text {
      color: #fff;
      font-size: 18px;
      font-weight: bold;
      margin-left: 10px;
      white-space: nowrap;
    }
  }
  
  .sidebar-menu {
    border-right: none;
    height: calc(100vh - 60px);
    overflow-y: auto;
  }
}

.header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  
  .header-left {
    display: flex;
    align-items: center;
  }
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      
      .username {
        margin-left: 10px;
        color: #606266;
      }
    }
  }
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

// 页面过渡动画
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
