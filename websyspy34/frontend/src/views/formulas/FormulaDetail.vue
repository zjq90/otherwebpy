<template>
  <div class="formula-detail-container">
    <el-button type="primary" text @click="goBack" style="margin-bottom: 20px;">
      <el-icon><ArrowLeft /></el-icon> 返回列表
    </el-button>

    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>配方详情</span>
          <div>
            <el-button type="primary" @click="handleEdit">编辑</el-button>
            <el-button type="primary" @click="handleAdjust">调整参数</el-button>
          </div>
        </div>
      </template>

      <el-descriptions :column="4" border>
        <el-descriptions-item label="配方编码">{{ formula.formula_code }}</el-descriptions-item>
        <el-descriptions-item label="配方名称">{{ formula.formula_name }}</el-descriptions-item>
        <el-descriptions-item label="混凝土类型">{{ formula.concrete_type }}</el-descriptions-item>
        <el-descriptions-item label="强度等级">{{ formula.strength_grade || '-' }}</el-descriptions-item>
        <el-descriptions-item label="版本号">{{ formula.version }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(formula.status)" size="small">{{ getStatusLabel(formula.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标准配方">
          <el-tag :type="formula.is_standard ? 'success' : 'info'" size="small">{{ formula.is_standard ? '是' : '否' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="水灰比">{{ formula.water_cement_ratio || '-' }}</el-descriptions-item>
        <el-descriptions-item label="坍落度">{{ formula.slump ? formula.slump + 'mm' : '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatTime(formula.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(formula.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ formula.created_by || '-' }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="4">{{ formula.description || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>配合比参数 (kg/m³)</el-divider>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic title="水泥" :value="formula.cement" :precision="2" suffix="kg">
            <template #prefix>
              <el-icon class="stat-icon"><Coin /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="砂" :value="formula.sand" :precision="2" suffix="kg">
            <template #prefix>
              <el-icon class="stat-icon"><Odometer /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="石子" :value="formula.gravel" :precision="2" suffix="kg">
            <template #prefix>
              <el-icon class="stat-icon"><Box /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="水" :value="formula.water" :precision="2" suffix="kg">
            <template #prefix>
              <el-icon class="stat-icon"><Watermelon /></el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 30px;">
        <el-col :span="6">
          <el-statistic title="外加剂" :value="formula.admixture" :precision="2" suffix="kg">
            <template #prefix>
              <el-icon class="stat-icon"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="粉煤灰" :value="formula.fly_ash" :precision="2" suffix="kg">
            <template #prefix>
              <el-icon class="stat-icon"><WindPower /></el-icon>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="6">
          <el-statistic title="矿粉" :value="formula.mineral_powder" :precision="2" suffix="kg">
            <template #prefix>
              <el-icon class="stat-icon"><Cpu /></el-icon>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <span>调整历史记录</span>
      </template>

      <el-table :data="adjustments" v-loading="adjustLoading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="水泥调整">
          <template #default="scope">
            <span v-if="scope.row.original_cement !== scope.row.adjusted_cement">
              {{ scope.row.original_cement }} → {{ scope.row.adjusted_cement }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="砂调整">
          <template #default="scope">
            <span v-if="scope.row.original_sand !== scope.row.adjusted_sand">
              {{ scope.row.original_sand }} → {{ scope.row.adjusted_sand }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="石子调整">
          <template #default="scope">
            <span v-if="scope.row.original_gravel !== scope.row.adjusted_gravel">
              {{ scope.row.original_gravel }} → {{ scope.row.adjusted_gravel }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="水调整">
          <template #default="scope">
            <span v-if="scope.row.original_water !== scope.row.adjusted_water">
              {{ scope.row.original_water }} → {{ scope.row.adjusted_water }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="project_name" label="项目名称" min-width="120" />
        <el-table-column prop="adjustment_reason" label="调整原因" min-width="150" />
        <el-table-column prop="adjusted_by" label="调整人" width="100" />
        <el-table-column prop="created_at" label="调整时间" width="160">
          <template #default="scope">
            {{ formatTime(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!adjustLoading && adjustments.length === 0" description="暂无调整记录" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { formulaApi } from '../../api'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const adjustLoading = ref(false)
const formula = ref({})
const adjustments = ref([])

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

const fetchFormulaDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    const res = await formulaApi.getById(id)
    formula.value = res
  } catch (error) {
    ElMessage.error('获取配方详情失败')
  } finally {
    loading.value = false
  }
}

const fetchAdjustments = async () => {
  adjustLoading.value = true
  try {
    const id = route.params.id
    const res = await formulaApi.getAdjustments(id)
    adjustments.value = res
  } catch (error) {
    console.error('获取调整记录失败:', error)
  } finally {
    adjustLoading.value = false
  }
}

const goBack = () => {
  router.push('/formulas')
}

const handleEdit = () => {
  ElMessage.info('请返回列表页进行编辑')
}

const handleAdjust = () => {
  ElMessage.info('请返回列表页进行参数调整')
}

onMounted(() => {
  fetchFormulaDetail()
  fetchAdjustments()
})
</script>

<style scoped>
.formula-detail-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-icon {
  font-size: 24px;
  color: #409eff;
}
</style>
