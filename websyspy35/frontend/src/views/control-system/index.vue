<template>
  <div class="control-system-page">
    <div class="page-header">
      <span class="page-title">控制系统监控</span>
      <el-button type="primary" @click="handleRefreshAll">
        <el-icon><Refresh /></el-icon>
        刷新状态
      </el-button>
      <el-switch
        v-model="autoRefresh"
        active-text="自动刷新"
        style="margin-left: 15px;"
        @change="handleAutoRefresh"
      />
    </div>
    
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stat-card" :class="overallStatus.class">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><component :is="overallStatus.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overallStatus.text }}</div>
              <div class="stat-label">系统整体状态</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card normal">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><View /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.normal }}</div>
              <div class="stat-label">正常监控项</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card warning">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.warning }}</div>
              <div class="stat-label">预警监控项</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card danger">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><CircleCloseFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.abnormal + stats.fault }}</div>
              <div class="stat-label">异常/故障项</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-tabs v-model="activeTab" type="card" style="margin-bottom: 20px;">
      <el-tab-pane label="断电保护" name="断电保护" />
      <el-tab-pane label="数据隔离" name="数据隔离" />
      <el-tab-pane label="抗干扰能力" name="抗干扰能力" />
      <el-tab-pane label="电压稳定" name="电压稳定" />
      <el-tab-pane label="全部监控" name="全部" />
    </el-tabs>
    
    <el-row :gutter="20">
      <el-col :span="12" v-for="item in filteredData" :key="item.id">
        <el-card class="monitor-card" :class="getMonitorCardClass(item)">
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <span class="item-name">{{ item.monitor_item }}</span>
                <el-tag :class="getMonitorTagClass(item.status)" size="small">
                  {{ item.status }}
                </el-tag>
              </div>
              <div class="header-right">
                <el-button type="primary" link size="small" @click="handleRefresh(item)">
                  刷新
                </el-button>
                <el-button type="primary" link size="small" @click="handleView(item)">
                  详情
                </el-button>
              </div>
            </div>
          </template>
          
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="监控类型">{{ item.monitor_type }}</el-descriptions-item>
            <el-descriptions-item label="是否启用">
              <el-tag :type="item.is_enabled ? 'success' : 'danger'" size="small">
                {{ item.is_enabled ? '已启用' : '已禁用' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="当前状态值">
              <span :class="getValueClass(item)">
                {{ item.current_value }}
                <span v-if="item.unit" style="margin-left: 5px; color: #909399;">{{ item.unit }}</span>
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="正常状态">{{ item.normal_status }}</el-descriptions-item>
            <el-descriptions-item label="最后检查时间" :span="2">{{ item.last_checked_at }}</el-descriptions-item>
          </el-descriptions>
          
          <div v-if="item.description" class="remark-section">
            <span class="remark-label">备注：</span>
            <span class="remark-content">{{ item.description }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>监控状态列表</span>
      </template>
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="monitor_item" label="监控项" width="200" />
        <el-table-column prop="monitor_type" label="监控类型" width="120" />
        <el-table-column label="当前状态值" width="150">
          <template #default="scope">
            <span :class="getValueClass(scope.row)">
              {{ scope.row.current_value }}
              <span v-if="scope.row.unit" style="margin-left: 5px; color: #909399;">{{ scope.row.unit }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="normal_status" label="正常状态" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :class="getMonitorTagClass(scope.row.status)" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_enabled" label="启用状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_enabled ? 'success' : 'danger'" size="small">
              {{ scope.row.is_enabled ? '已启用' : '已禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="last_checked_at" label="最后检查时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="handleRefresh(scope.row)">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
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
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="监控项名称" prop="monitor_item">
          <el-input v-model="form.monitor_item" placeholder="请输入监控项名称" />
        </el-form-item>
        <el-form-item label="监控类型" prop="monitor_type">
          <el-select v-model="form.monitor_type" placeholder="请选择监控类型" style="width: 100%;">
            <el-option label="断电保护" value="断电保护" />
            <el-option label="数据隔离" value="数据隔离" />
            <el-option label="抗干扰能力" value="抗干扰能力" />
            <el-option label="电压稳定" value="电压稳定" />
          </el-select>
        </el-form-item>
        <el-form-item label="当前状态值" prop="current_value">
          <el-input v-model="form.current_value" placeholder="请输入当前状态值" />
        </el-form-item>
        <el-form-item label="数值(可选)">
          <el-input-number v-model="form.numeric_value" :precision="2" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="单位">
          <el-input v-model="form.unit" placeholder="如：V、A、ms" />
        </el-form-item>
        <el-form-item label="正常状态" prop="normal_status">
          <el-input v-model="form.normal_status" placeholder="请输入正常状态描述" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
            <el-option label="正常" value="正常" />
            <el-option label="预警" value="预警" />
            <el-option label="异常" value="异常" />
            <el-option label="故障" value="故障" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否启用">
          <el-switch v-model="form.is_enabled" active-text="是" inactive-text="否" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="detailVisible"
      title="监控项详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="监控项名称">{{ detailForm.monitor_item }}</el-descriptions-item>
        <el-descriptions-item label="监控类型">{{ detailForm.monitor_type }}</el-descriptions-item>
        <el-descriptions-item label="当前状态值">
          <span :class="getValueClass(detailForm)">
            {{ detailForm.current_value }}
            <span v-if="detailForm.unit" style="margin-left: 5px;">{{ detailForm.unit }}</span>
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="数值">
          <span v-if="detailForm.numeric_value !== null">{{ detailForm.numeric_value }} {{ detailForm.unit || '' }}</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="正常状态">{{ detailForm.normal_status }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :class="getMonitorTagClass(detailForm.status)" size="small">
            {{ detailForm.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="是否启用">
          <el-tag :type="detailForm.is_enabled ? 'success' : 'danger'" size="small">
            {{ detailForm.is_enabled ? '已启用' : '已禁用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="最后检查时间">{{ detailForm.last_checked_at }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detailForm.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detailForm.updated_at }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailForm.description || '无' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, View, Edit, Delete, Warning, CircleCloseFilled,
  CircleCheckFilled, InfoFilled
} from '@element-plus/icons-vue'
import {
  getControlSystemStatusList, createControlSystemStatus,
  updateControlSystemStatus, deleteControlSystemStatus,
  refreshControlSystemStatus
} from '@/api/monitoring'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
let refreshTimer = null

const autoRefresh = ref(true)
const activeTab = ref('全部')

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const stats = reactive({
  normal: 0,
  warning: 0,
  abnormal: 0,
  fault: 0
})

const overallStatus = computed(() => {
  if (stats.fault > 0) {
    return { text: '系统故障', class: 'danger', icon: 'CircleCloseFilled' }
  }
  if (stats.abnormal > 0) {
    return { text: '系统异常', class: 'warning', icon: 'Warning' }
  }
  if (stats.warning > 0) {
    return { text: '存在预警', class: 'warning', icon: 'InfoFilled' }
  }
  return { text: '运行正常', class: 'normal', icon: 'CircleCheckFilled' }
})

const filteredData = computed(() => {
  if (activeTab.value === '全部') {
    return tableData.value
  }
  return tableData.value.filter(item => item.monitor_type === activeTab.value)
})

const defaultForm = {
  monitor_item: '',
  monitor_type: '',
  current_value: '',
  numeric_value: null,
  unit: '',
  normal_status: '',
  status: '正常',
  is_enabled: true,
  description: ''
}

const form = reactive({ ...defaultForm })
const detailForm = reactive({ ...defaultForm })

const rules = {
  monitor_item: [{ required: true, message: '请输入监控项名称', trigger: 'blur' }],
  monitor_type: [{ required: true, message: '请选择监控类型', trigger: 'change' }],
  current_value: [{ required: true, message: '请输入当前状态值', trigger: 'blur' }],
  normal_status: [{ required: true, message: '请输入正常状态描述', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑监控项' : '新增监控项')

const getMonitorCardClass = (item) => {
  const classMap = {
    '正常': '',
    '预警': 'card-warning',
    '异常': 'card-abnormal',
    '故障': 'card-fault'
  }
  return classMap[item.status] || ''
}

const getMonitorTagClass = (status) => {
  const classMap = {
    '正常': 'status-tag normal',
    '预警': 'status-tag warning',
    '异常': 'status-tag danger',
    '故障': 'status-tag danger'
  }
  return classMap[status] || 'status-tag normal'
}

const getValueClass = (item) => {
  if (item.status === '故障' || item.status === '异常') return 'value-danger'
  if (item.status === '预警') return 'value-warning'
  return ''
}

const calculateStats = (data) => {
  stats.normal = data.filter(item => item.status === '正常').length
  stats.warning = data.filter(item => item.status === '预警').length
  stats.abnormal = data.filter(item => item.status === '异常').length
  stats.fault = data.filter(item => item.status === '故障').length
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      order_by: 'monitor_type',
      order_dir: 'asc'
    }
    
    const res = await getControlSystemStatusList(params)
    tableData.value = res || []
    pagination.total = 20
    
    calculateStats(res || [])
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleRefreshAll = async () => {
  try {
    await refreshControlSystemStatus()
    ElMessage.success('已刷新所有监控项状态')
    fetchData()
  } catch (error) {
    console.error('刷新失败:', error)
  }
}

const handleRefresh = async (item) => {
  try {
    await refreshControlSystemStatus()
    ElMessage.success('已刷新')
    fetchData()
  } catch (error) {
    console.error('刷新失败:', error)
  }
}

const handleAutoRefresh = (val) => {
  if (val) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const handleView = (row) => {
  Object.assign(detailForm, { ...row })
  detailVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该监控项吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteControlSystemStatus(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateControlSystemStatus(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createControlSystemStatus(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const startAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  refreshTimer = setInterval(() => {
    fetchData()
  }, 30000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  fetchData()
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style lang="scss" scoped>
.control-system-page {
  padding: 20px;
  
  .page-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .page-title {
      font-size: 18px;
      font-weight: 600;
      margin-right: 20px;
    }
  }
  
  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      
      .stat-icon {
        margin-right: 15px;
        color: #409eff;
      }
      
      .stat-info {
        .stat-value {
          font-size: 24px;
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
    
    &.normal .stat-icon {
      color: #67c23a;
    }
    
    &.warning .stat-icon {
      color: #e6a23c;
    }
    
    &.danger .stat-icon {
      color: #f56c6c;
    }
  }
  
  .monitor-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .header-left {
        display: flex;
        align-items: center;
        
        .item-name {
          font-size: 16px;
          font-weight: 600;
          margin-right: 10px;
        }
      }
    }
    
    .remark-section {
      margin-top: 15px;
      padding-top: 15px;
      border-top: 1px solid #ebeef5;
      
      .remark-label {
        color: #909399;
        margin-right: 5px;
      }
      
      .remark-content {
        color: #606266;
      }
    }
    
    &.card-warning {
      border-left: 4px solid #e6a23c;
      background-color: #fdf6ec;
    }
    
    &.card-abnormal {
      border-left: 4px solid #f56c6c;
      background-color: #fef0f0;
    }
    
    &.card-fault {
      border-left: 4px solid #c00;
      background-color: #fff0f0;
    }
  }
  
  .value-danger {
    color: #f56c6c;
    font-weight: 600;
  }
  
  .value-warning {
    color: #e6a23c;
    font-weight: 600;
  }
}
</style>
