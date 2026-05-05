<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">订单管理</span>
    </div>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="订单编号">
          <el-input v-model="searchForm.order_no" placeholder="请输入订单编号" clearable />
        </el-form-item>
        <el-form-item label="用户">
          <el-input v-model="searchForm.user_id" placeholder="用户ID" clearable style="width: 100px" />
        </el-form-item>
        <el-form-item label="订单状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待接单" :value="0" />
            <el-option label="已接单" :value="1" />
            <el-option label="上门中" :value="2" />
            <el-option label="已完成" :value="3" />
            <el-option label="已取消" :value="4" />
            <el-option label="异常" :value="5" />
          </el-select>
        </el-form-item>
        <el-form-item label="区域">
          <el-input v-model="searchForm.area" placeholder="请输入区域" clearable />
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
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
    
    <el-card class="table-container">
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="order_no" label="订单编号" width="180" />
        <el-table-column prop="user_name" label="用户" width="100" />
        <el-table-column prop="user_phone" label="用户电话" width="120" />
        <el-table-column prop="address" label="回收地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="recycler_name" label="回收人员" width="100">
          <template #default="{ row }">
            {{ row.recycler_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]">
              {{ statusLabelMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="回收金额" width="100" align="center">
          <template #default="{ row }">
            {{ row.total_amount ? '¥' + row.total_amount : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="total_weight" label="回收重量" width="100" align="center">
          <template #default="{ row }">
            {{ row.total_weight ? row.total_weight + 'kg' : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              详情
            </el-button>
            <el-button 
              v-if="row.status === 0"
              type="warning" 
              link 
              size="small" 
              @click="handleAssign(row)"
            >
              分配
            </el-button>
            <el-button 
              v-if="row.status === 5"
              type="danger" 
              link 
              size="small" 
              @click="handleException(row)"
            >
              处理异常
            </el-button>
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
    
    <el-dialog v-model="detailVisible" title="订单详情" width="700px">
      <el-descriptions :column="2" border class="mb-20">
        <el-descriptions-item label="订单编号">{{ currentOrder.order_no }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">
          <el-tag :type="statusTypeMap[currentOrder.status]">
            {{ statusLabelMap[currentOrder.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户姓名">{{ currentOrder.user_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户电话">{{ currentOrder.user_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="回收地址" :span="2">{{ currentOrder.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="预约日期">{{ formatDate(currentOrder.appointment_date) }}</el-descriptions-item>
        <el-descriptions-item label="预约时段">{{ currentOrder.appointment_time || '-' }}</el-descriptions-item>
        <el-descriptions-item label="回收人员">{{ currentOrder.recycler_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="回收人员电话">{{ '-' }}</el-descriptions-item>
        <el-descriptions-item label="回收金额" v-if="currentOrder.total_amount">
          ¥{{ currentOrder.total_amount }}
        </el-descriptions-item>
        <el-descriptions-item label="回收重量" v-if="currentOrder.total_weight">
          {{ currentOrder.total_weight }}kg
        </el-descriptions-item>
        <el-descriptions-item label="获得积分" v-if="currentOrder.total_points">
          {{ currentOrder.total_points }}积分
        </el-descriptions-item>
        <el-descriptions-item label="区域">{{ currentOrder.area || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentOrder.remark || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(currentOrder.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="接单时间">{{ formatDate(currentOrder.accept_time) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatDate(currentOrder.complete_time) }}</el-descriptions-item>
        <el-descriptions-item label="取消时间">{{ formatDate(currentOrder.cancel_time) }}</el-descriptions-item>
      </el-descriptions>
      
      <div v-if="currentOrder.items && currentOrder.items.length > 0">
        <h4 class="mb-10">订单明细</h4>
        <el-table :data="currentOrder.items" size="small" border>
          <el-table-column prop="category_name" label="衣物分类" />
          <el-table-column prop="pricing_type" label="计价方式" align="center">
            <template #default="{ row }">
              {{ row.pricing_type === 0 ? '按件' : '按斤' }}
            </template>
          </el-table-column>
          <el-table-column prop="quantity" label="数量(件)" align="center">
            <template #default="{ row }">
              {{ row.quantity || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="weight" label="重量(kg)" align="center">
            <template #default="{ row }">
              {{ row.weight || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="unit_price" label="单价" align="center">
            <template #default="{ row }">
              ¥{{ row.unit_price }}
            </template>
          </el-table-column>
          <el-table-column prop="amount" label="小计" align="center">
            <template #default="{ row }">
              ¥{{ row.amount }}
            </template>
          </el-table-column>
          <el-table-column prop="points" label="积分" align="center">
            <template #default="{ row }">
              {{ row.points }}
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-if="currentOrder.cancel_reason" class="mt-20">
        <el-alert :title="'取消原因: ' + currentOrder.cancel_reason" type="warning" :closable="false" />
      </div>
      
      <div v-if="currentOrder.exception_reason" class="mt-20">
        <el-alert :title="'异常原因: ' + currentOrder.exception_reason" type="error" :closable="false" />
      </div>
    </el-dialog>
    
    <el-dialog v-model="assignVisible" title="分配订单" width="500px">
      <el-form label-width="100px">
        <el-form-item label="选择回收人员">
          <el-select 
            v-model="selectedRecyclerId" 
            placeholder="请选择回收人员" 
            style="width: 100%"
          >
            <el-option
              v-for="item in recyclerList"
              :key="item.id"
              :label="item.real_name + ' (' + item.area + ')'"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="assignVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmAssign">确认分配</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="exceptionVisible" title="处理异常订单" width="500px">
      <el-form label-width="100px">
        <el-form-item label="当前订单号">
          <span>{{ currentOrder.order_no }}</span>
        </el-form-item>
        <el-form-item label="异常原因">
          <el-input type="textarea" :rows="3" disabled :model-value="currentOrder.exception_reason" />
        </el-form-item>
        <el-form-item label="处理方式">
          <el-radio-group v-model="exceptionAction">
            <el-radio :value="3">标记完成</el-radio>
            <el-radio :value="4">取消订单</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exceptionVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmException">确认处理</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { getOrderList, getOrderById, assignOrder, updateOrder, getRecyclerList } from '@/api'

const loading = ref(false)
const detailVisible = ref(false)
const assignVisible = ref(false)
const exceptionVisible = ref(false)

const tableData = ref([])
const currentOrder = ref({})
const recyclerList = ref([])
const selectedRecyclerId = ref(null)
const exceptionAction = ref(4)
const dateRange = ref([])

const searchForm = reactive({
  order_no: '',
  user_id: '',
  status: null,
  area: '',
  start_date: '',
  end_date: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const statusTypeMap = {
  0: 'info',
  1: 'warning',
  2: 'primary',
  3: 'success',
  4: 'info',
  5: 'danger'
}

const statusLabelMap = {
  0: '待接单',
  1: '已接单',
  2: '上门中',
  3: '已完成',
  4: '已取消',
  5: '异常'
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
    }
    
    const res = await getOrderList(params)
    const data = res.data || {}
    tableData.value = data.list || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchRecyclers = async () => {
  try {
    const res = await getRecyclerList({ page: 1, page_size: 100, status: 1 })
    const data = res.data || {}
    recyclerList.value = data.list || []
  } catch (error) {
    console.error('获取回收人员列表失败:', error)
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.order_no = ''
  searchForm.user_id = ''
  searchForm.status = null
  searchForm.area = ''
  dateRange.value = []
  pagination.page = 1
  fetchData()
}

const handleView = async (row) => {
  try {
    const res = await getOrderById(row.id)
    currentOrder.value = res.data || {}
    detailVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
  }
}

const handleAssign = (row) => {
  currentOrder.value = { ...row }
  selectedRecyclerId.value = null
  fetchRecyclers()
  assignVisible.value = true
}

const handleConfirmAssign = async () => {
  if (!selectedRecyclerId.value) {
    ElMessage.warning('请选择回收人员')
    return
  }
  
  try {
    await assignOrder(currentOrder.value.id, selectedRecyclerId.value)
    ElMessage.success('分配成功')
    assignVisible.value = false
    fetchData()
  } catch (error) {
    console.error('分配失败:', error)
  }
}

const handleException = (row) => {
  currentOrder.value = { ...row }
  exceptionAction.value = 4
  exceptionVisible.value = true
}

const handleConfirmException = async () => {
  try {
    await updateOrder(currentOrder.value.id, { status: exceptionAction.value })
    ElMessage.success('处理成功')
    exceptionVisible.value = false
    fetchData()
  } catch (error) {
    console.error('处理失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.search-form {
  .el-form-item {
    margin-right: 0;
  }
}

.mb-10 {
  margin-bottom: 10px;
}

.mb-20 {
  margin-bottom: 20px;
}

.mt-20 {
  margin-top: 20px;
}
</style>
