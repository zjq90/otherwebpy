<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">突发事件上报</span>
          <div class="actions">
            <el-button type="danger" @click="handleAdd">
              <el-icon><Warning /></el-icon> 快速上报
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="事件类型">
          <el-select v-model="searchForm.event_type" placeholder="请选择类型" clearable>
            <el-option label="火灾" value="火灾" />
            <el-option label="盗窃" value="盗窃" />
            <el-option label="斗殴" value="斗殴" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="请选择优先级" clearable>
            <el-option label="紧急" value="紧急" />
            <el-option label="重要" value="重要" />
            <el-option label="一般" value="一般" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="待处理" />
            <el-option label="处理中" value="处理中" />
            <el-option label="已处理" value="已处理" />
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
        <el-table-column prop="report_title" label="事件标题" min-width="200" />
        <el-table-column prop="event_type" label="事件类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getEventType(row.event_type)">{{ row.event_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="发生地点" width="150" />
        <el-table-column prop="reporter_name" label="上报人" width="100" />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="report_time" label="上报时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.report_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="220">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button v-if="row.status !== '已处理'" type="success" link size="small" @click="handleProcess(row)">处理</el-button>
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
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="事件标题" prop="report_title">
          <el-input v-model="formData.report_title" placeholder="请输入事件标题" :disabled="isView" />
        </el-form-item>
        <el-form-item label="事件类型" prop="event_type">
          <el-select v-model="formData.event_type" placeholder="请选择事件类型" style="width: 100%" :disabled="isView">
            <el-option label="火灾" value="火灾" />
            <el-option label="盗窃" value="盗窃" />
            <el-option label="斗殴" value="斗殴" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="发生地点" prop="location">
          <el-input v-model="formData.location" placeholder="请输入发生地点" :disabled="isView" />
        </el-form-item>
        <el-form-item label="上报人" prop="reporter_name">
          <el-input v-model="formData.reporter_name" placeholder="请输入上报人姓名" :disabled="isView" />
        </el-form-item>
        <el-form-item label="联系电话" prop="reporter_phone">
          <el-input v-model="formData.reporter_phone" placeholder="请输入联系电话" :disabled="isView" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" placeholder="请选择优先级" style="width: 100%" :disabled="isView">
            <el-option label="紧急" value="紧急" />
            <el-option label="重要" value="重要" />
            <el-option label="一般" value="一般" />
          </el-select>
        </el-form-item>
        <el-form-item label="事件描述" prop="event_description">
          <el-input
            v-model="formData.event_description"
            type="textarea"
            :rows="4"
            placeholder="请详细描述事件情况"
            :disabled="isView"
          />
        </el-form-item>
        <el-divider v-if="isProcess">处理信息</el-divider>
        <el-form-item v-if="isProcess" label="处理人" prop="handle_person">
          <el-input v-model="formData.handle_person" placeholder="请输入处理人姓名" />
        </el-form-item>
        <el-form-item v-if="isProcess" label="处理结果" prop="handle_result">
          <el-input
            v-model="formData.handle_result"
            type="textarea"
            :rows="4"
            placeholder="请输入处理结果"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%" :disabled="isView">
            <el-option label="待处理" value="待处理" />
            <el-option label="处理中" value="处理中" />
            <el-option label="已处理" value="已处理" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ isView ? '关闭' : '取消' }}</el-button>
        <el-button v-if="!isView" type="primary" :loading="submitLoading" @click="handleSubmit">
          {{ isProcess ? '完成处理' : '确定' }}
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
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const isView = ref(false)
const isProcess = ref(false)

const searchForm = reactive({
  event_type: '',
  priority: '',
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
  report_title: '',
  event_type: '其他',
  location: '',
  reporter_name: '',
  reporter_phone: '',
  report_time: '',
  event_description: '',
  handle_person: '',
  handle_time: '',
  handle_result: '',
  priority: '一般',
  status: '待处理'
})

const formRules = {
  report_title: [{ required: true, message: '请输入事件标题', trigger: 'blur' }],
  event_type: [{ required: true, message: '请选择事件类型', trigger: 'change' }],
  location: [{ required: true, message: '请输入发生地点', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看突发事件'
  if (isProcess.value) return '处理突发事件'
  return isEdit.value ? '编辑突发事件' : '快速上报'
})

const getEventType = (type) => {
  const types = { '火灾': 'danger', '盗窃': 'warning', '斗殴': 'danger', '其他': 'info' }
  return types[type] || 'info'
}

const getPriorityType = (priority) => {
  const types = { '紧急': 'danger', '重要': 'warning', '一般': 'info' }
  return types[priority] || 'info'
}

const getStatusType = (status) => {
  const types = { '待处理': 'warning', '处理中': 'primary', '已处理': 'success' }
  return types[status] || 'info'
}

const formatDateTime = (time) => {
  if (!time) return '-'
  return time.replace('T', ' ').substring(0, 19)
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    const res = await security.getEmergencyList(params)
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
  searchForm.event_type = ''
  searchForm.priority = ''
  searchForm.status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.report_title = ''
  formData.event_type = '其他'
  formData.location = ''
  formData.reporter_name = ''
  formData.reporter_phone = ''
  formData.report_time = ''
  formData.event_description = ''
  formData.handle_person = ''
  formData.handle_time = ''
  formData.handle_result = ''
  formData.priority = '一般'
  formData.status = '待处理'
  isView.value = false
  isProcess.value = false
  formRef.value?.resetFields()
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleView = (row) => {
  resetForm()
  isView.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleProcess = (row) => {
  resetForm()
  isEdit.value = true
  isProcess.value = true
  Object.assign(formData, row)
  formData.status = '处理中'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除突发事件"${row.report_title}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await security.deleteEmergency(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!isView.value) {
    await formRef.value.validate()
  }
  submitLoading.value = true
  try {
    if (isProcess.value) {
      formData.handle_time = new Date().toISOString()
      formData.status = '已处理'
    }
    
    if (isEdit.value) {
      await security.updateEmergency(formData.id, formData)
      ElMessage.success(isProcess.value ? '处理完成' : '更新成功')
    } else {
      await security.createEmergency(formData)
      ElMessage.success('上报成功')
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
