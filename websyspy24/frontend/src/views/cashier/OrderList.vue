<template>
  <!-- 订单管理页面 -->
  <div class="order-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="订单号">
          <el-input
            v-model="searchForm.order_no"
            placeholder="请输入订单号"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="searchForm.start_date"
            type="date"
            placeholder="开始日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="searchForm.end_date"
            type="date"
            placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
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
      
      <el-divider />
      
      <div class="action-bar">
        <el-button type="success" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>
    
    <!-- 订单列表表格 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
      >
        <el-table-column prop="order_no" label="订单号" width="180" />
        <el-table-column prop="order_type" label="订单类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.order_type === 'recharge' ? 'warning' : 'primary'" effect="light">
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
            ¥{{ row.total_amount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="discount_amount" label="优惠金额" width="100">
          <template #default="{ row }">
            <span v-if="row.discount_amount > 0" class="text-success">
              -¥{{ row.discount_amount?.toFixed(2) || '0.00' }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="actual_amount" label="实付金额" width="100">
          <template #default="{ row }">
            <span class="text-danger">¥{{ row.actual_amount?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100">
          <template #default="{ row }">
            {{ getPaymentMethod(row.payment_method) }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="light">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="order_time" label="下单时间" width="160">
          <template #default="{ row }">
            {{ row.order_time ? formatDateTime(row.order_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="handleView(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
    
    <!-- 订单详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="订单详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单号">
          {{ currentOrder?.order_no }}
        </el-descriptions-item>
        <el-descriptions-item label="订单类型">
          <el-tag :type="currentOrder?.order_type === 'recharge' ? 'warning' : 'primary'">
            {{ currentOrder?.order_type === 'recharge' ? '充值' : '消费' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="会员">
          {{ currentOrder?.member_name || '散客' }}
        </el-descriptions-item>
        <el-descriptions-item label="支付方式">
          {{ getPaymentMethod(currentOrder?.payment_method) }}
        </el-descriptions-item>
        <el-descriptions-item label="商品金额">
          ¥{{ currentOrder?.total_amount?.toFixed(2) || '0.00' }}
        </el-descriptions-item>
        <el-descriptions-item label="优惠金额">
          <span v-if="currentOrder?.discount_amount > 0" class="text-success">
            -¥{{ currentOrder?.discount_amount?.toFixed(2) || '0.00' }}
          </span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="实付金额">
          <span class="text-danger">¥{{ currentOrder?.actual_amount?.toFixed(2) || '0.00' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="getStatusType(currentOrder?.status)">
            {{ getStatusText(currentOrder?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="下单时间" :span="2">
          {{ currentOrder?.order_time ? formatDateTime(currentOrder.order_time) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="支付时间" :span="2" v-if="currentOrder?.pay_time">
          {{ formatDateTime(currentOrder.pay_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="收银员" :span="2">
          {{ currentOrder?.cashier || '系统' }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2" v-if="currentOrder?.remarks">
          {{ currentOrder.remarks }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider />
      
      <div v-if="currentOrder?.order_items && currentOrder.order_items.length > 0">
        <div class="section-title">订单商品</div>
        <el-table :data="currentOrder.order_items" border size="small">
          <el-table-column prop="product_name" label="商品名称" />
          <el-table-column prop="unit_price" label="单价" width="100">
            <template #default="{ row }">
              ¥{{ row.unit_price?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量" width="80" />
          <el-table-column prop="subtotal" label="小计" width="100">
            <template #default="{ row }">
              ¥{{ row.subtotal?.toFixed(2) }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-if="currentOrder?.payments && currentOrder.payments.length > 0">
        <el-divider />
        <div class="section-title">支付记录</div>
        <el-table :data="currentOrder.payments" border size="small">
          <el-table-column prop="transaction_no" label="流水号" min-width="180" />
          <el-table-column prop="payment_method" label="支付方式" width="100">
            <template #default="{ row }">
              {{ getPaymentMethod(row.payment_method) }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="金额" width="100">
            <template #default="{ row }">
              ¥{{ row.amount?.toFixed(2) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
                {{ row.status === 'success' ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="pay_time" label="支付时间" width="160">
            <template #default="{ row }">
              {{ row.pay_time ? formatDateTime(row.pay_time) : '-' }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  order_no: '',
  status: '',
  start_date: '',
  end_date: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 详情相关
const detailDialogVisible = ref(false)
const currentOrder = ref(null)

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

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      order_no: searchForm.order_no || undefined,
      status: searchForm.status || undefined,
      start_date: searchForm.start_date || undefined,
      end_date: searchForm.end_date || undefined
    }
    
    const res = await api.getOrders(params)
    
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.order_no = ''
  searchForm.status = ''
  searchForm.start_date = ''
  searchForm.end_date = ''
  pagination.page = 1
  loadData()
}

// 分页变更
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

// 查看详情
const handleView = async (row) => {
  try {
    const res = await api.getOrder(row.id)
    if (res.success) {
      currentOrder.value = res.data
      detailDialogVisible.value = true
    }
  } catch (error) {
    console.error('获取订单详情失败:', error)
    ElMessage.error('获取订单详情失败')
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.order-list {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  gap: 10px;
}

.table-card {
  padding: 0;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
}

.text-danger {
  color: #F56C6C;
  font-weight: bold;
}

.text-success {
  color: #67C23A;
}

.section-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}
</style>
