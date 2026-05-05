<template>
  <div class="dashboard-page">
    <div class="card-container">
      <div class="stat-card" v-for="stat in statistics" :key="stat.title">
        <div class="stat-header">
          <span class="stat-title">{{ stat.title }}</span>
          <div class="stat-icon" :style="{ backgroundColor: stat.color }">
            <el-icon><component :is="stat.icon" /></el-icon>
          </div>
        </div>
        <div class="stat-value">{{ stat.value }}</div>
        <div class="stat-trend" :class="stat.trend === 'up' ? 'up' : 'down'">
          <el-icon><component :is="stat.trend === 'up' ? 'TrendCharts' : 'TrendCharts'" /></el-icon>
          <span>{{ stat.trendText }}</span>
        </div>
      </div>
    </div>
    
    <el-row :gutter="16" style="margin-top: 20px;">
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">设备状态分布</span>
          </div>
          <div class="chart-content" ref="equipmentChartRef"></div>
        </div>
      </el-col>
      <el-col :span="12">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">传感器数据趋势</span>
          </div>
          <div class="chart-content" ref="sensorChartRef"></div>
        </div>
      </el-col>
    </el-row>
    
    <el-row :gutter="16" style="margin-top: 20px;">
      <el-col :span="16">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">保养任务统计</span>
          </div>
          <div class="chart-content" ref="taskChartRef"></div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="chart-card">
          <div class="chart-header">
            <span class="chart-title">最新告警</span>
          </div>
          <div class="alarm-list">
            <div class="alarm-item" v-for="alarm in alarmList" :key="alarm.id">
              <div class="alarm-level" :class="alarm.level">
                <el-icon><Warning /></el-icon>
              </div>
              <div class="alarm-content">
                <div class="alarm-title">{{ alarm.title }}</div>
                <div class="alarm-time">{{ alarm.time }}</div>
              </div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import * as echarts from 'echarts'
import {
  Box, Monitor, Tools, Connection, Warning,
  TrendCharts
} from '@element-plus/icons-vue'
import { getEquipmentList, getSensorList } from '@/api/equipment'
import { getMaintenanceTaskStatistics } from '@/api/maintenance'

const equipmentChartRef = ref(null)
const sensorChartRef = ref(null)
const taskChartRef = ref(null)

const statistics = reactive([
  { title: '设备总数', value: '6', icon: 'Box', color: '#409eff', trend: 'up', trendText: '较昨日 +2' },
  { title: '运行中', value: '4', icon: 'Monitor', color: '#67c23a', trend: 'up', trendText: '正常运行' },
  { title: '待处理任务', value: '3', icon: 'Tools', color: '#e6a23c', trend: 'down', trendText: '较昨日 -1' },
  { title: '系统状态', value: '正常', icon: 'Connection', color: '#909399', trend: 'down', trendText: '无异常' }
])

const alarmList = reactive([
  { id: 1, title: '搅拌主机1号温度预警', level: 'warning', time: '10分钟前' },
  { id: 2, title: '皮带秤2号速度异常', level: 'error', time: '30分钟前' },
  { id: 3, title: '空压机1号压力偏高', level: 'warning', time: '1小时前' }
])

const initEquipmentChart = () => {
  const chart = echarts.init(equipmentChartRef.value)
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center'
    },
    series: [
      {
        name: '设备状态',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
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
        data: [
          { value: 4, name: '运行中', itemStyle: { color: '#67c23a' } },
          { value: 1, name: '维护中', itemStyle: { color: '#e6a23c' } },
          { value: 1, name: '停机', itemStyle: { color: '#909399' } }
        ]
      }
    ]
  }
  chart.setOption(option)
}

const initSensorChart = () => {
  const chart = echarts.init(sensorChartRef.value)
  const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`)
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['电流(A)', '温度(℃)', '振动(mm/s)']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: hours
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '电流(A)',
        type: 'line',
        smooth: true,
        data: [80, 85, 90, 88, 92, 87, 95, 90, 88, 92, 85, 88, 90, 87, 92, 88, 90, 85, 88, 92, 90, 87, 85, 80]
      },
      {
        name: '温度(℃)',
        type: 'line',
        smooth: true,
        data: [45, 48, 52, 55, 58, 60, 62, 58, 55, 52, 48, 45, 42, 40, 42, 45, 48, 52, 55, 58, 60, 58, 55, 50]
      },
      {
        name: '振动(mm/s)',
        type: 'line',
        smooth: true,
        data: [2.1, 2.3, 2.5, 2.2, 2.4, 2.6, 2.3, 2.1, 2.2, 2.4, 2.3, 2.1, 2.0, 1.9, 2.0, 2.1, 2.2, 2.3, 2.5, 2.4, 2.2, 2.1, 2.0, 1.9]
      }
    ]
  }
  chart.setOption(option)
}

const initTaskChart = () => {
  const chart = echarts.init(taskChartRef.value)
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['保养任务']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: ['待执行', '执行中', '已完成', '已逾期', '已取消']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '保养任务',
        type: 'bar',
        barWidth: '40%',
        data: [5, 2, 8, 1, 0],
        itemStyle: {
          color: function(params) {
            const colorList = ['#409eff', '#e6a23c', '#67c23a', '#f56c6c', '#909399']
            return colorList[params.dataIndex]
          }
        }
      }
    ]
  }
  chart.setOption(option)
}

onMounted(() => {
  initEquipmentChart()
  initSensorChart()
  initTaskChart()
})
</script>

<style lang="scss" scoped>
.dashboard-page {
  .alarm-list {
    height: 300px;
    overflow-y: auto;
    
    .alarm-item {
      display: flex;
      align-items: center;
      padding: 12px;
      border-bottom: 1px solid #ebeef5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .alarm-level {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        
        &.warning {
          background-color: #fdf6ec;
          color: #e6a23c;
        }
        
        &.error {
          background-color: #fde2e2;
          color: #f56c6c;
        }
      }
      
      .alarm-content {
        flex: 1;
        
        .alarm-title {
          font-size: 14px;
          color: #303133;
          margin-bottom: 4px;
        }
        
        .alarm-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }
}
</style>
