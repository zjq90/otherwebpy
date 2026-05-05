<template>
  <div class="inventory-page">
    <el-card shadow="hover" class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="物料类型">
          <el-select v-model="filterForm.material_type" placeholder="全部" clearable style="width: 140px">
            <el-option label="水泥" value="水泥" />
            <el-option label="砂石" value="砂石" />
            <el-option label="粉煤灰" value="粉煤灰" />
            <el-option label="外加剂" value="外加剂" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterForm.status" placeholder="全部" clearable style="width: 140px">
            <el-option label="正常" value="正常" />
            <el-option label="低库存" value="低库存" />
            <el-option label="空仓" value="空仓" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>重置
          </el-button>
        </el-form-item>
        <el-form-item style="margin-left: auto;">
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>新增料仓
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>料仓列表</span>
              <div class="header-actions">
                <el-button type="success" size="small" @click="fetchData">
                  <el-icon><Refresh /></el-icon>刷新
                </el-button>
              </div>
            </div>
          </template>
          <el-table :data="silosList" stripe v-loading="loading">
            <el-table-column prop="name" label="料仓名称" width="140" />
            <el-table-column prop="material_type" label="物料类型" width="100" />
            <el-table-column label="库存状态" min-width="220">
              <template #default="{ row }">
                <div class="inventory-status">
                  <span class="inventory-text">
                    {{ row.current_level.toFixed(2) }} / {{ row.capacity.toFixed(2) }} 吨
                  </span>
                  <el-progress 
                    :percentage="Math.min(100, (row.current_level / row.capacity) * 100)"
                    :stroke-width="12"
                    :color="getProgressColor(row)"
                  />
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="min_threshold" label="预警阈值(吨)" width="100">
              <template #default="{ row }">
                <span :class="{ 'text-danger': row.current_level <= row.min_threshold }">
                  {{ row.min_threshold }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleAdjust(row)">调整库存</el-button>
                <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
                <el-button type="primary" link @click="handleViewRecords(row)">记录</el-button>
                <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>实时库存分布</span>
          </template>
          <div ref="chartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="siloDialogVisible" :title="siloDialogTitle" width="500px">
      <el-form :model="siloForm" :rules="siloRules" ref="siloFormRef" label-width="100px">
        <el-form-item label="料仓名称" prop="name">
          <el-input v-model="siloForm.name" placeholder="请输入料仓名称" />
        </el-form-item>
        <el-form-item label="物料类型" prop="material_type">
          <el-select v-model="siloForm.material_type" placeholder="请选择物料类型" style="width: 100%">
            <el-option label="水泥" value="水泥" />
            <el-option label="砂石" value="砂石" />
            <el-option label="粉煤灰" value="粉煤灰" />
            <el-option label="外加剂" value="外加剂" />
          </el-select>
        </el-form-item>
        <el-form-item label="最大容量(吨)" prop="capacity">
          <el-input-number v-model="siloForm.capacity" :min="0" :step="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="当前库存(吨)" prop="current_level">
          <el-input-number v-model="siloForm.current_level" :min="0" :step="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="预警阈值(吨)" prop="min_threshold">
          <el-input-number v-model="siloForm.min_threshold" :min="0" :step="5" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="siloDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSiloSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="adjustDialogVisible" title="调整库存" width="450px">
      <el-form :model="adjustForm" :rules="adjustRules" ref="adjustFormRef" label-width="100px">
        <el-form-item label="料仓名称">
          <el-input :value="currentSilo?.name" disabled />
        </el-form-item>
        <el-form-item label="当前库存">
          <el-input :value="currentSilo?.current_level + ' 吨'" disabled />
        </el-form-item>
        <el-form-item label="变更类型" prop="change_type">
          <el-select v-model="adjustForm.change_type" placeholder="请选择变更类型" style="width: 100%">
            <el-option label="入库" value="入库" />
            <el-option label="出库" value="出库" />
            <el-option label="调整" value="调整" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量(吨)" prop="quantity">
          <el-input-number v-model="adjustForm.quantity" :min="0" :step="1" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="变更原因" prop="reason">
          <el-input v-model="adjustForm.reason" type="textarea" :rows="2" placeholder="请输入变更原因" />
        </el-form-item>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="adjustForm.operator" placeholder="请输入操作人姓名" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAdjustSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="recordsDialogVisible" title="库存变更记录" width="800px">
      <el-table :data="inventoryRecords" stripe max-height="400">
        <el-table-column prop="change_type" label="变更类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.change_type === '入库' ? 'success' : row.change_type === '出库' ? 'danger' : 'warning'">
              {{ row.change_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="变更数量(吨)" width="120">
          <template #default="{ row }">
            <span :class="row.change_type === '出库' ? 'text-danger' : 'text-success'">
              {{ row.change_type === '出库' ? '-' : '+' }}{{ row.quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance_before" label="变更前(吨)" width="100" />
        <el-table-column prop="balance_after" label="变更后(吨)" width="100" />
        <el-table-column prop="reason" label="变更原因" />
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="record_time" label="记录时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.record_time) }}
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import * as echarts from 'echarts'
import { siloApi } from '@/api'

const loading = ref(false)
const silosList = ref([])
const inventoryRecords = ref([])
const currentSilo = ref(null)

const siloDialogVisible = ref(false)
const adjustDialogVisible = ref(false)
const recordsDialogVisible = ref(false)
const isEdit = ref(false)
const chartRef = ref(null)

const filterForm = reactive({
  material_type: '',
  status: ''
})

const siloForm = reactive({
  id: null,
  name: '',
  material_type: '',
  capacity: 500,
  current_level: 0,
  min_threshold: 50,
  unit: '吨'
})

const adjustForm = reactive({
  silo_id: null,
  change_type: '',
  quantity: 0,
  reason: '',
  operator: ''
})

const siloFormRef = ref<FormInstance>()
const adjustFormRef = ref<FormInstance>()

const siloDialogTitle = computed(() => isEdit.value ? '编辑料仓' : '新增料仓')

const siloRules: FormRules = {
  name: [{ required: true, message: '请输入料仓名称', trigger: 'blur' }],
  material_type: [{ required: true, message: '请选择物料类型', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入最大容量', trigger: 'blur' }]
}

const adjustRules: FormRules = {
  change_type: [{ required: true, message: '请选择变更类型', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}

const getStatusType = (status) => {
  const types = { '正常': 'success', '低库存': 'warning', '空仓': 'danger' }
  return types[status] || 'info'
}

const getProgressColor = (row) => {
  const percentage = (row.current_level / row.capacity) * 100
  if (row.current_level <= row.min_threshold) return '#F56C6C'
  if (percentage < 30) return '#E6A23C'
  if (percentage < 70) return '#409EFF'
  return '#67C23A'
}

const formatTime = (time) => {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterForm.material_type) params.material_type = filterForm.material_type
    
    const res = await siloApi.getList({ limit: 100 })
    let data = res.data
    
    if (filterForm.status) {
      data = data.filter(item => item.status === filterForm.status)
    }
    
    silosList.value = data
    nextTick(() => {
      initChart()
    })
  } catch (error) {
    ElMessage.error('获取料仓数据失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const initChart = () => {
  if (!chartRef.value || silosList.value.length === 0) return
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}吨 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      top: 'center'
    },
    series: [
      {
        name: '库存',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['60%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        data: silosList.value.map(s => ({
          value: s.current_level,
          name: s.name,
          itemStyle: {
            color: s.current_level <= s.min_threshold ? '#F56C6C' : '#409EFF'
          }
        }))
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  filterForm.material_type = ''
  filterForm.status = ''
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(siloForm, {
    id: null,
    name: '',
    material_type: '',
    capacity: 500,
    current_level: 0,
    min_threshold: 50,
    unit: '吨'
  })
  siloDialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(siloForm, { ...row })
  siloDialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除料仓"${row.name}"吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await siloApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleAdjust = (row) => {
  currentSilo.value = row
  adjustForm.silo_id = row.id
  adjustForm.change_type = ''
  adjustForm.quantity = 0
  adjustForm.reason = ''
  adjustForm.operator = ''
  adjustDialogVisible.value = true
}

const handleViewRecords = async (row) => {
  currentSilo.value = row
  try {
    const res = await siloApi.getRecords({ silo_id: row.id, limit: 50 })
    inventoryRecords.value = res.data
    recordsDialogVisible.value = true
  } catch (error) {
    ElMessage.error('获取库存记录失败')
  }
}

const handleSiloSubmit = async () => {
  if (!siloFormRef.value) return
  
  await siloFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await siloApi.update(siloForm.id, siloForm)
          ElMessage.success('更新成功')
        } else {
          await siloApi.create(siloForm)
          ElMessage.success('创建成功')
        }
        siloDialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const handleAdjustSubmit = async () => {
  if (!adjustFormRef.value) return
  
  await adjustFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await siloApi.adjustInventory(adjustForm)
        ElMessage.success('库存调整成功')
        adjustDialogVisible.value = false
        fetchData()
      } catch (error) {
        ElMessage.error('库存调整失败')
      }
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.inventory-page {
  width: 100%;
}

.filter-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.inventory-status {
  width: 100%;
}

.inventory-text {
  display: block;
  margin-bottom: 4px;
  font-size: 12px;
  color: #606266;
}

.text-danger {
  color: #F56C6C;
  font-weight: 600;
}

.text-success {
  color: #67C23A;
  font-weight: 600;
}

.chart-container {
  width: 100%;
  height: 350px;
}
</style>
