<template>
  <div class="dashboard">
    <el-row :gutter="20" class="mb-20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon users">
              <el-icon size="30"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_users }}</div>
              <div class="stat-label">总用户数</div>
              <div class="stat-change">今日新增 +{{ stats.today_users }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon orders">
              <el-icon size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_orders }}</div>
              <div class="stat-label">总订单数</div>
              <div class="stat-change">今日新增 +{{ stats.today_orders }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon amount">
              <el-icon size="30"><Wallet /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ stats.total_amount?.toFixed(2) }}</div>
              <div class="stat-label">总回收金额</div>
              <div class="stat-change">今日 +¥{{ stats.today_amount?.toFixed(2) }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon weight">
              <el-icon size="30"><ScaleToOriginal /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_weight?.toFixed(2) }}kg</div>
              <div class="stat-label">总回收重量</div>
              <div class="stat-change">今日 +{{ stats.today_weight?.toFixed(2) }}kg</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mb-20">
      <el-col :span="8">
        <el-card class="quick-actions">
          <template #header>
            <span>快捷操作</span>
          </template>
          <el-row :gutter="10">
            <el-col :span="12" class="mb-10">
              <el-button type="primary" size="large" style="width: 100%;" @click="$router.push('/orders')">
                <el-icon><Document /></el-icon>
                <span>处理订单</span>
              </el-button>
            </el-col>
            <el-col :span="12" class="mb-10">
              <el-button type="success" size="large" style="width: 100%;" @click="$router.push('/feedbacks')">
                <el-icon><ChatDotRound /></el-icon>
                <span>处理反馈</span>
              </el-button>
            </el-col>
            <el-col :span="12">
              <el-button type="warning" size="large" style="width: 100%;" @click="$router.push('/announcements')">
                <el-icon><Edit /></el-icon>
                <span>发布公告</span>
              </el-button>
            </el-col>
            <el-col :span="12">
              <el-button type="info" size="large" style="width: 100%;" @click="$router.push('/consultations')">
                <el-icon><ChatLineSquare /></el-icon>
                <span>处理咨询</span>
              </el-button>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>待办事项</span>
          </template>
          <el-table :data="todos" style="width: 100%" size="small">
            <el-table-column prop="title" label="事项" />
            <el-table-column prop="count" label="数量" width="80" align="center">
              <template #default="{ row }">
                <el-tag type="danger" v-if="row.count > 0">{{ row.count }}</el-tag>
                <span v-else class="text-success">0</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="80" align="center">
              <template #default="{ row }">
                <el-button type="primary" link size="small" @click="handleTodoAction(row)">查看</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>回收人员排行</span>
          </template>
          <el-table :data="recyclerRanking" style="width: 100%" size="small">
            <el-table-column label="排名" width="60" align="center">
              <template #default="{ $index }">
                <el-tag v-if="$index < 3" :type="['danger', 'warning', 'success'][$index]">{{ $index + 1 }}</el-tag>
                <span v-else>{{ $index + 1 }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="real_name" label="姓名" width="80" />
            <el-table-column prop="completed_orders" label="完成订单" width="80" align="center" />
            <el-table-column prop="complete_rate" label="完成率">
              <template #default="{ row }">
                <span>{{ row.complete_rate }}%</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>回收趋势（最近30天）</span>
          </template>
          <div ref="trendChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>用户增长趋势（最近30天）</span>
          </template>
          <div ref="userGrowthChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" class="mt-20">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>分类回收统计</span>
          </template>
          <div ref="categoryChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>积分兑换统计</span>
          </template>
          <div ref="pointsChartRef" class="chart-container"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { 
  getDashboardStats, 
  getRecyclingTrend, 
  getUserGrowth,
  getCategoryStats,
  getPointsExchangeStats,
  getRecyclerPerformance
} from '@/api'

const router = useRouter()

const stats = ref({
  total_users: 0,
  today_users: 0,
  total_orders: 0,
  today_orders: 0,
  total_amount: 0,
  today_amount: 0,
  total_weight: 0,
  today_weight: 0,
  pending_feedbacks: 0,
  pending_orders: 0,
  exception_orders: 0
})

const todos = ref([])
const recyclerRanking = ref([])

const trendChartRef = ref(null)
const userGrowthChartRef = ref(null)
const categoryChartRef = ref(null)
const pointsChartRef = ref(null)

let trendChart = null
let userGrowthChart = null
let categoryChart = null
let pointsChart = null

const loadData = async () => {
  try {
    const [statsRes, trendRes, growthRes, categoryRes, pointsRes, recyclerRes] = await Promise.all([
      getDashboardStats(),
      getRecyclingTrend(30),
      getUserGrowth(30),
      getCategoryStats(),
      getPointsExchangeStats(30),
      getRecyclerPerformance(10)
    ])
    
    stats.value = statsRes.data || {}
    
    todos.value = [
      { title: '待处理订单', count: stats.value.pending_orders || 0, action: '/orders' },
      { title: '异常订单', count: stats.value.exception_orders || 0, action: '/orders?status=5' },
      { title: '待处理反馈', count: stats.value.pending_feedbacks || 0, action: '/feedbacks' },
      { title: '待发货兑换', count: 0, action: '/points-exchanges?status=0' }
    ]
    
    recyclerRanking.value = recyclerRes.data || []
    
    await nextTick()
    
    renderTrendChart(trendRes.data || [])
    renderUserGrowthChart(growthRes.data || [])
    renderCategoryChart(categoryRes.data || [])
    renderPointsChart(pointsRes.data || {})
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

const renderTrendChart = (data) => {
  if (!trendChartRef.value) return
  
  trendChart = echarts.init(trendChartRef.value)
  
  const dates = data.map(item => item.date)
  const orderCounts = data.map(item => item.order_count)
  const amounts = data.map(item => item.total_amount)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['订单数', '回收金额']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: [
      {
        type: 'value',
        name: '订单数'
      },
      {
        type: 'value',
        name: '金额(元)'
      }
    ],
    series: [
      {
        name: '订单数',
        type: 'bar',
        data: orderCounts,
        itemStyle: {
          color: '#409EFF'
        }
      },
      {
        name: '回收金额',
        type: 'line',
        yAxisIndex: 1,
        data: amounts,
        itemStyle: {
          color: '#67C23A'
        }
      }
    ]
  }
  
  trendChart.setOption(option)
}

const renderUserGrowthChart = (data) => {
  if (!userGrowthChartRef.value) return
  
  userGrowthChart = echarts.init(userGrowthChartRef.value)
  
  const dates = data.map(item => item.date)
  const newUsers = data.map(item => item.new_users)
  const cumulative = data.map(item => item.cumulative_users)
  
  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['新增用户', '累计用户']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '新增用户',
        type: 'bar',
        data: newUsers,
        itemStyle: {
          color: '#E6A23C'
        }
      },
      {
        name: '累计用户',
        type: 'line',
        smooth: true,
        data: cumulative,
        itemStyle: {
          color: '#F56C6C'
        }
      }
    ]
  }
  
  userGrowthChart.setOption(option)
}

