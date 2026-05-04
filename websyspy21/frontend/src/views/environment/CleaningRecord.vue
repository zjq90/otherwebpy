<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">清洁记录管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="清洁日期">
          <el-date-picker
            v-model="searchForm.cleaning_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            clearable
          />
        </el-form-item>
        <el-form-item label="清洁员">
          <el-input v-model="searchForm.cleaner_name" placeholder="请输入清洁员姓名" clearable />
        </el-form-item>
        <el-form-item label="清洁质量">
          <el-select v-model="searchForm.cleaning_quality" placeholder="请选择质量" clearable>
            <el-option label="优秀" value="优秀" />
            <el-option label="良好" value="良好" />
            <el-option label="合格" value="合格" />
            <el-option label="不合格" value="不合格" />
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
        <el-table-column label="保洁区域" width="150">
          <template #default="{ row }">
            {{ row.area?.area_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="cleaning_date" label="清洁日期" width="120" />
        <el-table-column prop="cleaner_name" label="清洁员" width="100" />
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
        <el-table-column prop="cleaning_items" label="清洁项目" show-overflow-tooltip />
        <el-table-column prop="cleaning_quality" label="清洁质量" width="100">
          <template #default="{ row }">
            <el-tag :type="getQualityType(row.cleaning_quality)">
              {{ row.cleaning_quality || '-' }}
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
      width="650px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="保洁区域" prop="area_id">
          <el-select
            v-model="formData.area_id"
            placeholder="请选择保洁区域"
            style="width: 100%"
            filterable
          >
            <el-option
              v-for="item in cleaningAreaList"
              :key="item.id"
              :label="item.area_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="清洁日期" prop="cleaning_date">
              <el-date-picker
                v-model="formData.cleaning_date"
                type="date"
                placeholder="选择清洁日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="清洁员" prop="cleaner_name">
              <el-input v-model="formData.cleaner_name" placeholder="请输入清洁员姓名" />
            </el-form-item>
          </el-col>
        </el-row>
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
        <el-form-item label="清洁项目" prop="cleaning_items">
          <el-input
            v-model="formData.cleaning_items"
            type="textarea"
            :rows="2"
            placeholder="请输入清洁项目"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="清洁质量" prop="cleaning_quality">
              <el-select v-model="formData.cleaning_quality" placeholder="请选择清洁质量" style="width: 100%">
                <el-option label="优秀" value="优秀" />
                <el-option label="良好" value="良好" />
                <el-option label="合格" value="合格" />
                <el-option label="不合格" value="不合格" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
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
import { environment } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const cleaningAreaList = ref([])

const searchForm = reactive({
  cleaning_date: '',
  cleaner_name: '',
  cleaning_quality: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const formData = reactive({
  id: null,
  area_id: null,
  cleaning_date: '',
  cleaner_name: '',
  start_time: '',
  end_time: '',
  cleaning_items: '',
  cleaning_quality: '',
  remarks: ''
})

const formRules = {
  area_id: [{ required: true, message: '请选择保洁区域', trigger: 'change' }],
  cleaning_date: [{ required: true, message: '请选择清洁日期', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑清洁记录' : '新增清洁记录')

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return datetime
}

const getQualityType = (quality) => {
  const types = { '优秀': 'success', '良好': 'primary', '合格': 'warning', '不合格': 'danger' }
  return types[quality] || 'info'
}

const loadCleaningAreaList = async () => {
  try {
    const res = await environment.getCleaningAreaList({ page: 1, page_size: 1000, status: '启用' })
    cleaningAreaList.value = res.data?.items || []
  } catch (error) {
    console.error('加载保洁区域列表失败:', error)
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
    const res = await environment.getCleaningRecordList(params)
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
  searchForm.cleaning_date = ''
  searchForm.cleaner_name = ''
  searchForm.cleaning_quality = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.area_id = null
  formData.cleaning_date = ''
  formData.cleaner_name = ''
  formData.start_time = ''
  formData.end_time = ''
  formData.cleaning_items = ''
  formData.cleaning_quality = ''
  formData.remarks = ''
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
    `确定要删除该清洁记录吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await environment.deleteCleaningRecord(row.id)
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
      await environment.updateCleaningRecord(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await environment.createCleaningRecord(formData)
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
  loadCleaningAreaList()
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
