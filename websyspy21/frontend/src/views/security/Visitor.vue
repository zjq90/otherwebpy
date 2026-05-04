<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">外来人员管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="访客姓名">
          <el-input v-model="searchForm.visitor_name" placeholder="请输入访客姓名" clearable />
        </el-form-item>
        <el-form-item label="被访人">
          <el-input v-model="searchForm.visited_person" placeholder="请输入被访人" clearable />
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
        <el-table-column prop="visitor_name" label="访客姓名" width="100" />
        <el-table-column prop="visitor_phone" label="访客电话" width="130" />
        <el-table-column prop="visitor_id_card" label="身份证号" width="180" />
        <el-table-column prop="visit_unit" label="访问单位" width="120" show-overflow-tooltip />
        <el-table-column prop="visited_person" label="被访人" width="100" />
        <el-table-column prop="visit_purpose" label="来访目的" width="100" show-overflow-tooltip />
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
        <el-table-column prop="visitor_count" label="人数" width="80" />
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
        <el-form-item label="访客姓名" prop="visitor_name">
          <el-input v-model="formData.visitor_name" placeholder="请输入访客姓名" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="访客电话" prop="visitor_phone">
              <el-input v-model="formData.visitor_phone" placeholder="请输入访客电话" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号" prop="visitor_id_card">
              <el-input v-model="formData.visitor_id_card" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="访问单位" prop="visit_unit">
              <el-input v-model="formData.visit_unit" placeholder="请输入访问单位" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="被访人" prop="visited_person">
              <el-input v-model="formData.visited_person" placeholder="请输入被访人" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="来访目的" prop="visit_purpose">
              <el-input v-model="formData.visit_purpose" placeholder="请输入来访目的" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="访客人数" prop="visitor_count">
              <el-input-number v-model="formData.visitor_count" :min="1" :max="100" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="携带证件" prop="credentials">
          <el-input
            v-model="formData.credentials"
            type="textarea"
            :rows="2"
            placeholder="请输入携带证件"
          />
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
        <el-form-item label="访客姓名">
          <el-input :value="exitFormData.visitor_name" disabled />
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
  visitor_name: '',
  visited_person: '',
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
  visitor_name: '',
  visitor_phone: '',
  visitor_id_card: '',
  visit_unit: '',
  visited_person: '',
  visit_purpose: '',
  entry_time: '',
  exit_time: '',
  visitor_count: 1,
  credentials: '',
  remarks: '',
  status: '在场'
})

const exitFormData = reactive({
  id: null,
  visitor_name: '',
  exit_time: '',
  remarks: ''
})

const formRules = {
  visitor_name: [{ required: true, message: '请输入访客姓名', trigger: 'blur' }]
}

const exitFormRules = {
  exit_time: [{ required: true, message: '请选择离开时间', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑访客记录' : '新增访客记录')

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
    const res = await security.getVisitorList(params)
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
  searchForm.visitor_name = ''
  searchForm.visited_person = ''
  searchForm.status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.visitor_name = ''
  formData.visitor_phone = ''
  formData.visitor_id_card = ''
  formData.visit_unit = ''
  formData.visited_person = ''
  formData.visit_purpose = ''
  formData.entry_time = ''
  formData.exit_time = ''
  formData.visitor_count = 1
  formData.credentials = ''
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
  exitFormData.visitor_name = row.visitor_name
  exitFormData.exit_time = new Date().toISOString().slice(0, 19).replace('T', ' ')
  exitFormData.remarks = row.remarks || ''
  exitDialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除访客"${row.visitor_name}"的记录吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await security.deleteVisitor(row.id)
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
      await security.updateVisitor(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await security.createVisitor(formData)
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
      exit_time: exitFormData.exit_time
    }
    if (exitFormData.remarks) {
      updateData.remarks = exitFormData.remarks
    }
    await security.updateVisitor(exitFormData.id, updateData)
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
