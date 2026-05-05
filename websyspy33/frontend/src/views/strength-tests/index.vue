<template>
  <div class="strength-tests-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>强度检测</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增检测
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="检测编号">
          <el-input
            v-model="searchForm.test_no"
            placeholder="请输入检测编号"
            clearable
          />
        </el-form-item>
        <el-form-item label="试块编号">
          <el-input
            v-model="searchForm.block_no"
            placeholder="请输入试块编号"
            clearable
          />
        </el-form-item>
        <el-form-item label="检测结果">
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
        <el-table-column prop="test_no" label="检测编号" width="140" />
        <el-table-column prop="block_no" label="试块编号" width="130" />
        <el-table-column prop="test_date" label="检测日期" width="110" />
        <el-table-column prop="actual_age" label="实际龄期(天)" width="110" />
        <el-table-column prop="tester" label="试验员" width="90" />
        <el-table-column prop="lab_temperature" label="室温(℃)" width="100" />
        <el-table-column prop="lab_humidity" label="湿度(%)" width="90" />
        <el-table-column prop="load_1" label="荷载1(kN)" width="100" />
        <el-table-column prop="load_2" label="荷载2(kN)" width="100" />
        <el-table-column prop="load_3" label="荷载3(kN)" width="100" />
        <el-table-column prop="avg_strength" label="平均强度(MPa)" width="130">
          <template #default="scope">
            <span :class="getStrengthClass(scope.row)">
              {{ scope.row.avg_strength }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="strength_ratio" label="强度比(%)" width="110">
          <template #default="scope">
            <el-tag :type="scope.row.strength_ratio >= 100 ? 'success' : 'danger'" size="small">
              {{ scope.row.strength_ratio }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="result" label="结果" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_qualified ? 'success' : 'danger'" effect="dark">
              {{ scope.row.result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
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
            <el-button type="warning" link v-if="scope.row.status === '草稿'" @click="handleSubmitTest(scope.row)">
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
      <el-descriptions :column="3" border v-if="isView">
        <el-descriptions-item label="检测编号">{{ formData.test_no }}</el-descriptions-item>
        <el-descriptions-item label="试块编号">{{ formData.block_no }}</el-descriptions-item>
        <el-descriptions-item label="试验员">{{ formData.tester }}</el-descriptions-item>
        <el-descriptions-item label="检测日期">{{ formData.test_date }}</el-descriptions-item>
        <el-descriptions-item label="实际龄期">{{ formData.actual_age }}天</el-descriptions-item>
        <el-descriptions-item label="室温">{{ formData.lab_temperature }}℃</el-descriptions-item>
        <el-descriptions-item label="设计强度">{{ formData.design_strength }}MPa</el-descriptions-item>
        <el-descriptions-item label="平均强度">{{ formData.avg_strength }}MPa</el-descriptions-item>
        <el-descriptions-item label="强度比">{{ formData.strength_ratio }}%</el-descriptions-item>
      </el-descriptions>
      
      <el-divider v-if="isView">检测数据详情</el-divider>
      
      <el-table :data="testDetails" style="width: 100%" v-if="isView">
        <el-table-column label="试块序号" prop="index" width="100" align="center" />
        <el-table-column label="破坏荷载(kN)" prop="load" width="120" />
        <el-table-column label="受压面积(mm²)" width="130">
          <template #default>
            22500 (150x150)
          </template>
        </el-table-column>
        <el-table-column label="抗压强度(MPa)" prop="strength" width="130" />
        <el-table-column label="与平均值偏差(%)" prop="deviation" width="150">
          <template #default="scope">
            <el-tag :type="Math.abs(scope.row.deviation) > 15 ? 'danger' : 'success'" size="small">
              {{ scope.row.deviation > 0 ? '+' : '' }}{{ scope.row.deviation }}%
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      
      <el-divider v-if="isView">检测结论</el-divider>
      
      <el-card v-if="isView">
        <div>
          <strong>检测结论：</strong>
          <span :style="{ color: formData.is_qualified ? '#67C23A' : '#F56C6C', fontWeight: 'bold' }">
            {{ formData.conclusion }}
          </span>
        </div>
      </el-card>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        v-if="!isView"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="检测编号">
              <el-input v-model="formData.test_no" placeholder="自动生成" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联试块" prop="block_id">
              <el-select v-model="formData.block_id" placeholder="请选择试块" style="width: 100%">
                <el-option v-for="block in testBlocks" :key="block.id" :label="block.block_no" :value="block.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="检测日期" prop="test_date">
              <el-date-picker
                v-model="formData.test_date"
                type="date"
                placeholder="请选择检测日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="实际龄期(天)" prop="actual_age">
              <el-input-number v-model="formData.actual_age" :min="1" :max="365" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="试验员" prop="tester">
              <el-input v-model="formData.tester" placeholder="请输入试验员" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实验室温度(℃)">
              <el-input-number v-model="formData.lab_temperature" :min="0" :max="40" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="实验室湿度(%)">
              <el-input-number v-model="formData.lab_humidity" :min="0" :max="100" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>荷载数据</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="试块1荷载(kN)" prop="load_1">
              <el-input-number v-model="formData.load_1" :min="0" :precision="1" style="width: 100%" @change="calculateStrength" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="试块2荷载(kN)" prop="load_2">
              <el-input-number v-model="formData.load_2" :min="0" :precision="1" style="width: 100%" @change="calculateStrength" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="试块3荷载(kN)" prop="load_3">
              <el-input-number v-model="formData.load_3" :min="0" :precision="1" style="width: 100%" @change="calculateStrength" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>强度计算结果</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="设计强度(MPa)">
              <el-input-number v-model="formData.design_strength" :min="10" :max="100" :precision="1" style="width: 100%" @change="calculateStrength" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平均强度(MPa)">
              <el-input v-model="formData.avg_strength" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="强度比(%)">
              <el-input v-model="formData.strength_ratio" disabled />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="检测结果">
              <el-radio-group v-model="formData.result">
                <el-radio value="合格">合格</el-radio>
                <el-radio value="不合格">不合格</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="检测结论">
          <el-input
            v-model="formData.conclusion"
            type="textarea"
            :rows="2"
            placeholder="请输入检测结论"
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
const testBlocks = ref([])
const testDetails = ref([])

const searchForm = reactive({
  test_no: '',
  block_no: '',
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
  test_no: '',
  block_id: null,
  block_no: '',
  test_date: dayjs().format('YYYY-MM-DD'),
  actual_age: 28,
  tester: '',
  lab_temperature: 23.0,
  lab_humidity: 60.0,
  load_1: 0,
  load_2: 0,
  load_3: 0,
  strength_1: 0,
  strength_2: 0,
  strength_3: 0,
  avg_strength: 0,
  strength_deviation: 0,
  design_strength: 30.0,
  strength_ratio: 0,
  result: '合格',
  is_qualified: true,
  conclusion: '',
  status: '草稿'
})

const rules = {
  block_id: [{ required: true, message: '请选择试块', trigger: 'change' }],
  test_date: [{ required: true, message: '请选择检测日期', trigger: 'change' }],
  actual_age: [{ required: true, message: '请输入实际龄期', trigger: 'blur' }],
  tester: [{ required: true, message: '请输入试验员', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看强度检测'
  return formData.id ? '编辑强度检测' : '新增强度检测'
})

const getStrengthClass = (row) => {
  if (!row.is_qualified) return 'text-red font-bold'
  return 'text-green font-bold'
}

const getStatusType = (status) => {
  const typeMap = {
    '草稿': 'info',
    '已提交': 'warning',
    '已审核': 'success'
  }
  return typeMap[status] || 'info'
}

const calculateStrength = () => {
  if (formData.load_1 > 0 && formData.load_2 > 0 && formData.load_3 > 0) {
    formData.strength_1 = round(formData.load_1 / 22.5, 1)
    formData.strength_2 = round(formData.load_2 / 22.5, 1)
    formData.strength_3 = round(formData.load_3 / 22.5, 1)
    
    formData.avg_strength = round((formData.strength_1 + formData.strength_2 + formData.strength_3) / 3, 1)
    
    if (formData.design_strength > 0) {
      formData.strength_ratio = round(formData.avg_strength / formData.design_strength * 100, 1)
      formData.is_qualified = formData.strength_ratio >= 100
      formData.result = formData.is_qualified ? '合格' : '不合格'
      
      if (formData.is_qualified) {
        formData.conclusion = `该组试块合格，强度代表值为${formData.avg_strength}MPa，达到设计强度的${formData.strength_ratio}%`
      } else {
        formData.conclusion = `该组试块不合格，强度代表值为${formData.avg_strength}MPa，仅达到设计强度的${formData.strength_ratio}%`
      }
    }
  }
}

const round = (num, precision) => {
  return Number(num.toFixed(precision))
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        test_no: 'ST20241201001',
        block_id: 1,
        block_no: 'TB20241201001',
        test_date: '2024-12-29',
        actual_age: 28,
        tester: '试验员甲',
        lab_temperature: 23.0,
        lab_humidity: 60.0,
        load_1: 787.5,
        load_2: 810.0,
        load_3: 765.0,
        strength_1: 35.0,
        strength_2: 36.0,
        strength_3: 34.0,
        avg_strength: 35.0,
        strength_deviation: 2.86,
        design_strength: 30.0,
        strength_ratio: 116.7,
        result: '合格',
        is_qualified: true,
        conclusion: '该组试块合格，强度代表值为35.0MPa，达到设计强度的116.7%',
        status: '已审核'
      },
      {
        id: 2,
        test_no: 'ST20241201002',
        block_id: 2,
        block_no: 'TB20241201002',
        test_date: '2024-12-08',
        actual_age: 7,
        tester: '试验员乙',
        lab_temperature: 22.5,
        lab_humidity: 58.0,
        load_1: 562.5,
        load_2: 540.0,
        load_3: 517.5,
        strength_1: 25.0,
        strength_2: 24.0,
        strength_3: 23.0,
        avg_strength: 24.0,
        strength_deviation: 4.17,
        design_strength: 30.0,
        strength_ratio: 80.0,
        result: '不合格',
        is_qualified: false,
        conclusion: '该组试块不合格，强度代表值为24.0MPa，仅达到设计强度的80.0%',
        status: '已提交'
      }
    ]
    pagination.total = 2
    
    testBlocks.value = [
      { id: 1, block_no: 'TB20241201001' },
      { id: 2, block_no: 'TB20241201002' },
      { id: 3, block_no: 'TB20241201003' }
    ]
  } catch (error) {
    console.error('获取强度检测数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.test_no = ''
  searchForm.block_no = ''
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
  formData.test_no = ''
  formData.block_id = null
  formData.block_no = ''
  formData.test_date = dayjs().format('YYYY-MM-DD')
  formData.actual_age = 28
  formData.tester = ''
  formData.lab_temperature = 23.0
  formData.lab_humidity = 60.0
  formData.load_1 = 0
  formData.load_2 = 0
  formData.load_3 = 0
  formData.strength_1 = 0
  formData.strength_2 = 0
  formData.strength_3 = 0
  formData.avg_strength = 0
  formData.strength_deviation = 0
  formData.design_strength = 30.0
  formData.strength_ratio = 0
  formData.result = '合格'
  formData.is_qualified = true
  formData.conclusion = ''
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
  
  testDetails.value = [
    { index: 1, load: row.load_1, strength: row.strength_1, deviation: round((row.strength_1 - row.avg_strength) / row.avg_strength * 100, 2) },
    { index: 2, load: row.load_2, strength: row.strength_2, deviation: round((row.strength_2 - row.avg_strength) / row.avg_strength * 100, 2) },
    { index: 3, load: row.load_3, strength: row.strength_3, deviation: round((row.strength_3 - row.avg_strength) / row.avg_strength * 100, 2) }
  ]
  
  dialogVisible.value = true
}

const handleSubmitTest = (row) => {
  ElMessageBox.confirm(
    '确定要提交该强度检测记录吗？提交后将进入审核流程。',
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
    '确定要审核通过该强度检测记录吗？',
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
.strength-tests-container {
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

.text-red {
  color: #F56C6C;
  font-weight: bold;
}

.text-green {
  color: #67C23A;
  font-weight: bold;
}
</style>
