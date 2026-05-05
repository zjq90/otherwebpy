<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">积分兑换</span>
    </div>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="兑换单号">
          <el-input v-model="searchForm.exchange_no" placeholder="请输入兑换单号" clearable />
        </el-form-item>
        <el-form-item label="用户">
          <el-input v-model="searchForm.user_name" placeholder="用户名/手机号" clearable />
        </el-form-item>
        <el-form-item label="兑换状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待处理" :value="0" />
            <el-option label="已确认" :value="1" />
            <el-option label="已发货" :value="2" />
            <el-option label="已完成" :value="3" />
            <el-option label="已取消" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="兑换时间">
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
        <el-table-column prop="exchange_no" label="兑换单号" width="180" />
        <el-table-column prop="user_name" label="用户" />
        <el-table-column prop="user_phone" label="手机号" width="120" />
        <el-table-column prop="product_name" label="兑换商品" />
        <el-table-column prop="product_image" label="商品图片" width="80" align="center">
          <template #default="{ row }">
            <el-image 
              :src="row.product_image || defaultImage" 
              fit="cover"
              style="width: 50px; height: 50px; border-radius: 4px;"
            />
          </template>
        </el-table-column>
        <el-table-column prop="points" label="消耗积分" align="center" width="100">
          <template #default="{ row }">
            <span style="color: #e6a23c; font-weight: 600;">{{ row.points || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="兑换数量" align="center" width="80" />
        <el-table-column prop="status" label="状态" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]">
              {{ statusLabelMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="shipping_name" label="收货人" width="100">
          <template #default="{ row }">
            {{ row.shipping_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="shipping_phone" label="收货电话" width="120">
          <template #default="{ row }">
            {{ row.shipping_phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="兑换时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              详情
            </el-button>
            <el-button 
              v-if="row.status === 0"
              type="warning" 
              link 
              size="small" 
              @click="handleConfirm(row)"
            >
              确认
            </el-button>
            <el-button 
              v-if="row.status === 1"
              type="success" 
              link 
              size="small" 
              @click="handleShip(row)"
            >
              发货
            </el-button>
            <el-button 
              v-if="row.status === 0 || row.status === 1"
              type="danger" 
              link 
              size="small" 
              @click="handleCancel(row)"
            >
              取消
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
    
    <el-dialog v-model="detailVisible" title="兑换详情" width="700px">
      <el-descriptions :column="2" border class="mb-20">
        <el-descriptions-item label="兑换单号">{{ currentExchange.exchange_no }}</el-descriptions-item>
        <el-descriptions-item label="兑换状态">
          <el-tag :type="statusTypeMap[currentExchange.status]">
            {{ statusLabelMap[currentExchange.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户姓名">{{ currentExchange.user_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户电话">{{ currentExchange.user_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="商品名称">{{ currentExchange.product_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="消耗积分">
          <span style="color: #e6a23c; font-weight: 600;">{{ currentExchange.points || 0 }}积分</span>
        </el-descriptions-item>
        <el-descriptions-item label="兑换数量">{{ currentExchange.quantity || 1 }}</el-descriptions-item>
        <el-descriptions-item label="商品原价">
          {{ currentExchange.product_original_price ? '¥' + currentExchange.product_original_price : '-' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider content-position="left">收货信息</el-divider>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="收货人">{{ currentExchange.shipping_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentExchange.shipping_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="收货地址" :span="2">{{ currentExchange.shipping_address || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <template v-if="currentExchange.status >= 2">
        <el-divider content-position="left">物流信息</el-divider>
        <el-descriptions :column="2" border>
          <el-descriptions-item label="物流公司">{{ currentExchange.shipping_company || '-' }}</el-descriptions-item>
          <el-descriptions-item label="物流单号">{{ currentExchange.shipping_no || '-' }}</el-descriptions-item>
          <el-descriptions-item label="发货时间">{{ formatDate(currentExchange.shipped_at) }}</el-descriptions-item>
          <el-descriptions-item label="完成时间">{{ formatDate(currentExchange.completed_at) }}</el-descriptions-item>
        </el-descriptions>
      </template>
      
      <el-descriptions :column="1" border class="mt-20">
        <el-descriptions-item label="兑换时间">{{ formatDate(currentExchange.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="取消时间" v-if="currentExchange.status === 4">
          {{ formatDate(currentExchange.canceled_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="取消原因" v-if="currentExchange.cancel_reason">
          {{ currentExchange.cancel_reason }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" v-if="currentExchange.remark">
          {{ currentExchange.remark }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    
    <el-dialog v-model="shipVisible" title="发货" width="500px">
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司">
          <el-input v-model="shipForm.shipping_company" placeholder="请输入物流公司" />
        </el-form-item>
        <el-form-item label="物流单号">
          <el-input v-model="shipForm.shipping_no" placeholder="请输入物流单号" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="shipForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="shipVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmShip">确认发货</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="cancelVisible" title="取消兑换" width="500px">
      <el-form :model="cancelForm" label-width="100px">
        <el-form-item label="取消原因">
          <el-input v-model="cancelForm.cancel_reason" type="textarea" :rows="3" placeholder="请输入取消原因" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="cancelVisible = false">取消</el-button>
          <el-button type="danger" @click="handleConfirmCancel">确认取消</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { getPointsExchangeList, updatePointsExchange, getProductById } from '@/api'

const loading = ref(false)
const detailVisible = ref(false)
const shipVisible = ref(false)
const cancelVisible = ref(false)

const tableData = ref([])
const currentExchange = ref({})
const dateRange = ref([])
const defaultImage = 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=gift%20box%20product%20icon&image_size=square'

const searchForm = reactive({
  exchange_no: '',
  user_name: '',
  status: null,
  start_date: '',
  end_date: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const shipForm = reactive({
  shipping_company: '',
  shipping_no: '',
  remark: ''
})

const cancelForm = reactive({
  cancel_reason: ''
})

const statusTypeMap = {
  0: 'warning',
  1: 'primary',
  2: 'info',
  3: 'success',
  4: 'info'
}

const statusLabelMap = {
  0: '待处理',
  1: '已确认',
  2: '已发货',
  3: '已完成',
  4: '已取消'
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
    
    const res = await getPointsExchangeList(params)
    const data = res.data || {}
    tableData.value = data.list || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.exchange_no = ''
  searchForm.user_name = ''
  searchForm.status = null
  dateRange.value = []
  pagination.page = 1
  fetchData()
}

const handleView = (row) => {
  currentExchange.value = { ...row }
  detailVisible.value = true
}

const handleConfirm = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要确认此兑换吗？确认后将扣除用户积分。`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updatePointsExchange(row.id, { status: 1 })
    ElMessage.success('确认成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

const handleShip = (row) => {
  currentExchange.value = { ...row }
  shipForm.shipping_company = ''
  shipForm.shipping_no = ''
  shipForm.remark = ''
  shipVisible.value = true
}

const handleConfirmShip = async () => {
  try {
    await updatePointsExchange(currentExchange.value.id, {
      status: 2,
      ...shipForm
    })
    ElMessage.success('发货成功')
    shipVisible.value = false
    fetchData()
  } catch (error) {
    console.error('发货失败:', error)
  }
}

const handleCancel = (row) => {
  currentExchange.value = { ...row }
  cancelForm.cancel_reason = ''
  cancelVisible.value = true
}

const handleConfirmCancel = async () => {
  try {
    await updatePointsExchange(currentExchange.value.id, {
      status: 4,
      cancel_reason: cancelForm.cancel_reason
    })
    ElMessage.success('取消成功')
    cancelVisible.value = false
    fetchData()
  } catch (error) {
    console.error('取消失败:', error)
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

.mt-20 {
  margin-top: 20px;
}
</style>
