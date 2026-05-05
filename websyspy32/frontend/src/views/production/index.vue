<template>
  <div class="production-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>生产计划管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAddPlan">
              <el-icon><Plus /></el-icon>新增计划
            </el-button>
          </div>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="所有计划" name="all">
          <el-table :data="plansList" stripe v-loading="loading">
            <el-table-column prop="plan_name" label="计划名称" min-width="180" />
            <el-table-column prop="plan_date" label="计划日期" width="120" />
            <el-table-column prop="concrete_volume" label="计划方量(立方米)" width="140" />
            <el-table-column prop="concrete_grade" label="混凝土标号" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getPlanStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
            <el-table-column label="操作" width="280" fixed="right">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleViewDemands(row)">
                  查看需求
                </el-button>
                <el-button type="success" link @click="handleGenerateDemands(row)">
                  重新计算
                </el-button>
                <el-button type="primary" link @click="handleEditPlan(row)">编辑</el-button>
                <el-button type="danger" link @click="handleDeletePlan(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <el-tab-pane label="物料需求预测" name="demands">
          <div style="margin-bottom: 16px;">
            <el-radio-group v-model="demandFilter" @change="handleDemandFilterChange">
              <el-radio-button value="all">全部需求</el-radio-button>
              <el-radio-button value="pending">待处理</el-radio-button>
              <el-radio-button value="urgent">紧急</el-radio-button>
            </el-radio-group>
            <el-button type="primary" size="small" style="margin-left: 16px;" @click="fetchDemands">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
          </div>
          
          <el-table :data="demandsList" stripe v-loading="demandsLoading">
            <el-table-column label="生产计划" min-width="150">
              <template #default="{ row }">
                {{ getPlanName(row.production_plan_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="material_type" label="物料类型" width="100" />
            <el-table-column prop="required_quantity" label="预测需求量(吨)" width="130">
              <template #default="{ row }">
                {{ row.required_quantity.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="current_stock" label="当前库存(吨)" width="110">
              <template #default="{ row }">
                {{ row.current_stock.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="shortage" label="缺口量(吨)" width="100">
              <template #default="{ row }">
                <el-tag :type="row.shortage > 0 ? 'danger' : 'success'">
                  {{ row.shortage.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="unit_consumption" label="单位消耗" width="100">
              <template #default="{ row }">
                {{ row.unit_consumption }} 吨/立方米
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)" size="small">
                  {{ getPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getDemandStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleCreateOrder(row)">
                  创建采购单
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="planDialogVisible" :title="planDialogTitle" width="600px">
      <el-form :model="planForm" :rules="planRules" ref="planFormRef" label-width="120px">
        <el-form-item label="计划名称" prop="plan_name">
          <el-input v-model="planForm.plan_name" placeholder="请输入计划名称" />
        </el-form-item>
        <el-form-item label="计划日期" prop="plan_date">
          <el-date-picker
            v-model="planForm.plan_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="计划方量(立方米)" prop="concrete_volume">
          <el-input-number v-model="planForm.concrete_volume" :min="0" :step="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="混凝土标号" prop="concrete_grade">
          <el-select v-model="planForm.concrete_grade" placeholder="请选择混凝土标号" style="width: 100%">
            <el-option label="C15" value="C15" />
            <el-option label="C20" value="C20" />
            <el-option label="C25" value="C25" />
            <el-option label="C30" value="C30" />
            <el-option label="C35" value="C35" />
            <el-option label="C40" value="C40" />
            <el-option label="C45" value="C45" />
            <el-option label="C50" value="C50" />
            <el-option label="C60" value="C60" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="planForm.status" style="width: 100%">
            <el-option label="待执行" value="待执行" />
            <el-option label="执行中" value="执行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已取消" value="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="planForm.description" type="textarea" :rows="3" placeholder="请输入描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePlanSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="demandsDialogVisible" title="物料需求详情" width="800px">
      <el-table :data="currentPlanDemands" stripe>
        <el-table-column prop="material_type" label="物料类型" width="120" />
        <el-table-column prop="required_quantity" label="预测需求量(吨)" width="130">
          <template #default="{ row }">
            {{ row.required_quantity.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_stock" label="当前库存(吨)" width="120">
          <template #default="{ row }">
            {{ row.current_stock.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="shortage" label="缺口量(吨)" width="100">
          <template #default="{ row }">
            <el-tag :type="row.shortage > 0 ? 'danger' : 'success'">
              {{ row.shortage.toFixed(2) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit_consumption" label="单位消耗" width="130">
          <template #default="{ row }">
            {{ row.unit_consumption }} 吨/立方米
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)" size="small">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="getDemandStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="demandsDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { productionApi } from '@/api'

const router = useRouter()
const loading = ref(false)
const demandsLoading = ref(false)
const activeTab = ref('all')
const demandFilter = ref('all')

const plansList = ref([])
const demandsList = ref([])
const currentPlanDemands = ref([])

const planDialogVisible = ref(false)
const demandsDialogVisible = ref(false)
const isEditPlan = ref(false)

const planFormRef = ref<FormInstance>()

const planForm = reactive({
  id: null,
  plan_name: '',
  plan_date: '',
  concrete_volume: 0,
  concrete_grade: '',
  status: '待执行',
  description: ''
})

const planRules: FormRules = {
  plan_name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }],
  concrete_volume: [{ required: true, message: '请输入计划方量', trigger: 'blur' }]
}

const planDialogTitle = computed(() => isEditPlan.value ? '编辑生产计划' : '新增生产计划')

const getPlanStatusType = (status) => {
  const types = {
    '待执行': 'warning',
    '执行中': 'primary',
    '已完成': 'success',
    '已取消': 'info'
  }
  return types[status] || 'info'
}

const getDemandStatusType = (status) => {
  const types = {
    '待处理': 'danger',
    '部分补货': 'warning',
    '已满足': 'success',
    '已补货': 'success'
  }
  return types[status] || 'info'
}

const getPriorityType = (priority) => {
  const types = { 1: 'danger', 2: 'warning', 3: '', 4: 'info' }
  return types[priority] || ''
}

const getPriorityText = (priority) => {
  const texts = { 1: '紧急', 2: '高', 3: '中', 4: '低' }
  return texts[priority] || '未知'
}

const getPlanName = (planId) => {
  const plan = plansList.value.find(p => p.id === planId)
  return plan ? plan.plan_name : '未知计划'
}

const fetchPlans = async () => {
  loading.value = true
  try {
    const res = await productionApi.getPlans({ limit: 100 })
    plansList.value = res.data
  } catch (error) {
    ElMessage.error('获取生产计划失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchDemands = async () => {
  demandsLoading.value = true
  try {
    let res
    if (demandFilter.value === 'pending') {
      res = await productionApi.getPendingDemands()
    } else {
      res = await productionApi.getDemands({ limit: 100 })
    }
    
    let data = res.data
    if (demandFilter.value === 'urgent') {
      data = data.filter(item => item.priority === 1 || item.priority === 2)
    }
    
    demandsList.value = data
  } catch (error) {
    ElMessage.error('获取物料需求失败')
    console.error(error)
  } finally {
    demandsLoading.value = false
  }
}

const handleDemandFilterChange = () => {
  fetchDemands()
}

const handleAddPlan = () => {
  isEditPlan.value = false
  Object.assign(planForm, {
    id: null,
    plan_name: '',
    plan_date: '',
    concrete_volume: 0,
    concrete_grade: '',
    status: '待执行',
    description: ''
  })
  planDialogVisible.value = true
}

const handleEditPlan = (row) => {
  isEditPlan.value = true
  Object.assign(planForm, { ...row })
  planDialogVisible.value = true
}

const handleDeletePlan = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除生产计划"${row.plan_name}"吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await productionApi.deletePlan(row.id)
    ElMessage.success('删除成功')
    fetchPlans()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleViewDemands = (row) => {
  currentPlanDemands.value = demandsList.value.filter(d => d.production_plan_id === row.id)
  demandsDialogVisible.value = true
}

const handleGenerateDemands = async (row) => {
  try {
    await productionApi.generateDemands(row.id)
    ElMessage.success('物料需求重新计算成功')
    fetchDemands()
  } catch (error) {
    ElMessage.error('重新计算失败')
  }
}

const handleCreateOrder = (row) => {
  router.push({ path: '/suppliers', query: { materialType: row.material_type, quantity: row.shortage } })
}

const handlePlanSubmit = async () => {
  if (!planFormRef.value) return
  
  await planFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEditPlan.value) {
          await productionApi.updatePlan(planForm.id, planForm)
          ElMessage.success('更新成功')
        } else {
          await productionApi.createPlan(planForm)
          ElMessage.success('创建成功，已自动生成物料需求')
        }
        planDialogVisible.value = false
        fetchPlans()
        fetchDemands()
      } catch (error) {
        ElMessage.error(isEditPlan.value ? '更新失败' : '创建失败')
      }
    }
  })
}

onMounted(() => {
  fetchPlans()
  fetchDemands()
})
</script>

<style scoped>
.production-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}
</style>
