<template>
  <div class="page-container">
    <el-card shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">养护记录管理</span>
          <div class="actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="养护日期">
          <el-date-picker
            v-model="searchForm.maintenance_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            clearable
          />
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
        <el-form-item label="操作人">
          <el-input v-model="searchForm.operator" placeholder="请输入操作人" clearable />
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
        <el-table-column prop="maintenance_date" label="养护日期" width="120" />
        <el-table-column label="关联计划" width="150">
          <template #default="{ row }">
            {{ row.plan?.plan_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_type" label="养护类型" width="120">
          <template #default="{ row }">
            <el-tag type="primary">{{ row.maintenance_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="操作人" width="100" />
        <el-table-column prop="work_content" label="工作内容" min-width="150" show-overflow-tooltip />
        <el-table-column prop="materials_used" label="使用材料" min-width="120" show-overflow-tooltip />
        <el-table-column prop="quality" label="养护质量" width="100">
          <template #default="{ row }">
            <el-tag :type="getQualityType(row.quality)">
              {{ row.quality || '-' }}
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
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="养护日期" prop="maintenance_date">
              <el-date-picker
                v-model="formData.maintenance_date"
                type="date"
                placeholder="选择养护日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
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
            <el-form-item label="关联计划" prop="plan_id">
              <el-select
                v-model="formData.plan_id"
                placeholder="请选择养护计划（可选）"
                style="width: 100%"
                filterable
                clearable
              >
                <el-option
                  v-for="item in maintenancePlanList"
                  :key="item.id"
                  :label="item.plan_name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
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
        </el-row>
        <el-form-item label="操作人" prop="operator">
          <el-input v-model="formData.operator" placeholder="请输入操作人" />
        </el-form-item>
        <el-form-item label="工作内容" prop="work_content">
          <el-input
            v-model="formData.work_content"
            type="textarea"
            :rows="3"
            placeholder="请输入工作内容"
          />
        </el-form-item>
        <el-form-item label="使用材料" prop="materials_used">
          <el-input
            v-model="formData.materials_used"
            type="textarea"
            :rows="2"
            placeholder="请输入使用材料"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="养护质量" prop="quality">
              <el-select v-model="formData.quality" placeholder="请选择养护质量" style="width: 100%">
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

const greenPlantList = ref([])
const maintenancePlanList = ref([])

const searchForm = reactive({
  maintenance_date: '',
  maintenance_type: '',
  operator: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const formData = reactive({
  id: null,
  plan_id: null,
  plant_id: null,
  maintenance_date: '',
  maintenance_type: '',
  operator: '',
  work_content: '',
  materials_used: '',
  quality: '',
  remarks: ''
})

const formRules = {
  plant_id: [{ required: true, message: '请选择关联植物', trigger: 'change' }],
  maintenance_date: [{ required: true, message: '请选择养护日期', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑养护记录' : '新增养护记录')

const getQualityType = (quality) => {
  const types = { '优秀': 'success', '良好': 'primary', '合格': 'warning', '不合格': 'danger' }
  return types[quality] || 'info'
}

const loadGreenPlantList = async () => {
  try {
    const res = await environment.getGreenPlantList({ page: 1, page_size: 1000 })
    greenPlantList.value = res.data?.items || []
  } catch (error) {
    console.error('加载绿化植物列表失败:', error)
  }
}

const loadMaintenancePlanList = async () => {
  try {
    const res = await environment.getMaintenancePlanList({ page: 1, page_size: 1000 })
    maintenancePlanList.value = res.data?.items || []
  } catch (error) {
    console.error('加载养护计划列表失败:', error)
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
    const res = await environment.getMaintenanceRecordList(params)
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
  searchForm.maintenance_date = ''
  searchForm.maintenance_type = ''
  searchForm.operator = ''
  handleSearch()
}

const resetForm = () => {
  formData.id = null
  formData.plan_id = null
  formData.plant_id = null
  formData.maintenance_date = ''
  formData.maintenance_type = ''
  formData.operator = ''
  formData.work_content = ''
  formData.materials_used = ''
  formData.quality = ''
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
    `确定要删除该养护记录吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await environment.deleteMaintenanceRecord(row.id)
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
      await environment.updateMaintenanceRecord(formData.id, formData)
      ElMessage.success('更新成功')
    } else {
      await environment.createMaintenanceRecord(formData)
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
  loadMaintenancePlanList()
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
