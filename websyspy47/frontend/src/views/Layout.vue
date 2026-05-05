<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <el-icon size="32"><Recycling /></el-icon>
        <span class="logo-text">旧衣物回收系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataLine /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        
        <el-sub-menu index="user">
          <template #title>
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </template>
          <el-menu-item index="/users">
            <el-icon><UserFilled /></el-icon>
            <span>用户列表</span>
          </el-menu-item>
          <el-menu-item index="/feedbacks">
            <el-icon><ChatDotRound /></el-icon>
            <span>投诉反馈</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="order">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>订单管理</span>
          </template>
          <el-menu-item index="/orders">
            <el-icon><List /></el-icon>
            <span>订单列表</span>
          </el-menu-item>
          <el-menu-item index="/order-stats">
            <el-icon><TrendCharts /></el-icon>
            <span>订单统计</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="recycler">
          <template #title>
            <el-icon><Avatar /></el-icon>
            <span>回收人员</span>
          </template>
          <el-menu-item index="/recyclers">
            <el-icon><User /></el-icon>
            <span>人员管理</span>
          </el-menu-item>
          <el-menu-item index="/performance">
            <el-icon><Trophy /></el-icon>
            <span>绩效考核</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="category">
          <template #title>
            <el-icon><Collection /></el-icon>
            <span>价格分类</span>
          </template>
          <el-menu-item index="/categories">
            <el-icon><Folder /></el-icon>
            <span>分类管理</span>
          </el-menu-item>
          <el-menu-item index="/pricing-rules">
            <el-icon><Wallet /></el-icon>
            <span>价格规则</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="product">
          <template #title>
            <el-icon><Goods /></el-icon>
            <span>商品积分</span>
          </template>
          <el-menu-item index="/products">
            <el-icon><ShoppingBag /></el-icon>
            <span>商品管理</span>
          </el-menu-item>
          <el-menu-item index="/points-rules">
            <el-icon><Coin /></el-icon>
            <span>积分规则</span>
          </el-menu-item>
          <el-menu-item index="/points-exchanges">
            <el-icon><Promotion /></el-icon>
            <span>积分兑换</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/announcements">
          <el-icon><Bell /></el-icon>
          <span>公告管理</span>
        </el-menu-item>
        
        <el-sub-menu index="cs">
          <template #title>
            <el-icon><Service /></el-icon>
            <span>客服管理</span>
          </template>
          <el-menu-item index="/cs-staffs">
            <el-icon><UserFilled /></el-icon>
            <span>客服人员</span>
          </el-menu-item>
          <el-menu-item index="/consultations">
            <el-icon><ChatLineSquare /></el-icon>
            <span>咨询记录</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="current-page">{{ currentPageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              <span>管理员</span>
              <el-icon class="icon-arrow"><ArrowDown /></el-icon>
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

const activeMenu = computed(() => route.path)

const currentPageTitle = computed(() => {
  const matched = route.matched
  if (matched.length > 1) {
    return matched[matched.length - 1].meta?.title || ''
  }
  return ''
})
</script>

<style lang="scss" scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  
  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    border-bottom: 1px solid #3a4a5b;
    
    .logo-text {
      margin-left: 10px;
    }
  }
  
  .sidebar-menu {
    border-right: none;
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
    .current-page {
      font-size: 16px;
      font-weight: 500;
      color: #303133;
    }
  }
  
  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      cursor: pointer;
      color: #606266;
      
      span {
        margin: 0 5px;
      }
      
      .icon-arrow {
        font-size: 12px;
      }
    }
  }
}

.main-content {
  background-color: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}
</style>
