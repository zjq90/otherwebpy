<template>
  <div class="environment-module">
    <el-card>
      <template #header>
        <el-tabs v-model="activeTab" @tab-click="handleTabClick">
          <el-tab-pane label="监测点位" name="points" />
          <el-tab-pane label="粉尘监测" name="dust" />
          <el-tab-pane label="噪音监测" name="noise" />
          <el-tab-pane label="废水监测" name="wastewater" />
          <el-tab-pane label="报警记录" name="alarms" />
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

const activeTab = ref('points')

const tabRouteMap = {
  'points': '/environment/points',
  'dust': '/environment/dust',
  'noise': '/environment/noise',
  'wastewater': '/environment/wastewater',
  'alarms': '/environment/alarms'
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
.environment-module {
  padding: 10px;
}
</style>
