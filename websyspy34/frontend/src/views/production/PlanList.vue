<template>
  <div class="plan-list-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="关键词">
          <el-input v-model="queryParams.keyword" placeholder="搜索计划编码/名称/项目" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
            <el-option label="已延期" value="delayed" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="queryParams.priority" placeholder="请选择" clearable>
            <el-option label="1级(最低)" :value="1" />
            <el-option label="2级" :value="2" />
            <el-option label="3级" :value="3" />
            <el-option label="4级" :value="4" />
            <el-option label="5级(最高)" :value="5" />
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
          <span>生产计划列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增计划
          </el-button>
        </div>
      </template>

      <el-table :data="planList" v-loading="loading" stripe @row-click="handleRowClick" highlight-current-row>
        <el-table-column prop="plan_code" label="计划编码" min-width="120" />
        <el-table-column prop="plan_name" label="计划名称" min-width="150" />
        <el-table-column prop="project_name" label="项目名称" min-width="150" />
        <el-table-column prop="project_location" label="项目地址" min-width="150" show-overflow-tooltip />
        <el-table-column prop="total_volume" label="总方量(m³)" width="120">
          <template #default="scope">
            <span>{{ scope.row.total_volume || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="completed_volume" label="已完成(m³)" width="120">
          <template #default="scope">
            <div>
              <span>{{ scope.row.completed_volume || 0 }}</span>
              <el-progress 
                :percentage="getProgress(scope.row)" 
                :stroke-width="8" 
                style="width: 100px; margin-top: 4px;"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)" size="small">
              {{ scope.row.priority }}级
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
        <el-table-column prop="planned_start_date" label="计划开始" width="160">
          <template #default="scope">
            {{ formatTime(scope.row.planned_start_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="planned_end_date" label="计划结束" width="160">
          <template #default="scope">
            {{ formatTime(scope.row.planned_end_date) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" text @click.stop="viewDetail(scope.row.id)">详情</el-button>
            <el-button type="primary" text @click.stop="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" text @click.stop="handleDelete(scope.row)">取消</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" destroy-on-close>
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划编码" prop="plan_code">
              <el-input v-model="formData.plan_code" placeholder="自动生成或手动输入" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划名称" prop="plan_name">
              <el-input v-model="formData.plan_name" placeholder="请输入计划名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">项目信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="项目名称">
              <el-input v-model="formData.project_name" placeholder="请输入项目名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="项目地址">
              <el-input v-model="formData.project_location" placeholder="请输入项目地址" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="联系人">
              <el-input v-model="formData.contact_person" placeholder="请输入联系人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话">
              <el-input v-model="formData.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider content-position="left">计划信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划开始时间">
              <el-date-picker
                v-model="formData.planned_start_date"
                type="datetime"
                placeholder="选择开始时间"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划结束时间">
              <el-date-picker
                v-model="formData.planned_end_date"
                type="datetime"
                placeholder="选择结束时间"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="总方量(m³)" prop="total_volume">
              <el-input-number v-model="formData.total_volume" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="优先级" prop="priority">
              <el-select v-model="formData.priority" style="width: 100%;">
                <el-option label="1级(最低)" :value="1" />
                <el-option label="2级" :value="2" />
                <el-option label="3级" :value="3" />
                <el-option label="4级" :value="4" />
                <el-option label="5级(最高)" :value="5" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="formData.status" style="width: 100%;">
                <el-option label="待处理" value="pending" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
                <el-option label="已延期" value="delayed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="formData.remarks" type="textarea" :rows="3" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productionApi } from '../../api'

const router = useRouter()
const loading = ref(false)
const planList = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const queryParams = reactive({
  keyword: '',
  status: '',
  priority: null,
  skip: 1,
  limit: 20
})

const defaultFormData = {
  plan_code: '',
  plan_name: '',
  project_name: '',
  project_location: '',
  contact_person: '',
  contact_phone: '',
  planned_start_date: null,
  planned_end_date: null,
  total_volume: 0,
  priority: 3,
  status: 'pending',
  remarks: ''
}

const formData = reactive({ ...defaultFormData })

const rules = {
  plan_code: [{ required: true, message: '请输入计划编码', trigger: 'blur' }],
  plan_name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  total_volume: [{ required: true, message: '请输入总方量', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑生产计划' : '新增生产计划')

const fetchPlanList = async () => {
  loading.value = true
  try {
    const params = {
      skip: (queryParams.skip - 1) * queryParams.limit,
      limit: queryParams.limit
    }
    if (queryParams.keyword) params.keyword = queryParams.keyword
    if (queryParams.status) params.status = queryParams.status
    if (queryParams.priority) params.priority = queryParams.priority

    const res = await productionApi.getPlans(params)
    planList.value = res
    total.value = res.length >= queryParams.limit ? (queryParams.skip + 1) * queryParams.limit : queryParams.skip * queryParams.limit + res.length
  } catch (error) {
    ElMessage.error('获取计划列表失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getProgress = (row) => {
  if (!row.total_volume || row.total_volume === 0) return 0
  return Math.round((row.completed_volume || 0) / row.total_volume * 100)
}

const getPriorityType = (priority) => {
  const types = {
    1: 'info',
    2: 'info',
    3: 'warning',
    4: 'danger',
    5: 'danger'
  }
  return types[priority] || 'info'
}

const getStatusType = (status) => {
  const types = {
    'pending': 'info',
    'in_progress': 'primary',
    'completed': 'success',
    'cancelled': 'danger',
    'delayed': 'warning'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'cancelled': '已取消',
    'delayed': '已延期'
  }
  return labels[status] || status
}

const handleSearch = () => {
  queryParams.skip = 1
  fetchPlanList()
}

const handleReset = () => {
  queryParams.keyword = ''
  queryParams.status = ''
  queryParams.priority = null
  queryParams.skip = 1
  fetchPlanList()
}

const handleSizeChange = (val) => {
  queryParams.limit = val
  fetchPlanList()
}

const handleCurrentChange = (val) => {
  queryParams.skip = val
  fetchPlanList()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(formData, defaultFormData)
  formData.plan_code = 'PL' + Date.now().toString().slice(-8)
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消该生产计划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await productionApi.deletePlan(row.id)
    ElMessage.success('取消成功')
    fetchPlanList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('取消失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await productionApi.updatePlan(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await productionApi.createPlan(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchPlanList()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const viewDetail = (id) => {
  router.push(`/plans/${id}`)
}

const handleRowClick = (row) => {
  viewDetail(row.id)
}

onMounted(() => {
  fetchPlanList()
})
</script>

<style scoped>
.plan-list-container {
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
</style>
