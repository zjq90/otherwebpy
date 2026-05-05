<template>
  <div class="dashboard-container">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon size="28"><List /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ dashboardData.summary?.in_progress_orders || 0 }}</div>
              <div class="stats-label">进行中任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon size="28"><Clock /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ dashboardData.summary?.pending_orders || 0 }}</div>
              <div class="stats-label">待处理任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon size="28"><Warning /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value" :class="{ critical: dashboardData.summary?.critical_alerts > 0 }">
                {{ dashboardData.summary?.open_alerts || 0 }}
              </div>
              <div class="stats-label">未处理预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" shadow="hover">
          <div class="stats-content">
            <div class="stats-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
              <el-icon size="28"><Truck /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value">{{ dashboardData.summary?.available_resources || 0 }}</div>
              <div class="stats-label">可用资源</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>进行中的生产任务</span>
              <el-button type="primary" text @click="goToOrders">查看全部</el-button>
            </div>
          </template>
          <el-table :data="dashboardData.in_progress_orders || []" v-loading="loading" stripe>
            <el-table-column prop="order_code" label="任务单号" min-width="120" />
            <el-table-column prop="current_stage" label="当前阶段" min-width="100">
              <template #default="scope">
                <el-tag :type="getStageType(scope.row.current_stage)" effect="dark">
                  {{ getStageLabel(scope.row.current_stage) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" label="进度" min-width="150">
              <template #default="scope">
                <el-progress :percentage="scope.row.progress || 0" :color="getProgressColor(scope.row.progress)" />
              </template>
            </el-table-column>
            <el-table-column prop="volume" label="方量(m³)" width="100" />
            <el-table-column prop="updated_at" label="更新时间" min-width="160">
              <template #default="scope">
                {{ formatTime(scope.row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="scope">
                <el-button type="primary" text @click="viewOrder(scope.row.id)">详情</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && (!dashboardData.in_progress_orders || dashboardData.in_progress_orders.length === 0)" description="暂无进行中的任务" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="section-card">
          <template #header>
            <div class="card-header">
              <span>最新预警</span>
              <el-button type="primary" text @click="goToAlerts">查看全部</el-button>
            </div>
          </template>
          <div class="alert-list">
            <div v-for="alert in dashboardData.recent_alerts || []" :key="alert.id" class="alert-item" @click="viewAlert(alert.id)">
              <div class="alert-icon" :class="alert.alert_level">
                <el-icon><Bell /></el-icon>
              </div>
              <div class="alert-content">
                <div class="alert-title">{{ alert.alert_title }}</div>
                <div class="alert-time">{{ formatTime(alert.created_at) }}</div>
              </div>
              <el-tag :type="getAlertType(alert.alert_level)" size="small">
                {{ getAlertLabel(alert.alert_level) }}
              </el-tag>
            </div>
            <el-empty v-if="!loading && (!dashboardData.recent_alerts || dashboardData.recent_alerts.length === 0)" description="暂无预警" />
          </div>
        </el-card>

        <el-card class="section-card" style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>资源状态</span>
            </div>
          </template>
          <div class="resource-status">
            <div class="status-item">
              <span class="status-label">可用资源</span>
              <span class="status-value available">{{ dashboardData.summary?.available_resources || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">使用中</span>
              <span class="status-value in-use">{{ dashboardData.summary?.in_use_resources || 0 }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">今日完成</span>
              <span class="status-value completed">{{ dashboardData.summary?.completed_today || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { monitoringApi } from '../api'

const router = useRouter()
const loading = ref(false)
const dashboardData = ref({})
let refreshInterval = null

const fetchDashboardData = async () => {
  loading.value = true
  try {
    const res = await monitoringApi.getDashboard()
    dashboardData.value = res
  } catch (error) {
    console.error('获取面板数据失败:', error)
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getStageType = (stage) => {
  const types = {
    'batching': 'info',
    'mixing': 'warning',
    'discharging': 'primary',
    'completed': 'success'
  }
  return types[stage] || 'info'
}

const getStageLabel = (stage) => {
  const labels = {
    'batching': '配料中',
    'mixing': '搅拌中',
    'discharging': '出料中',
    'completed': '已完成'
  }
  return labels[stage] || stage
}

const getProgressColor = (progress) => {
  if (progress >= 80) return '#67c23a'
  if (progress >= 50) return '#409eff'
  return '#e6a23c'
}

const getAlertType = (level) => {
  const types = {
    'info': 'info',
    'warning': 'warning',
    'error': 'danger',
    'critical': 'danger'
  }
  return types[level] || 'warning'
}

const getAlertLabel = (level) => {
  const labels = {
    'info': '信息',
    'warning': '警告',
    'error': '错误',
    'critical': '严重'
  }
  return labels[level] || level
}

const viewOrder = (id) => {
  router.push(`/orders/${id}`)
}

const viewAlert = (id) => {
  router.push('/alerts')
}

const goToOrders = () => {
  router.push('/orders')
}

const goToAlerts = () => {
  router.push('/alerts')
}

onMounted(() => {
  fetchDashboardData()
  refreshInterval = setInterval(fetchDashboardData, 30000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  border-radius: 8px;
}

.stats-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stats-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stats-info {
  flex: 1;
}

.stats-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stats-value.critical {
  color: #f56c6c;
}

.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.section-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-list {
  max-height: 300px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.alert-item:hover {
  background-color: #f5f7fa;
}

.alert-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.alert-icon.info {
  background-color: #409eff;
}

.alert-icon.warning {
  background-color: #e6a23c;
}

.alert-icon.error {
  background-color: #f56c6c;
}

.alert-icon.critical {
  background-color: #c0392b;
}

.alert-content {
  flex: 1;
  min-width: 0;
}

.alert-title {
  font-size: 14px;
  color: #303133;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.alert-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.resource-status {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  font-size: 14px;
  color: #606266;
}

.status-value {
  font-size: 20px;
  font-weight: bold;
}

.status-value.available {
  color: #67c23a;
}

.status-value.in-use {
  color: #409eff;
}

.status-value.completed {
  color: #909399;
}
</style>
