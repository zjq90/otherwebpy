<template>
  <div class="batches-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>生产批次</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增批次
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="批次号">
          <el-input
            v-model="searchForm.batch_no"
            placeholder="请输入批次号"
            clearable
          />
        </el-form-item>
        <el-form-item label="强度等级">
          <el-select v-model="searchForm.strength_grade" placeholder="请选择" clearable>
            <el-option label="C15" value="C15" />
            <el-option label="C20" value="C20" />
            <el-option label="C25" value="C25" />
            <el-option label="C30" value="C30" />
            <el-option label="C35" value="C35" />
            <el-option label="C40" value="C40" />
            <el-option label="C45" value="C45" />
            <el-option label="C50" value="C50" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待生产" value="待生产" />
            <el-option label="生产中" value="生产中" />
            <el-option label="已完成" value="已完成" />
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
        <el-table-column prop="batch_no" label="批次号" width="150" />
        <el-table-column prop="project_name" label="工程项目" min-width="180" show-overflow-tooltip />
        <el-table-column prop="construction_site" label="施工部位" width="120" />
        <el-table-column prop="strength_grade" label="强度等级" width="100" />
        <el-table-column prop="planned_volume" label="计划方量(m³)" width="120">
          <template #default="scope">
            {{ scope.row.planned_volume || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="actual_volume" label="实际方量(m³)" width="120">
          <template #default="scope">
            {{ scope.row.actual_volume || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="truck_no" label="运输车号" width="100" />
        <el-table-column prop="operator" label="操作员" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="dark">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link @click="handleViewRecords(scope.row)">
              生产记录
            </el-button>
            <el-button type="warning" link v-if="scope.row.status === '待生产'" @click="handleStartProduction(scope.row)">
              开始生产
            </el-button>
            <el-button type="success" link v-if="scope.row.status === '生产中'" @click="handleCompleteProduction(scope.row)">
              完成生产
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
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="批次号" prop="batch_no">
              <el-input v-model="formData.batch_no" placeholder="自动生成" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="强度等级" prop="strength_grade">
              <el-select v-model="formData.strength_grade" placeholder="请选择" style="width: 100%" :disabled="isView">
                <el-option label="C15" value="C15" />
                <el-option label="C20" value="C20" />
                <el-option label="C25" value="C25" />
                <el-option label="C30" value="C30" />
                <el-option label="C35" value="C35" />
                <el-option label="C40" value="C40" />
                <el-option label="C45" value="C45" />
                <el-option label="C50" value="C50" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="工程项目" prop="project_name">
          <el-input v-model="formData.project_name" placeholder="请输入工程项目名称" :disabled="isView" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="施工部位" prop="construction_site">
              <el-input v-model="formData.construction_site" placeholder="请输入施工部位" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划方量(m³)" prop="planned_volume">
              <el-input-number
                v-model="formData.planned_volume"
                :min="0"
                :precision="2"
                style="width: 100%"
                :disabled="isView"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="运输车号">
              <el-input v-model="formData.truck_no" placeholder="请输入运输车号" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="司机">
              <el-input v-model="formData.driver" placeholder="请输入司机姓名" :disabled="isView" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="操作员">
              <el-input v-model="formData.operator" placeholder="请输入操作员" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-tag :type="getStatusType(formData.status)" effect="dark">
                {{ formData.status || '待生产' }}
              </el-tag>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="实际方量(m³)" v-if="formData.status === '已完成'">
          <el-input-number
            v-model="formData.actual_volume"
            :min="0"
            :precision="2"
            style="width: 100%"
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
import { useRouter } from 'vue-router'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isView = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  batch_no: '',
  strength_grade: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  id: null,
  batch_no: '',
  mix_design_id: null,
  project_name: '',
  construction_site: '',
  strength_grade: '',
  planned_volume: 0,
  actual_volume: null,
  truck_no: '',
  driver: '',
  operator: '',
  status: '待生产'
})

const rules = {
  project_name: [{ required: true, message: '请输入工程项目名称', trigger: 'blur' }],
  construction_site: [{ required: true, message: '请输入施工部位', trigger: 'blur' }],
  strength_grade: [{ required: true, message: '请选择强度等级', trigger: 'change' }],
  planned_volume: [{ required: true, message: '请输入计划方量', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看生产批次'
  return formData.id ? '编辑生产批次' : '新增生产批次'
})

const getStatusType = (status) => {
  const typeMap = {
    '待生产': 'info',
    '生产中': 'warning',
    '已完成': 'success'
  }
  return typeMap[status] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        batch_no: 'PB20241201001',
        mix_design_id: 1,
        project_name: '市民中心建设项目',
        construction_site: '主体结构',
        strength_grade: 'C30',
        planned_volume: 200.0,
        actual_volume: 205.5,
        truck_no: '皖A12345',
        driver: '张三',
        operator: '操作员甲',
        status: '已完成'
      },
      {
        id: 2,
        batch_no: 'PB20241201002',
        mix_design_id: 2,
        project_name: '地铁一号线工程',
        construction_site: '基础工程',
        strength_grade: 'C35',
        planned_volume: 350.0,
        actual_volume: null,
        truck_no: '皖A23456',
        driver: '李四',
        operator: '操作员乙',
        status: '生产中'
      },
      {
        id: 3,
        batch_no: 'PB20241201003',
        mix_design_id: 3,
        project_name: '商业综合体项目',
        construction_site: '地下室',
        strength_grade: 'C40',
        planned_volume: 500.0,
        actual_volume: null,
        truck_no: '皖A34567',
        driver: '王五',
        operator: '操作员丙',
        status: '待生产'
      }
    ]
    pagination.total = 3
  } catch (error) {
    console.error('获取生产批次数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.batch_no = ''
  searchForm.strength_grade = ''
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
  formData.batch_no = ''
  formData.project_name = ''
  formData.construction_site = ''
  formData.strength_grade = ''
  formData.planned_volume = 0
  formData.actual_volume = null
  formData.truck_no = ''
  formData.driver = ''
  formData.operator = ''
  formData.status = '待生产'
  formRef.value?.resetFields()
}

const handleAdd = () => {
  isView.value = false
  resetForm()
  dialogVisible.value = true
}

const handleView = (row) => {
  isView.value = true
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleViewRecords = (row) => {
  router.push(`/production/records?batch_id=${row.id}`)
}

const handleStartProduction = (row) => {
  ElMessageBox.confirm(
    `确定要开始生产批次"${row.batch_no}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.status = '生产中'
    ElMessage.success('已开始生产')
    fetchData()
  }).catch(() => {})
}

const handleCompleteProduction = (row) => {
  ElMessageBox.confirm(
    `确定要完成生产批次"${row.batch_no}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(() => {
    row.status = '已完成'
    row.actual_volume = row.planned_volume * 1.02
    ElMessage.success('生产已完成')
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
.batches-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-form {
  margin-bottom: 20px;
}
</style>
