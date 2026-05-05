<template>
  <div class="settlements-page">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>结算管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleAddSettlement">
              <el-icon><Plus /></el-icon>新增结算单
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" type="border-card">
        <el-tab-pane label="所有结算单" name="all">
          <div style="margin-bottom: 16px;">
            <el-form :inline="true">
              <el-form-item label="付款状态">
                <el-select v-model="filterForm.payment_status" placeholder="全部" clearable style="width: 140px">
                  <el-option label="待付款" value="待付款" />
                  <el-option label="部分付款" value="部分付款" />
                  <el-option label="已付款" value="已付款" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="fetchSettlements">
                  <el-icon><Search /></el-icon>搜索
                </el-button>
                <el-button type="primary" @click="handleReset">
                  <el-icon><Refresh /></el-icon>重置
                </el-button>
              </el-form-item>
            </el-form>
          </div>

          <el-table :data="settlementsList" stripe v-loading="loading">
            <el-table-column prop="settlement_no" label="结算单编号" width="180" />
            <el-table-column prop="settlement_date" label="结算日期" width="110" />
            <el-table-column prop="material_type" label="物料类型" width="100" />
            <el-table-column prop="quantity" label="数量(吨)" width="100">
              <template #default="{ row }">
                {{ row.quantity.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="unit_price" label="单价(元/吨)" width="110">
              <template #default="{ row }">
                ¥{{ row.unit_price.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_amount" label="结算金额(元)" width="120">
              <template #default="{ row }">
                <span class="amount-text">¥{{ row.total_amount.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="tax_rate" label="税率" width="80">
              <template #default="{ row }">
                {{ (row.tax_rate * 100).toFixed(0) }}%
              </template>
            </el-table-column>
            <el-table-column prop="tax_amount" label="税额(元)" width="100">
              <template #default="{ row }">
                ¥{{ row.tax_amount.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_payable" label="应付总额(元)" width="130">
              <template #default="{ row }">
                <span class="total-text">¥{{ row.total_payable.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="paid_amount" label="已付金额(元)" width="120">
              <template #default="{ row }">
                <span class="paid-text">¥{{ row.paid_amount.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="payment_status" label="付款状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getPaymentStatusType(row.payment_status)">
                  {{ row.payment_status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button 
                  type="success" 
                  link 
                  @click="handlePay(row)"
                  :disabled="row.payment_status === '已付款'"
                >
                  付款
                </el-button>
                <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
                <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="待付款结算单" name="pending">
          <el-table :data="pendingSettlements" stripe>
            <el-table-column prop="settlement_no" label="结算单编号" width="180" />
            <el-table-column prop="settlement_date" label="结算日期" width="110" />
            <el-table-column prop="material_type" label="物料类型" width="100" />
            <el-table-column prop="quantity" label="数量(吨)" width="100">
              <template #default="{ row }">
                {{ row.quantity.toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="total_payable" label="应付总额(元)" width="130">
              <template #default="{ row }">
                <span class="total-text">¥{{ row.total_payable.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="paid_amount" label="已付金额(元)" width="120">
              <template #default="{ row }">
                <span class="paid-text">¥{{ row.paid_amount.toFixed(2) }}</span>
              </template>
            </el-table-column>
            <el-table-column label="付款进度" min-width="200">
              <template #default="{ row }">
                <div class="payment-progress">
                  <el-progress 
                    :percentage="row.total_payable > 0 ? (row.paid_amount / row.total_payable) * 100 : 0"
                    :stroke-width="16"
                    color="#67C23A"
                  />
                  <span class="progress-text">
                    {{ row.paid_amount.toFixed(2) }} / {{ row.total_payable.toFixed(2) }} 元
                  </span>
                </div>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" fixed="right">
              <template #default="{ row }">
                <el-button type="success" link @click="handlePay(row)">
                  付款
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="summary-card">
            <el-row :gutter="20">
              <el-col :span="8">
                <el-statistic title="待付款结算单数量">
                  <template #default>
                    <span class="stat-value">{{ pendingSettlements.length }}</span>
                    <span class="stat-unit">笔</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="8">
                <el-statistic title="应付总额">
                  <template #default>
                    <span class="stat-value">¥</span>
                    <span class="stat-value">{{ totalPendingAmount.toFixed(2) }}</span>
                  </template>
                </el-statistic>
              </el-col>
              <el-col :span="8">
                <el-statistic title="已付金额">
                  <template #default>
                    <span class="stat-value">¥</span>
                    <span class="stat-value">{{ totalPaidAmount.toFixed(2) }}</span>
                  </template>
                </el-statistic>
              </el-col>
            </el-row>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="settlementDialogVisible" :title="settlementDialogTitle" width="600px">
      <el-form :model="settlementForm" :rules="settlementRules" ref="settlementFormRef" label-width="120px">
        <el-form-item label="关联采购订单" prop="purchase_order_id">
          <el-select 
            v-model="settlementForm.purchase_order_id" 
            placeholder="请选择已完成的采购订单" 
            style="width: 100%"
            :disabled="isEdit"
            @change="handleOrderChange"
          >
            <el-option
              v-for="order in completedOrders"
              :key="order.id"
              :label="`${order.order_no} - ${order.material_type} - ${order.quantity}吨`"
              :value="order.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="结算日期" prop="settlement_date">
          <el-date-picker
            v-model="settlementForm.settlement_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结算数量(吨)" prop="quantity">
          <el-input-number v-model="settlementForm.quantity" :min="0" :step="10" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价(元/吨)" prop="unit_price">
          <el-input-number v-model="settlementForm.unit_price" :min="0" :step="10" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="税率" prop="tax_rate">
          <el-select v-model="settlementForm.tax_rate" style="width: 100%">
            <el-option label="13%" :value="0.13" />
            <el-option label="9%" :value="0.09" />
            <el-option label="6%" :value="0.06" />
            <el-option label="0%" :value="0" />
          </el-select>
        </el-form-item>
        <el-form-item label="付款状态" prop="payment_status">
          <el-select v-model="settlementForm.payment_status" style="width: 100%">
            <el-option label="待付款" value="待付款" />
            <el-option label="部分付款" value="部分付款" />
            <el-option label="已付款" value="已付款" />
          </el-select>
        </el-form-item>
        <el-form-item label="已付金额(元)" prop="paid_amount">
          <el-input-number v-model="settlementForm.paid_amount" :min="0" :step="100" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注" prop="remark">
          <el-input v-model="settlementForm.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="settlementDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSettlementSubmit">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="payDialogVisible" title="付款" width="450px">
      <el-form :model="payForm" :rules="payRules" ref="payFormRef" label-width="100px">
        <el-form-item label="结算单编号">
          <el-input :value="currentSettlement?.settlement_no" disabled />
        </el-form-item>
        <el-form-item label="应付总额">
          <el-input :value="`¥${currentSettlement?.total_payable?.toFixed(2)}`" disabled />
        </el-form-item>
        <el-form-item label="已付金额">
          <el-input :value="`¥${currentSettlement?.paid_amount?.toFixed(2)}`" disabled />
        </el-form-item>
        <el-form-item label="待付金额">
          <el-input 
            :value="`¥${(currentSettlement ? currentSettlement.total_payable - currentSettlement.paid_amount : 0).toFixed(2)}`" 
            disabled 
          />
        </el-form-item>
        <el-form-item label="本次付款" prop="amount">
          <el-input-number 
            v-model="payForm.amount" 
            :min="0" 
            :max="currentSettlement ? currentSettlement.total_payable - currentSettlement.paid_amount : 0"
            :step="100" 
            :precision="2" 
            style="width: 100%" 
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePaySubmit">确认付款</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { settlementApi, supplierApi } from '@/api'

const loading = ref(false)
const activeTab = ref('all')

const settlementsList = ref([])
const pendingSettlements = ref([])
const completedOrders = ref([])
const currentSettlement = ref(null)

const settlementDialogVisible = ref(false)
const payDialogVisible = ref(false)
const isEdit = ref(false)

const settlementFormRef = ref<FormInstance>()
const payFormRef = ref<FormInstance>()

const filterForm = reactive({
  payment_status: ''
})

const settlementForm = reactive({
  id: null,
  purchase_order_id: null,
  settlement_date: '',
  quantity: 0,
  unit_price: 0,
  tax_rate: 0.13,
  payment_status: '待付款',
  paid_amount: 0,
  remark: ''
})

const payForm = reactive({
  amount: 0
})

const settlementRules: FormRules = {
  purchase_order_id: [{ required: true, message: '请选择采购订单', trigger: 'change' }],
  settlement_date: [{ required: true, message: '请选择结算日期', trigger: 'change' }],
  quantity: [{ required: true, message: '请输入结算数量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

const payRules: FormRules = {
  amount: [{ required: true, message: '请输入付款金额', trigger: 'blur' }]
}

const settlementDialogTitle = computed(() => isEdit.value ? '编辑结算单' : '新增结算单')

const totalPendingAmount = computed(() => {
  return pendingSettlements.value.reduce((sum, s) => sum + s.total_payable, 0)
})

const totalPaidAmount = computed(() => {
  return pendingSettlements.value.reduce((sum, s) => sum + s.paid_amount, 0)
})

const getPaymentStatusType = (status) => {
  const types = {
    '待付款': 'danger',
    '部分付款': 'warning',
    '已付款': 'success'
  }
  return types[status] || 'info'
}

const fetchSettlements = async () => {
  loading.value = true
  try {
    let res
    if (filterForm.payment_status) {
      res = await settlementApi.getList({ limit: 100 })
      settlementsList.value = res.data.filter(s => s.payment_status === filterForm.payment_status)
    } else {
      res = await settlementApi.getList({ limit: 100 })
      settlementsList.value = res.data
    }
  } catch (error) {
    ElMessage.error('获取结算单列表失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const fetchPendingSettlements = async () => {
  try {
    const res = await settlementApi.getPendingPayments()
    pendingSettlements.value = res.data
  } catch (error) {
    ElMessage.error('获取待付款结算单失败')
  }
}

const fetchCompletedOrders = async () => {
  try {
    const res = await supplierApi.getOrdersByStatus('已完成')
    completedOrders.value = res.data
  } catch (error) {
    console.error('获取已完成订单失败')
  }
}

const handleOrderChange = (orderId) => {
  const order = completedOrders.value.find(o => o.id === orderId)
  if (order) {
    settlementForm.quantity = order.quantity
    settlementForm.unit_price = order.unit_price
  }
}

const handleReset = () => {
  filterForm.payment_status = ''
  fetchSettlements()
}

const handleAddSettlement = () => {
  isEdit.value = false
  const today = new Date().toISOString().split('T')[0]
  Object.assign(settlementForm, {
    id: null,
    purchase_order_id: null,
    settlement_date: today,
    quantity: 0,
    unit_price: 0,
    tax_rate: 0.13,
    payment_status: '待付款',
    paid_amount: 0,
    remark: ''
  })
  settlementDialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(settlementForm, { ...row })
  settlementDialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除结算单"${row.settlement_no}"吗？`, '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await settlementApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchSettlements()
    fetchPendingSettlements()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handlePay = (row) => {
  currentSettlement.value = row
  payForm.amount = row.total_payable - row.paid_amount
  payDialogVisible.value = true
}

const handleSettlementSubmit = async () => {
  if (!settlementFormRef.value) return
  
  await settlementFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await settlementApi.update(settlementForm.id, settlementForm)
          ElMessage.success('更新成功')
        } else {
          await settlementApi.create(settlementForm)
          ElMessage.success('创建成功')
        }
        settlementDialogVisible.value = false
        fetchSettlements()
        fetchPendingSettlements()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      }
    }
  })
}

const handlePaySubmit = async () => {
  if (!payFormRef.value) return
  
  await payFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        await settlementApi.pay(currentSettlement.value.id, payForm.amount)
        ElMessage.success('付款成功')
        payDialogVisible.value = false
        fetchSettlements()
        fetchPendingSettlements()
      } catch (error) {
        ElMessage.error('付款失败')
      }
    }
  })
}

onMounted(() => {
  fetchSettlements()
  fetchPendingSettlements()
  fetchCompletedOrders()
})
</script>

<style scoped>
.settlements-page {
  width: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.amount-text {
  color: #409EFF;
  font-weight: 600;
}

.total-text {
  color: #F56C6C;
  font-weight: 600;
  font-size: 14px;
}

.paid-text {
  color: #67C23A;
  font-weight: 600;
}

.payment-progress {
  width: 100%;
}

.progress-text {
  display: block;
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.summary-card {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-unit {
  font-size: 14px;
  color: #909399;
  margin-left: 4px;
}
</style>
