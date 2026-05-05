<template>
  <div class="log-list-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="任务单ID">
          <el-input-number v-model="queryParams.order_id" :min="1" placeholder="请输入" clearable style="width: 150px;" />
        </el-form-item>
        <el-form-item label="生产阶段">
          <el-select v-model="queryParams.stage" placeholder="请选择" clearable>
            <el-option label="配料中" value="batching" />
            <el-option label="搅拌中" value="mixing" />
            <el-option label="出料中" value="discharging" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="queryParams.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="queryParams.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 200px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon> 搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon> 重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <span>生产日志列表</span>
      </template>

      <el-table :data="logList" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_id" label="任务单ID" width="100" />
        <el-table-column prop="stage" label="生产阶段" width="100">
          <template #default="scope">
            <el-tag :type="getStageType(scope.row.stage)" size="small">
              {{ getStageLabel(scope.row.stage) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="批次重量" min-width="200">
          <template #default="scope">
            <div class="batch-info">
              <span v-if="scope.row.batch_weight_cement">水泥: {{ scope.row.batch_weight_cement }}kg</span>
              <span v-if="scope.row.batch_weight_sand">砂: {{ scope.row.batch_weight_sand }}kg</span>
              <span v-if="scope.row.batch_weight_gravel">石: {{ scope.row.batch_weight_gravel }}kg</span>
              <span v-if="scope.row.batch_weight_water">水: {{ scope.row.batch_weight_water }}kg</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="mixing_time" label="搅拌时间(秒)" width="120" />
        <el-table-column prop="discharge_volume" label="出料方量(m³)" width="120" />
        <el-table-column prop="temperature" label="温度(°C)" width="100" />
        <el-table-column prop="humidity" label="湿度(%)" width="100" />
        <el-table-column prop="log_message" label="日志消息" min-width="200" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="queryParams.skip"
        v-model:page-size="queryParams.limit"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { monitoringApi } from '../../api'

const loading = ref(false)
const logList = ref([])
const total = ref(0)

const queryParams = reactive({
  order_id: null,
  stage: '',
  start_time: null,
  end_time: null,
  skip: 1,
  limit: 20
})

const fetchLogList = async () => {
  loading.value = true
  try {
    const params = {
      skip: (queryParams.skip - 1) * queryParams.limit,
      limit: queryParams.limit
    }
    if (queryParams.order_id) params.order_id = queryParams.order_id
    if (queryParams.stage) params.stage = queryParams.stage
    if (queryParams.start_time) params.start_time = queryParams.start_time
    if (queryParams.end_time) params.end_time = queryParams.end_time

    const res = await monitoringApi.getLogs(params)
    logList.value = res
    total.value = res.length >= queryParams.limit ? (queryParams.skip + 1) * queryParams.limit : queryParams.skip * queryParams.limit + res.length
  } catch (error) {
    ElMessage.error('获取日志列表失败')
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

const handleSearch = () => {
  queryParams.skip = 1
  fetchLogList()
}

const handleReset = () => {
  queryParams.order_id = null
  queryParams.stage = ''
  queryParams.start_time = null
  queryParams.end_time = null
  queryParams.skip = 1
  fetchLogList()
}

const handleSizeChange = (val) => {
  queryParams.limit = val
  fetchLogList()
}

const handleCurrentChange = (val) => {
  queryParams.skip = val
  fetchLogList()
}

onMounted(() => {
  fetchLogList()
})
</script>

<style scoped>
.log-list-container {
  padding: 0;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.table-card {
  border-radius: 8px;
}

.batch-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: #606266;
}
</style>
