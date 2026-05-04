<template>
  <div class="finance">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>财务统计</span>
          <div class="header-actions">
            <el-date-picker
              v-model="filterDate"
              type="month"
              placeholder="选择月份"
              value-format="YYYY-MM"
              style="width: 150px; margin-right: 10px;"
              clearable
            />
            <el-button type="primary" @click="loadStats">
              <el-icon><Search /></el-icon>
              查询
            </el-button>
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #409EFF;">
                <el-icon :size="28"><Document /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ stats.bills?.total_count || 0 }}</div>
                <div class="stat-label">账单总数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #67C23A;">
                <el-icon :size="28"><Money /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value money-text">¥{{ stats.bills?.total_amount || 0 }}</div>
                <div class="stat-label">总金额</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #67C23A;">
                <el-icon :size="28"><CircleCheck /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value money-text">¥{{ stats.bills?.paid_amount || 0 }}</div>
                <div class="stat-label">已收金额</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover" class="stat-card">
            <div class="stat-content">
              <div class="stat-icon" style="background: #E6A23C;">
                <el-icon :size="28"><Warning /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value money-text">¥{{ stats.bills?.overdue_amount || 0 }}</div>
                <div class="stat-label">逾期金额</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>应收/实收统计</span>
            </template>
            <el-table :data="receivableData" stripe style="width: 100%">
              <el-table-column prop="type" label="类型" width="150">
                <template #default="scope">
                  <el-tag :type="scope.row.tagType">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="amount" label="金额">
                <template #default="scope">
                  <span :class="scope.row.className">¥{{ scope.row.amount }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="percent" label="占比">
                <template #default="scope">
                  <el-progress 
                    :percentage="scope.row.percent" 
                    :color="scope.row.progressColor"
                    :stroke-width="10"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>票据统计</span>
            </template>
            <el-table :data="invoiceData" stripe style="width: 100%">
              <el-table-column prop="type" label="类型" width="150">
                <template #default="scope">
                  <el-tag :type="scope.row.tagType">{{ scope.row.type }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="数量" width="100" />
              <el-table-column prop="amount" label="金额">
                <template #default="scope">
                  <span :class="scope.row.className">¥{{ scope.row.amount }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>按费用项目统计</span>
            </template>
            <el-table :data="feeItemStats" stripe style="width: 100%">
              <el-table-column prop="fee_item_name" label="费用项目" width="200">
                <template #default="scope">
                  <el-tag type="primary">{{ scope.row.fee_item_name || scope.row.fee_item_id }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="bill_count" label="账单数量" width="100">
                <template #default="scope">
                  <el-badge :value="scope.row.bill_count || 0" class="item">
                    <span class="badge-text">笔</span>
                  </el-badge>
                </template>
              </el-table-column>
              <el-table-column prop="total_amount" label="总金额" width="150">
                <template #default="scope">
                  <span class="amount-text">¥{{ scope.row.total_amount || 0 }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="paid_amount" label="已收金额" width="150">
                <template #default="scope">
                  <span class="paid-text">¥{{ scope.row.paid_amount || 0 }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="unpaid_amount" label="待收金额" width="150">
                <template #default="scope">
                  <span class="unpaid-text">¥{{ (scope.row.total_amount || 0) - (scope.row.paid_amount || 0) }}</span>
                </template>
              </el-table-column>
              <el-table-column label="收缴率" width="200">
                <template #default="scope">
                  <el-progress 
                    :percentage="getRate(scope.row.paid_amount, scope.row.total_amount)" 
                    :color="getProgressColor(scope.row.paid_amount, scope.row.total_amount)"
                  />
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { invoiceApi } from '@/api'

const filterDate = ref('')
const loading = ref(false)

const stats = reactive({
  bills: {
    total_count: 0,
    total_amount: 0,
    paid_amount: 0,
    unpaid_amount: 0,
    overdue_amount: 0
  },
  invoices: {
    total_count: 0,
    total_amount: 0
  }
})

const feeItemStats = ref([])

const receivableData = computed(() => {
  const total = stats.bills.total_amount || 0
  const paid = stats.bills.paid_amount || 0
  const unpaid = stats.bills.unpaid_amount || 0
  const overdue = stats.bills.overdue_amount || 0
  
  return [
    {
      type: '总应收',
      amount: total,
      percent: 100,
      tagType: 'primary',
      className: 'amount-text',
      progressColor: '#409EFF'
    },
    {
      type: '已实收',
      amount: paid,
      percent: total > 0 ? Math.round((paid / total) * 100) : 0,
      tagType: 'success',
      className: 'paid-text',
      progressColor: '#67C23A'
    },
    {
      type: '待实收',
      amount: unpaid,
      percent: total > 0 ? Math.round((unpaid / total) * 100) : 0,
      tagType: 'warning',
      className: 'unpaid-text',
      progressColor: '#E6A23C'
    },
    {
      type: '逾期',
      amount: overdue,
      percent: total > 0 ? Math.round((overdue / total) * 100) : 0,
      tagType: 'danger',
      className: 'overdue-text',
      progressColor: '#F56C6C'
    }
  ]
})

const invoiceData = computed(() => {
  return [
    {
      type: '已开具票据',
      count: stats.invoices.total_count || 0,
      amount: stats.invoices.total_amount || 0,
      tagType: 'success',
      className: 'paid-text'
    }
  ]
})

const getRate = (paid, total) => {
  if (!total || total === 0) return 0
  return Math.round((paid / total) * 100)
}

const getProgressColor = (paid, total) => {
  const rate = getRate(paid, total)
  if (rate >= 80) return '#67C23A'
  if (rate >= 50) return '#E6A23C'
  return '#F56C6C'
}

const loadStats = async () => {
  loading.value = true
  try {
    const params = {}
    if (filterDate.value) {
      const [year, month] = filterDate.value.split('-')
      params.year = parseInt(year)
      params.month = parseInt(month)
    }
    
    const res = await invoiceApi.getFinancialStats(params)
    const data = res.data
    
    stats.bills.total_count = data.bills?.total_count || 0
    stats.bills.total_amount = data.bills?.total_amount || 0
    stats.bills.paid_amount = data.bills?.paid_amount || 0
    stats.bills.unpaid_amount = data.bills?.unpaid_amount || 0
    stats.bills.overdue_amount = data.bills?.overdue_amount || 0
    
    stats.invoices.total_count = data.invoices?.total_count || 0
    stats.invoices.total_amount = data.invoices?.total_amount || 0
    
    feeItemStats.value = data.fee_item_breakdown || []
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.finance {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
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
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.money-text {
  color: #67C23A;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.amount-text {
  color: #409EFF;
  font-weight: bold;
}

.paid-text {
  color: #67C23A;
  font-weight: bold;
}

.unpaid-text {
  color: #E6A23C;
  font-weight: bold;
}

.overdue-text {
  color: #F56C6C;
  font-weight: bold;
}

.badge-text {
  padding: 0 10px;
  color: #606266;
}
</style>
