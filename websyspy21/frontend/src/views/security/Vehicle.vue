<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">车辆出入登记</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="车牌号">
          <el-input v-model="searchForm.plate_number" placeholder="请输入车牌号" clearable />
        </el-form-item>
        <el-form-item label="车主姓名">
          <el-input v-model="searchForm.owner_name" placeholder="请输入车主姓名" clearable />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="在场" value="在场" />
            <el-option label="已离开" value="已离开" />
          </el-select>
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

      <el-table :data="tableData" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="plate_number" label="车牌号" width="120" />
        <el-table-column prop="vehicle_type" label="车辆类型" width="100" />
        <el-table-column prop="owner_name" label="车主姓名" width="100" />
        <el-table-column prop="owner_phone" label="车主电话" width="130" />
        <el-table-column label="进入时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.entry_time) }}
          </template>
        </el-table-column>
        <el-table-column label="离开时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.exit_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="purpose" label="来访目的" width="120" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '在场' ? 'warning' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="220">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '在场'"
              type="success"
              link
              size="small"
              @click="handleExit(row)"
            >
              登记离开
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        class="pagination"
      />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="650px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="车牌号" prop="plate_number">
          <el-input v-model="formData.plate_number" placeholder="请输入车牌号" />
        </el-form-item>
        <el-form-item label="车辆类型" prop="vehicle_type">
          <el-select v-model="formData.vehicle_type" placeholder="请选择车辆类型" clearable style="width: 100%">
            <el-option label="轿车" value="轿车" />
            <el-option label="SUV" value="SUV" />
            <el-option label="货车" value="货车" />
            <el-option label="电动车" value="电动车" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="车主姓名" prop="owner_name">
          <el-input v-model="formData.owner_name" placeholder="请输入车主姓名" />
        </el-form-item>
        <el-form-item label="车主电话" prop="owner_phone">
          <el-input v-model="formData.owner_phone" placeholder="请输入车主电话" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入口门岗" prop="entry_gate">
              <el-input v-model="formData.entry_gate" placeholder="请输入入口门岗" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出口门岗" prop="exit_gate">
              <el-input v-model="formData.exit_gate" placeholder="请输入出口门岗" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="来访目的" prop="purpose">
          <el-input v-model="formData.purpose" placeholder="请输入来访目的" />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
        <el-form-item v-if="isEdit" label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="在场" value="在场" />
            <el-option label="已离开" value="已离开" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="exitDialogVisible"
      title="登记离开"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="exitFormRef"
        :model="exitFormData"
        :rules="exitFormRules"
        label-width="100px"
      >
        <el-form-item label="车牌号">
          <el-input :value="exitFormData.plate_number" disabled />
        </el-form-item>
        <el-form-item label="出口门岗" prop="exit_gate">
          <el-input v-model="exitFormData.exit_gate" placeholder="请输入出口门岗" />
        </el-form-item>
        <el-form-item label="离开时间" prop="exit_time">
          <el-date-picker
            v-model="exitFormData.exit_time"
            type="datetime"
            placeholder="选择离开时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="exitFormData.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="exitDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="exitSubmitLoading" @click="handleExitSubmit">
          确认离开
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { security } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const exitSubmitLoading = ref(false)
const dialogVisible = ref(false)
const exitDialogVisible = ref(false)
const formRef = ref(null)
const exitFormRef = ref(null)
const isEdit = ref(false)

const searchForm = reactive({
  plate_number: '',
  owner_name: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const formData = reactive({
  id: null,
  plate_number: '',
  vehicle_type: '',
  owner_name: '',
  owner_phone: '',
  entry_time: '',
  exit_time: '',
  entry_gate: '',
  exit_gate: '',
  purpose: '',
  remarks: '',
  status: '在场'
})

const exitFormData = reactive({
  id: null,
  plate_number: '',
  exit_gate: '',
  exit_time: '',
  remarks: ''
})

const formRules = {
  plate_number: [{ required: true, message: '请输入车牌号', trigger: 'blur' }]
}

const exitFormRules = {
  exit_time: [{ required: true, message: '请选择离开时间', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑车辆登记' : '新增车辆登记')

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    const res = await security.getVehicleList(params)
    tableData.value = res.data?.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.plate_number = ''
  searchForm.owner_name = ''
  searchForm.status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.plate_number = ''
  formData.vehicle_type = ''
  formData.owner_name = ''
  formData.owner_phone = ''
  formData.entry_time = ''
  formData.exit_time = ''
  formData.entry_gate = ''
  formData.exit_gate = ''
  formData.purpose = ''
  formData.remarks = ''
  formData.status = '在场'
  formRef.value?.resetFields()
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleExit = (row) => {
  exitFormData.id = row.id
  exitFormData.plate_number = row.plate_number
  exitFormData.exit_gate = row.exit_gate || ''
  exitFormData.exit_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  exitFormData.remarks = row.remarks || ''
  exitDialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除车辆"${row.plate_number}"的登记记录吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await security.deleteVehicle(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await security.updateVehicle(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await security.createVehicle(formData)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error?.response?.data?.detail || '提交失败')
  } finally {
    submitLoading.value = false
  }
}

const handleExitSubmit = async () => {
  await exitFormRef.value.validate()
  exitSubmitLoading.value = true
  try {
    const updateData = {
      status: '已离开',
      exit_time: exitFormData.exit_time,
      exit_gate: exitFormData.exit_gate
    }
    if (exitFormData.remarks) {
      updateData.remarks = exitFormData.remarks
    }
    await security.updateVehicle(exitFormData.id, updateData)
    ElMessage.success('离开登记成功')
    exitDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
    ElMessage.error(error?.response?.data?.detail || '提交失败')
  } finally {
    exitSubmitLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.page-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.search-form {
  margin-bottom: 20px;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
}
</style>
