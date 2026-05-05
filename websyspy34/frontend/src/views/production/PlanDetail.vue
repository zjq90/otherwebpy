<template>
  <div class="plan-detail-container">
    <el-button type="primary" text @click="goBack" style="margin-bottom: 20px;">
      <el-icon><ArrowLeft /></el-icon> 返回列表
    </el-button>

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>生产计划详情</span>
          <div>
            <el-button type="primary" @click="handleEdit">编辑</el-button>
            <el-button v-if="plan.status === 'pending'" type="success" @click="handleStart">开始</el-button>
            <el-button v-if="plan.status === 'in_progress'" type="warning" @click="handleDelay">延期</el-button>
            <el-button v-if="plan.status !== 'cancelled' && plan.status !== 'completed'" type="danger" @click="handleCancel">取消</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="4" border>
        <el-descriptions-item label="计划编码">{{ plan.plan_code }}</el-descriptions-item>
        <el-descriptions-item label="计划名称">{{ plan.plan_name }}</el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityType(plan.priority)" size="small">{{ plan.priority }}级</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(plan.status)" size="small">{{ getStatusLabel(plan.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="项目名称" :span="2">{{ plan.project_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="项目地址" :span="2">{{ plan.project_location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ plan.contact_person || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ plan.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="总方量">{{ plan.total_volume || 0 }} m³</el-descriptions-item>
        <el-descriptions-item label="已完成">
          <el-progress :percentage="getProgress(plan)" :stroke-width="10" />
        </el-descriptions-item>
        <el-descriptions-item label="计划开始时间">{{ formatTime(plan.planned_start_date) }}</el-descriptions-item>
        <el-descriptions-item label="计划结束时间">{{ formatTime(plan.planned_end_date) }}</el-descriptions-item>
        <el-descriptions-item label="实际开始时间">{{ formatTime(plan.actual_start_date) }}</el-descriptions-item>
        <el-descriptions-item label="实际结束时间">{{ formatTime(plan.actual_end_date) }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(plan.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(plan.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ plan.created_by || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="4">{{ plan.remarks || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <span>关联生产任务单</span>
      </template>
      <el-table :data="plan.orders || []" stripe>
        <el-table-column prop="order_code" label="任务单号" min-width="120" />
        <el-table-column prop="batch_number" label="批次号" min-width="120" />
        <el-table-column prop="volume" label="方量(m³)" width="100" />
        <el-table-column prop="pouring_location" label="浇筑位置" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="150">
          <template #default="scope">
            <el-progress :percentage="scope.row.progress || 0" :stroke-width="8" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="scope">
            <el-button type="primary" text @click="viewOrder(scope.row.id)">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!plan.orders || plan.orders.length === 0" description="暂无关联任务单" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { productionApi } from '../../api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const plan = ref({})

const fetchPlanDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const res = await productionApi.getPlanById(id)
    plan.value = res
  } catch (error) {
    ElMessage.error('获取计划详情失败')
  } finally {
    loading.value = false
  }
}

const formatTime = (time) => {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

const getProgress = (p) => {
  if (!p.total_volume || p.total_volume === 0) return 0
  return Math.round((p.completed_volume || 0) / p.total_volume * 100)
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

const goBack = () => {
  router.push('/plans')
}

const handleEdit = () => {
  ElMessage.info('编辑功能请返回列表页操作')
}

const handleStart = async () => {
  try {
    await ElMessageBox.confirm('确定要开始该生产计划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await productionApi.updatePlan(plan.value.id, { status: 'in_progress' })
    ElMessage.success('计划已开始')
    fetchPlanDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleDelay = async () => {
  try {
    await ElMessageBox.confirm('确定要将该计划标记为延期吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await productionApi.updatePlan(plan.value.id, { status: 'delayed' })
    ElMessage.success('计划已标记为延期')
    fetchPlanDetail()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleCancel = async () => {
  try {
    await ElMessageBox.confirm('确定要取消该生产计划吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await productionApi.deletePlan(plan.value.id)
    ElMessage.success('计划已取消')
    router.push('/plans')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const viewOrder = (id) => {
  router.push(`/orders/${id}`)
}

onMounted(() => {
  fetchPlanDetail()
})
</script>

<style scoped>
.plan-detail-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
