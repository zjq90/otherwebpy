<template>
  <div class="production-container">
    <el-card class="menu-card" shadow="never">
      <el-menu
        :default-active="activeMenu"
        router
        mode="horizontal"
        background-color="#fff"
        text-color="#606266"
        active-text-color="#409EFF"
        class="top-menu"
      >
        <el-menu-item index="/production/records">
          <el-icon><Document /></el-icon>
          生产记录
        </el-menu-item>
        <el-menu-item index="/production/equipment">
          <el-icon><Tools /></el-icon>
          设备管理
        </el-menu-item>
        <el-menu-item index="/production/utilization">
          <el-icon><PieChart /></el-icon>
          设备利用率
        </el-menu-item>
        <el-menu-item index="/production/energy">
          <el-icon><Lightning /></el-icon>
          能耗指标
        </el-menu-item>
        <el-menu-item index="/production/stats">
          <el-icon><TrendCharts /></el-icon>
          统计分析
        </el-menu-item>
      </el-menu>
    </el-card>
    
    <router-view style="margin-top: 20px;" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Document, Tools, PieChart, Lightning, TrendCharts } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => {
  return route.path
})
</script>

<style scoped>
.production-container {
  padding: 0;
}

.menu-card {
  border-radius: 8px;
}

.top-menu {
  border-bottom: none;
}

.top-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
  margin: 0 5px;
  border-radius: 4px;
}
</style>
