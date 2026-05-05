<template>
  <div class="energy-page">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <span>能耗指标</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-value">{{ energyStats.electricity.toFixed(2) }}</div>
              <div class="stats-label">电力消耗 (kWh)</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-value">{{ energyStats.water.toFixed(2) }}</div>
              <div class="stats-label">水消耗 (吨)</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-value">{{ energyStats.diesel.toFixed(2) }}</div>
              <div class="stats-label">柴油消耗 (升)</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-value">¥{{ energyStats.totalCost.toFixed(2) }}</div>
              <div class="stats-label">总能耗成本</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="searchForm.startDate"
            type="date"
            placeholder="选择开始日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="searchForm.endDate"
            type="date"
            placeholder="选择结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="能源类型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable>
            <el-option label="电力" value="电力" />
            <el-option label="水" value="水" />
            <el-option label="柴油" value="柴油" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column prop="energy_type" label="能源类型" width="100">
          <template #default="scope">
            <el-tag :type="getEnergyTagType(scope.row.energy_type)">
              {{ scope.row.energy_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="consumption_amount" label="消耗量" width="120">
          <template #default="scope">
            {{ scope.row.consumption_amount?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="cost" label="成本 (元)" width="120">
          <template #default="scope">
            {{ scope.row.cost?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="scope">
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增能耗记录" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="日期" prop="record_date">
          <el-date-picker
            v-model="form.record_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="能源类型" prop="energy_type">
          <el-select v-model="form.energy_type" placeholder="请选择" style="width: 100%">
            <el-option label="电力" value="电力" />
            <el-option label="水" value="水" />
            <el-option label="柴油" value="柴油" />
          </el-select>
        </el-form-item>
        <el-form-item label="消耗量" prop="consumption_amount">
          <el-input-number v-model="form.consumption_amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="成本 (元)" prop="cost">
          <el-input-number v-model="form.cost" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { productionApi } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const tableData = ref([])

const searchForm = reactive({
  startDate: '',
  endDate: '',
  type: ''
})

const form = reactive({
  record_date: '',
  energy_type: '',
  consumption_amount: 0,
  cost: 0
})

const rules = {
  record_date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  energy_type: [{ required: true, message: '请选择能源类型', trigger: 'change' }]
}

const energyStats = computed(() => {
  const stats = { electricity: 0, water: 0, diesel: 0, totalCost: 0 }
  tableData.value.forEach(item => {
    if (item.energy_type === '电力') stats.electricity += item.consumption_amount || 0
    if (item.energy_type === '水') stats.water += item.consumption_amount || 0
    if (item.energy_type === '柴油') stats.diesel += item.consumption_amount || 0
    stats.totalCost += item.cost || 0
  })
  return stats
})

const getEnergyTagType = (type) => {
  const map = { '电力': 'primary', '水': 'success', '柴油': 'warning' }
  return map[type] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await productionApi.getEnergyConsumption()
    tableData.value = res.data || []
  } catch (e) {
    console.error('加载数据失败:', e)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadData()
}

const handleAdd = () => {
  Object.assign(form, { record_date: '', energy_type: '', consumption_amount: 0, cost: 0 })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        await productionApi.createEnergyConsumption({
          ...form,
          unit: form.energy_type === '电力' ? 'kWh' : form.energy_type === '水' ? '吨' : '升'
        })
        ElMessage.success('创建成功')
        dialogVisible.value = false
        loadData()
      } catch (e) {
        ElMessage.error('创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
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
  text-align: center;
}
.stats-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
}
.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
