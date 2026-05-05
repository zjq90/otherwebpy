<template>
  <div class="mix-designs-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>配比设计</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增配比
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="配合比编号">
          <el-input
            v-model="searchForm.design_no"
            placeholder="请输入配合比编号"
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
            <el-option label="草稿" value="草稿" />
            <el-option label="已审批" value="已审批" />
            <el-option label="已启用" value="已启用" />
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
        <el-table-column prop="design_no" label="配合比编号" width="150" />
        <el-table-column prop="mix_name" label="配合比名称" min-width="200" />
        <el-table-column prop="strength_grade" label="强度等级" width="100">
          <template #default="scope">
            <el-tag type="primary">{{ scope.row.strength_grade }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="design_age" label="设计龄期(天)" width="110" />
        <el-table-column prop="slump" label="坍落度(mm)" width="120" />
        <el-table-column prop="cement_content" label="水泥用量(kg/m³)" width="130" />
        <el-table-column prop="water_cement_ratio" label="水胶比" width="100">
          <template #default="scope">
            <span class="highlight-text">{{ scope.row.water_cement_ratio }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sand_ratio" label="砂率(%)" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="是否启用" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'" effect="dark">
              {{ scope.row.is_active ? '启用中' : '已停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link v-if="!scope.row.is_active" @click="handleEnable(scope.row)">
              启用
            </el-button>
            <el-button type="danger" link v-if="scope.row.is_active" @click="handleDisable(scope.row)">
              停用
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
      width="900px"
      :close-on-click-modal="false"
    >
      <el-descriptions :column="4" border v-if="isView">
        <el-descriptions-item label="配合比编号">{{ formData.design_no }}</el-descriptions-item>
        <el-descriptions-item label="配合比名称">{{ formData.mix_name }}</el-descriptions-item>
        <el-descriptions-item label="强度等级">{{ formData.strength_grade }}</el-descriptions-item>
        <el-descriptions-item label="设计龄期">{{ formData.design_age }}天</el-descriptions-item>
        <el-descriptions-item label="坍落度">{{ formData.slump }}mm</el-descriptions-item>
        <el-descriptions-item label="设计人">{{ formData.designed_by }}</el-descriptions-item>
        <el-descriptions-item label="设计日期">{{ formData.design_date }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ formData.status }}</el-descriptions-item>
      </el-descriptions>
      
      <el-divider v-if="isView">配合比详情</el-divider>
      
      <el-descriptions :column="3" border v-if="isView">
        <el-descriptions-item label="水泥用量">{{ formData.cement_content }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="砂子用量">{{ formData.sand_content }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="石子用量">{{ formData.stone_content }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="用水量">{{ formData.water_content }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="外加剂用量">{{ formData.admixture_content }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="粉煤灰用量">{{ formData.fly_ash_content }} kg/m³</el-descriptions-item>
        <el-descriptions-item label="水胶比">{{ formData.water_cement_ratio }}</el-descriptions-item>
        <el-descriptions-item label="砂率">{{ formData.sand_ratio }}%</el-descriptions-item>
        <el-descriptions-item label="是否启用">{{ formData.is_active ? '是' : '否' }}</el-descriptions-item>
      </el-descriptions>
      
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        v-if="!isView"
      >
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="配合比编号" prop="design_no">
              <el-input v-model="formData.design_no" placeholder="自动生成" disabled />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="配合比名称" prop="mix_name">
              <el-input v-model="formData.mix_name" placeholder="请输入配合比名称" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="强度等级" prop="strength_grade">
              <el-select v-model="formData.strength_grade" placeholder="请选择" style="width: 100%">
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
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="设计龄期(天)" prop="design_age">
              <el-input-number v-model="formData.design_age" :min="3" :max="90" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="坍落度(mm)" prop="slump">
              <el-input-number v-model="formData.slump" :min="0" :max="250" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="设计人" prop="designed_by">
              <el-input v-model="formData.designed_by" placeholder="请输入设计人" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>配合比参数</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="水泥用量(kg/m³)" prop="cement_content">
              <el-input-number v-model="formData.cement_content" :min="100" :max="600" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="砂子用量(kg/m³)" prop="sand_content">
              <el-input-number v-model="formData.sand_content" :min="400" :max="1000" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="石子用量(kg/m³)" prop="stone_content">
              <el-input-number v-model="formData.stone_content" :min="800" :max="1500" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="用水量(kg/m³)" prop="water_content">
              <el-input-number v-model="formData.water_content" :min="100" :max="250" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="外加剂用量(kg/m³)">
              <el-input-number v-model="formData.admixture_content" :min="0" :max="30" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="粉煤灰用量(kg/m³)">
              <el-input-number v-model="formData.fly_ash_content" :min="0" :max="200" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="水胶比" prop="water_cement_ratio">
              <el-input-number v-model="formData.water_cement_ratio" :min="0.2" :max="0.8" :precision="3" :step="0.01" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="砂率(%)" prop="sand_ratio">
              <el-input-number v-model="formData.sand_ratio" :min="25" :max="55" :precision="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择" style="width: 100%">
                <el-option label="草稿" value="草稿" />
                <el-option label="已审批" value="已审批" />
                <el-option label="已启用" value="已启用" />
              </el-select>
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

const searchForm = reactive({
  design_no: '',
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
  design_no: '',
  mix_name: '',
  strength_grade: 'C30',
  design_age: 28,
  slump: 150.0,
  cement_content: 360.0,
  sand_content: 750.0,
  stone_content: 1100.0,
  water_content: 180.0,
  admixture_content: 5.4,
  fly_ash_content: 70.0,
  water_cement_ratio: 0.5,
  sand_ratio: 40.0,
  designed_by: '',
  design_date: dayjs().format('YYYY-MM-DD'),
  status: '草稿',
  is_active: false
})

const rules = {
  mix_name: [{ required: true, message: '请输入配合比名称', trigger: 'blur' }],
  strength_grade: [{ required: true, message: '请选择强度等级', trigger: 'change' }],
  design_age: [{ required: true, message: '请输入设计龄期', trigger: 'blur' }],
  slump: [{ required: true, message: '请输入坍落度', trigger: 'blur' }],
  cement_content: [{ required: true, message: '请输入水泥用量', trigger: 'blur' }],
  sand_content: [{ required: true, message: '请输入砂子用量', trigger: 'blur' }],
  stone_content: [{ required: true, message: '请输入石子用量', trigger: 'blur' }],
  water_content: [{ required: true, message: '请输入用水量', trigger: 'blur' }],
  water_cement_ratio: [{ required: true, message: '请输入水胶比', trigger: 'blur' }],
  sand_ratio: [{ required: true, message: '请输入砂率', trigger: 'blur' }],
  designed_by: [{ required: true, message: '请输入设计人', trigger: 'blur' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看配合比'
  return formData.id ? '编辑配合比' : '新增配合比'
})

const getStatusType = (status) => {
  const typeMap = {
    '草稿': 'info',
    '已审批': 'warning',
    '已启用': 'success'
  }
  return typeMap[status] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        design_no: 'MDC302024001',
        mix_name: 'C30普通混凝土配合比',
        strength_grade: 'C30',
        design_age: 28,
        slump: 150.0,
        cement_content: 360.0,
        sand_content: 750.0,
        stone_content: 1100.0,
        water_content: 180.0,
        admixture_content: 5.4,
        fly_ash_content: 70.0,
        water_cement_ratio: 0.5,
        sand_ratio: 40.0,
        designed_by: '设计员A',
        design_date: '2024-01-15',
        status: '已启用',
        is_active: true
      },
      {
        id: 2,
        design_no: 'MDC352024002',
        mix_name: 'C35高强混凝土配合比',
        strength_grade: 'C35',
        design_age: 28,
        slump: 180.0,
        cement_content: 400.0,
        sand_content: 720.0,
        stone_content: 1080.0,
        water_content: 170.0,
        admixture_content: 6.0,
        fly_ash_content: 80.0,
        water_cement_ratio: 0.425,
        sand_ratio: 38.0,
        designed_by: '设计员B',
        design_date: '2024-02-20',
        status: '已审批',
        is_active: false
      },
      {
        id: 3,
        design_no: 'MDC252024003',
        mix_name: 'C25泵送混凝土配合比',
        strength_grade: 'C25',
        design_age: 28,
        slump: 160.0,
        cement_content: 320.0,
        sand_content: 780.0,
        stone_content: 1050.0,
        water_content: 185.0,
        admixture_content: 4.8,
        fly_ash_content: 60.0,
        water_cement_ratio: 0.578,
        sand_ratio: 42.0,
        designed_by: '设计员C',
        design_date: '2024-03-10',
        status: '草稿',
        is_active: false
      }
    ]
    pagination.total = 3
  } catch (error) {
    console.error('获取配比数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.design_no = ''
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
  formData.design_no = ''
  formData.mix_name = ''
  formData.strength_grade = 'C30'
  formData.design_age = 28
  formData.slump = 150.0
  formData.cement_content = 360.0
  formData.sand_content = 750.0
  formData.stone_content = 1100.0
  formData.water_content = 180.0
  formData.admixture_content = 5.4
  formData.fly_ash_content = 70.0
  formData.water_cement_ratio = 0.5
  formData.sand_ratio = 40.0
  formData.designed_by = ''
  formData.design_date = dayjs().format('YYYY-MM-DD')
  formData.status = '草稿'
  formData.is_active = false
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

const handleEnable = (row) => {
  ElMessageBox.confirm(
    `确定要启用配合比"${row.mix_name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.is_active = true
    row.status = '已启用'
    ElMessage.success('启用成功')
    fetchData()
  }).catch(() => {})
}

const handleDisable = (row) => {
  ElMessageBox.confirm(
    `确定要停用配合比"${row.mix_name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.is_active = false
    ElMessage.success('停用成功')
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
.mix-designs-container {
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

.highlight-text {
  color: #409EFF;
  font-weight: bold;
}
</style>
