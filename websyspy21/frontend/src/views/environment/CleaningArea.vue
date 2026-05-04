<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">保洁区域管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="区域名称">
          <el-input v-model="searchForm.area_name" placeholder="请输入区域名称" clearable />
        </el-form-item>
        <el-form-item label="区域类型">
          <el-select v-model="searchForm.area_type" placeholder="请选择类型" clearable>
            <el-option label="楼栋" value="楼栋" />
            <el-option label="楼层" value="楼层" />
            <el-option label="公共区域" value="公共区域" />
            <el-option label="道路" value="道路" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="启用" value="启用" />
            <el-option label="停用" value="停用" />
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

      <el-table :data="tableData" v-loading="loading" stripe style="width: 100%" row-key="id">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="area_name" label="区域名称" min-width="150" />
        <el-table-column prop="area_code" label="区域编号" width="120" />
        <el-table-column prop="area_type" label="区域类型" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.area_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="area_size" label="区域面积(㎡)" width="120" />
        <el-table-column prop="cleaning_frequency" label="清洁频次" width="120" />
        <el-table-column prop="responsible_person" label="责任人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '启用' ? 'success' : 'danger'">
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
      width="650px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="区域名称" prop="area_name">
              <el-input v-model="formData.area_name" placeholder="请输入区域名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域编号" prop="area_code">
              <el-input v-model="formData.area_code" placeholder="请输入区域编号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="区域类型" prop="area_type">
              <el-select v-model="formData.area_type" placeholder="请选择区域类型" style="width: 100%">
                <el-option label="楼栋" value="楼栋" />
                <el-option label="楼层" value="楼层" />
                <el-option label="公共区域" value="公共区域" />
                <el-option label="道路" value="道路" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="区域面积(㎡)" prop="area_size">
              <el-input-number v-model="formData.area_size" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="清洁频次" prop="cleaning_frequency">
              <el-input v-model="formData.cleaning_frequency" placeholder="例如：每日清洁" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="启用" value="启用" />
                <el-option label="停用" value="停用" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="清洁标准" prop="cleaning_standard">
          <el-input
            v-model="formData.cleaning_standard"
            type="textarea"
            :rows="3"
            placeholder="请输入清洁标准"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="责任人" prop="responsible_person">
              <el-input v-model="formData.responsible_person" placeholder="请输入责任人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="责任人电话" prop="responsible_phone">
              <el-input v-model="formData.responsible_phone" placeholder="请输入联系电话" />
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

const searchForm = reactive({
  area_name: '',
  area_type: '',
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
  area_name: '',
  area_code: '',
  area_type: '',
  area_size: null,
  cleaning_frequency: '',
  cleaning_standard: '',
  responsible_person: '',
  responsible_phone: '',
  status: '启用'
})

const formRules = {
  area_name: [{ required: true, message: '请输入区域名称', trigger: 'blur' }],
  area_type: [{ required: true, message: '请选择区域类型', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑保洁区域' : '新增保洁区域')

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    const res = await environment.getCleaningAreaList(params)
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
  searchForm.area_name = ''
  searchForm.area_type = ''
  searchForm.status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.area_name = ''
  formData.area_code = ''
  formData.area_type = ''
  formData.area_size = null
  formData.cleaning_frequency = ''
  formData.cleaning_standard = ''
  formData.responsible_person = ''
  formData.responsible_phone = ''
  formData.status = '启用'
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
    `确定要删除保洁区域"${row.area_name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await environment.deleteCleaningArea(row.id)
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
      await environment.updateCleaningArea(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await environment.createCleaningArea(formData)
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
