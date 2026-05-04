<template>
  <!-- 流水对账页面 -->
  <div class="reconcile-page">
    <!-- 日期选择和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="对账日期">
          <el-date-picker
            v-model="searchForm.date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 180px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadReconcileData">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button type="success" @click="loadToday">
            <el-icon><Calendar /></el-icon>
            今日
          </el-button>
          <el-button @click="loadData">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#409EFF"><List /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ reconcileData?.order_stats?.total || 0 }}</div>
              <div class="stat-label">总订单数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#67C23A"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ reconcileData?.order_stats?.paid || 0 }}</div>
              <div class="stat-label">已支付</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#E6A23C"><Clock /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ reconcileData?.order_stats?.pending || 0 }}</div>
              <div class="stat-label">待支付</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#F56C6C"><Money /></el-icon>
            <div class="stat-info">
              <div class="stat-value">¥{{ (reconcileData?.payment_stats?.total_amount || 0).toFixed(2) }}</div>
              <div class="stat-label">实收金额</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <!-- 支付方式统计 -->
      <el-col :span="8">
        <el-card class="method-card">
          <template #header>
            <span>支付方式统计</span>
          </template>
          
          <el-table :data="methodStats" border v-loading="loading">
            <el-table-column prop="method" label="支付方式" />
            <el-table-column prop="count" label="笔数" width="100">
              <template #default="{ row }">
                <span class="text-primary">{{ row.count }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="150">
              <template #default="{ row }">
                <span class="text-danger">¥{{ row.amount.toFixed(2) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <!-- 订单统计详情 -->
      <el-col :span="16">
        <el-card class="order-stats-card">
          <template #header>
            <span>订单统计详情</span>
          </template>
          
          <el-descriptions :column="2" border>
            <el-descriptions-item label="总订单金额">
              <span class="text-primary">¥{{ (reconcileData?.order_stats?.total_amount || 0).toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="优惠金额">
              <span class="text-success">-¥{{ (reconcileData?.order_stats?.discount_amount || 0).toFixed(2) }}</span>
            </el-descriptions-item>
            <el-descriptions-item label="实际收款">
              <span class="text-danger" style="font-size: 18px; font-weight: bold;">
                ¥{{ (reconcileData?.order_stats?.actual_amount || 0).toFixed(2) }}
              </span>
            </el-descriptions-item>
            <el-descriptions-item label="已取消订单">
              {{ reconcileData?.order_stats?.cancelled || 0 }} 笔
            </el-descriptions-item>
          </el-descriptions>
          
          <el-divider />
          
          <div class="action-bar">
            <el-button type="primary" @click="exportReconcile">
              <el-icon><Download /></el-icon>
              导出对账报表
            </el-button>
            <el-button type="success" @click="viewOrders">
              <el-icon><View /></el-icon>
              查看订单列表
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 订单列表（展开显示） -->
    <el-card v-if="showOrders" class="orders-card">
      <template #header>
        <div class="card-header">
          <span>当日订单列表</span>
          <el-button type="text" size="small" @click="showOrders = false">
            <el-icon><Close /></el-icon>
            关闭
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="ordersData"
        v-loading="ordersLoading"
        border
        stripe
      >
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="order_type" label="类型" width="80">
          <template #default="{ row }">
            <el-tag :type="row.order_type === 'recharge' ? 'warning' : 'primary'" size="small">
              {{ row.order_type === 'recharge' ? '充值' : '消费' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="member_name" label="会员" width="100">
          <template #default="{ row }">
            {{ row.member_name || '散客' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="商品金额" width="100">
          <template #default="{ row }">
            ¥{{ row.total_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="discount_amount" label="优惠" width="80">
          <template #default="{ row }">
            <span v-if="row.discount_amount > 0" class="text-success">-¥{{ row.discount_amount?.toFixed(2) }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="actual_amount" label="实付" width="100">
          <template #default="{ row }">
            <span class="text-danger">¥{{ row.actual_amount?.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            {{ getPaymentMethod(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_time" label="时间" width="160">
          <template #default="{ row }">
            {{ row.order_time ? formatDateTime(row.order_time) : '-' }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 搜索表单
const searchForm = reactive({
  date: dayjs().format('YYYY-MM-DD')
})

// 对账数据
const reconcileData = ref(null)
const loading = ref(false)
const showOrders = ref(false)
const ordersData = ref([])
const ordersLoading = ref(false)

// 支付方式统计
const methodStats = computed(() => {
  if (!reconcileData.value?.payment_stats?.by_method) return []
  
  const methodMap = {
    cash: '现金',
    wechat: '微信支付',
    alipay: '支付宝',
    card: '会员卡'
  }
  
  const stats = []
  const byMethod = reconcileData.value.payment_stats.by_method
  
  for (const [key, value] of Object.entries(byMethod)) {
    if (value > 0 || (reconcileData.value.payment_stats.total_amount > 0)) {
      stats.push({
        method: methodMap[key] || key,
        count: reconcileData.value.payment_stats.total_count || 0,
        amount: value
      })
    }
  }
  
  return stats
})

// 获取支付方式文本
const getPaymentMethod = (method) => {
  const map = {
    cash: '现金',
    wechat: '微信支付',
    alipay: '支付宝',
    card: '会员卡'
  }
  return map[method] || method
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    pending: 'warning',
    paid: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待支付',
    paid: '已支付',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 加载对账数据
const loadReconcileData = async () => {
  loading.value = true
  try {
    const res = await api.getDailyReconcile(searchForm.date)
    if (res.success) {
      reconcileData.value = res.data
    }
  } catch (error) {
    console.error('加载对账数据失败:', error)
    ElMessage.error('加载对账数据失败')
  } finally {
    loading.value = false
  }
}

// 加载今日数据
const loadToday = () => {
  searchForm.date = dayjs().format('YYYY-MM-DD')
  loadReconcileData()
}

// 查看订单列表
const viewOrders = async () => {
  showOrders.value = true
  ordersLoading.value = true
  try {
    const res = await api.getOrders({
      start_date: searchForm.date,
      end_date: searchForm.date,
      page_size: 100
    })
    ordersData.value = res.items || []
  } catch (error) {
    console.error('加载订单失败:', error)
    ElMessage.error('加载订单失败')
  } finally {
    ordersLoading.value = false
  }
}

// 导出对账报表
const exportReconcile = () => {
  ElMessage.success('导出功能开发中...')
}

onMounted(() => {
  loadReconcileData()
})
</script>

<style scoped>
.reconcile-page {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

/* 文本样式 */
.text-primary {
  color: #409EFF;
  font-weight: bold;
}

.text-success {
  color: #67C23A;
  font-weight: bold;
}

.text-danger {
  color: #F56C6C;
  font-weight: bold;
}

/* 操作栏 */
.action-bar {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

/* 订单卡片 */
.orders-card {
  margin-top: 20px;
}
</style>
