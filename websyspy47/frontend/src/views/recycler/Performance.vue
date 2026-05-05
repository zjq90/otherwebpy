<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">绩效考核</span>
    </div>
    
    <el-row :gutter="20" class="mb-20">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
              <el-icon :size="30"><Trophy /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ totalRecyclers }}</div>
              <div class="stat-label">回收人员总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);">
              <el-icon :size="30"><Star /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ excellentCount }}</div>
              <div class="stat-label">优秀员工数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-card">
            <div class="stat-icon" style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);">
              <el-icon :size="30"><Medal /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ avgScore || 0 }}分</div>
              <div class="stat-label">平均绩效分</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="回收人员">
          <el-select v-model="searchForm.recycler_id" placeholder="全部" clearable style="width: 150px">
            <el-option
              v-for="item in recyclerList"
              :key="item.id"
              :label="item.real_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="考核周期">
          <el-select v-model="searchForm.period_type" placeholder="全部" clearable>
            <el-option label="月度" :value="0" />
            <el-option label="季度" :value="1" />
            <el-option label="年度" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="考核年份">
          <el-select v-model="searchForm.year" placeholder="全部" clearable>
            <el-option 
              v-for="year in yearList" 
              :key="year" 
              :label="year + '年'" 
              :value="year" 
            />
          </el-select>
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
    
    <el-card class="table-container">
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="recycler_name" label="回收人员" />
        <el-table-column prop="period_type" label="考核周期" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="periodTypeMap[row.period_type]">
              {{ periodTypeLabelMap[row.period_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="year_month" label="考核年月" width="120" align="center">
          <template #default="{ row }">
            {{ row.year }}年{{ row.month || '-' }}月
          </template>
        </el-table-column>
        <el-table-column prop="order_count" label="订单数" width="80" align="center" />
        <el-table-column prop="completed_count" label="完成数" width="80" align="center">
          <template #default="{ row }">
            <span style="color: #67c23a;">{{ row.completed_count || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="回收金额" width="120" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600;">¥{{ row.total_amount || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="评分" width="120" align="center">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.score || 0" 
              :color="getScoreColor(row.score)"
              :stroke-width="10"
              :text-inside="true"
            />
          </template>
        </el-table-column>
        <el-table-column prop="grade" label="等级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getGradeType(row.grade)" size="large">
              {{ gradeMap[row.grade] || row.grade }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="comment" label="考核意见" min-width="150" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>绩效等级分布</span>
          </template>
          <div ref="gradeChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>月度绩效趋势</span>
          </template>
          <div ref="trendChartRef" style="height: 300px;"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { getPerformanceList, getRecyclerList } from '@/api'

const loading = ref(false)
const tableData = ref([])
const recyclerList = ref([])
const gradeChartRef = ref(null)
const trendChartRef = ref(null)

let gradeChart = null
let trendChart = null

const searchForm = reactive({
  recycler_id: null,
  period_type: null,
  year: null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const totalRecyclers = ref(0)
const excellentCount = ref(0)
const avgScore = ref(0)

const yearList = computed(() => {
  const currentYear = dayjs().year()
  const years = []
  for (let i = 0; i < 5; i++) {
    years.push(currentYear - i)
  }
  return years
})

const periodTypeMap = {
  0: 'info',
  1: 'primary',
  2: 'success'
}

const periodTypeLabelMap = {
  0: '月度',
  1: '季度',
  2: '年度'
}

const gradeMap = {
  'A': '优秀',
  'B': '良好',
  'C': '合格',
  'D': '待改进'
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const getScoreColor = (score) => {
  if (!score) return '#909399'
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getGradeType = (grade) => {
  switch (grade) {
    case 'A': return 'success'
    case 'B': return 'primary'
    case 'C': return 'warning'
    case 'D': return 'danger'
    default: return 'info'
  }
}

const fetchRecyclers = async () => {
  try {
    const res = await getRecyclerList({ page: 1, page_size: 1000 })
    const data = res.data || {}
    recyclerList.value = data.list || []
    totalRecyclers.value = data.total || 0
  } catch (error) {
    console.error('获取回收人员列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    const res = await getPerformanceList(params)
    const data = res.data || {}
    tableData.value = data.list || []
    pagination.total = data.total || 0
    
    calculateStats(data.list || [])
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const calculateStats = (list) => {
  if (list.length === 0) {
    excellentCount.value = 0
    avgScore.value = 0
    return
  }
  
  excellentCount.value = list.filter(item => item.grade === 'A').length
  const totalScore = list.reduce((sum, item) => sum + (item.score || 0), 0)
  avgScore.value = Math.round(totalScore / list.length)
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.recycler_id = null
  searchForm.period_type = null
  searchForm.year = null
  pagination.page = 1
  fetchData()
}

const renderGradeChart = () => {
  if (!gradeChartRef.value) return
  
  if (!gradeChart) {
    gradeChart = echarts.init(gradeChartRef.value)
  }
  
  const gradeData = [
    { value: 3, name: '优秀(A)' },
    { value: 5, name: '良好(B)' },
    { value: 2, name: '合格(C)' },
    { value: 1, name: '待改进(D)' }
  ]
  
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
        name: '绩效等级',
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
          position: 'outside'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: gradeData.map((item, index) => ({
          ...item,
          itemStyle: {
            color: ['#67c23a', '#409eff', '#e6a23c', '#f56c6c'][index]
          }
        }))
      }
    ]
  }
  
  gradeChart.setOption(option)
}

const renderTrendChart = () => {
  if (!trendChartRef.value) return
  
  if (!trendChart) {
    trendChart = echarts.init(trendChartRef.value)
  }
  
  const months = []
  const scores = []
  const currentMonth = dayjs()
  
  for (let i = 5; i >= 0; i--) {
    const month = currentMonth.subtract(i, 'month')
    months.push(month.format('M月'))
    scores.push(Math.floor(Math.random() * 20) + 70)
  }
  
  const option = {
    tooltip: {
      trigger: 'axis'
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
      data: months
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [
      {
        name: '平均绩效',
        type: 'line',
        smooth: true,
        stack: 'Total',
        itemStyle: {
          color: '#667eea'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.1)' }
          ])
        },
        markLine: {
          data: [
            { type: 'average', name: '平均值' }
          ]
        },
        data: scores
      }
    ]
  }
  
  trendChart.setOption(option)
}

const handleResize = () => {
  gradeChart?.resize()
  trendChart?.resize()
}

onMounted(() => {
  fetchRecyclers()
  fetchData()
  window.addEventListener('resize', handleResize)
  
  setTimeout(() => {
    renderGradeChart()
    renderTrendChart()
  }, 100)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  gradeChart?.dispose()
  trendChart?.dispose()
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

.search-form {
  .el-form-item {
    margin-right: 0;
  }
}

.mt-20 {
  margin-top: 20px;
}
</style>
