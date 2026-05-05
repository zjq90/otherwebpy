<template>
  <div class="logs-page">
    <div class="page-header">
      <span class="page-title">运行日志</span>
    </div>
    
    <el-card class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="设备">
          <el-select v-model="searchForm.equipment_id" placeholder="请选择设备" clearable style="width: 200px;">
            <el-option
              v-for="item in equipmentList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="日志类型">
          <el-select v-model="searchForm.log_type" placeholder="请选择类型" clearable>
            <el-option label="运行状态" value="运行状态" />
            <el-option label="故障告警" value="故障告警" />
            <el-option label="预警信息" value="预警信息" />
            <el-option label="操作记录" value="操作记录" />
            <el-option label="系统消息" value="系统消息" />
          </el-select>
        </el-form-item>
        <el-form-item label="严重程度">
          <el-select v-model="searchForm.severity" placeholder="请选择严重程度" clearable>
            <el-option label="低" value="低" />
            <el-option label="中" value="中" />
            <el-option label="高" value="高" />
            <el-option label="紧急" value="紧急" />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 350px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-value">{{ statData.total }}</div>
            <div class="stat-label">总日志数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card warning">
          <div class="stat-content">
            <div class="stat-value">{{ statData.warning }}</div>
            <div class="stat-label">预警信息</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card danger">
          <div class="stat-content">
            <div class="stat-value">{{ statData.alarm }}</div>
            <div class="stat-label">故障告警</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card info">
          <div class="stat-content">
            <div class="stat-value">{{ statData.normal }}</div>
            <div class="stat-label">正常运行</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>日志列表</span>
        </div>
      </template>
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="设备" width="150">
          <template #default="scope">
            {{ getEquipmentName(scope.row.equipment_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="log_type" label="日志类型" width="120">
          <template #default="scope">
            <el-tag :class="getLogTypeClass(scope.row.log_type)" size="small">
              {{ scope.row.log_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="scope">
            <el-tag :class="getSeverityClass(scope.row.severity)" size="small">
              {{ scope.row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="日志标题" width="200" show-overflow-tooltip />
        <el-table-column prop="description" label="详细内容" min-width="250" show-overflow-tooltip />
        <el-table-column prop="operator" label="操作人" width="100">
          <template #default="scope">
            {{ scope.row.operator || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              <el-icon><View /></el-icon>
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 15px;"
      />
    </el-card>
    
    <el-dialog
      v-model="detailVisible"
      title="日志详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="设备">{{ getEquipmentName(detailForm.equipment_id) }}</el-descriptions-item>
        <el-descriptions-item label="日志类型">
          <el-tag :class="getLogTypeClass(detailForm.log_type)" size="small">
            {{ detailForm.log_type }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="严重程度">
          <el-tag :class="getSeverityClass(detailForm.severity)" size="small">
            {{ detailForm.severity }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作人">{{ detailForm.operator || '-' }}</el-descriptions-item>
        <el-descriptions-item label="日志标题" :span="2">{{ detailForm.title }}</el-descriptions-item>
        <el-descriptions-item label="详细内容" :span="2">
          <div style="white-space: pre-wrap; max-height: 200px; overflow-y: auto;">{{ detailForm.description }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detailForm.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detailForm.updated_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, View } from '@element-plus/icons-vue'
import { getOperationLogList, createOperationLog } from '@/api/monitoring'
import { getEquipmentList } from '@/api/equipment'

const loading = ref(false)
const detailVisible = ref(false)

const equipmentList = ref([])

const searchForm = reactive({
  equipment_id: null,
  log_type: '',
  severity: '',
  dateRange: []
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const statData = reactive({
  total: 0,
  warning: 0,
  alarm: 0,
  normal: 0
})

const defaultDetailForm = {
  id: null,
  equipment_id: null,
  log_type: '',
  severity: '',
  title: '',
  description: '',
  operator: '',
  created_at: '',
  updated_at: ''
}

const detailForm = reactive({ ...defaultDetailForm })

const getEquipmentName = (id) => {
  const item = equipmentList.value.find(e => e.id === id)
  return item ? item.name : '-'
}

const getLogTypeClass = (logType) => {
  const classMap = {
    '运行状态': 'status-tag normal',
    '故障告警': 'status-tag danger',
    '预警信息': 'status-tag warning',
    '操作记录': 'status-tag info',
    '系统消息': 'status-tag info'
  }
  return classMap[logType] || 'status-tag normal'
}

const getSeverityClass = (severity) => {
  const classMap = {
    '低': 'status-tag normal',
    '中': 'status-tag warning',
    '高': 'status-tag danger',
    '紧急': 'status-tag danger'
  }
  return classMap[severity] || 'status-tag normal'
}

const fetchEquipmentList = async () => {
  try {
    const res = await getEquipmentList({ limit: 1000 })
    equipmentList.value = res
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      order_by: 'created_at',
      order_dir: 'desc'
    }
    
    if (searchForm.equipment_id) {
      params.equipment_id = searchForm.equipment_id
    }
    if (searchForm.log_type) {
      params.log_type = searchForm.log_type
    }
    if (searchForm.severity) {
      params.severity = searchForm.severity
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_time = searchForm.dateRange[0]
      params.end_time = searchForm.dateRange[1]
    }
    
    const res = await getOperationLogList(params)
    tableData.value = res || []
    pagination.total = 100
    
    calculateStats(res || [])
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const calculateStats = (data) => {
  statData.total = data.length
  statData.warning = data.filter(item => item.log_type === '预警信息').length
  statData.alarm = data.filter(item => item.log_type === '故障告警').length
  statData.normal = data.filter(item => item.log_type === '运行状态').length
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    equipment_id: null,
    log_type: '',
    severity: '',
    dateRange: []
  })
  pagination.page = 1
  fetchData()
}

const handleView = (row) => {
  Object.assign(detailForm, { ...row })
  detailVisible.value = true
}

onMounted(() => {
  fetchEquipmentList()
  fetchData()
})
</script>

<style lang="scss" scoped>
.logs-page {
  padding: 20px;
  
  .page-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .page-title {
      font-size: 18px;
      font-weight: 600;
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-card {
    text-align: center;
    
    &.warning {
      border-left: 4px solid #e6a23c;
    }
    
    &.danger {
      border-left: 4px solid #f56c6c;
    }
    
    &.info {
      border-left: 4px solid #409eff;
    }
    
    .stat-content {
      .stat-value {
        font-size: 28px;
        font-weight: 600;
        color: #303133;
        margin-bottom: 5px;
      }
      
      .stat-label {
        font-size: 14px;
        color: #909399;
      }
    }
  }
}
</style>
