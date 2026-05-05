<template>
  <div class="alarms-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stats-card" style="background: linear-gradient(135deg, #ff6b6b, #ee5a5a);">
          <div class="stats-content">
            <div class="stats-value">{{ alarmStats.pending }}</div>
            <div class="stats-label">待处理</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" style="background: linear-gradient(135deg, #ffa502, #ff9f43);">
          <div class="stats-content">
            <div class="stats-value">{{ alarmStats.total }}</div>
            <div class="stats-label">总报警数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" style="background: linear-gradient(135deg, #5f27cd, #341f97);">
          <div class="stats-content">
            <div class="stats-value">{{ alarmStats.urgent }}</div>
            <div class="stats-label">紧急报警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card" style="background: linear-gradient(135deg, #00d2d3, #01a3a4);">
          <div class="stats-content">
            <div class="stats-value">{{ alarmStats.handled }}</div>
            <div class="stats-label">已处理</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报警记录</span>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading" row-key="id">
        <el-table-column prop="alarm_time" label="报警时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.alarm_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="alarm_type" label="报警类型" width="100">
          <template #default="scope">
            <el-tag :type="getAlarmTypeTag(scope.row.alarm_type)">
              {{ scope.row.alarm_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="point_name" label="监测点位" width="120">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.monitoring_point?.point_name || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="alarm_level" label="报警等级" width="100">
          <template #default="scope">
            <el-tag :type="getAlarmLevelTag(scope.row.alarm_level)">
              {{ scope.row.alarm_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="actual_value" label="实际值" width="100">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold;">
              {{ scope.row.actual_value }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="threshold_value" label="阈值" width="100">
          <template #default="scope">
            {{ scope.row.threshold_value }}
          </template>
        </el-table-column>
        <el-table-column prop="message" label="报警信息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="is_handled" label="处理状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_handled ? 'success' : 'danger'">
              {{ scope.row.is_handled ? '已处理' : '待处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button
              v-if="!scope.row.is_handled"
              type="primary"
              link
              @click="handleAlarm(scope.row)"
            >
              处理
            </el-button>
            <el-button type="info" link @click="viewDetail(scope.row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailDialogVisible" title="报警详情" width="500px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="报警时间">{{ formatTime(currentAlarm.alarm_time) }}</el-descriptions-item>
        <el-descriptions-item label="报警类型">{{ currentAlarm.alarm_type }}</el-descriptions-item>
        <el-descriptions-item label="报警等级">
          <el-tag :type="getAlarmLevelTag(currentAlarm.alarm_level)">{{ currentAlarm.alarm_level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="处理状态">
          <el-tag :type="currentAlarm.is_handled ? 'success' : 'danger'">{{ currentAlarm.is_handled ? '已处理' : '待处理' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="实际值" span="2">
          <span style="color: #f56c6c; font-weight: bold;">{{ currentAlarm.actual_value }}</span>
          <span style="margin-left: 10px; color: #909399;">(阈值: {{ currentAlarm.threshold_value }})</span>
        </el-descriptions-item>
        <el-descriptions-item label="报警信息" span="2">{{ currentAlarm.message }}</el-descriptions-item>
        <el-descriptions-item label="处理人" span="2">{{ currentAlarm.handled_by || '-' }}</el-descriptions-item>
        <el-descriptions-item label="处理时间" span="2">{{ formatTime(currentAlarm.handled_time) || '-' }}</el-descriptions-item>
        <el-descriptions-item label="处理方法" span="2">{{ currentAlarm.handling_method || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>

    <el-dialog v-model="handleDialogVisible" title="处理报警" width="500px">
      <el-form :model="handleForm" label-width="80px">
        <el-form-item label="处理人">
          <el-input v-model="handleForm.handled_by" placeholder="请输入处理人姓名" />
        </el-form-item>
        <el-form-item label="处理方法">
          <el-input
            v-model="handleForm.handling_method"
            type="textarea"
            :rows="3"
            placeholder="请输入处理方法描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="handleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitHandle" :loading="submitting">确认处理</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { environmentApi } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const tableData = ref([])
const detailDialogVisible = ref(false)
const handleDialogVisible = ref(false)
const currentAlarm = ref({})
const handleForm = reactive({
  handled_by: '',
  handling_method: ''
})

const alarmStats = computed(() => {
  const data = tableData.value
  return {
    total: data.length,
    pending: data.filter(item => !item.is_handled).length,
    handled: data.filter(item => item.is_handled).length,
    urgent: data.filter(item => item.alarm_level === '紧急').length
  }
})

const getAlarmTypeTag = (type) => {
  const map = { '粉尘超标': 'warning', '噪音超标': 'info', '废水超标': 'success' }
  return map[type] || 'info'
}

const getAlarmLevelTag = (level) => {
  const map = { '紧急': 'danger', '重要': 'warning', '一般': 'info' }
  return map[level] || 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await environmentApi.getAlarms()
    tableData.value = res.data || []
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const viewDetail = (row) => {
  currentAlarm.value = row
  detailDialogVisible.value = true
}

const handleAlarm = (row) => {
  currentAlarm.value = row
  handleForm.handled_by = ''
  handleForm.handling_method = ''
  handleDialogVisible.value = true
}

const submitHandle = async () => {
  if (!handleForm.handled_by) {
    ElMessage.warning('请输入处理人')
    return
  }
  
  submitting.value = true
  try {
    await environmentApi.handleAlarm(currentAlarm.value.id, {
      handled_by: handleForm.handled_by,
      handling_method: handleForm.handling_method
    })
    ElMessage.success('处理成功')
    handleDialogVisible.value = false
    loadData()
  } catch (e) {
    ElMessage.error('处理失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.stats-card {
  color: white;
  text-align: center;
}
.stats-value {
  font-size: 28px;
  font-weight: bold;
}
.stats-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 5px;
}
</style>
