<template>
  <div class="test-blocks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>试块管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增试块
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="试块编号">
          <el-input
            v-model="searchForm.block_no"
            placeholder="请输入试块编号"
            clearable
          />
        </el-form-item>
        <el-form-item label="批次号">
          <el-input
            v-model="searchForm.batch_no"
            placeholder="请输入批次号"
            clearable
          />
        </el-form-item>
        <el-form-item label="养护条件">
          <el-select v-model="searchForm.curing_condition" placeholder="请选择" clearable>
            <el-option label="标准养护" value="标准养护" />
            <el-option label="同条件养护" value="同条件养护" />
            <el-option label="自然养护" value="自然养护" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待试验" value="待试验" />
            <el-option label="已试验" value="已试验" />
            <el-option label="已作废" value="已作废" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="block_no" label="试块编号" width="140" />
        <el-table-column prop="batch_no" label="批次号" width="130" />
        <el-table-column prop="sample_date" label="取样日期" width="110" />
        <el-table-column prop="casting_date" label="浇筑日期" width="110" />
        <el-table-column prop="test_age" label="试验龄期(天)" width="110" />
        <el-table-column prop="planned_test_date" label="计划试验日期" width="120" />
        <el-table-column prop="block_size" label="试块尺寸" width="110" />
        <el-table-column prop="quantity" label="数量(组)" width="90" />
        <el-table-column prop="curing_condition" label="养护条件" width="120">
          <template #default="scope">
            <el-tag :type="getCuringTagType(scope.row.curing_condition)" size="small">
              {{ scope.row.curing_condition }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sample_location" label="取样位置" width="100" />
        <el-table-column prop="sampler" label="取样员" width="90" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="dark">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link v-if="scope.row.status === '待试验'" @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="success" link v-if="scope.row.status === '待试验'" @click="handleMarkTested(scope.row)">
              标记试验
            </el-button>
            <el-button type="danger" link v-if="scope.row.status === '待试验'" @click="handleMarkVoid(scope.row)">
              作废
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
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
        :rules="rules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="试块编号" prop="block_no">
              <el-input v-model="formData.block_no" placeholder="自动生成" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联批次">
              <el-select v-model="formData.batch_id" placeholder="请选择批次" style="width: 100%" :disabled="isView">
                <el-option v-for="batch in batches" :key="batch.id" :label="batch.batch_no" :value="batch.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="取样日期" prop="sample_date">
              <el-date-picker
                v-model="formData.sample_date"
                type="date"
                placeholder="请选择取样日期"
                style="width: 100%"
                :disabled="isView"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="浇筑日期" prop="casting_date">
              <el-date-picker
                v-model="formData.casting_date"
                type="date"
                placeholder="请选择浇筑日期"
                style="width: 100%"
                :disabled="isView"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="试验龄期(天)" prop="test_age">
              <el-select v-model="formData.test_age" placeholder="请选择" style="width: 100%" :disabled="isView">
                <el-option :label="3" :value="3" />
                <el-option :label="7" :value="7" />
                <el-option :label="14" :value="14" />
                <el-option :label="28" :value="28" />
                <el-option :label="56" :value="56" />
                <el-option :label="90" :value="90" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="试块尺寸" prop="block_size">
              <el-select v-model="formData.block_size" placeholder="请选择" style="width: 100%" :disabled="isView">
                <el-option label="100x100x100" value="100x100x100" />
                <el-option label="150x150x150" value="150x150x150" />
                <el-option label="200x200x200" value="200x200x200" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="数量(组)" prop="quantity">
              <el-input-number v-model="formData.quantity" :min="1" :max="10" style="width: 100%" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="养护条件" prop="curing_condition">
              <el-select v-model="formData.curing_condition" placeholder="请选择" style="width: 100%" :disabled="isView">
                <el-option label="标准养护" value="标准养护" />
                <el-option label="同条件养护" value="同条件养护" />
                <el-option label="自然养护" value="自然养护" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="取样位置" prop="sample_location">
              <el-select v-model="formData.sample_location" placeholder="请选择" style="width: 100%" :disabled="isView">
                <el-option label="出料口" value="出料口" />
                <el-option label="浇筑点" value="浇筑点" />
                <el-option label="搅拌车" value="搅拌车" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="取样员" prop="sampler">
              <el-input v-model="formData.sampler" placeholder="请输入取样员" :disabled="isView" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span v-if="!isView">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
        <span v-else>
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isView = ref(false)
const formRef = ref(null)
const batches = ref([])

const searchForm = reactive({
  block_no: '',
  batch_no: '',
  curing_condition: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  id: null,
  block_no: '',
  batch_id: null,
  sample_date: dayjs().format('YYYY-MM-DD'),
  casting_date: dayjs().format('YYYY-MM-DD'),
  test_age: 28,
  planned_test_date: '',
  block_size: '150x150x150',
  quantity: 3,
  curing_condition: '标准养护',
  sample_location: '出料口',
  sampler: '',
  status: '待试验'
})

const rules = {
  sample_date: [{ required: true, message: '请选择取样日期', trigger: 'change' }],
  casting_date: [{ required: true, message: '请选择浇筑日期', trigger: 'change' }],
  test_age: [{ required: true, message: '请选择试验龄期', trigger: 'change' }],
  block_size: [{ required: true, message: '请选择试块尺寸', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }],
  curing_condition: [{ required: true, message: '请选择养护条件', trigger: 'change' }],
  sampler: [{ required: true, message: '请输入取样员', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看试块'
  return formData.id ? '编辑试块' : '新增试块'
})

const getCuringTagType = (condition) => {
  const typeMap = {
    '标准养护': 'primary',
    '同条件养护': 'success',
    '自然养护': 'warning'
  }
  return typeMap[condition] || ''
}

const getStatusType = (status) => {
  const typeMap = {
    '待试验': 'warning',
    '已试验': 'success',
    '已作废': 'info'
  }
  return typeMap[status] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        block_no: 'TB20241201001',
        batch_id: 1,
        batch_no: 'PB20241201001',
        sample_date: '2024-12-01',
        casting_date: '2024-12-01',
        test_age: 28,
        planned_test_date: '2024-12-29',
        block_size: '150x150x150',
        quantity: 3,
        curing_condition: '标准养护',
        sample_location: '出料口',
        sampler: '取样员A',
        status: '待试验'
      },
      {
        id: 2,
        block_no: 'TB20241201002',
        batch_id: 1,
        batch_no: 'PB20241201001',
        sample_date: '2024-12-01',
        casting_date: '2024-12-01',
        test_age: 7,
        planned_test_date: '2024-12-08',
        block_size: '150x150x150',
        quantity: 3,
        curing_condition: '同条件养护',
        sample_location: '浇筑点',
        sampler: '取样员B',
        status: '已试验'
      },
      {
        id: 3,
        block_no: 'TB20241201003',
        batch_id: 2,
        batch_no: 'PB20241201002',
        sample_date: '2024-12-02',
        casting_date: '2024-12-02',
        test_age: 14,
        planned_test_date: '2024-12-16',
        block_size: '100x100x100',
        quantity: 3,
        curing_condition: '自然养护',
        sample_location: '搅拌车',
        sampler: '取样员C',
        status: '已作废'
      }
    ]
    pagination.total = 3
    
    batches.value = [
      { id: 1, batch_no: 'PB20241201001' },
      { id: 2, batch_no: 'PB20241201002' },
      { id: 3, batch_no: 'PB20241201003' }
    ]
  } catch (error) {
    console.error('获取试块数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.block_no = ''
  searchForm.batch_no = ''
  searchForm.curing_condition = ''
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchData()
}

const resetForm = () => {
  formData.id = null
  formData.block_no = ''
  formData.batch_id = null
  formData.sample_date = dayjs().format('YYYY-MM-DD')
  formData.casting_date = dayjs().format('YYYY-MM-DD')
  formData.test_age = 28
  formData.planned_test_date = ''
  formData.block_size = '150x150x150'
  formData.quantity = 3
  formData.curing_condition = '标准养护'
  formData.sample_location = '出料口'
  formData.sampler = ''
  formData.status = '待试验'
  formRef.value?.resetFields()
}

const handleAdd = () => {
  isView.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isView.value = false
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleView = (row) => {
  isView.value = true
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleMarkTested = (row) => {
  ElMessageBox.confirm(
    `确定要标记试块"${row.block_no}"为已试验吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(() => {
    row.status = '已试验'
    ElMessage.success('标记成功')
    fetchData()
  }).catch(() => {})
}

const handleMarkVoid = (row) => {
  ElMessageBox.confirm(
    `确定要作废试块"${row.block_no}"吗？作废后无法恢复。`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.status = '已作废'
    ElMessage.success('作废成功')
    fetchData()
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      fetchData()
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.test-blocks-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>
