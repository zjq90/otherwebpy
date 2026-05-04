<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon security">
              <el-icon :size="30"><PoliceCar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.personnelCount }}</div>
              <div class="stat-label">安保人员</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon monitor">
              <el-icon :size="30"><VideoCamera /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.monitorCount }}</div>
              <div class="stat-label">监控设备</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon vehicle">
              <el-icon :size="30"><Van /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.vehiclePresent }}</div>
              <div class="stat-label">在场车辆</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon emergency">
              <el-icon :size="30"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.emergencyPending }}</div>
              <div class="stat-label">待处理事件</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-cards">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">
              <el-icon><Bell /></el-icon> 突发事件列表
            </span>
          </template>
          <el-table :data="emergencyList" style="width: 100%" size="small">
            <el-table-column prop="report_title" label="事件标题" width="200" />
            <el-table-column prop="event_type" label="事件类型" width="100" />
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">{{ row.priority }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">
              <el-icon><User /></el-icon> 今日排班
            </span>
          </template>
          <el-table :data="todaySchedules" style="width: 100%" size="small">
            <el-table-column prop="personnel_name" label="人员" width="100" />
            <el-table-column prop="shift_type" label="班次" width="80" />
            <el-table-column prop="post" label="岗位" width="150" />
            <el-table-column prop="start_time" label="时间" width="150">
              <template #default="{ row }">
                {{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getScheduleStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-cards">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">
              <el-icon><Camera /></el-icon> 监控设备状态
            </span>
          </template>
          <el-table :data="monitorList" style="width: 100%" size="small">
            <el-table-column prop="device_name" label="设备名称" width="150" />
            <el-table-column prop="device_type" label="设备类型" width="100" />
            <el-table-column prop="location" label="位置" width="200" />
            <el-table-column prop="status" label="状态">
              <template #default="{ row }">
                <el-tag :type="getDeviceStatusType(row.status)" size="small">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">
              <el-icon><Sunny /></el-icon> 绿化植物统计
            </span>
          </template>
          <el-table :data="plantList" style="width: 100%" size="small">
            <el-table-column prop="plant_name" label="植物名称" width="120" />
            <el-table-column prop="plant_type" label="类型" width="80" />
            <el-table-column prop="quantity" label="数量" width="80" />
            <el-table-column prop="location" label="位置" width="200" />
            <el-table-column prop="growth_status" label="生长状态">
              <template #default="{ row }">
                <el-tag :type="getGrowthStatusType(row.growth_status)" size="small">{{ row.growth_status }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { security, environment } from '@/api'

const stats = ref({
  personnelCount: 0,
  monitorCount: 0,
  vehiclePresent: 0,
  emergencyPending: 0
})

const emergencyList = ref([])
const todaySchedules = ref([])
const monitorList = ref([])
const plantList = ref([])

const getPriorityType = (priority) => {
  const types = { '紧急': 'danger', '重要': 'warning', '一般': 'info' }
  return types[priority] || 'info'
}

const getStatusType = (status) => {
  const types = { '待处理': 'warning', '处理中': 'primary', '已处理': 'success' }
  return types[status] || 'info'
}

const getScheduleStatusType = (status) => {
  const types = { '待执行': 'info', '执行中': 'primary', '已完成': 'success', '取消': 'danger' }
  return types[status] || 'info'
}

const getDeviceStatusType = (status) => {
  const types = { '正常': 'success', '离线': 'warning', '故障': 'danger' }
  return types[status] || 'info'
}

const getGrowthStatusType = (status) => {
  const types = { '良好': 'success', '一般': 'warning', '较差': 'danger', '死亡': 'info' }
  return types[status] || 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.substring(0, 5)
}

const loadStats = async () => {
  try {
    const personnelRes = await security.getPersonnelList({ page: 1, page_size: 1 })
    const monitorRes = await security.getMonitorList({ page: 1, page_size: 1 })
    
    stats.value.personnelCount = personnelRes.total || 0
    stats.value.monitorCount = monitorRes.total || 0
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const loadEmergencyList = async () => {
  try {
    const res = await security.getEmergencyList({ page: 1, page_size: 5 })
    emergencyList.value = res.data?.items || []
    stats.value.emergencyPending = emergencyList.value.filter(e => e.status === '待处理' || e.status === '处理中').length
  } catch (error) {
    console.error('加载突发事件列表失败:', error)
  }
}

const loadSchedules = async () => {
  try {
    const res = await security.getScheduleList({ page: 1, page_size: 5 })
    todaySchedules.value = (res.data?.items || []).map(item => ({
      ...item,
      personnel_name: item.personnel?.name || '未知'
    }))
  } catch (error) {
    console.error('加载排班列表失败:', error)
  }
}

const loadMonitors = async () => {
  try {
    const res = await security.getMonitorList({ page: 1, page_size: 5 })
    monitorList.value = res.data?.items || []
  } catch (error) {
    console.error('加载监控设备列表失败:', error)
  }
}

const loadPlants = async () => {
  try {
    const res = await environment.getGreenPlantList({ page: 1, page_size: 5 })
    plantList.value = res.data?.items || []
  } catch (error) {
    console.error('加载绿化植物列表失败:', error)
  }
}

onMounted(() => {
  loadStats()
  loadEmergencyList()
  loadSchedules()
  loadMonitors()
  loadPlants()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-cards {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.security {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.monitor {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.vehicle {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.emergency {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.content-cards {
  margin-bottom: 20px;
}

.card-title {
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
