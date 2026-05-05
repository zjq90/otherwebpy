<template>
  <el-container class="app-container">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <el-icon :size="32" color="#409EFF"><DataAnalysis /></el-icon>
        <span class="logo-text">混凝土生产管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据概览</span>
        </el-menu-item>
        
        <el-sub-menu index="/production">
          <template #title>
            <el-icon><Grid /></el-icon>
            <span>生产数据分析</span>
          </template>
          <el-menu-item index="/production/records">生产记录</el-menu-item>
          <el-menu-item index="/production/equipment">设备管理</el-menu-item>
          <el-menu-item index="/production/utilization">设备利用率</el-menu-item>
          <el-menu-item index="/production/energy">能耗指标</el-menu-item>
          <el-menu-item index="/production/stats">统计分析</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="/cost">
          <template #title>
            <el-icon><Money /></el-icon>
            <span>成本核算与利润分析</span>
          </template>
          <el-menu-item index="/cost/materials">原材料管理</el-menu-item>
          <el-menu-item index="/cost/material-costs">原材料成本</el-menu-item>
          <el-menu-item index="/cost/employees">员工管理</el-menu-item>
          <el-menu-item index="/cost/labor-costs">人工成本</el-menu-item>
          <el-menu-item index="/cost/sales">销售记录</el-menu-item>
          <el-menu-item index="/cost/profit">利润分析</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="/environment">
          <template #title>
            <el-icon><Warning /></el-icon>
            <span>环保合规监管</span>
          </template>
          <el-menu-item index="/environment/points">监测点位</el-menu-item>
          <el-menu-item index="/environment/dust">粉尘监测</el-menu-item>
          <el-menu-item index="/environment/noise">噪音监测</el-menu-item>
          <el-menu-item index="/environment/wastewater">废水监测</el-menu-item>
          <el-menu-item index="/environment/alarms">报警记录</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header class="header">
        <div class="header-title">{{ currentRouteTitle }}</div>
        <div class="header-right">
          <el-badge :value="pendingAlarmCount" :hidden="pendingAlarmCount === 0" class="item">
            <el-button type="primary" text @click="goToAlarms">
              <el-icon><Bell /></el-icon>
              <span style="margin-left: 4px;">报警</span>
            </el-button>
          </el-badge>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  DataAnalysis, Grid, Money, Warning, Bell
} from '@element-plus/icons-vue'
import { environmentApi } from './api'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const currentRouteTitle = computed(() => route.meta.title || '数据概览')

const pendingAlarmCount = ref(0)

const loadPendingAlarms = async () => {
  try {
    const res = await environmentApi.getAlarms({ is_handled: false, limit: 1 })
    pendingAlarmCount.value = res.headers['x-total-count'] ? parseInt(res.headers['x-total-count']) : 0
  } catch (e) {
    console.error('加载待处理报警数失败:', e)
  }
}

const goToAlarms = () => {
  router.push('/environment/alarms')
}

onMounted(() => {
  loadPendingAlarms()
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
  overflow-x: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  border-bottom: 1px solid #1f2d3d;
}

.logo-text {
  margin-left: 10px;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
}

.el-menu {
  border-right: none;
}

.header {
  background: linear-gradient(90deg, #409EFF 0%, #66b1ff 100%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  color: #fff;
}

.header-title {
  font-size: 18px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 24px;
}

.card-container {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
}

.stat-card.blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card.green {
  background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.stat-card.orange {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-card.purple {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-card .value {
  font-size: 32px;
  font-weight: bold;
  color: #fff;
}

.stat-card .label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
  margin-top: 8px;
}

.search-form {
  margin-bottom: 20px;
}

.el-table {
  border-radius: 8px;
  overflow: hidden;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  text-align: right;
}

.over-limit {
  color: #f56c6c;
  font-weight: bold;
}

.normal-status {
  color: #67c23a;
}
</style>
