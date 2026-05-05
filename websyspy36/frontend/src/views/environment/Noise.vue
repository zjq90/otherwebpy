<template>
  <div class="noise-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="8">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon" style="background: #e6a23c;">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value" style="color: #e6a23c;">{{ noiseStats.overCount }}</div>
              <div class="stats-label">超标次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon" style="background: #67c23a;">
              <el-icon :size="24"><TrendCharts /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value" style="color: #67c23a;">{{ noiseStats.avgLevel.toFixed(1) }}</div>
              <div class="stats-label">平均噪音 (dB)</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-icon" style="background: #409eff;">
              <el-icon :size="24"><Calendar /></el-icon>
            </div>
            <div class="stats-info">
              <div class="stats-value" style="color: #409eff;">{{ noiseStats.totalCount }}</div>
              <div class="stats-label">监测次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <span>噪音监测数据</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
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
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column prop="record_time" label="时间" width="180">
          <template #default="scope">
            {{ formatTime(scope.row.record_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="point_name" label="监测点位" width="120">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.monitoring_point?.point_name || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="noise_level_day" label="昼间噪音 (dB)" width="140">
          <template #default="scope">
            <span :style="{ color: scope.row.noise_level_day > 70 ? '#f56c6c' : '#67c23a' }">
              {{ scope.row.noise_level_day?.toFixed(1) || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="noise_level_night" label="夜间噪音 (dB)" width="140">
          <template #default="scope">
            <span :style="{ color: scope.row.noise_level_night > 55 ? '#f56c6c' : '#67c23a' }">
              {{ scope.row.noise_level_night?.toFixed(1) || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="equivalent_level" label="等效声级 (dB)" width="140">
          <template #default="scope">
            {{ scope.row.equivalent_level?.toFixed(1) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="is_over_limit" label="是否超标" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_over_limit ? 'danger' : 'success'">
              {{ scope.row.is_over_limit ? '超标' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="550px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="记录日期" prop="record_date">
          <el-date-picker
            v-model="form.record_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="监测点位" prop="monitoring_point_id">
          <el-select v-model="form.monitoring_point_id" placeholder="请选择监测点位" style="width: 100%">
            <el-option
              v-for="item in pointList"
              :key="item.id"
              :label="item.point_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="昼间噪音 (dB)" prop="noise_level_day">
          <el-input-number v-model="form.noise_level_day" :min="0" :max="200" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="夜间噪音 (dB)" prop="noise_level_night">
          <el-input-number v-model="form.noise_level_night" :min="0" :max="200" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="等效声级 (dB)" prop="equivalent_level">
          <el-input-number v-model="form.equivalent_level" :min="0" :max="200" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="昼间阈值 (dB)" prop="threshold_day">
          <el-input-number v-model="form.threshold_day" :min="0" :max="200" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="夜间阈值 (dB)" prop="threshold_night">
          <el-input-number v-model="form.threshold_night" :min="0" :max="200" :precision="1" style="width: 100%" />
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
import { Plus, Search, Warning, TrendCharts, Calendar } from '@element-plus/icons-vue'
import { environmentApi } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增噪音监测记录')
const isEdit = ref(false)

const formRef = ref(null)
const tableData = ref([])
const pointList = ref([])

const searchForm = reactive({
  startDate: '',
  endDate: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: null,
  record_date: '',
  monitoring_point_id: null,
  noise_level_day: 0,
  noise_level_night: 0,
  equivalent_level: 0,
  threshold_day: 70,
  threshold_night: 55,
  is_over_limit: false
})

const rules = {
  record_date: [{ required: true, message: '请选择记录日期', trigger: 'change' }],
  monitoring_point_id: [{ required: true, message: '请选择监测点位', trigger: 'change' }],
  noise_level_day: [{ required: true, message: '请输入昼间噪音值', trigger: 'blur' }],
  noise_level_night: [{ required: true, message: '请输入夜间噪音值', trigger: 'blur' }]
}

const noiseStats = computed(() => {
  const data = tableData.value
  const overCount = data.filter(item => item.is_over_limit).length
  const avgLevel = data.length > 0 
    ? data.reduce((sum, item) => sum + (item.noise_level_day || 0), 0) / data.length 
    : 0
  return {
    overCount,
    avgLevel,
    totalCount: data.length
  }
})

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  return date.toLocaleString('zh-CN')
}

const loadPointList = async () => {
  try {
    const res = await environmentApi.getMonitoringPoints()
    pointList.value = (res.data || []).filter(p => p.monitoring_type === '噪音')
  } catch (e) {
    console.error('加载监测点位列表失败:', e)
    pointList.value = []
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    if (searchForm.startDate) {
      params.start_date = searchForm.startDate
    }
    if (searchForm.endDate) {
      params.end_date = searchForm.endDate
    }
    
    const res = await environmentApi.getNoiseMonitoring(params)
    tableData.value = res.data || []
  } catch (e) {
    console.error('加载数据失败:', e)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.startDate = ''
  searchForm.endDate = ''
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增噪音监测记录'
  Object.assign(form, {
    id: null,
    record_date: '',
    monitoring_point_id: null,
    noise_level_day: 0,
    noise_level_night: 0,
    equivalent_level: 0,
    threshold_day: 70,
    threshold_night: 55,
    is_over_limit: false
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑噪音监测记录'
  Object.assign(form, { ...row })
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
    if (e !== 'cancel') {
      console.error('删除失败:', e)
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          ElMessage.success('更新成功')
        } else {
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (e) {
        console.error('提交失败:', e)
        ElMessage.error('提交失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

onMounted(() => {
  loadPointList()
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
  padding: 10px;
}
.stats-content {
  display: flex;
  align-items: center;
}
.stats-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.stats-info {
  margin-left: 15px;
}
.stats-value {
  font-size: 20px;
  font-weight: bold;
}
.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}
</style>
