<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">订单统计</span>
    </div>
    
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overviewStats.total_orders || 0 }}</div>
              <div class="stat-label">总订单数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
              <el-icon :size="30"><Wallet /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ overviewStats.total_amount || 0 }}</div>
              <div class="stat-label">总回收金额</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
              <el-icon :size="30"><ScaleToOriginal /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ overviewStats.total_weight || 0 }}kg</div>
              <div class="stat-label">总回收重量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
              <el-icon :size="30"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ (overviewStats.completion_rate * 100 || 0).toFixed(1) }}%</div>
              <div class="stat-label">订单完成率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>每日回收趋势</span>
              <el-radio-group v-model="trendDays" size="small" @change="fetchDailyStats">
                <el-radio-button :value="7">近7天</el-radio-button>
                <el-radio-button :value="30">近30天</el-radio-button>
                <el-radio-button :value="90">近90天</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="recyclingChartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>订单状态分布</span>
            </div>
          </template>
          <div ref="statusChartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>月度统计对比</span>
              <el-radio-group v-model="compareType" size="small">
                <el-radio-button value="amount">金额</el-radio-button>
                <el-radio-button value="weight">重量</el-radio-button>
                <el-radio-button value="count">订单数</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div ref="compareChartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import { getOrderStats, getDailyStats } from '@/api'

const overviewStats = reactive({
  total_orders: 0,
  total_amount: 0,
  total_weight: 0,
  completion_rate: 0
})

const trendDays = ref(30)
const compareType = ref('amount')

const recyclingChartRef = ref(null)
const statusChartRef = ref(null)
const compareChartRef = ref(null)

let recyclingChart = null
let statusChart = null
let compareChart = null

const fetchOverviewStats = async () => {
  try {
    const res = await getOrderStats()
    const data = res.data || {}
    Object.assign(overviewStats, data)
  } catch (error) {
    console.error('获取订单统计失败:', error)
  }
}

const fetchDailyStats = async () => {
  try {
    const res = await getDailyStats(trendDays.value)
    const data = res.data || []
    renderRecyclingChart(data)
    renderCompareChart(data)
  } catch (error) {
    console.error('获取每日统计失败:', error)
  }
}

const renderRecyclingChart = (data) => {
  if (!recyclingChartRef.value) return
  
  if (!recyclingChart) {
    recyclingChart = echarts.init(recyclingChartRef.value)
  }
  
  const dates = data.map(item => item.date)
  const amounts = data.map(item => item.total_amount || 0)
  const weights = data.map(item => item.total_weight || 0)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['回收金额', '回收重量'],
      top: 10
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        boundaryGap: false,
        data: dates
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '金额(元)',
        position: 'left',
        axisLine: {
          lineStyle: {
            color: '#667eea'
          }
        }
      },
      {
        type: 'value',
        name: '重量(kg)',
        position: 'right',
        axisLine: {
          lineStyle: {
            color: '#f093fb'
          }
        }
      }
    ],
    series: [
      {
        name: '回收金额',
        type: 'line',
        smooth: true,
        itemStyle: {
          color: '#667eea'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.3)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ])
        },
        data: amounts
      },
      {
        name: '回收重量',
        type: 'bar',
        yAxisIndex: 1,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#f093fb' },
            { offset: 1, color: '#f5576c' }
          ])
        },
        data: weights
      }
    ]
  }
  
  recyclingChart.setOption(option)
}

const renderStatusChart = () => {
  if (!statusChartRef.value) return
  
  if (!statusChart) {
    statusChart = echarts.init(statusChartRef.value)
  }
  
  const statusData = [
    { value: overviewStats.total_orders * 0.15, name: '待接单' },
    { value: overviewStats.total_orders * 0.1, name: '已接单' },
    { value: overviewStats.total_orders * 0.05, name: '上门中' },
    { value: overviewStats.total_orders * 0.6, name: '已完成' },
    { value: overviewStats.total_orders * 0.07, name: '已取消' },
    { value: overviewStats.total_orders * 0.03, name: '异常' }
  ].filter(item => item.value > 0)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '订单状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: statusData.map((item, index) => ({
          ...item,
          itemStyle: {
            color: ['#909399', '#e6a23c', '#409eff', '#67c23a', '#909399', '#f56c6c'][index]
          }
        }))
      }
    ]
  }
  
  statusChart.setOption(option)
}

const renderCompareChart = (data) => {
  if (!compareChartRef.value) return
  
  if (!compareChart) {
    compareChart = echarts.init(compareChartRef.value)
  }
  
  const dates = data.map(item => item.date)
  const seriesData = {
    amount: {
      name: '回收金额',
      data: data.map(item => item.total_amount || 0),
      color: '#667eea',
      unit: '元'
    },
    weight: {
      name: '回收重量',
      data: data.map(item => item.total_weight || 0),
      color: '#4facfe',
      unit: 'kg'
    },
    count: {
      name: '订单数量',
      data: data.map(item => item.order_count || 0),
      color: '#43e97b',
      unit: '单'
    }
  }
  
  const currentData = seriesData[compareType.value]
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: function(params) {
        const result = [params[0].name]
        params.forEach(param => {
          result.push(param.marker + param.seriesName + ': ' + param.value + ' ' + currentData.unit)
        })
        return result.join('<br/>')
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: [
      {
        type: 'category',
        data: dates
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: currentData.unit === '单' ? '数量' : currentData.unit === '元' ? '金额' : '重量'
      }
    ],
    series: [
      {
        name: currentData.name,
        type: 'bar',
        barWidth: '60%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: currentData.color },
            { offset: 1, color: currentData.color + '80' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        data: currentData.data
      }
    ]
  }
  
  compareChart.setOption(option)
}

const handleResize = () => {
  recyclingChart?.resize()
  statusChart?.resize()
  compareChart?.resize()
}

watch(compareType, () => {
  fetchDailyStats()
})

onMounted(() => {
  fetchOverviewStats()
  fetchDailyStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  recyclingChart?.dispose()
  statusChart?.dispose()
  compareChart?.dispose()
})
</script>

<style lang="scss" scoped>
.stat-card {
  display: flex;
  align-items: center;
  
  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }
  
  .stat-info {
    margin-left: 16px;
    
    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
    
    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-top: 4px;
    }
  }
}

.chart-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.mt-20 {
  margin-top: 20px;
}
</style>
