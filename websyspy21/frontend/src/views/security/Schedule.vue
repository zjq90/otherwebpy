<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">安保排班管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="排班日期">
          <el-date-picker
            v-model="searchForm.schedule_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            clearable
          />
        </el-form-item>
        <el-form-item label="班次">
          <el-select v-model="searchForm.shift_type" placeholder="请选择班次" clearable>
            <el-option label="早班" value="早班" />
            <el-option label="中班" value="中班" />
            <el-option label="晚班" value="晚班" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待执行" value="待执行" />
            <el-option label="执行中" value="执行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="取消" value="取消" />
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
        <el-table-column prop="personnel_name" label="安保人员" width="120">
          <template #default="{ row }">
            {{ row.personnel?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="schedule_date" label="排班日期" width="120" />
        <el-table-column prop="shift_type" label="班次" width="100">
          <template #default="{ row }">
            <el-tag :type="getShiftType(row.shift_type)">{{ row.shift_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="time" label="时间" width="150">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }} - {{ formatTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="post" label="岗位" width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="180">
          <template #default="{ row }">
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
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="安保人员" prop="personnel_id">
          <el-select v-model="formData.personnel_id" placeholder="请选择安保人员" style="width: 100%">
            <el-option
              v-for="item in personnelList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="排班日期" prop="schedule_date">
          <el-date-picker
            v-model="formData.schedule_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="班次" prop="shift_type">
          <el-select v-model="formData.shift_type" placeholder="请选择班次" style="width: 100%">
            <el-option label="早班" value="早班" />
            <el-option label="中班" value="中班" />
            <el-option label="晚班" value="晚班" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间" prop="start_time">
          <el-time-select
            v-model="formData.start_time"
            :picker-options="{ start: '00:00', step: '00:30', end: '23:30' }"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间" prop="end_time">
          <el-time-select
            v-model="formData.end_time"
            :picker-options="{ start: '00:00', step: '00:30', end: '23:30' }"
            placeholder="选择时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="岗位" prop="post">
          <el-input v-model="formData.post" placeholder="请输入岗位" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="待执行" value="待执行" />
            <el-option label="执行中" value="执行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="取消" value="取消" />
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

const personnelList = ref([])

const searchForm = reactive({
  schedule_date: '',
  shift_type: '',
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
  personnel_id: null,
  schedule_date: '',
  shift_type: '',
  start_time: '',
  end_time: '',
  post: '',
  status: '待执行'
})

const formRules = {
  personnel_id: [{ required: true, message: '请选择安保人员', trigger: 'change' }],
  schedule_date: [{ required: true, message: '请选择排班日期', trigger: 'change' }],
  shift_type: [{ required: true, message: '请选择班次', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑安保排班' : '新增安保排班')

const getShiftType = (type) => {
  const types = { '早班': 'success', '中班': 'warning', '晚班': 'danger' }
  return types[type] || 'info'
}

const getStatusType = (status) => {
  const types = { '待执行': 'info', '执行中': 'primary', '已完成': 'success', '取消': 'danger' }
  return types[status] || 'info'
}

const formatTime = (time) => {
  if (!time) return '-'
  return time.substring(0, 5)
}

const loadPersonnelList = async () => {
  try {
    const res = await security.getPersonnelList({ page: 1, page_size: 100, status: '在职' })
    personnelList.value = res.data?.items || []
  } catch (error) {
    console.error('加载安保人员列表失败:', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    const res = await security.getScheduleList(params)
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
  searchForm.schedule_date = ''
  searchForm.shift_type = ''
  searchForm.status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.personnel_id = null
  formData.schedule_date = ''
  formData.shift_type = ''
  formData.start_time = ''
  formData.end_time = ''
  formData.post = ''
  formData.status = '待执行'
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
  Object.assign(formData, {
    ...row,
    schedule_date: row.schedule_date,
    personnel_id: row.personnel_id
  })
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    '确定要删除该排班记录吗？',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await security.deleteSchedule(row.id)
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
      await security.updateSchedule(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await security.createSchedule(formData)
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

onMounted(() => {
  loadPersonnelList()
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
