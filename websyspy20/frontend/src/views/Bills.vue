<template>
  <div class="bills">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>账单列表</span>
          <div class="header-actions">
            <el-select v-model="searchForm.status" placeholder="状态筛选" clearable style="width: 120px; margin-right: 10px;">
              <el-option label="待缴费" value="pending" />
              <el-option label="部分缴费" value="partial" />
              <el-option label="已缴费" value="paid" />
              <el-option label="逾期" value="overdue" />
            </el-select>
            <el-date-picker
              v-model="searchForm.date"
              type="month"
              placeholder="选择月份"
              value-format="YYYY-MM"
              style="width: 150px; margin-right: 10px;"
              clearable
            />
            <el-button type="primary" @click="loadData">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button type="success" @click="showBatchGenerate" style="margin-left: 10px;">
              <el-icon><Plus /></el-icon>
              批量生成
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="bills" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="bill_number" label="账单编号" width="180" />
        <el-table-column label="房产信息" width="180">
          <template #default="scope">
            <div>
              <div>{{ scope.row.property_info?.property_number || '-' }}</div>
              <div class="sub-text">{{ scope.row.property_info?.owner_name || '-' }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="费用项目" width="120">
          <template #default="scope">
            {{ scope.row.fee_item_info?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="计费周期" width="100">
          <template #default="scope">
            {{ scope.row.billing_year }}年{{ scope.row.billing_month }}月
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="账单金额" width="100">
          <template #default="scope">
            <span class="amount-text">¥{{ scope.row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="已付金额" width="100">
          <template #default="scope">
            <span class="paid-text">¥{{ scope.row.paid_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column label="待付金额" width="100">
          <template #default="scope">
            <span :class="getUnpaidClass(scope.row)">
              ¥{{ (scope.row.amount - scope.row.paid_amount).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="120" />
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleDetail(scope.row)">
              详情
            </el-button>
            <el-button 
              v-if="['pending', 'partial', 'overdue'].includes(scope.row.status)" 
              type="success" 
              link 
              @click="handlePay(scope.row)"
            >
              缴费
            </el-button>
            <el-button 
              v-if="['pending', 'partial', 'overdue'].includes(scope.row.status)" 
              type="warning" 
              link 
              @click="handleRemind(scope.row)"
            >
              催缴
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <el-dialog v-model="batchGenerateVisible" title="批量生成账单" width="500px">
      <el-form :model="batchForm" label-width="100px">
        <el-form-item label="计费年份">
          <el-date-picker
            v-model="batchForm.year"
            type="year"
            placeholder="选择年份"
            value-format="YYYY"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="计费月份">
          <el-select v-model="batchForm.month" placeholder="选择月份" style="width: 100%;">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchGenerateVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchGenerate" :loading="generating">
          生成账单
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="payDialogVisible" title="账单缴费" width="500px">
      <el-descriptions :column="1" border style="margin-bottom: 20px;">
        <el-descriptions-item label="账单编号">{{ currentBill?.bill_number }}</el-descriptions-item>
        <el-descriptions-item label="房产信息">{{ currentBill?.property_info?.property_number }}</el-descriptions-item>
        <el-descriptions-item label="费用项目">{{ currentBill?.fee_item_info?.name }}</el-descriptions-item>
        <el-descriptions-item label="账单金额">¥{{ currentBill?.amount }}</el-descriptions-item>
        <el-descriptions-item label="已付金额">¥{{ currentBill?.paid_amount }}</el-descriptions-item>
        <el-descriptions-item label="待付金额">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ currentBill ? (currentBill.amount - currentBill.paid_amount).toFixed(2) : 0 }}
          </span>
        </el-descriptions-item>
      </el-descriptions>
      <el-form :model="payForm" label-width="100px">
        <el-form-item label="支付金额">
          <el-input-number
            v-model="payForm.amount"
            :min="0"
            :max="maxPayAmount"
            :precision="2"
            :step="1"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="payForm.payment_method" style="width: 100%;">
            <el-option label="现金" value="cash" />
            <el-option label="微信支付" value="wechat" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="交易流水号">
          <el-input v-model="payForm.transaction_id" placeholder="可选" />
        </el-form-item>
        <el-form-item label="收款人">
          <el-input v-model="payForm.collector" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePaySubmit" :loading="paying">
          确认缴费
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="账单详情" width="700px">
      <el-descriptions :column="2" border v-if="currentBill">
        <el-descriptions-item label="账单编号" :span="2">{{ currentBill.bill_number }}</el-descriptions-item>
        <el-descriptions-item label="房产编号">{{ currentBill.property_info?.property_number }}</el-descriptions-item>
        <el-descriptions-item label="业主姓名">{{ currentBill.property_info?.owner_name }}</el-descriptions-item>
        <el-descriptions-item label="费用项目">{{ currentBill.fee_item_info?.name }}</el-descriptions-item>
        <el-descriptions-item label="计费周期">{{ currentBill.billing_year }}年{{ currentBill.billing_month }}月</el-descriptions-item>
        <el-descriptions-item label="账单金额">
          <span style="color: #f56c6c; font-weight: bold;">¥{{ currentBill.amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="已付金额">
          <span style="color: #67c23a; font-weight: bold;">¥{{ currentBill.paid_amount }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="账单状态">
          <el-tag :type="getStatusTag(currentBill.status)">{{ getStatusLabel(currentBill.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="缴费截止">{{ currentBill.due_date }}</el-descriptions-item>
        <el-descriptions-item label="生成时间">{{ currentBill.generated_at }}</el-descriptions-item>
        <el-descriptions-item label="支付时间">{{ currentBill.paid_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="支付方式">{{ getPaymentMethodLabel(currentBill.payment_method) }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ currentBill.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { billApi, reminderApi } from '@/api'

const bills = ref([])
const loading = ref(false)
const generating = ref(false)
const paying = ref(false)
const currentBill = ref(null)

const searchForm = reactive({
  status: '',
  date: ''
})

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const batchGenerateVisible = ref(false)
const payDialogVisible = ref(false)
const detailVisible = ref(false)

const batchForm = reactive({
  year: new Date().getFullYear().toString(),
  month: new Date().getMonth() + 1
})

const payForm = reactive({
  amount: 0,
  payment_method: 'cash',
  transaction_id: '',
  collector: ''
})

const maxPayAmount = computed(() => {
  if (!currentBill.value) return 0
  return currentBill.value.amount - currentBill.value.paid_amount
})

const getStatusTag = (status) => {
  const map = {
    'pending': 'warning',
    'partial': 'info',
    'paid': 'success',
    'overdue': 'danger',
    'cancelled': 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    'pending': '待缴费',
    'partial': '部分缴费',
    'paid': '已缴费',
    'overdue': '逾期',
    'cancelled': '已取消'
  }
  return map[status] || status
}

const getPaymentMethodLabel = (method) => {
  const map = {
    'cash': '现金',
    'wechat': '微信支付',
    'alipay': '支付宝',
    'bank_transfer': '银行转账',
    'other': '其他'
  }
  return map[method] || '-'
}

const getUnpaidClass = (row) => {
  const unpaid = row.amount - row.paid_amount
  if (unpaid > 0 && row.status === 'overdue') {
    return 'text-danger'
  }
  return unpaid > 0 ? 'text-warning' : 'text-success'
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    if (searchForm.date) {
      const [year, month] = searchForm.date.split('-')
      params.billing_year = parseInt(year)
      params.billing_month = parseInt(month)
    }
    const res = await billApi.getList(params)
    bills.value = res.data
    total.value = res.data.length
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const showBatchGenerate = () => {
  batchForm.year = new Date().getFullYear().toString()
  batchForm.month = new Date().getMonth() + 1
  batchGenerateVisible.value = true
}

const handleBatchGenerate = async () => {
  if (!batchForm.year || !batchForm.month) {
    ElMessage.warning('请选择年份和月份')
    return
  }
  
  generating.value = true
  try {
    const res = await billApi.batchGenerate({
      billing_year: parseInt(batchForm.year),
      billing_month: batchForm.month
    })
    ElMessage.success(`生成完成：新增 ${res.data.generated_count} 条账单，跳过 ${res.data.skipped_count} 条已存在账单`)
    batchGenerateVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    generating.value = false
  }
}

const handleDetail = (row) => {
  currentBill.value = row
  detailVisible.value = true
}

const handlePay = (row) => {
  currentBill.value = row
  payForm.amount = row.amount - row.paid_amount
  payForm.payment_method = 'cash'
  payForm.transaction_id = ''
  payForm.collector = ''
  payDialogVisible.value = true
}

const handlePaySubmit = async () => {
  if (payForm.amount <= 0) {
    ElMessage.warning('请输入支付金额')
    return
  }
  
  paying.value = true
  try {
    await billApi.pay(currentBill.value.id, {
      amount: payForm.amount,
      payment_method: payForm.payment_method,
      transaction_id: payForm.transaction_id || undefined,
      collector: payForm.collector || undefined
    })
    ElMessage.success('缴费成功')
    payDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    paying.value = false
  }
}

const handleRemind = async (row) => {
  try {
    await ElMessageBox.confirm('确定要对该账单发送催缴通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await reminderApi.sendReminder(row.id)
    ElMessage.success('催缴通知已发送')
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.bills {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.sub-text {
  font-size: 12px;
  color: #909399;
}

.amount-text {
  color: #f56c6c;
  font-weight: bold;
}

.paid-text {
  color: #67c23a;
  font-weight: bold;
}

.text-danger {
  color: #f56c6c;
  font-weight: bold;
}

.text-warning {
  color: #e6a23c;
  font-weight: bold;
}

.text-success {
  color: #67c23a;
  font-weight: bold;
}
</style>
