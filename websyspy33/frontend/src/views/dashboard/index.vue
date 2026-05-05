<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value">{{ stats.suppliers }}</div>
              <div class="stat-label">供应商总数</div>
            </div>
            <div class="stat-icon icon-blue">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value">{{ stats.productions }}</div>
              <div class="stat-label">本月生产批次</div>
            </div>
            <div class="stat-icon icon-green">
              <el-icon><Timer /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value">{{ stats.inspections }}</div>
              <div class="stat-label">原材料检验</div>
            </div>
            <div class="stat-icon icon-orange">
              <el-icon><Search /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-value">{{ stats.qualityRate }}%</div>
              <div class="stat-label">质量合格率</div>
            </div>
            <div class="stat-icon icon-purple">
              <el-icon><TrendCharts /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>生产质量趋势</span>
          </template>
          <div ref="chartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>供应商等级分布</span>
          </template>
          <div ref="pieChartRef" style="height: 350px;"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>近期生产批次</span>
            <el-link type="primary" :underline="false" style="float: right;" @click="$router.push('/production/batches')">
              查看全部
            </el-link>
          </template>
          <el-table :data="recentBatches" style="width: 100%">
            <el-table-column prop="batch_no" label="批次号" width="150" />
            <el-table-column prop="project_name" label="工程项目" show-overflow-tooltip />
            <el-table-column prop="strength_grade" label="强度等级" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>近期质量报告</span>
            <el-link type="primary" :underline="false" style="float: right;" @click="$router.push('/quality-reports')">
              查看全部
            </el-link>
          </template>
          <el-table :data="recentReports" style="width: 100%">
            <el-table-column prop="report_no" label="报告编号" width="130" />
            <el-table-column prop="report_type" label="报告类型" width="120" />
            <el-table-column prop="overall_result" label="结果" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.is_qualified ? 'success' : 'danger'" size="small">
                  {{ scope.row.overall_result }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="report_date" label="报告日期" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const stats = ref({
  suppliers: 15,
  productions: 32,
  inspections: 68,
  qualityRate: 96.5
})

const recentBatches = ref([
  { batch_no: 'PB20241201001', project_name: '市民中心建设项目', strength_grade: 'C30', status: '已完成' },
  { batch_no: 'PB20241201002', project_name: '地铁一号线工程', strength_grade: 'C35', status: '生产中' },
  { batch_no: 'PB20241201003', project_name: '商业综合体项目', strength_grade: 'C40', status: '已完成' },
  { batch_no: 'PB20241201004', project_name: '住宅小区一期', strength_grade: 'C25', status: '待生产' }
])

const recentReports = ref([
  { report_no: 'QR20241201001', report_type: '出厂合格证', overall_result: '合格', is_qualified: true, report_date: '2024-12-01' },
  { report_no: 'QR20241201002', report_type: '质量追溯报告', overall_result: '合格', is_qualified: true, report_date: '2024-12-01' },
  { report_no: 'QR20241201003', report_type: '强度检测报告', overall_result: '不合格', is_qualified: false, report_date: '2024-11-30' }
])

const chartRef = ref(null)
const pieChartRef = ref(null)

const getStatusType = (status) => {
  const typeMap = {
    '已完成': 'success',
    '生产中': 'warning',
    '待生产': 'info'
  }
  return typeMap[status] || 'info'
}

const initLineChart = () => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['水胶比偏差', '生产批次']
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
      data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    },
    yAxis: [
      {
        type: 'value',
        name: '偏差率(%)',
        position: 'left'
      },
      {
        type: 'value',
        name: '批次数量',
        position: 'right'
      }
    ],
    series: [
      {
        name: '水胶比偏差',
        type: 'line',
        smooth: true,
        data: [1.2, 0.8, 1.5, 0.9, 1.1, 1.3, 0.7],
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '生产批次',
        type: 'bar',
        yAxisIndex: 1,
        data: [5, 8, 6, 7, 4, 3, 2],
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

const initPieChart = () => {
  if (!pieChartRef.value) return
  
  const chart = echarts.init(pieChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '供应商等级',
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
          formatter: '{b}: {c}家 ({d}%)'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 16,
            fontWeight: 'bold'
          }
        },
        data: [
          { value: 5, name: 'A级供应商', itemStyle: { color: '#67C23A' } },
          { value: 7, name: 'B级供应商', itemStyle: { color: '#E6A23C' } },
          { value: 3, name: 'C级供应商', itemStyle: { color: '#F56C6C' } }
        ]
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

onMounted(() => {
  initLineChart()
  initPieChart()
})
</script>

<style scoped>
.dashboard-container {
  padding: 0;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1.5;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: #fff;
}

.icon-blue {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.icon-green {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.icon-orange {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
}

.icon-purple {
  background: linear-gradient(135deg, #909399, #a6a9ad);
}
</style>
