<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">巡逻记录管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="巡逻日期">
          <el-date-picker
            v-model="searchForm.patrol_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            clearable
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="异常" value="异常" />
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
        <el-table-column label="巡逻路线" width="150">
          <template #default="{ row }">
            {{ row.route?.route_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="patrol_date" label="巡逻日期" width="120" />
        <el-table-column label="开始时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="结束时间" width="170">
          <template #default="{ row }">
            {{ formatDateTime(row.end_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="checkpoints_completed" label="已完成巡检点" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
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
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="巡逻路线" prop="route_id">
          <el-select
            v-model="formData.route_id"
            placeholder="请选择巡逻路线"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in patrolRouteList"
              :key="item.id"
              :label="item.route_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="安保人员" prop="personnel_id">
          <el-select
            v-model="formData.personnel_id"
            placeholder="请选择安保人员"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in personnelList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="巡逻日期" prop="patrol_date">
          <el-date-picker
            v-model="formData.patrol_date"
            type="date"
            placeholder="选择巡逻日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-date-picker
                v-model="formData.start_time"
                type="datetime"
                placeholder="选择开始时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-date-picker
                v-model="formData.end_time"
                type="datetime"
                placeholder="选择结束时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="已完成巡检点" prop="checkpoints_completed">
          <el-input
            v-model="formData.checkpoints_completed"
            type="textarea"
            :rows="2"
            placeholder="请输入已完成巡检点"
          />
        </el-form-item>
        <el-form-item label="异常情况" prop="abnormalities">
          <el-input
            v-model="formData.abnormalities"
            type="textarea"
            :rows="2"
            placeholder="请输入异常情况（如有）"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="进行中" value="进行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="异常" value="异常" />
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

const patrolRouteList = ref([])
const personnelList = ref([])

const searchForm = reactive({
  patrol_date: '',
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
  route_id: null,
  personnel_id: null,
  patrol_date: '',
  start_time: '',
  end_time: '',
  checkpoints_completed: '',
  abnormalities: '',
  status: '进行中'
})

const formRules = {
  route_id: [{ required: true, message: '请选择巡逻路线', trigger: 'change' }],
  personnel_id: [{ required: true, message: '请选择安保人员', trigger: 'change' }],
  patrol_date: [{ required: true, message: '请选择巡逻日期', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑巡逻记录' : '新增巡逻记录')

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime
}

const getStatusType = (status) => {
  switch (status) {
    case '进行中':
      return 'primary'
    case '已完成':
      return 'success'
    case '异常':
      return 'danger'
    default:
      return 'info'
  }
}

const loadPatrolRouteList = async () => {
  try {
    const res = await security.getPatrolRouteList({ page: 1, page_size: 1000 })
    patrolRouteList.value = res.data?.items || []
  } catch (error) {
    console.error('加载巡逻路线列表失败:', error)
  }
}

const loadPersonnelList = async () => {
  try {
    const res = await security.getPersonnelList({ page: 1, page_size: 1000, status: '在职' })
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
    const res = await security.getPatrolRecordList(params)
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
  searchForm.patrol_date = ''
  searchForm.status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.route_id = null
  formData.personnel_id = null
  formData.patrol_date = ''
  formData.start_time = ''
  formData.end_time = ''
  formData.checkpoints_completed = ''
  formData.abnormalities = ''
  formData.status = '进行中'
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

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除该巡逻记录吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await security.deletePatrolRecord(row.id)
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
      await security.updatePatrolRecord(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await security.createPatrolRecord(formData)
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
  loadData()
  loadPatrolRouteList()
  loadPersonnelList()
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