const renderCategoryChart = (data) => {
  if (!categoryChartRef.value) return
  
  categoryChart = echarts.init(categoryChartRef.value)
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}件 ({d}%)'
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 10,
      top: 20,
      bottom: 20
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['40%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          }
        },
        data: data.map(item => ({
          name: item.category_name || '其他',
          value: item.item_count
        }))
      }
    ]
  }
  
  categoryChart.setOption(option)
}

const renderPointsChart = (data) => {
  if (!pointsChartRef.value) return
  
  pointsChart = echarts.init(pointsChartRef.value)
  
  const statusData = Object.entries(data.status_distribution || {}).map(([name, value]) => ({
    name,
    value
  }))
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c}次 ({d}%)'
    },
    legend: {
      top: 'bottom'
    },
    series: [
      {
        type: 'pie',
        radius: ['30%', '60%'],
        center: ['50%', '45%'],
        data: statusData.length > 0 ? statusData : [
          { name: '待发货', value: 0 },
          { name: '已发货', value: 0 },
          { name: '已收货', value: 0 },
          { name: '已取消', value: 0 }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }
  
  pointsChart.setOption(option)
}

const handleTodoAction = (row) => {
  router.push(row.action)
}

onMounted(() => {
  loadData()
  
  window.addEventListener('resize', () => {
    trendChart?.resize()
    userGrowthChart?.resize()
    categoryChart?.resize()
    pointsChart?.resize()
  })
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stat-card {
    .stat-content {
      display: flex;
      align-items: center;
      
      .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff;
        
        &.users {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        &.orders {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }
        &.amount {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }
        &.weight {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }
      }
      
      .stat-info {
        margin-left: 15px;
        
        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: #303133;
        }
        
        .stat-label {
          font-size: 14px;
          color: #909399;
          margin: 5px 0;
        }
        
        .stat-change {
          font-size: 12px;
          color: #67c23a;
        }
      }
    }
  }
  
  .chart-container {
    height: 300px;
  }
  
  .mt-20 {
    margin-top: 20px;
  }
  
  .text-success {
    color: #67c23a;
  }
}
</style>
