<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">养护计划管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="计划名称">
          <el-input v-model="searchForm.plan_name" placeholder="请输入计划名称" clearable />
        </el-form-item>
        <el-form-item label="养护类型">
          <el-select v-model="searchForm.maintenance_type" placeholder="请选择类型" clearable>
            <el-option label="浇水" value="浇水" />
            <el-option label="施肥" value="施肥" />
            <el-option label="修剪" value="修剪" />
            <el-option label="病虫害防治" value="病虫害防治" />
            <el-option label="其他" value="其他" />
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
        <el-table-column prop="plan_name" label="计划名称" min-width="150" />
        <el-table-column label="关联植物" width="120">
          <template #default="{ row }">
            {{ row.plant?.plant_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_type" label="养护类型" width="120">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.maintenance_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="frequency" label="养护频次" width="120" />
        <el-table-column label="开始日期" width="120">
          <template #default="{ row }">
            {{ row.start_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="结束日期" width="120">
          <template #default="{ row }">
            {{ row.end_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="responsible_person" label="责任人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="220">
          <template #default="{ row }">
            <el-button
              v-if="row.status === '待执行' || row.status === '执行中'"
              type="success"
              link
              size="small"
              @click="handleComplete(row)"
            >
              完成
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
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划名称" prop="plan_name">
              <el-input v-model="formData.plan_name" placeholder="请输入计划名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联植物" prop="plant_id">
              <el-select
                v-model="formData.plant_id"
                placeholder="请选择植物"
                style="width: 100%"
                filterable
              >
                <el-option
                  v-for="item in greenPlantList"
                  :key="item.id"
                  :label="item.plant_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="养护类型" prop="maintenance_type">
              <el-select v-model="formData.maintenance_type" placeholder="请选择养护类型" style="width: 100%">
                <el-option label="浇水" value="浇水" />
                <el-option label="施肥" value="施肥" />
                <el-option label="修剪" value="修剪" />
                <el-option label="病虫害防治" value="病虫害防治" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="养护频次" prop="frequency">
              <el-input v-model="formData.frequency" placeholder="例如：每周一次" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="formData.start_date"
                type="date"
                placeholder="选择开始日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期" prop="end_date">
              <el-date-picker
                v-model="formData.end_date"
                type="date"
                placeholder="选择结束日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="养护描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入养护描述"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="责任人" prop="responsible_person">
              <el-input v-model="formData.responsible_person" placeholder="请输入责任人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="待执行" value="待执行" />
                <el-option label="执行中" value="执行中" />
                <el-option label="已完成" value="已完成" />
                <el-option label="取消" value="取消" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
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
import { environment } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const greenPlantList = ref([])

const searchForm = reactive({
  plan_name: '',
  maintenance_type: '',
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
  plant_id: null,
  plan_name: '',
  maintenance_type: '',
  frequency: '',
  start_date: '',
  end_date: '',
  description: '',
  responsible_person: '',
  status: '待执行'
})

const formRules = {
  plan_name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  plant_id: [{ required: true, message: '请选择关联植物', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑养护计划' : '新增养护计划')

const getStatusType = (status) => {
  const types = { '待执行': 'info', '执行中': 'primary', '已完成': 'success', '取消': 'danger' }
  return types[status] || 'info'
}

const loadGreenPlantList = async () => {
  try {
    const res = await environment.getGreenPlantList({ page: 1, page_size: 1000 })
    greenPlantList.value = res.data?.items || []
  } catch (error) {
    console.error('加载绿化植物列表失败:', error)
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
    const res = await environment.getMaintenancePlanList(params)
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
  searchForm.plan_name = ''
  searchForm.maintenance_type = ''
  searchForm.status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.plant_id = null
  formData.plan_name = ''
  formData.maintenance_type = ''
  formData.frequency = ''
  formData.start_date = ''
  formData.end_date = ''
  formData.description = ''
  formData.responsible_person = ''
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
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleComplete = (row) => {
  ElMessageBox.confirm(
    `确定要将养护计划"${row.plan_name}"标记为已完成吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await environment.updateMaintenancePlan(row.id, { status: '已完成' })
      ElMessage.success('标记成功')
      loadData()
    } catch (error) {
      console.error('操作失败:', error)
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除养护计划"${row.plan_name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await environment.deleteMaintenancePlan(row.id)
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
      await environment.updateMaintenancePlan(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await environment.createMaintenancePlan(formData)
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
  loadGreenPlantList()
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
