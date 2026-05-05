<template>
  <div class="history-page">
    <div class="page-header">
      <span class="page-title">历史数据</span>
    </div>
    
    <el-card class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="设备">
          <el-select v-model="searchForm.equipment_id" placeholder="请选择设备" clearable style="width: 200px;" @change="handleEquipmentChange">
            <el-option
              v-for="item in equipmentList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="传感器">
          <el-select v-model="searchForm.sensor_id" placeholder="请选择传感器" clearable style="width: 200px;">
            <el-option
              v-for="item in filteredSensorList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="时间范围">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 350px;"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据趋势图</span>
        </div>
      </template>
      <div ref="chartRef" style="height: 350px;"></div>
    </el-card>
    
    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>数据列表</span>
          <el-button type="primary" size="small" @click="handleExport">
            <el-icon><Download /></el-icon>
            导出数据
          </el-button>
        </div>
      </template>
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
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
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
        style="margin-top: 15px;"
      />
    </el-card>
    
    <el-dialog
      v-model="detailVisible"
      title="数据详情"
      width="500px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="传感器">{{ detailData.sensor_name }}</el-descriptions-item>
        <el-descriptions-item label="所属设备">{{ detailData.equipment_name }}</el-descriptions-item>
        <el-descriptions-item label="数值">
          <span :class="getValueClass(detailData)">{{ detailData.value }}</span>
          <span style="margin-left: 5px;">{{ detailData.unit || '' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :class="getDataStatusClass(detailData.status)" size="small">
            {{ detailData.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="采集时间">{{ detailData.record_time }}</el-descriptions-item>
        <el-descriptions-item label="说明">{{ detailData.description || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detailData.created_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { ElMessage } from 'element-plus'
import { Search, Refresh, Download, View } from '@element-plus/icons-vue'
import { getSensorDataList, getSensorDataStatistics } from '@/api/monitoring'
import { getEquipmentList, getSensorList } from '@/api/equipment'

const loading = ref(false)
const detailVisible = ref(false)
const chartRef = ref(null)
let chartInstance = null

const equipmentList = ref([])
const sensorList = ref([])

const searchForm = reactive({
  equipment_id: null,
  sensor_id: null,
  dateRange: []
})

const filteredSensorList = computed(() => {
  if (searchForm.equipment_id) {
    return sensorList.value.filter(s => s.equipment_id === searchForm.equipment_id)
  }
  return sensorList.value
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const tableData = ref([])
const detailData = reactive({})

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
        markLine: {
          data: [
            { type: 'average', name: '平均值' }
          ]
        },
        data: []
      }
    ]
  }
  
  chartInstance.setOption(option)
}

const updateChart = (dataList) => {
  if (!chartInstance || !dataList || dataList.length === 0) return
  
  const sortedData = [...dataList].sort((a, b) => {
    return new Date(a.record_time) - new Date(b.record_time)
  })
  
  const times = sortedData.map(item => item.record_time)
  const values = sortedData.map(item => parseFloat(item.value))
  
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
    const res = await getSensorList({ limit: 1000 })
    sensorList.value = res
  } catch (error) {
    console.error('获取传感器列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      order_by: 'record_time',
      order_dir: 'desc'
    }
    
    if (searchForm.equipment_id) {
      params.equipment_id = searchForm.equipment_id
    }
    if (searchForm.sensor_id) {
      params.sensor_id = searchForm.sensor_id
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_time = searchForm.dateRange[0]
      params.end_time = searchForm.dateRange[1]
    }
    
    const res = await getSensorDataList(params)
    tableData.value = res || []
    pagination.total = 100
    
    if (searchForm.sensor_id && res && res.length > 0) {
      const chartParams = {
        sensor_id: searchForm.sensor_id,
        limit: 50,
        order_by: 'record_time',
        order_dir: 'desc'
      }
      if (searchForm.dateRange && searchForm.dateRange.length === 2) {
        chartParams.start_time = searchForm.dateRange[0]
        chartParams.end_time = searchForm.dateRange[1]
      }
      const chartRes = await getSensorDataList(chartParams)
      updateChart(chartRes)
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleEquipmentChange = () => {
  searchForm.sensor_id = null
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    equipment_id: null,
    sensor_id: null,
    dateRange: []
  })
  pagination.page = 1
  fetchData()
}

const handleView = (row) => {
  Object.assign(detailData, row)
  detailVisible.value = true
}

const handleExport = () => {
  ElMessage.success('导出功能开发中')
}

onMounted(() => {
  fetchEquipmentList()
  fetchSensorList()
  fetchData()
  nextTick(() => {
    initChart()
  })
})
</script>

<style lang="scss" scoped>
.history-page {
  padding: 20px;
  
  .page-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .page-title {
      font-size: 18px;
      font-weight: 600;
    }
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
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
