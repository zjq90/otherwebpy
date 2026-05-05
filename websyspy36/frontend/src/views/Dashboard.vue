<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <div class="stat-card blue">
          <div class="value">{{ stats.totalProduction }}</div>
          <div class="label">本月总产量 (m³)</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card green">
          <div class="value">{{ stats.totalSales }}</div>
          <div class="label">本月总销售额 (万元)</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card orange">
          <div class="value">{{ stats.totalProfit }}</div>
          <div class="label">本月总毛利 (万元)</div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card purple">
          <div class="value">{{ stats.pendingAlarms }}</div>
          <div class="label">待处理报警 (条)</div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 24px;">
      <el-col :span="12">
        <div class="card-container">
          <h3 style="margin-bottom: 16px;">产量趋势</h3>
          <div ref="productionChart" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-container">
          <h3 style="margin-bottom: 16px;">设备利用率</h3>
          <div ref="utilizationChart" style="height: 350px;"></div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 24px;">
      <el-col :span="12">
        <div class="card-container">
          <h3 style="margin-bottom: 16px;">成本构成分析</h3>
          <div ref="costChart" style="height: 350px;"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="card-container">
          <h3 style="margin-bottom: 16px;">近期报警记录</h3>
          <el-table :data="recentAlarms" style="width: 100%">
            <el-table-column prop="alarm_time" label="报警时间" width="180">
              <template #default="scope">
                {{ formatTime(scope.row.alarm_time) }}
              </template>
            </el-table-column>
            <el-table-column prop="alarm_type" label="报警类型" width="100" />
            <el-table-column prop="alarm_level" label="级别" width="80">
              <template #default="scope">
                <el-tag :type="getAlarmLevelType(scope.row.alarm_level)">
                  {{ scope.row.alarm_level }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="message" label="报警描述" min-width="150" show-overflow-tooltip />
            <el-table-column prop="is_handled" label="状态" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.is_handled ? 'success' : 'danger'">
                  {{ scope.row.is_handled ? '已处理' : '待处理' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { productionApi, costApi, environmentApi } from '@/api'
import dayjs from 'dayjs'

const productionChart = ref(null)
const utilizationChart = ref(null)
const costChart = ref(null)

const stats = reactive({
  totalProduction: 0,
  totalSales: 0,
  totalProfit: 0,
  pendingAlarms: 0
})

const recentAlarms = ref([])

const formatTime = (time) => {
  return time ? dayjs(time).format('YYYY-MM-DD HH:mm') : '-'
}

const getAlarmLevelType = (level) => {
  switch (level) {
    case '紧急': return 'danger'
    case '重要': return 'warning'
    default: return 'info'
  }
}

const loadStats = async () => {
  try {
    const [productionRes, energyRes, alarmsRes] = await Promise.all([
      productionApi.getMonthlyStats(),
      productionApi.getEnergyStats(),
      environmentApi.getAlarms({ is_handled: false, limit: 5 })
    ])
    
    if (productionRes.data && productionRes.data.length > 0) {
      const latest = productionRes.data[productionRes.data.length - 1]
      stats.totalProduction = latest.total_production?.toFixed(2) || 0
    }
    
    if (alarmsRes.data) {
      recentAlarms.value = alarmsRes.data
      stats.pendingAlarms = alarmsRes.data.length
    }
    
    stats.totalSales = '128.5'
    stats.totalProfit = '32.8'
  } catch (e) {
    console.error('加载统计数据失败:', e)
    stats.totalProduction = '856.5'
    stats.totalSales = '128.5'
    stats.totalProfit = '32.8'
    stats.pendingAlarms = 2
  }
}

const initProductionChart = () => {
  if (!productionChart.value) return
  
  const chart = echarts.init(productionChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['总产量', '合格产量']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月']
    },
    yAxis: {
      type: 'value',
      name: '立方米'
    },
    series: [
      {
        name: '总产量',
        type: 'line',
        smooth: true,
        data: [820, 932, 901, 934, 1290, 1330, 1320, 1450, 1380, 1520, 1480, 1600],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
          ])
        },
        lineStyle: {
          color: '#667eea',
          width: 2
        }
      },
      {
        name: '合格产量',
        type: 'line',
        smooth: true,
        data: [780, 890, 860, 890, 1220, 1280, 1260, 1400, 1320, 1450, 1420, 1530],
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(17, 153, 142, 0.5)' },
            { offset: 1, color: 'rgba(17, 153, 142, 0.1)' }
          ])
        },
        lineStyle: {
          color: '#11998e',
          width: 2
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => chart.resize())
}

const initUtilizationChart = () => {
  if (!utilizationChart.value) return
  
  const chart = echarts.init(utilizationChart.value)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['搅拌机1号', '搅拌机2号', '运输车1号', '运输车2号', '泵车1号']
    },
    yAxis: {
      type: 'value',
      name: '百分比(%)',
      max: 100
    },
    series: [
      {
        name: '实际工作',
        type: 'bar',
        stack: 'total',
        data: [75, 82, 68, 72, 60],
        itemStyle: {
          color: '#667eea'
        }
      },
      {
        name: '维护',
        type: 'bar',
        stack: 'total',
        data: [5, 3, 8, 4, 6],
        itemStyle: {
          color: '#f093fb'
        }
      },
      {
        name: '闲置',
        type: 'bar',
        stack: 'total',
        data: [20, 15, 24, 24, 34],
        itemStyle: {
          color: '#e0e0e0'
        }
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => chart.resize())
}

const initCostChart = () => {
  if (!costChart.value) return
  
  const chart = echarts.init(costChart.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '成本构成',
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
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: 45, name: '原材料', itemStyle: { color: '#667eea' } },
          { value: 20, name: '人工', itemStyle: { color: '#11998e' } },
          { value: 15, name: '能耗', itemStyle: { color: '#f093fb' } },
          { value: 10, name: '设备折旧', itemStyle: { color: '#4facfe' } },
          { value: 10, name: '其他', itemStyle: { color: '#f5576c' } }
        ]
      }
    ]
  }
  
  chart.setOption(option)
  
  window.addEventListener('resize', () => chart.resize())
}

onMounted(async () => {
  await loadStats()
  await nextTick()
  initProductionChart()
  initUtilizationChart()
  initCostChart()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}
</style>
