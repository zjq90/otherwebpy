<template>
  <div class="cost-module">
    <el-card>
      <template #header>
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <el-tab-pane label="原材料管理" name="materials" />
          <el-tab-pane label="原材料成本" name="material-costs" />
          <el-tab-pane label="员工管理" name="employees" />
          <el-tab-pane label="人工成本" name="labor-costs" />
          <el-tab-pane label="销售记录" name="sales" />
          <el-tab-pane label="利润分析" name="profit" />
        </el-tabs>
      </template>
      
      <router-view />
    </el-card>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

const activeTab = ref('materials')

const tabRouteMap = {
  'materials': '/cost/materials',
  'material-costs': '/cost/material-costs',
  'employees': '/cost/employees',
  'labor-costs': '/cost/labor-costs',
  'sales': '/cost/sales',
  'profit': '/cost/profit'
}

const handleTabClick = (tab) => {
  const targetPath = tabRouteMap[tab.paneName]
  if (targetPath && route.path !== targetPath) {
    router.push(targetPath)
  }
}

watch(
  () => route.path,
  (path) => {
    for (const [tabName, tabPath] of Object.entries(tabRouteMap)) {
      if (path.startsWith(tabPath)) {
        activeTab.value = tabName
        break
      }
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.cost-module {
  padding: 10px;
}
</style>
