<template>
  <div class="dashboard">
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-left">
              <div class="stat-icon icon-blue">
                <el-icon><Box /></el-icon>
              </div>
            </div>
            <div class="stat-right">
              <div class="stat-value">{{ stats.total_silos }}</div>
              <div class="stat-label">料仓总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card" @click="goToInventory">
          <div class="stat-content">
            <div class="stat-left">
              <div class="stat-icon icon-red">
                <el-icon><Warning /></el-icon>
              </div>
            </div>
            <div class="stat-right">
              <div class="stat-value" :class="{ 'text-danger': stats.low_inventory_count > 0 }">
                {{ stats.low_inventory_count }}
              </div>
              <div class="stat-label">低库存预警</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-left">
              <div class="stat-icon icon-green">
                <el-icon><TrendCharts /></el-icon>
              </div>
            </div>
            <div class="stat-right">
              <div class="stat-value">{{ stats.total_production_plans }}</div>
              <div class="stat-label">生产计划</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-left">
              <div class="stat-icon icon-orange">
                <el-icon><Money /></el-icon>
              </div>
            </div>
            <div class="stat-right">
              <div class="stat-value">{{ stats.pending_settlements }}</div>
              <div class="stat-label">待付款结算</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="14">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>料仓库存分布</span>
              <el-button type="primary" size="small" @click="refreshData">
                <el-icon><Refresh /></el-icon>刷新
              </el-button>
            </div>
          </template>
          <div ref="inventoryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>低库存预警</span>
          </template>
          <div class="alert-list" v-if="lowInventoryList.length > 0">
            <div v-for="item in lowInventoryList" :key="item.silo_id" class="alert-item">
              <el-tag type="danger" effect="dark" class="alert-tag">
                <el-icon><WarningFilled /></el-icon>
                预警
              </el-tag>
              <div class="alert-info">
                <div class="alert-name">{{ item.silo_name }}</div>
                <div class="alert-detail">
                  <span>物料: {{ item.material_type }}</span>
                  <span>当前库存: {{ item.current_level }} 吨</span>
                  <span>预警线: {{ item.min_threshold }} 吨</span>
                </div>
                <el-progress 
                  :percentage="item.percentage" 
                  :stroke-width="8"
                  :color="item.percentage < 20 ? '#F56C6C' : '#E6A23C'"
                />
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无低库存预警" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>待处理物料需求</span>
          </template>
          <el-table :data="pendingDemands" stripe max-height="300">
            <el-table-column prop="material_type" label="物料类型" width="100" />
            <el-table-column prop="required_quantity" label="需求量(吨)" width="100">
              <template #default="{ row }">
                <span>{{ row.required_quantity.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="current_stock" label="当前库存(吨)" width="100">
              <template #default="{ row }">
                <span>{{ row.current_stock.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="shortage" label="缺口(吨)">
              <template #default="{ row }">
                <el-tag :type="row.shortage > 0 ? 'danger' : 'success'">
                  {{ row.shortage.toFixed(2) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="80">
              <template #default="{ row }">
                <el-tag :type="getPriorityType(row.priority)">
                  {{ getPriorityText(row.priority) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <span>供应商评级分布</span>
          </template>
          <div ref="supplierChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { dashboardApi, siloApi, productionApi, supplierApi } from '@/api'

const router = useRouter()
const inventoryChartRef = ref(null)
const supplierChartRef = ref(null)

const stats = ref({
  total_silos: 0,
  low_inventory_count: 0,
  total_production_plans: 0,
  pending_demands: 0,
  total_suppliers: 0,
  pending_settlements: 0
})

const lowInventoryList = ref([])
const pendingDemands = ref([])
const silosList = ref([])
const suppliersList = ref([])

const goToInventory = () => {
  router.push('/inventory')
}

const getPriorityType = (priority) => {
  const types = { 1: 'danger', 2: 'warning', 3: '', 4: 'info' }
  return types[priority] || ''
}

const getPriorityText = (priority) => {
  const texts = { 1: '紧急', 2: '高', 3: '中', 4: '低' }
  return texts[priority] || '未知'
}

const fetchStats = async () => {
  try {
    const res = await dashboardApi.getStats()
    stats.value = res.data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

const fetchLowInventory = async () => {
  try {
    const res = await siloApi.getLowInventory()
    lowInventoryList.value = res.data
    stats.value.low_inventory_count = res.data.length
  } catch (error) {
    console.error('获取低库存预警失败:', error)
  }
}

const fetchPendingDemands = async () => {
  try {
    const res = await productionApi.getPendingDemands()
    pendingDemands.value = res.data
  } catch (error) {
    console.error('获取待处理需求失败:', error)
  }
}

const fetchSilos = async () => {
  try {
    const res = await siloApi.getList()
    silosList.value = res.data
  } catch (error) {
    console.error('获取料仓列表失败:', error)
  }
}

const fetchSuppliers = async () => {
  try {
    const res = await supplierApi.getList()
    suppliersList.value = res.data
  } catch (error) {
    console.error('获取供应商列表失败:', error)
  }
}

const initInventoryChart = () => {
  if (!inventoryChartRef.value || silosList.value.length === 0) return
  
  const chart = echarts.init(inventoryChartRef.value)
  
  const categories = silosList.value.map(s => s.name)
  const currentData = silosList.value.map(s => s.current_level)
  const capacityData = silosList.value.map(s => s.capacity)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    legend: {
      data: ['当前库存', '最大容量'],
      top: 0
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '15%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: categories
    },
    yAxis: {
      type: 'value',
      name: '吨'
    },
    series: [
      {
        name: '当前库存',
        type: 'bar',
        data: currentData,
        itemStyle: {
          color: (params) => {
            const silo = silosList.value[params.dataIndex]
            if (silo.current_level <= silo.min_threshold) {
              return '#F56C6C'
            }
            return '#409EFF'
          }
        }
      },
      {
        name: '最大容量',
        type: 'bar',
        data: capacityData,
        itemStyle: {
          color: '#909399'
        }
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initSupplierChart = () => {
  if (!supplierChartRef.value || suppliersList.value.length === 0) return
  
  const chart = echarts.init(supplierChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c}分 ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      top: 'center'
    },
    series: [
      {
        name: '评分',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}\n{c}分'
        },
        data: suppliersList.value.map(s => ({
          value: s.overall_rating,
          name: s.name,
          itemStyle: {
            color: s.overall_rating >= 8 ? '#67C23A' : s.overall_rating >= 6 ? '#E6A23C' : '#F56C6C'
          }
        }))
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const refreshData = () => {
  fetchAllData()
}

const fetchAllData = async () => {
  await Promise.all([
    fetchStats(),
    fetchLowInventory(),
    fetchPendingDemands(),
    fetchSilos(),
    fetchSuppliers()
  ])
  
  nextTick(() => {
    initInventoryChart()
    initSupplierChart()
  })
}

onMounted(() => {
  fetchAllData()
})
</script>

<style scoped>
.dashboard {
  width: 100%;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.icon-blue {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.icon-red {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.icon-green {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.icon-orange {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
}

.stat-right {
  margin-left: 16px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-value.text-danger {
  color: #F56C6C;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.chart-card {
  height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  width: 100%;
  height: 320px;
}

.alert-list {
  max-height: 320px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  padding: 12px;
  border-radius: 8px;
  background-color: #fef0f0;
  margin-bottom: 10px;
  border: 1px solid #fbc4c4;
}

.alert-tag {
  margin-right: 12px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 4px;
}

.alert-info {
  flex: 1;
}

.alert-name {
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.alert-detail {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #606266;
  margin-bottom: 8px;
}
</style>
