<template>
  <el-container class="app-container">
    <!-- 侧边栏 -->
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon :size="28" color="#409EFF"><OfficeBuilding /></el-icon>
        <span>物业信息管理</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/property-projects">
          <el-icon><OfficeBuilding /></el-icon>
          <span>物业项目管理</span>
        </el-menu-item>
        <el-menu-item index="/properties">
          <el-icon><House /></el-icon>
          <span>房产信息管理</span>
        </el-menu-item>
        <el-menu-item index="/owners">
          <el-icon><User /></el-icon>
          <span>业主/住户管理</span>
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
            <el-breadcrumb-item v-if="currentRoute.meta.title">
              {{ currentRoute.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-button type="primary" :icon="Plus" @click="handleGenerateTestData">
            生成测试数据
          </el-button>
        </div>
      </el-header>

      <!-- 内容区 -->
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { testDataApi } from '@/api'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const currentRoute = computed(() => route)

// 生成测试数据
const handleGenerateTestData = async () => {
  try {
    await ElMessageBox.confirm(
      '此操作将清除现有数据并生成新的测试数据，是否继续？',
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const res = await testDataApi.generate(true)
    if (res.success) {
      ElMessage.success(res.message)
      // 刷新页面以更新数据
      router.go(0)
    } else {
      ElMessage.error(res.message)
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成测试数据失败:', error)
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.app-container {
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
  gap: 10px;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 1px solid #3a4a5c;
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
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

/* 卡片样式 */
.card {
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

/* 表格操作按钮样式 */
.table-actions {
  display: flex;
  gap: 8px;
}

/* 状态标签样式 */
.status-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.status-vacant {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.status-rented {
  background-color: #ecf5ff;
  color: #409eff;
}

.status-occupied {
  background-color: #f0f9eb;
  color: #67c23a;
}
</style>
