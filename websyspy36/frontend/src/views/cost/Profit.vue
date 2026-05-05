<template>
  <div class="profit-page">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-value" style="color: #67c23a;">¥{{ summary.totalSales.toFixed(2) }}</div>
            <div class="stats-label">总销售额</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-value" style="color: #e6a23c;">¥{{ summary.totalCost.toFixed(2) }}</div>
            <div class="stats-label">总成本</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-value" style="color: #409eff;">¥{{ summary.totalProfit.toFixed(2) }}</div>
            <div class="stats-label">总毛利</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card">
          <div class="stats-content">
            <div class="stats-value" style="color: #909399;">{{ summary.avgMargin.toFixed(1) }}%</div>
            <div class="stats-label">平均毛利率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card>
      <template #header>
        <span>利润分析明细</span>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="analysis_date" label="分析日期" width="120" />
        <el-table-column prop="concrete_type" label="混凝土类型" width="120">
          <template #default="scope">
            <el-tag type="primary" size="small">{{ scope.row.concrete_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_quantity" label="销售数量 (m³)" width="120">
          <template #default="scope">
            {{ scope.row.total_quantity?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        
        <el-table-column label="成本构成" header-align="center" align="center">
          <el-table-column prop="material_cost_per_cubic" label="原材料成本" width="100">
            <template #default="scope">
              ¥{{ scope.row.material_cost_per_cubic?.toFixed(2) || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="labor_cost_per_cubic" label="人工成本" width="100">
            <template #default="scope">
              ¥{{ scope.row.labor_cost_per_cubic?.toFixed(2) || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="energy_cost_per_cubic" label="能耗成本" width="100">
            <template #default="scope">
              ¥{{ scope.row.energy_cost_per_cubic?.toFixed(2) || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="total_cost_per_cubic" label="单方总成本" width="100">
            <template #default="scope">
              <span style="color: #e6a23c; font-weight: bold;">
                ¥{{ scope.row.total_cost_per_cubic?.toFixed(2) || 0 }}
              </span>
            </template>
          </el-table-column>
        </el-table-column>
        
        <el-table-column label="利润指标" header-align="center" align="center">
          <el-table-column prop="sales_price_per_cubic" label="销售单价" width="100">
            <template #default="scope">
              ¥{{ scope.row.sales_price_per_cubic?.toFixed(2) || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="gross_profit_per_cubic" label="单方毛利" width="100">
            <template #default="scope">
              <span style="color: #67c23a; font-weight: bold;">
                ¥{{ scope.row.gross_profit_per_cubic?.toFixed(2) || 0 }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="gross_profit_margin" label="毛利率" width="100">
            <template #default="scope">
              <el-progress
                :percentage="scope.row.gross_profit_margin?.toFixed(1) || 0"
                :stroke-width="12"
                :color="getMarginColor(scope.row.gross_profit_margin)"
              />
            </template>
          </el-table-column>
        </el-table-column>
        
        <el-table-column prop="total_gross_profit" label="总毛利 (元)" width="120">
          <template #default="scope">
            <span style="color: #67c23a; font-weight: bold;">
              ¥{{ scope.row.total_gross_profit?.toFixed(2) || 0 }}
            </span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { costApi } from '@/api'

const loading = ref(false)
const tableData = ref([])

const summary = computed(() => {
  const data = tableData.value
  return {
    totalSales: data.reduce((sum, item) => sum + (item.total_sales || 0), 0),
    totalCost: data.reduce((sum, item) => sum + (item.total_cost || 0), 0),
    totalProfit: data.reduce((sum, item) => sum + (item.total_gross_profit || 0), 0),
    avgMargin: data.length > 0 
      ? data.reduce((sum, item) => sum + (item.gross_profit_margin || 0), 0) / data.length 
      : 0
  }
})

const getMarginColor = (margin) => {
  if (margin >= 30) return '#67c23a'
  if (margin >= 20) return '#e6a23c'
  return '#f56c6c'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await costApi.getProfitAnalysis()
    tableData.value = res.data || []
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.stats-card {
  text-align: center;
}
.stats-value {
  font-size: 24px;
  font-weight: bold;
}
.stats-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>
