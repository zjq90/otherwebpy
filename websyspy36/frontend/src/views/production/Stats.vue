<template>
  <div class="stats-page">
    <el-card class="card-container">
      <template #header>
        <span>生产数据统计分析</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>日产量统计</span>
            </template>
            <div ref="dailyChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>月产量统计</span>
            </template>
            <div ref="monthlyChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>设备利用率统计</span>
            </template>
            <div ref="utilizationChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>能耗统计</span>
            </template>
            <div ref="energyChart" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-card style="margin-top: 20px;">
        <template #header>
          <span>生产数据汇总</span>
        </template>
        <el-table :data="summaryData" style="width: 100%">
          <el-table-column prop="date" label="日期" width="120" />
          <el-table-column prop="total_production" label="总产量 (m³)" width="120">
            <template #default="scope">
              {{ scope.row.total_production?.toFixed(2) || 0 }}
            </template>
          </el-table-column>
          <el-table-column prop="total_batch" label="总批次" width="100" />
          <el-table-column prop="qualified_rate" label="合格率 (%)" width="120">
            <template #default="scope">
              {{ scope.row.qualified_rate?.toFixed(1) || 0 }}%
            </template>
          </el-table-column>
          <el-table-column prop="total_working_hours" label="总工时 (h)" width="120">
            <template #default="scope">
              {{ scope.row.total_working_hours?.toFixed(1) || 0 }}
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const dailyChart = ref(null)
const monthlyChart = ref(null)
const utilizationChart = ref(null)
const energyChart = ref(null)

const summaryData = ref([
  { date: '2025-04-01', total_production: 1250.5, total_batch: 25, qualified_rate: 98.5, total_working_hours: 10.5 },
  { date: '2025-04-02', total_production: 1180.3, total_batch: 23, qualified_rate: 99.0, total_working_hours: 9.8 },
  { date: '2025-04-03', total_production: 1320.8, total_batch: 28, qualified_rate: 98.8, total_working_hours: 11.2 },
  { date: '2025-04-04', total_production: 980.2, total_batch: 20, qualified_rate: 97.5, total_working_hours: 8.5 },
  { date: '2025-04-05', total_production: 1420.0, total_batch: 30, qualified_rate: 99.2, total_working_hours: 12.0 },
])

const initCharts = () => {
  if (!dailyChart.value) return
  
  const dailyInstance = echarts.init(dailyChart.value)
  dailyInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['04-01', '04-02', '04-03', '04-04', '04-05', '04-06', '04-07']
    },
    yAxis: { type: 'value', name: '产量 (m³)' },
    series: [{
      data: [1250, 1180, 1320, 980, 1420, 1350, 1280],
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.3 }
    }]
  })
  
  const monthlyInstance = echarts.init(monthlyChart.value)
  monthlyInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['1月', '2月', '3月', '4月']
    },
    yAxis: { type: 'value', name: '产量 (m³)' },
    series: [{
      data: [32000, 28500, 35800, 28000],
      type: 'bar',
      itemStyle: { color: '#409eff' }
    }]
  })
  
  const utilizationInstance = echarts.init(utilizationChart.value)
  utilizationInstance.setOption({
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: '60%',
      data: [
        { value: 75, name: '工作' },
        { value: 10, name: '维护' },
        { value: 15, name: '闲置' }
      ]
    }]
  })
  
  const energyInstance = echarts.init(energyChart.value)
  energyInstance.setOption({
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: ['电力', '水', '柴油']
    },
    yAxis: { type: 'value' },
    series: [{
      data: [45000, 12000, 8500],
      type: 'bar',
      itemStyle: {
        color: (params) => {
          const colors = ['#409eff', '#67c23a', '#e6a23c']
          return colors[params.dataIndex]
        }
      }
    }]
  })
}

onMounted(() => {
  nextTick(() => {
    initCharts()
  })
})
</script>

<style scoped>
</style>
