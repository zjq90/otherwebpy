<template>
  <div class="settlement-orders-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>结算单管理</span>
          <div class="header-buttons">
            <el-button type="primary" @click="handleAutoGenerate">
              <el-icon><MagicStick /></el-icon>
              自动生成
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              新增结算单
            </el-button>
          </div>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="结算单号">
          <el-input
            v-model="searchForm.settlement_no"
            placeholder="请输入结算单号"
            clearable
          />
        </el-form-item>
        <el-form-item label="供应商">
          <el-select v-model="searchForm.supplier_id" placeholder="请选择供应商" clearable style="width: 180px">
            <el-option v-for="supplier in suppliers" :key="supplier.id" :label="supplier.name" :value="supplier.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="结算周期">
          <el-select v-model="searchForm.settlement_period" placeholder="请选择" clearable>
            <el-option label="2024年1月" value="2024年1月" />
            <el-option label="2024年2月" value="2024年2月" />
            <el-option label="2024年3月" value="2024年3月" />
            <el-option label="2024年4月" value="2024年4月" />
            <el-option label="2024年5月" value="2024年5月" />
            <el-option label="2024年6月" value="2024年6月" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="待确认" value="待确认">
              <el-tag type="info" effect="dark" size="small">待确认</el-tag>
            </el-option>
            <el-option label="已确认" value="已确认">
              <el-tag type="warning" effect="dark" size="small">已确认</el-tag>
            </el-option>
            <el-option label="已付款" value="已付款">
              <el-tag type="success" effect="dark" size="small">已付款</el-tag>
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="settlement_no" label="结算单号" width="140" />
        <el-table-column prop="supplier_name" label="供应商名称" min-width="180" />
        <el-table-column prop="settlement_period" label="结算周期" width="120" />
        <el-table-column prop="start_date" label="开始日期" width="110" />
        <el-table-column prop="end_date" label="结束日期" width="110" />
        <el-table-column prop="total_quantity" label="总数量" width="100">
          <template #default="scope">
            {{ scope.row.total_quantity }} 吨
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额(元)" width="130">
          <template #default="scope">
            <span class="amount-text">¥{{ formatNumber(scope.row.total_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="discount_amount" label="优惠金额(元)" width="120">
          <template #default="scope">
            <span v-if="scope.row.discount_amount > 0" class="discount-text">
              -¥{{ formatNumber(scope.row.discount_amount) }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="final_amount" label="结算金额(元)" width="140">
          <template #default="scope">
            <span class="final-amount">¥{{ formatNumber(scope.row.final_amount) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by" label="创建人" width="90" />
        <el-table-column prop="created_date" label="创建日期" width="110" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" effect="dark" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="primary" link v-if="scope.row.status === '待确认'" @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link v-if="scope.row.status === '待确认'" @click="handleConfirm(scope.row)">
              确认
            </el-button>
            <el-button type="success" link v-if="scope.row.status === '已确认'" @click="handlePay(scope.row)">
              付款
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="900px"
    >
      <el-descriptions :column="3" border>
        <el-descriptions-item label="结算单号">{{ currentOrder.settlement_no }}</el-descriptions-item>
        <el-descriptions-item label="供应商">{{ currentOrder.supplier_name }}</el-descriptions-item>
        <el-descriptions-item label="结算周期">{{ currentOrder.settlement_period }}</el-descriptions-item>
        <el-descriptions-item label="开始日期">{{ currentOrder.start_date }}</el-descriptions-item>
        <el-descriptions-item label="结束日期">{{ currentOrder.end_date }}</el-descriptions-item>
        <el-descriptions-item label="创建人">{{ currentOrder.created_by }}</el-descriptions-item>
        <el-descriptions-item label="创建日期">{{ currentOrder.created_date }}</el-descriptions-item>
        <el-descriptions-item label="状态" :span="2">
          <el-tag :type="getStatusType(currentOrder.status)" effect="dark">
            {{ currentOrder.status }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider>材料明细</el-divider>
      
      <el-table :data="orderDetails" style="width: 100%">
        <el-table-column label="材料类型" prop="material_type" width="150" />
        <el-table-column label="数量(吨)" prop="quantity" width="120" />
        <el-table-column label="单价(元/吨)" prop="unit_price" width="130">
          <template #default="scope">
            ¥{{ formatNumber(scope.row.unit_price) }}
          </template>
        </el-table-column>
        <el-table-column label="金额(元)" prop="amount" width="150">
          <template #default="scope">
            ¥{{ formatNumber(scope.row.amount) }}
          </template>
        </el-table-column>
      </el-table>
      
      <el-divider>金额汇总</el-divider>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="总数量">
            <template #default>
              {{ currentOrder.total_quantity }} 吨
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="总金额">
            <template #default>
              <span class="amount-text">¥{{ formatNumber(currentOrder.total_amount) }}</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="8">
          <el-statistic title="优惠金额">
            <template #default>
              <span v-if="currentOrder.discount_amount > 0" class="discount-text">
                -¥{{ formatNumber(currentOrder.discount_amount) }}
              </span>
              <span v-else>-</span>
            </template>
          </el-statistic>
        </el-col>
      </el-row>
      
      <el-divider />
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-statistic title="结算金额">
            <template #default>
              <span class="final-amount">¥{{ formatNumber(currentOrder.final_amount) }}</span>
            </template>
          </el-statistic>
        </el-col>
        <el-col :span="12">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="备注">
              {{ currentOrder.remark || '无' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-col>
      </el-row>
      <template #footer>
        <el-button @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="generateDialogVisible"
      title="自动生成结算单"
      width="600px"
    >
      <el-form ref="generateFormRef" :model="generateForm" :rules="generateRules" label-width="120px">
        <el-form-item label="选择供应商" prop="supplier_id">
          <el-select v-model="generateForm.supplier_id" placeholder="请选择供应商" style="width: 100%">
            <el-option v-for="supplier in suppliers" :key="supplier.id" :label="supplier.name" :value="supplier.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="结算周期" prop="settlement_period">
          <el-select v-model="generateForm.settlement_period" placeholder="请选择结算周期" style="width: 100%">
            <el-option label="2024年1月" value="2024年1月" />
            <el-option label="2024年2月" value="2024年2月" />
            <el-option label="2024年3月" value="2024年3月" />
            <el-option label="2024年4月" value="2024年4月" />
            <el-option label="2024年5月" value="2024年5月" />
            <el-option label="2024年6月" value="2024年6月" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleGenerateConfirm">生成结算单</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const generateDialogVisible = ref(false)
const isView = ref(false)
const generateFormRef = ref(null)
const currentOrder = ref({})
const orderDetails = ref([])
const suppliers = ref([])

const searchForm = reactive({
  settlement_no: '',
  supplier_id: null,
  settlement_period: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const generateForm = reactive({
  supplier_id: null,
  settlement_period: ''
})

const generateRules = {
  supplier_id: [{ required: true, message: '请选择供应商', trigger: 'change' }],
  settlement_period: [{ required: true, message: '请选择结算周期', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  return '查看结算单'
})

const formatNumber = (num) => {
  if (num === null || num === undefined) return '0'
  return num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getStatusType = (status) => {
  const typeMap = {
    '待确认': 'info',
    '已确认': 'warning',
    '已付款': 'success'
  }
  return typeMap[status] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        settlement_no: 'SO202401001',
        supplier_id: 1,
        supplier_name: '山水水泥有限公司',
        settlement_period: '2024年1月',
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        total_quantity: 500.00,
        total_amount: 275000.00,
        discount_amount: 8250.00,
        final_amount: 266750.00,
        created_by: '财务员A',
        created_date: '2024-02-01',
        remark: '2024年1月份水泥货款结算',
        status: '已付款'
      },
      {
        id: 2,
        settlement_no: 'SO202401002',
        supplier_id: 2,
        supplier_name: '海螺水泥集团',
        settlement_period: '2024年1月',
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        total_quantity: 350.00,
        total_amount: 192500.00,
        discount_amount: 5775.00,
        final_amount: 186725.00,
        created_by: '财务员B',
        created_date: '2024-02-01',
        remark: '2024年1月份骨料货款结算',
        status: '已确认'
      },
      {
        id: 3,
        settlement_no: 'SO202401003',
        supplier_id: 3,
        supplier_name: '华新水泥股份',
        settlement_period: '2024年1月',
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        total_quantity: 200.00,
        total_amount: 110000.00,
        discount_amount: 0.00,
        final_amount: 110000.00,
        created_by: '财务员C',
        created_date: '2024-02-05',
        remark: '2024年1月份外加剂货款结算',
        status: '待确认'
      }
    ]
    pagination.total = 3
    
    suppliers.value = [
      { id: 1, name: '山水水泥有限公司' },
      { id: 2, name: '海螺水泥集团' },
      { id: 3, name: '华新水泥股份' }
    ]
  } catch (error) {
    console.error('获取结算单数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.settlement_no = ''
  searchForm.supplier_id = null
  searchForm.settlement_period = ''
  searchForm.status = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchData()
}

const handleView = (row) => {
  currentOrder.value = { ...row }
  
  orderDetails.value = [
    { material_type: '水泥', quantity: 300.00, unit_price: 550.00, amount: 165000.00 },
    { material_type: '骨料', quantity: 200.00, unit_price: 550.00, amount: 110000.00 }
  ]
  
  dialogVisible.value = true
}

const handleEdit = (row) => {
  ElMessage.info('编辑功能开发中...')
}

const handleConfirm = (row) => {
  ElMessageBox.confirm(
    `确定要确认结算单"${row.settlement_no}"吗？确认后将无法修改。`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    row.status = '已确认'
    ElMessage.success('确认成功')
    fetchData()
  }).catch(() => {})
}

const handlePay = (row) => {
  ElMessageBox.confirm(
    `确定要标记结算单"${row.settlement_no}"为已付款吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'success'
    }
  ).then(() => {
    row.status = '已付款'
    ElMessage.success('付款成功')
    fetchData()
  }).catch(() => {})
}

const handleAutoGenerate = () => {
  generateForm.supplier_id = null
  generateForm.settlement_period = ''
  generateDialogVisible.value = true
}

const handleAdd = () => {
  ElMessage.info('新增结算单功能开发中...')
}

const handleGenerateConfirm = async () => {
  if (!generateFormRef.value) return
  
  await generateFormRef.value.validate(async (valid) => {
    if (valid) {
      ElMessage.success('结算单生成成功')
      generateDialogVisible.value = false
      fetchData()
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.settlement-orders-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-buttons {
  display: flex;
  gap: 10px;
}

.search-form {
  margin-bottom: 20px;
}

.amount-text {
  color: #303133;
  font-weight: 500;
}

.discount-text {
  color: #67C23A;
  font-weight: 500;
}

.final-amount {
  color: #F56C6C;
  font-weight: bold;
  font-size: 16px;
}
</style>
