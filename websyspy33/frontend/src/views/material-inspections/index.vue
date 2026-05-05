<template>
  <div class="inspections-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>原材料检验</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增检验
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="检验编号">
          <el-input
            v-model="searchForm.inspection_no"
            placeholder="请输入检验编号"
            clearable
          />
        </el-form-item>
        <el-form-item label="检验结果">
          <el-select v-model="searchForm.result" placeholder="请选择" clearable>
            <el-option label="合格" value="合格" />
            <el-option label="不合格" value="不合格" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="草稿" value="草稿" />
            <el-option label="已提交" value="已提交" />
            <el-option label="已审核" value="已审核" />
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
        <el-table-column prop="inspection_no" label="检验编号" width="150" />
        <el-table-column prop="batch_no" label="批次号" width="130" />
        <el-table-column prop="sample_no" label="样品号" width="120" />
        <el-table-column prop="sample_date" label="取样日期" width="120" />
        <el-table-column prop="inspector" label="检验员" width="100" />
        <el-table-column prop="inspection_date" label="检验日期" width="120" />
        <el-table-column prop="result" label="检验结果" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_qualified ? 'success' : 'danger'">
              {{ scope.row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="lab_temperature" label="实验室温度(℃)" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link v-if="scope.row.status === '草稿'" @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link v-if="scope.row.status === '草稿'" @click="handleSubmitInspection(scope.row)">
              提交
            </el-button>
            <el-button type="success" link v-if="scope.row.status === '已提交'" @click="handleApprove(scope.row)">
              审核
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
      width="800px"
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
            <el-form-item label="检验编号" prop="inspection_no">
              <el-input v-model="formData.inspection_no" placeholder="自动生成" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="批次号" prop="batch_no">
              <el-input v-model="formData.batch_no" placeholder="请输入批次号" :disabled="isView" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="样品号" prop="sample_no">
              <el-input v-model="formData.sample_no" placeholder="请输入样品号" :disabled="isView" />
            </el-form-item>
          </el-col>
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
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="检验员" prop="inspector">
              <el-input v-model="formData.inspector" placeholder="请输入检验员" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="检验日期" prop="inspection_date">
              <el-date-picker
                v-model="formData.inspection_date"
                type="date"
                placeholder="请选择检验日期"
                style="width: 100%"
                :disabled="isView"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实验室温度(℃)">
              <el-input-number
                v-model="formData.lab_temperature"
                :min="0"
                :max="50"
                :precision="1"
                style="width: 100%"
                :disabled="isView"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实验室湿度(%)">
              <el-input-number
                v-model="formData.lab_humidity"
                :min="0"
                :max="100"
                :precision="1"
                style="width: 100%"
                :disabled="isView"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="检验结果" prop="result">
          <el-radio-group v-model="formData.result" :disabled="isView">
            <el-radio value="合格">合格</el-radio>
            <el-radio value="不合格">不合格</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="检验结论">
          <el-input
            v-model="formData.conclusion"
            type="textarea"
            :rows="2"
            placeholder="请输入检验结论"
            :disabled="isView"
          />
        </el-form-item>
        <el-form-item label="检验标准">
          <el-input
            v-model="formData.standard_value"
            type="textarea"
            :rows="2"
            placeholder="请输入检验标准（JSON格式）"
            :disabled="isView"
          />
        </el-form-item>
        <el-form-item label="检测数据">
          <el-input
            v-model="formData.test_data"
            type="textarea"
            :rows="3"
            placeholder="请输入检测数据（JSON格式）"
            :disabled="isView"
          />
        </el-form-item>
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

const searchForm = reactive({
  inspection_no: '',
  result: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  id: null,
  inspection_no: '',
  material_id: null,
  supplier_id: null,
  batch_no: '',
  sample_no: '',
  sample_date: dayjs().format('YYYY-MM-DD'),
  inspector: '',
  inspection_date: dayjs().format('YYYY-MM-DD'),
  inspection_items: null,
  test_data: '',
  standard_value: '',
  result: '合格',
  conclusion: '',
  is_qualified: true,
  lab_temperature: 23.0,
  lab_humidity: 60.0,
  status: '草稿'
})

const rules = {
  batch_no: [{ required: true, message: '请输入批次号', trigger: 'blur' }],
  sample_no: [{ required: true, message: '请输入样品号', trigger: 'blur' }],
  sample_date: [{ required: true, message: '请选择取样日期', trigger: 'change' }],
  inspector: [{ required: true, message: '请输入检验员', trigger: 'blur' }],
  result: [{ required: true, message: '请选择检验结果', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看检验记录'
  return formData.id ? '编辑检验记录' : '新增检验记录'
})

const getStatusType = (status) => {
  const typeMap = {
    '草稿': 'info',
    '已提交': 'warning',
    '已审核': 'success'
  }
  return typeMap[status] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        inspection_no: 'INSP20241201001',
        batch_no: 'BATCH10001',
        sample_no: 'SAMPLE001',
        sample_date: '2024-12-01',
        inspector: '李工',
        inspection_date: '2024-12-02',
        result: '合格',
        is_qualified: true,
        lab_temperature: 23.0,
        lab_humidity: 60.0,
        status: '已审核'
      },
      {
        id: 2,
        inspection_no: 'INSP20241201002',
        batch_no: 'BATCH10002',
        sample_no: 'SAMPLE002',
        sample_date: '2024-12-01',
        inspector: '王工',
        inspection_date: '2024-12-02',
        result: '不合格',
        is_qualified: false,
        lab_temperature: 22.5,
        lab_humidity: 58.0,
        status: '已提交'
      },
      {
        id: 3,
        inspection_no: 'INSP20241201003',
        batch_no: 'BATCH10003',
        sample_no: 'SAMPLE003',
        sample_date: '2024-12-02',
        inspector: '张工',
        inspection_date: '2024-12-03',
        result: '合格',
        is_qualified: true,
        lab_temperature: 24.0,
        lab_humidity: 62.0,
        status: '草稿'
      }
    ]
    pagination.total = 3
  } catch (error) {
    console.error('获取检验数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.inspection_no = ''
  searchForm.result = ''
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
  formData.inspection_no = ''
  formData.batch_no = ''
  formData.sample_no = ''
  formData.sample_date = dayjs().format('YYYY-MM-DD')
  formData.inspector = ''
  formData.inspection_date = dayjs().format('YYYY-MM-DD')
  formData.result = '合格'
  formData.conclusion = ''
  formData.test_data = ''
  formData.standard_value = ''
  formData.lab_temperature = 23.0
  formData.lab_humidity = 60.0
  formData.status = '草稿'
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

const handleSubmitInspection = (row) => {
  ElMessageBox.confirm(
    '确定要提交该检验记录吗？提交后将进入审核流程。',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.status = '已提交'
    ElMessage.success('提交成功')
    fetchData()
  }).catch(() => {})
}

const handleApprove = (row) => {
  ElMessageBox.confirm(
    '确定要审核通过该检验记录吗？',
    '提示',
    {
      confirmButtonText: '通过',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(() => {
    row.status = '已审核'
    ElMessage.success('审核通过')
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
.inspections-container {
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
