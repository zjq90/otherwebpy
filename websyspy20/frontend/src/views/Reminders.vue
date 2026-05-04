<template>
  <div class="reminders">
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div class="stat-value">{{ stats.overdue_bills_count }}</div>
            <div class="stat-label">逾期账单数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div style="text-align: center;">
            <div class="stat-value">{{ stats.total_reminders }}</div>
            <div class="stat-label">总催缴次数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <span>快速操作</span>
            <el-button type="warning" @click="handleBatchRemind">
              <el-icon><Bell /></el-icon>
              批量催缴所有逾期账单
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="逾期账单列表" name="overdue">
        <el-card>
          <el-table :data="overdueBills" stripe style="width: 100%" v-loading="loading">
            <el-table-column prop="bill_number" label="账单编号" width="180" />
            <el-table-column label="房产信息" width="180">
              <template #default="scope">
                <div>
                  <div>{{ scope.row.property_info?.property_number || '-' }}</div>
                  <div class="sub-text">{{ scope.row.property_info?.owner_name || '-' }}</div>
                  <div class="sub-text">{{ scope.row.property_info?.owner_phone || '-' }}</div>
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
            <el-table-column label="逾期金额" width="120">
              <template #default="scope">
                <span class="overdue-amount">
                  ¥{{ (scope.row.amount - scope.row.paid_amount).toFixed(2) }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="截止日期" width="120">
              <template #default="scope">
                <el-tag type="danger">{{ scope.row.due_date }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="催缴记录" width="100">
              <template #default="scope">
                <el-button type="primary" link @click="viewReminderHistory(scope.row)">
                  查看
                </el-button>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="scope">
                <el-button type="primary" link @click="handlePay(scope.row)">
                  缴费
                </el-button>
                <el-button type="warning" link @click="handleRemind(scope.row)">
                  催缴
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="催缴历史记录" name="history">
        <el-card>
          <el-table :data="reminderHistory" stripe style="width: 100%" v-loading="loadingHistory">
            <el-table-column prop="reminder_count" label="催缴次数" width="100">
              <template #default="scope">
                第{{ scope.row.reminder_count }}次
              </template>
            </el-table-column>
            <el-table-column prop="method" label="催缴方式" width="100">
              <template #default="scope">
                <el-tag>{{ getMethodLabel(scope.row.method) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="催缴内容" min-width="300">
              <template #default="scope">
                <el-text class="content-text" size="small">
                  {{ scope.row.content || '暂无内容' }}
                </el-text>
              </template>
            </el-table-column>
            <el-table-column prop="operator" label="执行人" width="100" />
            <el-table-column prop="reminded_at" label="催缴时间" width="180" />
            <el-table-column prop="remark" label="备注" width="150" />
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="historyVisible" title="催缴历史记录" width="900px">
      <el-descriptions :column="2" border style="margin-bottom: 20px;" v-if="selectedBill">
        <el-descriptions-item label="账单编号">{{ selectedBill.bill_number }}</el-descriptions-item>
        <el-descriptions-item label="房产编号">{{ selectedBill.property_info?.property_number }}</el-descriptions-item>
        <el-descriptions-item label="业主姓名">{{ selectedBill.property_info?.owner_name }}</el-descriptions-item>
        <el-descriptions-item label="逾期金额">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ (selectedBill.amount - selectedBill.paid_amount).toFixed(2) }}
          </span>
        </el-descriptions-item>
      </el-descriptions>
      <el-table :data="currentReminders" stripe style="width: 100%">
        <el-table-column prop="reminder_count" label="催缴次数" width="100">
          <template #default="scope">
            第{{ scope.row.reminder_count }}次
          </template>
        </el-table-column>
        <el-table-column prop="method" label="催缴方式" width="120">
          <template #default="scope">
            <el-tag>{{ getMethodLabel(scope.row.method) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="催缴内容" min-width="300">
          <template #default="scope">
            <div style="white-space: pre-line; font-size: 13px;">
              {{ scope.row.content || '暂无内容' }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="operator" label="执行人" width="100" />
        <el-table-column prop="reminded_at" label="催缴时间" width="180" />
      </el-table>
    </el-dialog>

    <el-dialog v-model="remindVisible" title="发送催缴通知" width="500px">
      <el-descriptions :column="1" border style="margin-bottom: 20px;" v-if="selectedBill">
        <el-descriptions-item label="账单编号">{{ selectedBill.bill_number }}</el-descriptions-item>
        <el-descriptions-item label="业主">{{ selectedBill.property_info?.owner_name }}</el-descriptions-item>
        <el-descriptions-item label="逾期金额">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ (selectedBill.amount - selectedBill.paid_amount).toFixed(2) }}
          </span>
        </el-descriptions-item>
      </el-descriptions>
      <el-form :model="remindForm" label-width="100px">
        <el-form-item label="催缴方式">
          <el-select v-model="remindForm.method" style="width: 100%;">
            <el-option label="通知单" value="notice" />
            <el-option label="短信" value="sms" />
            <el-option label="电话" value="phone" />
            <el-option label="微信" value="wechat" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行人">
          <el-input v-model="remindForm.operator" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="remindVisible = false">取消</el-button>
        <el-button type="primary" @click="sendReminder" :loading="sending">
          发送催缴
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="payDialogVisible" title="账单缴费" width="500px">
      <el-descriptions :column="1" border style="margin-bottom: 20px;" v-if="selectedBill">
        <el-descriptions-item label="账单编号">{{ selectedBill.bill_number }}</el-descriptions-item>
        <el-descriptions-item label="账单金额">¥{{ selectedBill.amount }}</el-descriptions-item>
        <el-descriptions-item label="已付金额">¥{{ selectedBill.paid_amount }}</el-descriptions-item>
        <el-descriptions-item label="待付金额">
          <span style="color: #f56c6c; font-weight: bold;">
            ¥{{ selectedBill ? (selectedBill.amount - selectedBill.paid_amount).toFixed(2) : 0 }}
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
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="payDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePaySubmit" :loading="paying">
          确认缴费
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { billApi, reminderApi } from '@/api'

const activeTab = ref('overdue')
const loading = ref(false)
const loadingHistory = ref(false)
const sending = ref(false)
const paying = ref(false)

const overdueBills = ref([])
const reminderHistory = ref([])
const currentReminders = ref([])
const selectedBill = ref(null)

const historyVisible = ref(false)
const remindVisible = ref(false)
const payDialogVisible = ref(false)

const stats = reactive({
  overdue_bills_count: 0,
  total_reminders: 0
})

const remindForm = reactive({
  method: 'notice',
  operator: ''
})

const payForm = reactive({
  amount: 0,
  payment_method: 'cash'
})

const maxPayAmount = computed(() => {
  if (!selectedBill.value) return 0
  return selectedBill.value.amount - selectedBill.value.paid_amount
})

const getMethodLabel = (method) => {
  const map = {
    'notice': '通知单',
    'sms': '短信',
    'phone': '电话',
    'wechat': '微信'
  }
  return map[method] || method
}

const loadOverdueBills = async () => {
  loading.value = true
  try {
    const res = await billApi.getOverdue()
    overdueBills.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadReminderHistory = async () => {
  loadingHistory.value = true
  try {
    const res = await reminderApi.getList({ limit: 100 })
    reminderHistory.value = res.data
  } catch (error) {
    console.error(error)
  } finally {
    loadingHistory.value = false
  }
}

const loadStats = async () => {
  try {
    const res = await reminderApi.getStats()
    stats.overdue_bills_count = res.data.overdue_bills_count || 0
    stats.total_reminders = res.data.total_reminders || 0
  } catch (error) {
    console.error(error)
  }
}

const viewReminderHistory = async (row) => {
  selectedBill.value = row
  try {
    const res = await reminderApi.getByBill(row.id)
    currentReminders.value = res.data
    historyVisible.value = true
  } catch (error) {
    console.error(error)
  }
}

const handleRemind = (row) => {
  selectedBill.value = row
  remindForm.method = 'notice'
  remindForm.operator = ''
  remindVisible.value = true
}

const sendReminder = async () => {
  sending.value = true
  try {
    await reminderApi.sendReminder(selectedBill.value.id, {
      method: remindForm.method,
      operator: remindForm.operator || undefined
    })
    ElMessage.success('催缴通知已发送')
    remindVisible.value = false
    loadOverdueBills()
    loadStats()
  } catch (error) {
    console.error(error)
  } finally {
    sending.value = false
  }
}

const handleBatchRemind = async () => {
  try {
    await ElMessageBox.confirm('确定要对所有逾期账单发送催缴通知吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const res = await reminderApi.batchRemindOverdue()
    ElMessage.success(`已对 ${res.data.count} 个逾期账单发送催缴`)
    loadOverdueBills()
    loadStats()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handlePay = (row) => {
  selectedBill.value = row
  payForm.amount = row.amount - row.paid_amount
  payForm.payment_method = 'cash'
  payDialogVisible.value = true
}

const handlePaySubmit = async () => {
  if (payForm.amount <= 0) {
    ElMessage.warning('请输入支付金额')
    return
  }
  
  paying.value = true
  try {
    await billApi.pay(selectedBill.value.id, {
      amount: payForm.amount,
      payment_method: payForm.payment_method
    })
    ElMessage.success('缴费成功')
    payDialogVisible.value = false
    loadOverdueBills()
    loadStats()
  } catch (error) {
    console.error(error)
  } finally {
    paying.value = false
  }
}

onMounted(() => {
  loadOverdueBills()
  loadStats()
})
</script>

<style scoped>
.reminders {
  padding: 0;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #f56c6c;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.sub-text {
  font-size: 12px;
  color: #909399;
}

.overdue-amount {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}

.content-text {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
