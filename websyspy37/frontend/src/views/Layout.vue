<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <el-header style="background-color: #409eff; color: #fff; display: flex; align-items: center; justify-content: space-between; padding: 0 20px;">
      <div style="display: flex; align-items: center;">
        <el-icon :size="28" style="margin-right: 10px;">
          <OfficeBuilding />
        </el-icon>
        <span style="font-size: 20px; font-weight: bold;">ERP企业资源管理系统</span>
      </div>
      <div>
        <el-button type="primary" text @click="goTestData" style="color: #fff;">
          <el-icon style="margin-right: 5px;"><DataAnalysis /></el-icon>
          测试数据
        </el-button>
      </div>
    </el-header>

    <div class="main-content">
      <!-- 侧边栏菜单 -->
      <el-aside class="sidebar">
        <el-menu
          :default-active="activeMenu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409eff"
          router
          style="border-right: none; height: 100%;"
        >
          <el-menu-item index="/dashboard">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </el-menu-item>

          <el-sub-menu index="sales">
            <template #title>
              <el-icon><ShoppingCart /></el-icon>
              <span>销售模块</span>
            </template>
            <el-menu-item index="/sales/customer">
              <el-icon><User /></el-icon>
              <span>客户管理</span>
            </el-menu-item>
            <el-menu-item index="/sales/order">
              <el-icon><Document /></el-icon>
              <span>订单管理</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="production">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>生产模块</span>
            </template>
            <el-menu-item index="/production/product">
              <el-icon><Goods /></el-icon>
              <span>产品管理</span>
            </el-menu-item>
            <el-menu-item index="/production/plan">
              <el-icon><Calendar /></el-icon>
              <span>生产计划</span>
            </el-menu-item>
            <el-menu-item index="/production/task">
              <el-icon><List /></el-icon>
              <span>生产任务</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="inventory">
            <template #title>
              <el-icon><Box /></el-icon>
              <span>库存模块</span>
            </template>
            <el-menu-item index="/inventory/warehouse">
              <el-icon><OfficeBuilding /></el-icon>
              <span>仓库管理</span>
            </el-menu-item>
            <el-menu-item index="/inventory/inventory">
              <el-icon><Box /></el-icon>
              <span>库存管理</span>
            </el-menu-item>
            <el-menu-item index="/inventory/stock-in">
              <el-icon><Download /></el-icon>
              <span>入库管理</span>
            </el-menu-item>
            <el-menu-item index="/inventory/stock-out">
              <el-icon><Upload /></el-icon>
              <span>出库管理</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="finance">
            <template #title>
              <el-icon><Wallet /></el-icon>
              <span>财务模块</span>
            </template>
            <el-menu-item index="/finance/account">
              <el-icon><Wallet /></el-icon>
              <span>账户管理</span>
            </el-menu-item>
            <el-menu-item index="/finance/income">
              <el-icon><Plus /></el-icon>
              <span>收入管理</span>
            </el-menu-item>
            <el-menu-item index="/finance/expense">
              <el-icon><Minus /></el-icon>
              <span>支出管理</span>
            </el-menu-item>
            <el-menu-item index="/finance/invoice">
              <el-icon><Ticket /></el-icon>
              <span>发票管理</span>
            </el-menu-item>
          </el-sub-menu>

          <el-sub-menu index="hr">
            <template #title>
              <el-icon><UserFilled /></el-icon>
              <span>人事模块</span>
            </template>
            <el-menu-item index="/hr/department">
              <el-icon><OfficeBuilding /></el-icon>
              <span>部门管理</span>
            </el-menu-item>
            <el-menu-item index="/hr/position">
              <el-icon><Medal /></el-icon>
              <span>职位管理</span>
            </el-menu-item>
            <el-menu-item index="/hr/employee">
              <el-icon><User /></el-icon>
              <span>员工管理</span>
            </el-menu-item>
            <el-menu-item index="/hr/attendance">
              <el-icon><Clock /></el-icon>
              <span>考勤管理</span>
            </el-menu-item>
            <el-menu-item index="/hr/salary">
              <el-icon><Money /></el-icon>
              <span>薪资管理</span>
            </el-menu-item>
          </el-sub-menu>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-main class="content-area">
        <router-view />
      </el-main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { 
  HomeFilled, OfficeBuilding, DataAnalysis, ShoppingCart, 
  User, Document, Tools, Goods, Calendar, List, 
  Box, Download, Upload, Wallet, Plus, Minus, 
  Ticket, UserFilled, Medal, Clock, Money 
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)

const goTestData = () => {
  router.push('/test-data')
}
</script>
