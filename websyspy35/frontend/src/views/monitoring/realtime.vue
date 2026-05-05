<template>
  <div class="realtime-page">
    <div class="page-header">
      <span class="page-title">实时监测</span>
      <el-select v-model="selectedEquipment" placeholder="选择设备" clearable style="width: 220px; margin-right: 15px;" @change="handleEquipmentChange">
        <el-option
          v-for="item in equipmentList"
          :key="item.id"
          :label="item.name"
          :value="item.id"
        />
      </el-select>
      <el-button type="primary" @click="handleRefresh">
        <el-icon><Refresh /></el-icon>
        刷新数据
      </el-button>
      <el-switch
        v-model="autoRefresh"
        active-text="自动刷新"
        style="margin-left: 15px;"
        @change="handleAutoRefresh"
      />
    </div>
    
    <el-row :gutter="20">
      <el-col :span="6" v-for="sensor in sensorList" :key="sensor.id">
        <el-card class="sensor-card" :class="getSensorCardClass(sensor)">
          <div class="sensor-header">
            <span class="sensor-name">{{ sensor.name }}</span>
            <el-tag :class="getSensorStatusClass(sensor)" size="small">
              {{ getSensorStatus(sensor) }}
            </el-tag>
          </div>
          <div class="sensor-info">
            <div class="sensor-type">{{ sensor.type }}</div>
            <div class="sensor-device">{{ getEquipmentName(sensor.equipment_id) }}</div>
          </div>
          <div class="sensor-value">
            <span class="value">{{ getLatestValue(sensor.id) }}</span>
            <span class="unit">{{ sensor.unit || '' }}</span>
          </div>
          <div class="sensor-range">
            正常范围: {{ sensor.min_threshold || '-' }} - {{ sensor.max_threshold || '-' }}
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据趋势图</span>
          <el-select v-model="chartSensorId" placeholder="选择传感器" clearable style="width: 200px;" @change="handleChartSensorChange">
            <el-option
              v-for="item in sensorList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </div>
      </template>
      <div ref="chartRef" style="height: 350px;"></div>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <span>实时数据列表</span>
      </template>
      <el-table :data="realtimeData" stripe v-loading="loading">
        <el-table-column prop="sensor_name" label="传感器" width="180" />
        <el-table-column prop="equipment_name" label="所属设备" width="150" />
        <el-table-column prop="value" label="数值" width="120">
          <template #default="scope">
            <span :class="getValueClass(scope.row)">{{ scope.row.value }}</span>
            <span style="margin-left: 5px; color: #909399;">{{ scope.row.unit || '' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :class="getDataStatusClass(scope.row.status)" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="record_time" label="采集时间" width="180" />
        <el-table-column prop="description" label="说明" show-overflow-tooltip />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getSensorDataList, getSensorDataStatistics, createSensorData } from '@/api/monitoring'
import { getEquipmentList, getSensorList } from '@/api/equipment'

const loading = ref(false)
const chartRef = ref(null)
let chartInstance = null
let refreshTimer = null

const equipmentList = ref([])
const sensorList = ref([])
const selectedEquipment = ref(null)
const autoRefresh = ref(true)
const chartSensorId = ref(null)
const realtimeData = ref([])
const latestValues = reactive({})

const initChart = () => {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['数值']
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
      data: []
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '数值',
        type: 'line',
        smooth: true,
        areaStyle: {
          opacity: 0.3
        },
        data: []
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const updateChart = (dataList) => {
  if (!chartInstance || !dataList || dataList.length === 0) return
  
  const times = dataList.map(item => item.record_time || item.timestamp)
  const values = dataList.map(item => parseFloat(item.value))
  
  chartInstance.setOption({
    xAxis: {
      data: times
    },
    series: [
      {
        data: values
      }
    ]
  })
}

const getEquipmentName = (id) => {
  const item = equipmentList.value.find(e => e.id === id)
  return item ? item.name : '-'
}

const getLatestValue = (sensorId) => {
  return latestValues[sensorId] !== undefined ? latestValues[sensorId] : '--'
}

const getSensorStatus = (sensor) => {
  const value = parseFloat(getLatestValue(sensor.id))
  if (isNaN(value)) return '正常'
  
  if (sensor.min_threshold !== null && sensor.min_threshold !== undefined && value < sensor.min_threshold) {
    return '预警'
  }
  if (sensor.max_threshold !== null && sensor.max_threshold !== undefined && value > sensor.max_threshold) {
    return '报警'
  }
  return '正常'
}

const getSensorCardClass = (sensor) => {
  const status = getSensorStatus(sensor)
  if (status === '报警') return 'sensor-card-alarm'
  if (status === '预警') return 'sensor-card-warning'
  return 'sensor-card-normal'
}

const getSensorStatusClass = (sensor) => {
  const status = getSensorStatus(sensor)
  const classMap = {
    '正常': 'status-tag normal',
    '预警': 'status-tag warning',
    '报警': 'status-tag danger'
  }
  return classMap[status] || 'status-tag normal'
}

const getDataStatusClass = (status) => {
  const classMap = {
    '正常': 'status-tag normal',
    '预警': 'status-tag warning',
    '报警': 'status-tag danger'
  }
  return classMap[status] || 'status-tag normal'
}

const getValueClass = (row) => {
  if (row.status === '报警') return 'value-danger'
  if (row.status === '预警') return 'value-warning'
  return ''
}

const fetchEquipmentList = async () => {
  try {
    const res = await getEquipmentList({ limit: 1000 })
    equipmentList.value = res
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

const fetchSensorList = async () => {
  try {
    const params = {}
    if (selectedEquipment.value) {
      params.equipment_id = selectedEquipment.value
    }
    const res = await getSensorList(params)
    sensorList.value = res
    
    if (sensorList.value.length > 0 && !chartSensorId.value) {
      chartSensorId.value = sensorList.value[0].id
    }
  } catch (error) {
    console.error('获取传感器列表失败:', error)
  }
}

const fetchSensorData = async () => {
  loading.value = true
  try {
    const params = {
      limit: 50,
      order_by: 'record_time',
      order_dir: 'desc'
    }
    if (chartSensorId.value) {
      params.sensor_id = chartSensorId.value
    }
    
    const res = await getSensorDataList(params)
    realtimeData.value = res || []
    
    res.forEach(item => {
      if (item.sensor_id !== undefined && item.value !== undefined) {
        latestValues[item.sensor_id] = item.value
      }
    })
    
    if (chartSensorId.value) {
      const chartParams = {
        sensor_id: chartSensorId.value,
        limit: 20,
        order_by: 'record_time',
        order_dir: 'desc'
      }
      const chartRes = await getSensorDataList(chartParams)
      const sortedData = [...chartRes].reverse()
      updateChart(sortedData)
    }
  } catch (error) {
    console.error('获取传感器数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleEquipmentChange = () => {
  fetchSensorList()
  fetchSensorData()
}

const handleRefresh = () => {
  fetchSensorData()
  ElMessage.success('数据已刷新')
}

const handleAutoRefresh = (val) => {
  if (val) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const handleChartSensorChange = () => {
  fetchSensorData()
}

const startAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
  refreshTimer = setInterval(() => {
    fetchSensorData()
  }, 5000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  fetchEquipmentList()
  fetchSensorList()
  fetchSensorData()
  nextTick(() => {
    initChart()
  })
  
  if (autoRefresh.value) {
    startAutoRefresh()
  }
})

onUnmounted(() => {
  stopAutoRefresh()
  if (chartInstance) {
    chartInstance.dispose()
  }
})
</script>

<style lang="scss" scoped>
.realtime-page {
  padding: 20px;
  
  .page-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .page-title {
      font-size: 18px;
      font-weight: 600;
      margin-right: 20px;
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .sensor-card {
    margin-bottom: 20px;
    
    &.sensor-card-normal {
      border-left: 4px solid #67c23a;
    }
    
    &.sensor-card-warning {
      border-left: 4px solid #e6a23c;
      background-color: #fdf6ec;
    }
    
    &.sensor-card-alarm {
      border-left: 4px solid #f56c6c;
      background-color: #fef0f0;
    }
    
    .sensor-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      
      .sensor-name {
        font-size: 16px;
        font-weight: 600;
      }
    }
    
    .sensor-info {
      color: #909399;
      font-size: 13px;
      margin-bottom: 10px;
      
      .sensor-type {
        margin-right: 10px;
      }
    }
    
    .sensor-value {
      margin-bottom: 10px;
      
      .value {
        font-size: 28px;
        font-weight: 600;
        color: #409eff;
      }
      
      .unit {
        font-size: 14px;
        color: #909399;
        margin-left: 5px;
      }
    }
    
    .sensor-range {
      font-size: 12px;
      color: #909399;
    }
  }
  
  .value-danger {
    color: #f56c6c;
    font-weight: 600;
  }
  
  .value-warning {
    color: #e6a23c;
    font-weight: 600;
  }
}
</style>
