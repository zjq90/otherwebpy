<template>
  <div class="sensor-page">
    <div class="page-header">
      <span class="page-title">传感器管理</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增传感器
      </el-button>
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
        <el-form-item label="传感器类型">
          <el-select v-model="searchForm.sensor_type" placeholder="请选择类型" clearable>
            <el-option label="电流" value="电流" />
            <el-option label="温度" value="温度" />
            <el-option label="振动" value="振动" />
            <el-option label="速度" value="速度" />
            <el-option label="压力" value="压力" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="正常" />
            <el-option label="故障" value="故障" />
            <el-option label="离线" value="离线" />
          </el-select>
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
    
    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="sensor_code" label="传感器编号" width="140" />
        <el-table-column prop="name" label="传感器名称" width="180" />
        <el-table-column prop="sensor_type" label="传感器类型" width="100" />
        <el-table-column label="所属设备" width="150">
          <template #default="scope">
            {{ getEquipmentName(scope.row.equipment_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="installation_location" label="安装位置" width="150" show-overflow-tooltip />
        <el-table-column label="阈值范围" width="180">
          <template #default="scope">
            {{ scope.row.min_value }} ~ {{ scope.row.max_value }} {{ scope.row.unit }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :class="getStatusClass(scope.row.status)" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">
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
      />
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="传感器编号" prop="sensor_code">
              <el-input v-model="form.sensor_code" placeholder="请输入传感器编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="传感器名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入传感器名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="传感器类型" prop="sensor_type">
              <el-select v-model="form.sensor_type" placeholder="请选择类型" style="width: 100%;">
                <el-option label="电流" value="电流" />
                <el-option label="温度" value="温度" />
                <el-option label="振动" value="振动" />
                <el-option label="速度" value="速度" />
                <el-option label="压力" value="压力" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属设备" prop="equipment_id">
              <el-select v-model="form.equipment_id" placeholder="请选择设备" style="width: 100%;">
                <el-option
                  v-for="item in equipmentList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="安装位置" prop="installation_location">
              <el-input v-model="form.installation_location" placeholder="请输入安装位置" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位" prop="unit">
              <el-input v-model="form.unit" placeholder="如：A、℃、mm/s" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最小值" prop="min_value">
              <el-input-number v-model="form.min_value" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="最大值" prop="max_value">
              <el-input-number v-model="form.max_value" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="预警阈值" prop="warning_threshold">
              <el-input-number v-model="form.warning_threshold" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="报警阈值" prop="alarm_threshold">
              <el-input-number v-model="form.alarm_threshold" :step="0.1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
                <el-option label="正常" value="正常" />
                <el-option label="故障" value="故障" />
                <el-option label="离线" value="离线" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="description">
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
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import { getSensorList, createSensor, updateSensor, deleteSensor } from '@/api/equipment'
import { getEquipmentList } from '@/api/equipment'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const equipmentList = ref([])

const searchForm = reactive({
  equipment_id: null,
  sensor_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const defaultForm = {
  sensor_code: '',
  name: '',
  sensor_type: '',
  equipment_id: null,
  installation_location: '',
  unit: '',
  min_value: 0,
  max_value: 100,
  warning_threshold: 80,
  alarm_threshold: 90,
  status: '正常',
  description: ''
}

const form = reactive({ ...defaultForm })

const rules = {
  sensor_code: [{ required: true, message: '请输入传感器编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入传感器名称', trigger: 'blur' }],
  sensor_type: [{ required: true, message: '请选择传感器类型', trigger: 'change' }],
  equipment_id: [{ required: true, message: '请选择所属设备', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑传感器' : '新增传感器')

const getStatusClass = (status) => {
  const classMap = {
    '正常': 'status-tag normal',
    '故障': 'status-tag fault',
    '离线': 'status-tag stopped'
  }
  return classMap[status] || 'status-tag normal'
}

const getEquipmentName = (id) => {
  const item = equipmentList.value.find(e => e.id === id)
  return item ? item.name : '-'
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
      ...searchForm
    }
    if (!params.equipment_id) delete params.equipment_id
    if (!params.sensor_type) delete params.sensor_type
    if (!params.status) delete params.status
    
    const res = await getSensorList(params)
    tableData.value = res
    pagination.total = 100
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    equipment_id: null,
    sensor_type: '',
    status: ''
  })
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除传感器 "${row.name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteSensor(row.id)
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
          await updateSensor(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createSensor(form)
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

onMounted(() => {
  fetchEquipmentList()
  fetchData()
})
</script>
