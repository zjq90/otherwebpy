<template>
  <div class="resource-list-container">
    <el-card class="filter-card">
      <el-form :inline="true" :model="queryParams">
        <el-form-item label="关键词">
          <el-input v-model="queryParams.keyword" placeholder="搜索资源编码/名称/车牌号" clearable @keyup.enter="handleSearch" />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="queryParams.resource_type" placeholder="请选择" clearable>
            <el-option label="搅拌车" value="mixer_truck" />
            <el-option label="铲车" value="forklift" />
            <el-option label="泵车" value="pump" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="请选择" clearable>
            <el-option label="可用" value="available" />
            <el-option label="使用中" value="in_use" />
            <el-option label="维护中" value="maintenance" />
            <el-option label="不可用" value="unavailable" />
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
          <span>资源列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon> 新增资源
          </el-button>
        </div>
      </template>

      <el-table :data="resourceList" v-loading="loading" stripe>
        <el-table-column prop="resource_code" label="资源编码" min-width="120" />
        <el-table-column prop="resource_name" label="资源名称" min-width="150" />
        <el-table-column prop="resource_type" label="资源类型" width="100">
          <template #default="scope">
            <el-tag :type="getTypeTag(scope.row.resource_type)" size="small">
              {{ getTypeLabel(scope.row.resource_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="型号" min-width="120" />
        <el-table-column prop="capacity" label="容量" width="100">
          <template #default="scope">
            {{ scope.row.capacity || '-' }} {{ scope.row.capacity_unit || '' }}
          </template>
        </el-table-column>
        <el-table-column prop="license_plate" label="车牌号" width="120" />
        <el-table-column prop="manufacture_year" label="制造年份" width="100" />
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
            <el-button type="primary" text @click="handleEdit(scope.row)">编辑</el-button>
            <el-button 
              v-if="scope.row.status === 'available'" 
              type="success" 
              text 
              @click="handleAllocate(scope.row)"
            >分配</el-button>
            <el-button 
              v-if="scope.row.status === 'in_use'" 
              type="warning" 
              text 
              @click="handleRelease(scope.row)"
            >释放</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" destroy-on-close>
      <el-form :model="formData" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="资源编码" prop="resource_code">
              <el-input v-model="formData.resource_code" placeholder="请输入资源编码" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资源名称" prop="resource_name">
              <el-input v-model="formData.resource_name" placeholder="请输入资源名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="资源类型" prop="resource_type">
              <el-select v-model="formData.resource_type" placeholder="请选择" style="width: 100%;">
                <el-option label="搅拌车" value="mixer_truck" />
                <el-option label="铲车" value="forklift" />
                <el-option label="泵车" value="pump" />
                <el-option label="其他" value="other" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="请选择" style="width: 100%;">
                <el-option label="可用" value="available" />
                <el-option label="使用中" value="in_use" />
                <el-option label="维护中" value="maintenance" />
                <el-option label="不可用" value="unavailable" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="formData.model" placeholder="请输入型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车牌号">
              <el-input v-model="formData.license_plate" placeholder="请输入车牌号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="容量">
              <el-input-number v-model="formData.capacity" :min="0" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="容量单位">
              <el-input v-model="formData.capacity_unit" placeholder="如: m³, 吨" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="制造年份">
              <el-input-number v-model="formData.manufacture_year" :min="2000" :max="2030" style="width: 100%;" />
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

    <el-dialog v-model="allocateDialogVisible" title="分配资源" width="500px" destroy-on-close>
      <el-form :model="allocateForm" label-width="100px">
        <el-form-item label="资源名称">
          <el-input :value="currentResource?.resource_name" disabled />
        </el-form-item>
        <el-form-item label="分配给计划">
          <el-select v-model="allocateForm.plan_id" placeholder="选择生产计划（可选）" clearable style="width: 100%;">
            <el-option v-for="plan in planList" :key="plan.id" :label="plan.plan_name" :value="plan.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分配给任务">
          <el-select v-model="allocateForm.order_id" placeholder="选择生产任务（可选）" clearable style="width: 100%;">
            <el-option v-for="order in orderList" :key="order.id" :label="order.order_code" :value="order.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="分配原因">
          <el-input v-model="allocateForm.allocation_reason" type="textarea" :rows="2" placeholder="请输入分配原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="allocateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitAllocate">确认分配</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productionApi } from '../../api'

const loading = ref(false)
const resourceList = ref([])
const planList = ref([])
const orderList = ref([])
const total = ref(0)
const dialogVisible = ref(false)
const allocateDialogVisible = ref(false)
const isEdit = ref(false)
const currentResource = ref(null)
const formRef = ref(null)

const queryParams = reactive({
  keyword: '',
  resource_type: '',
  status: '',
  skip: 1,
  limit: 20
})

const defaultFormData = {
  resource_code: '',
  resource_name: '',
  resource_type: '',
  model: '',
  capacity: null,
  capacity_unit: 'm³',
  license_plate: '',
  manufacture_year: null,
  status: 'available',
  remarks: ''
}

const formData = reactive({ ...defaultFormData })

const allocateForm = reactive({
  resource_id: null,
  plan_id: null,
  order_id: null,
  allocation_reason: ''
})

const rules = {
  resource_code: [{ required: true, message: '请输入资源编码', trigger: 'blur' }],
  resource_name: [{ required: true, message: '请输入资源名称', trigger: 'blur' }],
  resource_type: [{ required: true, message: '请选择资源类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑资源' : '新增资源')

const fetchResourceList = async () => {
  loading.value = true
  try {
    const params = {
      skip: (queryParams.skip - 1) * queryParams.limit,
      limit: queryParams.limit
    }
    if (queryParams.keyword) params.keyword = queryParams.keyword
    if (queryParams.resource_type) params.resource_type = queryParams.resource_type
    if (queryParams.status) params.status = queryParams.status

    const res = await productionApi.getResources(params)
    resourceList.value = res
    total.value = res.length >= queryParams.limit ? (queryParams.skip + 1) * queryParams.limit : queryParams.skip * queryParams.limit + res.length
  } catch (error) {
    ElMessage.error('获取资源列表失败')
  } finally {
    loading.value = false
  }
}

const fetchPlansAndOrders = async () => {
  try {
    const [plans, orders] = await Promise.all([
      productionApi.getPlans({ limit: 100 }),
      productionApi.getOrders({ limit: 100 })
    ])
    planList.value = plans
    orderList.value = orders
  } catch (error) {
    console.error('获取计划和任务失败:', error)
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getTypeTag = (type) => {
  const types = {
    'mixer_truck': 'primary',
    'forklift': 'success',
    'pump': 'warning',
    'other': 'info'
  }
  return types[type] || 'info'
}

const getTypeLabel = (type) => {
  const labels = {
    'mixer_truck': '搅拌车',
    'forklift': '铲车',
    'pump': '泵车',
    'other': '其他'
  }
  return labels[type] || type
}

const getStatusType = (status) => {
  const types = {
    'available': 'success',
    'in_use': 'primary',
    'maintenance': 'warning',
    'unavailable': 'danger'
  }
  return types[status] || 'info'
}

const getStatusLabel = (status) => {
  const labels = {
    'available': '可用',
    'in_use': '使用中',
    'maintenance': '维护中',
    'unavailable': '不可用'
  }
  return labels[status] || status
}

const handleSearch = () => {
  queryParams.skip = 1
  fetchResourceList()
}

const handleReset = () => {
  queryParams.keyword = ''
  queryParams.resource_type = ''
  queryParams.status = ''
  queryParams.skip = 1
  fetchResourceList()
}

const handleSizeChange = (val) => {
  queryParams.limit = val
  fetchResourceList()
}

const handleCurrentChange = (val) => {
  queryParams.skip = val
  fetchResourceList()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(formData, defaultFormData)
  formData.resource_code = 'RES' + Date.now().toString().slice(-8)
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleAllocate = (row) => {
  currentResource.value = row
  allocateForm.resource_id = row.id
  allocateForm.plan_id = null
  allocateForm.order_id = null
  allocateForm.allocation_reason = ''
  allocateDialogVisible.value = true
}

const handleRelease = async (row) => {
  try {
    await ElMessageBox.confirm('确定要释放该资源吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await productionApi.releaseResource(row.id)
    ElMessage.success('释放成功')
    fetchResourceList()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('释放失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await productionApi.updateResource(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await productionApi.createResource(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchResourceList()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const handleSubmitAllocate = async () => {
  try {
    await productionApi.allocateResource(allocateForm)
    ElMessage.success('分配成功')
    allocateDialogVisible.value = false
    fetchResourceList()
  } catch (error) {
    ElMessage.error('分配失败')
  }
}

onMounted(() => {
  fetchResourceList()
  fetchPlansAndOrders()
})
</script>

<style scoped>
.resource-list-container {
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
