<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409EFF;">
              <el-icon :size="30"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.properties }}</div>
              <div class="stat-label">房产总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67C23A;">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.bills }}</div>
              <div class="stat-label">账单总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #E6A23C;">
              <el-icon :size="30"><Bell /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.overdue }}</div>
              <div class="stat-label">逾期账单</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #F56C6C;">
              <el-icon :size="30"><Ticket /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.invoices }}</div>
              <div class="stat-label">已开票数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>快捷操作</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="quick-action" @click="goTo('/fee-items')">
                <el-icon :size="40" color="#409EFF"><Plus /></el-icon>
                <span>新增费用项目</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="quick-action" @click="goTo('/properties')">
                <el-icon :size="40" color="#67C23A"><OfficeBuilding /></el-icon>
                <span>房产管理</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="quick-action" @click="showBatchGenerate">
                <el-icon :size="40" color="#E6A23C"><Document /></el-icon>
                <span>批量生成账单</span>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="quick-action" @click="goTo('/reminders')">
                <el-icon :size="40" color="#F56C6C"><Bell /></el-icon>
                <span>催缴管理</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>系统信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="系统名称">物业管理系统</el-descriptions-item>
            <el-descriptions-item label="系统版本">1.0.0</el-descriptions-item>
            <el-descriptions-item label="后端API">FastAPI</el-descriptions-item>
            <el-descriptions-item label="前端框架">Vue 3</el-descriptions-item>
            <el-descriptions-item label="UI组件">Element Plus</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="batchGenerateVisible" title="批量生成账单" width="500px">
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="计费年份">
          <el-date-picker
            v-model="batchForm.year"
            type="year"
            placeholder="选择年份"
            value-format="YYYY"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="计费月份">
          <el-select v-model="batchForm.month" placeholder="选择月份" style="width: 100%;">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchGenerateVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchGenerate" :loading="generating">
          生成账单
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { billApi, propertyApi } from '@/api'

const router = useRouter()

const stats = ref({
  properties: 0,
  bills: 0,
  overdue: 0,
  invoices: 0
})

const batchGenerateVisible = ref(false)
const generating = ref(false)
const batchForm = ref({
  year: new Date().getFullYear().toString(),
  month: new Date().getMonth() + 1
})

const goTo = (path) => {
  router.push(path)
}

const showBatchGenerate = () => {
  batchForm.value.year = new Date().getFullYear().toString()
  batchForm.value.month = new Date().getMonth() + 1
  batchGenerateVisible.value = true
}

const handleBatchGenerate = async () => {
  if (!batchForm.value.year || !batchForm.value.month) {
    ElMessage.warning('请选择年份和月份')
    return
  }
  
  generating.value = true
  try {
    const res = await billApi.batchGenerate({
      billing_year: parseInt(batchForm.value.year),
      billing_month: batchForm.value.month
    })
    ElMessage.success(`生成完成：新增 ${res.data.generated_count} 条账单，跳过 ${res.data.skipped_count} 条已存在账单`)
    batchGenerateVisible.value = false
    loadStats()
  } catch (error) {
    console.error(error)
  } finally {
    generating.value = false
  }
}

const loadStats = async () => {
  try {
    const [propsRes, billsRes, overdueRes] = await Promise.all([
      propertyApi.getList({ limit: 1 }),
      billApi.getList({ limit: 1 }),
      billApi.getOverdue({ limit: 1 })
    ])
    stats.value.properties = propsRes.headers['x-total-count'] || propsRes.data.length
    stats.value.bills = billsRes.headers['x-total-count'] || billsRes.data.length
    stats.value.overdue = overdueRes.headers['x-total-count'] || overdueRes.data.length
    stats.value.invoices = 0
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s;
}

.quick-action:hover {
  background-color: #f5f7fa;
}

.quick-action span {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
</style>
