<template>
  <el-config-provider :locale="zhCn">
    <div class="app-container">
      <el-container>
        <el-aside width="220px" class="app-aside">
          <div class="logo">
            <el-icon :size="32" color="#409EFF"><Dumbbell /></el-icon>
            <span class="logo-text">健身房管理系统</span>
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
              <span>工作台</span>
            </el-menu-item>
            
            <el-sub-menu index="members">
              <template #title>
                <el-icon><User /></el-icon>
                <span>会员管理</span>
              </template>
              <el-menu-item index="/members/list">会员列表</el-menu-item>
              <el-menu-item index="/members/add">新增会员</el-menu-item>
            </el-sub-menu>
            
            <el-sub-menu index="archive">
              <template #title>
                <el-icon><Document /></el-icon>
                <span>档案管理</span>
              </template>
              <el-menu-item index="/archive/physical-tests">体测数据</el-menu-item>
              <el-menu-item index="/archive/fitness-goals">运动目标</el-menu-item>
              <el-menu-item index="/archive/consumptions">消费记录</el-menu-item>
              <el-menu-item index="/archive/courses">课程参与</el-menu-item>
            </el-sub-menu>
            
            <el-menu-item index="/levels">
              <el-icon><Medal /></el-icon>
              <span>等级权益</span>
            </el-menu-item>
            
            <el-menu-item index="/status-logs">
              <el-icon><List /></el-icon>
              <span>状态日志</span>
            </el-menu-item>
            
            <el-sub-menu index="test">
              <template #title>
                <el-icon><Tools /></el-icon>
                <span>测试功能</span>
              </template>
              <el-menu-item index="/test/generate">生成测试数据</el-menu-item>
              <el-menu-item index="/test/helper">测试助手</el-menu-item>
            </el-sub-menu>
          </el-menu>
        </el-aside>
        
        <el-container>
          <el-header class="app-header">
            <div class="header-left">
              <el-breadcrumb separator="/">
                <el-breadcrumb-item
                  v-for="item in breadcrumbs"
                  :key="item.path"
                  :to="item.path"
                >
                  {{ item.name }}
                </el-breadcrumb-item>
              </el-breadcrumb>
            </div>
            <div class="header-right">
              <el-dropdown>
                <span class="user-info">
                  <el-icon><UserFilled /></el-icon>
                  <span>管理员</span>
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
          
          <el-main class="app-main">
            <router-view />
          </el-main>
        </el-container>
      </el-container>
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import {
  HomeFilled, User, Document, Medal, List, Tools,
  Dumbbell, UserFilled
} from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => route.path)

const breadcrumbs = computed(() => {
  const matched = route.matched.filter(item => item.meta && item.meta.title)
  return matched.map(item => ({
    path: item.path,
    name: item.meta.title
  }))
})
</script>

<style lang="scss">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.app-container {
  height: 100%;
}

.el-container {
  height: 100%;
}

.app-aside {
  background-color: #304156;
  transition: width 0.3s;

  .logo {
    display: flex;
    align-items: center;
    padding: 20px;
    background-color: #263445;

    .logo-text {
      margin-left: 12px;
      font-size: 18px;
      font-weight: bold;
      color: #fff;
      white-space: nowrap;
    }
  }

  .el-menu {
    border-right: none;
  }
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);

  .header-left {
    .el-breadcrumb {
      font-size: 14px;
    }
  }

  .header-right {
    .user-info {
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #606266;
    }
  }
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.page-container {
  background-color: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.page-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .page-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }
}

.table-actions {
  display: flex;
  gap: 8px;
}

.status-tag {
  &.active {
    background-color: #f0f9eb;
    color: #67c23a;
  }
  
  &.frozen {
    background-color: #fdf6ec;
    color: #e6a23c;
  }
  
  &.cancelled {
    background-color: #fef0f0;
    color: #f56c6c;
  }
}

.level-tag {
  &.bronze {
    background-color: #f5f0eb;
    color: #cd7f32;
  }
  
  &.silver {
    background-color: #f0f0f0;
    color: #c0c0c0;
  }
  
  &.gold {
    background-color: #fffbf0;
    color: #ffd700;
  }
}
</style>
