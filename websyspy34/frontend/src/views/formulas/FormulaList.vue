<template>
  <div class="formula-list-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="关键词">
          <el-input v-model="queryParams.keyword" placeholder="搜索配方编码/名称" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="混凝土类型">
          <el-select v-model="queryParams.concrete_type" placeholder="请选择" clearable>
            <el-option label="普通混凝土" value="普通混凝土" />
            <el-option label="泵送混凝土" value="泵送混凝土" />
            <el-option label="水下混凝土" value="水下混凝土" />
            <el-option label="抗渗混凝土" value="抗渗混凝土" />
          </el-select>
        </el-form-item>
        <el-form-item label="强度等级">
          <el-select v-model="queryParams.strength_grade" placeholder="请选择" clearable>
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
          <el-select v-model="queryParams.status" placeholder="请选择" clearable>
            <el-option label="启用" value="active" />
            <el-option label="停用" value="inactive" />
            <el-option label="草稿" value="draft" />
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
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>配方列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增配方
          </el-button>
        </div>
      </template>

      <el-table :data="formulaList" v-loading="loading" stripe @row-click="handleRowClick" highlight-current-row>
        <el-table-column prop="formula_code" label="配方编码" min-width="120" />
        <el-table-column prop="formula_name" label="配方名称" min-width="150" />
        <el-table-column prop="concrete_type" label="混凝土类型" width="120" />
        <el-table-column prop="strength_grade" label="强度等级" width="100" />
        <el-table-column label="配合比(kg/m³)" min-width="300">
          <template #default="scope">
            <div class="ratio-info">
              <span>水泥: {{ scope.row.cement }}</span>
              <span>砂: {{ scope.row.sand }}</span>
              <span>石: {{ scope.row.gravel }}</span>
              <span>水: {{ scope.row.water }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="version" label="版本" width="80" />
        <el-table-column prop="is_standard" label="标准配方" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_standard ? 'success' : 'info'" size="small">
              {{ scope.row.is_standard ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" text @click.stop="viewDetail(scope.row.id)">查看</el-button>
            <el-button type="primary" text @click.stop="handleEdit(scope.row)">编辑</el-button>
            <el-button type="primary" text @click.stop="handleAdjust(scope.row)">调整</el-button>
            <el-button type="danger" text @click.stop="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="queryParams.skip"
        v-model:page-size="queryParams.limit"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="800px" destroy-on-close>
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="配方编码" prop="formula_code">
              <el-input v-model="formData.formula_code" placeholder="请输入配方编码" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="配方名称" prop="formula_name">
              <el-input v-model="formData.formula_name" placeholder="请输入配方名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="混凝土类型" prop="concrete_type">
              <el-select v-model="formData.concrete_type" placeholder="请选择" style="width: 100%;">
                <el-option label="普通混凝土" value="普通混凝土" />
                <el-option label="泵送混凝土" value="泵送混凝土" />
                <el-option label="水下混凝土" value="水下混凝土" />
                <el-option label="抗渗混凝土" value="抗渗混凝土" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="强度等级" prop="strength_grade">
              <el-select v-model="formData.strength_grade" placeholder="请选择" style="width: 100%;">
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
        <el-divider content-position="left">配合比参数 (kg/m³)</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="水泥">
              <el-input-number v-model="formData.cement" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="砂">
              <el-input-number v-model="formData.sand" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="石子">
              <el-input-number v-model="formData.gravel" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="水">
              <el-input-number v-model="formData.water" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="外加剂">
              <el-input-number v-model="formData.admixture" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="粉煤灰">
              <el-input-number v-model="formData.fly_ash" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="矿粉">
              <el-input-number v-model="formData.mineral_powder" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="水灰比">
              <el-input-number v-model="formData.water_cement_ratio" :min="0" :precision="3" :step="0.01" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="坍落度(mm)">
              <el-input-number v-model="formData.slump" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">其他参数</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="formData.status">
                <el-radio label="active">启用</el-radio>
                <el-radio label="inactive">停用</el-radio>
                <el-radio label="draft">草稿</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="标准配方">
              <el-switch v-model="formData.is_standard" active-text="是" inactive-text="否" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入配方描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="adjustDialogVisible" title="调整配方参数" width="700px" destroy-on-close>
      <el-alert title="调整将记录历史并增加版本号" type="warning" show-icon style="margin-bottom: 20px;" />
      <el-form :model="adjustForm" label-width="120px">
        <el-divider content-position="left">调整原因</el-divider>
        <el-form-item label="项目名称">
          <el-input v-model="adjustForm.project_name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="调整原因">
          <el-input v-model="adjustForm.adjustment_reason" type="textarea" :rows="2" placeholder="请输入调整原因" />
        </el-form-item>
        <el-form-item label="项目要求">
          <el-input v-model="adjustForm.project_requirements" type="textarea" :rows="2" placeholder="请输入项目要求" />
        </el-form-item>
        <el-divider content-position="left">参数调整</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="水泥">
              <div class="adjust-input">
                <span class="original-value">{{ currentFormula?.cement || 0 }}</span>
                <el-icon><ArrowRight /></el-icon>
                <el-input-number v-model="adjustForm.adjusted_cement" :min="0" :precision="2" />
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="砂">
              <div class="adjust-input">
                <span class="original-value">{{ currentFormula?.sand || 0 }}</span>
                <el-icon><ArrowRight /></el-icon>
                <el-input-number v-model="adjustForm.adjusted_sand" :min="0" :precision="2" />
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="石子">
              <div class="adjust-input">
                <span class="original-value">{{ currentFormula?.gravel || 0 }}</span>
                <el-icon><ArrowRight /></el-icon>
                <el-input-number v-model="adjustForm.adjusted_gravel" :min="0" :precision="2" />
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="水">
              <div class="adjust-input">
                <span class="original-value">{{ currentFormula?.water || 0 }}</span>
                <el-icon><ArrowRight /></el-icon>
                <el-input-number v-model="adjustForm.adjusted_water" :min="0" :precision="2" />
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="外加剂">
              <div class="adjust-input">
                <span class="original-value">{{ currentFormula?.admixture || 0 }}</span>
                <el-icon><ArrowRight /></el-icon>
                <el-input-number v-model="adjustForm.adjusted_admixture" :min="0" :precision="2" />
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="粉煤灰">
              <div class="adjust-input">
                <span class="original-value">{{ currentFormula?.fly_ash || 0 }}</span>
                <el-icon><ArrowRight /></el-icon>
                <el-input-number v-model="adjustForm.adjusted_fly_ash" :min="0" :precision="2" />
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitAdjust">确认调整</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { formulaApi } from '../api'

const router = useRouter()
const loading = ref(false)
const formulaList = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const adjustDialogVisible = ref(false)
const isEdit = ref(false)
const currentFormula = ref(null)
const formRef = ref(null)

const queryParams = reactive({
  keyword: '',
  concrete_type: '',
  strength_grade: '',
  status: '',
  skip: 1,
  limit: 20
})

const defaultFormData = {
  formula_code: '',
  formula_name: '',
  concrete_type: '',
  strength_grade: '',
  description: '',
  cement: 0,
  sand: 0,
  gravel: 0,
  water: 0,
  admixture: 0,
  fly_ash: 0,
  mineral_powder: 0,
  water_cement_ratio: null,
  slump: null,
  status: 'active',
  is_standard: true,
  version: 1
}

const formData = reactive({ ...defaultFormData })

const adjustForm = reactive({
  formula_id: null,
  project_name: '',
  adjustment_reason: '',
  project_requirements: '',
  adjusted_cement: null,
  adjusted_sand: null,
  adjusted_gravel: null,
  adjusted_water: null,
  adjusted_admixture: null,
  adjusted_fly_ash: null,
  adjusted_mineral_powder: null
})

const rules = {
  formula_code: [{ required: true, message: '请输入配方编码', trigger: 'blur' }],
  formula_name: [{ required: true, message: '请输入配方名称', trigger: 'blur' }],
  concrete_type: [{ required: true, message: '请选择混凝土类型', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑配方' : '新增配方')

const fetchFormulaList = async () => {
  loading.value = true
  try {
    const params = {
      skip: (queryParams.skip - 1) * queryParams.limit,
      limit: queryParams.limit
    }
    if (queryParams.keyword) params.keyword = queryParams.keyword
    if (queryParams.concrete_type) params.concrete_type = queryParams.concrete_type
    if (queryParams.strength_grade) params.strength_grade = queryParams.strength_grade
    if (queryParams.status) params.status = queryParams.status

    const res = await formulaApi.getList(params)
    formulaList.value = res
    total.value = res.length >= queryParams.limit ? (queryParams.skip + 1) * queryParams.limit : queryParams.skip * queryParams.limit + res.length
  } catch (error) {
    ElMessage.error('获取配方列表失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const types = {
    'active': 'success',
    'inactive': 'danger',
    'draft': 'info'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    'active': '启用',
    'inactive': '停用',
    'draft': '草稿'
  }
  return labels[status] || status
}

const handleSearch = () => {
  queryParams.skip = 1
  fetchFormulaList()
}

const handleReset = () => {
  queryParams.keyword = ''
  queryParams.concrete_type = ''
  queryParams.strength_grade = ''
  queryParams.status = ''
  queryParams.skip = 1
  fetchFormulaList()
}

const handleSizeChange = (val) => {
  queryParams.limit = val
  fetchFormulaList()
}

const handleCurrentChange = (val) => {
  queryParams.skip = val
  fetchFormulaList()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(formData, defaultFormData)
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该配方吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await formulaApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchFormulaList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleAdjust = (row) => {
  currentFormula.value = row
  adjustForm.formula_id = row.id
  adjustForm.project_name = ''
  adjustForm.adjustment_reason = ''
  adjustForm.project_requirements = ''
  adjustForm.adjusted_cement = row.cement
  adjustForm.adjusted_sand = row.sand
  adjustForm.adjusted_gravel = row.gravel
  adjustForm.adjusted_water = row.water
  adjustForm.adjusted_admixture = row.admixture
  adjustForm.adjusted_fly_ash = row.fly_ash
  adjustForm.adjusted_mineral_powder = row.mineral_powder
  adjustDialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await formulaApi.update(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await formulaApi.create(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchFormulaList()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const handleSubmitAdjust = async () => {
  try {
    await formulaApi.adjust(adjustForm.formula_id, adjustForm)
    ElMessage.success('调整成功，版本号已更新')
    adjustDialogVisible.value = false
    fetchFormulaList()
  } catch (error) {
    ElMessage.error('调整失败')
  }
}

const viewDetail = (id) => {
  router.push(`/formulas/${id}`)
}

const handleRowClick = (row) => {
  viewDetail(row.id)
}

onMounted(() => {
  fetchFormulaList()
})
</script>

<style scoped>
.formula-list-container {
  padding: 0;
}

.filter-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.table-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ratio-info {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  font-size: 12px;
  color: #606266;
}

.adjust-input {
  display: flex;
  align-items: center;
  gap: 8px;
}

.original-value {
  color: #909399;
  text-decoration: line-through;
}
</style>
