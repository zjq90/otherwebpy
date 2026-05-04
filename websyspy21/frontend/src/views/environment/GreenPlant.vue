<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">绿化植物管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="植物名称">
          <el-input v-model="searchForm.plant_name" placeholder="请输入植物名称" clearable />
        </el-form-item>
        <el-form-item label="植物类型">
          <el-select v-model="searchForm.plant_type" placeholder="请选择类型" clearable>
            <el-option label="乔木" value="乔木" />
            <el-option label="灌木" value="灌木" />
            <el-option label="花卉" value="花卉" />
            <el-option label="草坪" value="草坪" />
          </el-select>
        </el-form-item>
        <el-form-item label="生长状态">
          <el-select v-model="searchForm.growth_status" placeholder="请选择状态" clearable>
            <el-option label="良好" value="良好" />
            <el-option label="一般" value="一般" />
            <el-option label="较差" value="较差" />
            <el-option label="死亡" value="死亡" />
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
        <el-table-column prop="plant_name" label="植物名称" width="120" />
        <el-table-column prop="plant_code" label="植物编号" width="120" />
        <el-table-column prop="plant_type" label="植物类型" width="100">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.plant_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="scientific_name" label="学名" width="150" />
        <el-table-column prop="location" label="种植位置" min-width="150" />
        <el-table-column prop="quantity" label="数量" width="80" />
        <el-table-column prop="growth_status" label="生长状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getGrowthStatusType(row.growth_status)">
              {{ row.growth_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responsible_person" label="责任人" width="100" />
        <el-table-column label="操作" fixed="right" width="220">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">查看</el-button>
            <el-button type="success" link size="small" @click="handleViewMaintenance(row)">养护</el-button>
            <el-button type="warning" link size="small" @click="handleEdit(row)">编辑</el-button>
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
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="植物名称" prop="plant_name">
              <el-input v-model="formData.plant_name" placeholder="请输入植物名称" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="植物编号" prop="plant_code">
              <el-input v-model="formData.plant_code" placeholder="请输入植物编号" :disabled="isView" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="植物类型" prop="plant_type">
              <el-select v-model="formData.plant_type" placeholder="请选择植物类型" style="width: 100%" :disabled="isView">
                <el-option label="乔木" value="乔木" />
                <el-option label="灌木" value="灌木" />
                <el-option label="花卉" value="花卉" />
                <el-option label="草坪" value="草坪" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="数量" prop="quantity">
              <el-input-number v-model="formData.quantity" :min="1" style="width: 100%" :disabled="isView" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="学名" prop="scientific_name">
              <el-input v-model="formData.scientific_name" placeholder="请输入学名" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="种植日期" prop="planting_date">
              <el-date-picker
                v-model="formData.planting_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
                :disabled="isView"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="种植位置" prop="location">
          <el-input v-model="formData.location" placeholder="请输入种植位置" :disabled="isView" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="责任人" prop="responsible_person">
              <el-input v-model="formData.responsible_person" placeholder="请输入责任人" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生长状态" prop="growth_status">
              <el-select v-model="formData.growth_status" placeholder="请选择生长状态" style="width: 100%" :disabled="isView">
                <el-option label="良好" value="良好" />
                <el-option label="一般" value="一般" />
                <el-option label="较差" value="较差" />
                <el-option label="死亡" value="死亡" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
            :disabled="isView"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">{{ isView ? '关闭' : '取消' }}</el-button>
        <el-button v-if="!isView" type="primary" :loading="submitLoading" @click="handleSubmit">
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
const isView = ref(false)

const searchForm = reactive({
  plant_name: '',
  plant_type: '',
  growth_status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const formData = reactive({
  id: null,
  plant_name: '',
  plant_code: '',
  plant_type: '',
  scientific_name: '',
  location: '',
  planting_date: '',
  quantity: 1,
  growth_status: '良好',
  responsible_person: '',
  remarks: ''
})

const formRules = {
  plant_name: [{ required: true, message: '请输入植物名称', trigger: 'blur' }],
  plant_type: [{ required: true, message: '请选择植物类型', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看绿化植物'
  return isEdit.value ? '编辑绿化植物' : '新增绿化植物'
})

const getGrowthStatusType = (status) => {
  const types = { '良好': 'success', '一般': 'warning', '较差': 'danger', '死亡': 'info' }
  return types[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    const res = await environment.getGreenPlantList(params)
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
  searchForm.plant_name = ''
  searchForm.plant_type = ''
  searchForm.growth_status = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.plant_name = ''
  formData.plant_code = ''
  formData.plant_type = ''
  formData.scientific_name = ''
  formData.location = ''
  formData.planting_date = ''
  formData.quantity = 1
  formData.growth_status = '良好'
  formData.responsible_person = ''
  formData.remarks = ''
  isView.value = false
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

const handleViewMaintenance = (row) => {
  ElMessage.info(`请跳转至养护计划管理页面查看"${row.plant_name}"的养护计划`)
}

const handleEdit = (row) => {
  isEdit.value = true
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除绿化植物"${row.plant_name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await environment.deleteGreenPlant(row.id)
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
      await environment.updateGreenPlant(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await environment.createGreenPlant(formData)
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
