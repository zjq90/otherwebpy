<template>
  <div class="production-container">
    <el-card>
      <template #header>
        <span>生产质量追踪</span>
      </template>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card" @click="$router.push('/production/batches')">
            <div class="card-content">
              <div class="card-icon icon-blue">
                <el-icon size="32"><List /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-title">生产批次</div>
                <div class="card-desc">管理混凝土生产批次</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card" @click="$router.push('/production/records')">
            <div class="card-content">
              <div class="card-icon icon-green">
                <el-icon size="32"><Reading /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-title">生产记录</div>
                <div class="card-desc">查看每盘生产详细记录</div>
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="8">
          <el-card shadow="hover" class="stat-card" @click="$router.push('/mix-designs')">
            <div class="card-content">
              <div class="card-icon icon-orange">
                <el-icon size="32"><Document /></el-icon>
              </div>
              <div class="card-info">
                <div class="card-title">配比设计</div>
                <div class="card-desc">管理混凝土配合比设计</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>今日生产统计</span>
            </template>
            <el-table :data="todayStats" style="width: 100%">
              <el-table-column prop="strength_grade" label="强度等级" width="100" />
              <el-table-column prop="batch_count" label="批次数量" width="100" />
              <el-table-column prop="total_volume" label="总方量(m³)" width="120" />
              <el-table-column prop="abnormal_count" label="异常记录" width="100">
                <template #default="scope">
                  <span :class="scope.row.abnormal_count > 0 ? 'text-red' : ''">
                    {{ scope.row.abnormal_count }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="qualify_rate" label="合格率" width="100">
                <template #default="scope">
                  <el-tag :type="scope.row.qualify_rate >= 95 ? 'success' : 'warning'">
                    {{ scope.row.qualify_rate }}%
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card>
            <template #header>
              <span>生产质量趋势</span>
            </template>
            <div ref="chartRef" style="height: 300px;"></div>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px;">
        <el-col :span="24">
          <el-card>
            <template #header>
              <span>近期生产批次</span>
              <el-link type="primary" :underline="false" style="float: right;" @click="$router.push('/production/batches')">
                查看全部
              </el-link>
            </template>
            <el-table :data="recentBatches" style="width: 100%">
              <el-table-column prop="batch_no" label="批次号" width="150" />
              <el-table-column prop="project_name" label="工程项目" min-width="180" show-overflow-tooltip />
              <el-table-column prop="construction_site" label="施工部位" width="120" />
              <el-table-column prop="strength_grade" label="强度等级" width="100">
                <template #default="scope">
                  <el-tag type="primary">{{ scope.row.strength_grade }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="planned_volume" label="计划方量(m³)" width="120" />
              <el-table-column prop="actual_volume" label="实际方量(m³)" width="120">
                <template #default="scope">
                  {{ scope.row.actual_volume || '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="operator" label="操作员" width="100" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusType(scope.row.status)" effect="dark">
                    {{ scope.row.status }}
                  </el-tag>
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
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const chartRef = ref(null)

const todayStats = ref([
  { strength_grade: 'C30', batch_count: 5, total_volume: 185.5, abnormal_count: 0, qualify_rate: 100.0 },
  { strength_grade: 'C35', batch_count: 3, total_volume: 120.0, abnormal_count: 1, qualify_rate: 96.7 },
  { strength_grade: 'C25', batch_count: 2, total_volume: 80.0, abnormal_count: 0, qualify_rate: 100.0 }
])

const recentBatches = ref([
  {
    batch_no: 'PB20241201001',
    project_name: '市民中心建设项目',
    construction_site: '主体结构',
    strength_grade: 'C30',
    planned_volume: 200.0,
    actual_volume: 205.5,
    operator: '操作员甲',
    status: '已完成'
  },
  {
    batch_no: 'PB20241201002',
    project_name: '地铁一号线工程',
    construction_site: '基础工程',
    strength_grade: 'C35',
    planned_volume: 350.0,
    actual_volume: null,
    operator: '操作员乙',
    status: '生产中'
  },
  {
    batch_no: 'PB20241201003',
    project_name: '商业综合体项目',
    construction_site: '地下室',
    strength_grade: 'C40',
    planned_volume: 500.0,
    actual_volume: null,
    operator: '操作员丙',
    status: '待生产'
  },
  {
    batch_no: 'PB20241201004',
    project_name: '住宅小区一期',
    construction_site: '地面层',
    strength_grade: 'C25',
    planned_volume: 150.0,
    actual_volume: 152.0,
    operator: '操作员丁',
    status: '已完成'
  }
])

const getStatusType = (status) => {
  const typeMap = {
    '待生产': 'info',
    '生产中': 'warning',
    '已完成': 'success'
  }
  return typeMap[status] || 'info'
}

const initChart = () => {
  if (!chartRef.value) return
  
  const chart = echarts.init(chartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['水胶比偏差', '合格批次'],
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
        name: '合格批次',
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
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      },
      {
        name: '合格批次',
        type: 'bar',
        yAxisIndex: 1,
        data: [8, 10, 7, 9, 6, 4, 2],
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart.resize())
}

onMounted(() => {
  initChart()
})
</script>

<style scoped>
.production-container {
  padding: 0;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.card-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.card-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
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

.card-info {
  flex: 1;
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.card-desc {
  font-size: 14px;
  color: #909399;
}

.text-red {
  color: #F56C6C;
  font-weight: bold;
}
</style>
