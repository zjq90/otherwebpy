<template>
  <div class="invoices">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>票据管理</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleQuickInvoice">
              <el-icon><Plus /></el-icon>
              快速开票
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="票据列表" name="list">
          <div class="filter-bar">
            <el-select v-model="searchForm.status" placeholder="状态筛选" clearable style="width: 120px; margin-right: 10px;">
              <el-option label="待开具" value="pending" />
              <el-option label="已开具" value="issued" />
              <el-option label="已作废" value="voided" />
            </el-select>
            <el-select v-model="searchForm.invoice_type" placeholder="类型筛选" clearable style="width: 120px; margin-right: 10px;">
              <el-option label="收据" value="receipt" />
              <el-option label="发票" value="invoice" />
            </el-select>
            <el-button type="primary" @click="loadInvoices">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
          </div>

          <el-table :data="invoices" stripe style="width: 100%" v-loading="loading">
            <el-table-column prop="invoice_number" label="票据编号" width="200" />
            <el-table-column prop="invoice_type" label="类型" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.invoice_type === 'invoice' ? 'primary' : 'success'">
                  {{ scope.row.invoice_type === 'invoice' ? '发票' : '收据' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额" width="120">
              <template #default="scope">
                <span class="amount-text">¥{{ scope.row.amount }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="invoice_title" label="发票抬头" width="180">
              <template #default="scope">
                {{ scope.row.invoice_title || '-' }}
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusTag(scope.row.status)">
                  {{ getStatusLabel(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="issuer" label="开票人" width="80" />
            <el-table-column prop="issued_at" label="开票时间" width="180" />
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="scope">
                <el-button 
                  v-if="scope.row.status === 'pending'" 
                  type="primary" 
                  link 
                  @click="handleIssue(scope.row)"
                >
                  开具
                </el-button>
                <el-button 
                  v-if="scope.row.status === 'issued'" 
                  type="primary" 
                  link 
                  @click="handlePreview(scope.row)"
                >
                  预览
                </el-button>
                <el-button 
                  v-if="scope.row.status === 'issued'" 
                  type="warning" 
                  link 
                  @click="handleVoid(scope.row)"
                >
                  作废
                </el-button>
                <el-button type="primary" link @click="handleDetail(scope.row)">
                  详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalInvoices"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadInvoices"
            @current-change="loadInvoices"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-tab-pane>

        <el-tab-pane label="待开票账单" name="pending">
          <div class="filter-bar">
            <el-input 
              v-model="pendingSearchForm.search" 
              placeholder="搜索房产编号、业主姓名、账单编号" 
              clearable 
              style="width: 250px; margin-right: 10px;"
              @keyup.enter="loadPendingBills"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-button type="primary" @click="loadPendingBills">
              搜索
            </el-button>
          </div>

          <el-table 
            :data="pendingBills" 
            stripe 
            style="width: 100%" 
            v-loading="pendingLoading"
            @selection-change="handlePendingSelectionChange"
          >
            <el-table-column type="selection" width="50" />
            <el-table-column prop="bill_number" label="账单编号" width="180" />
            <el-table-column prop="property_number" label="房产编号" width="150" />
            <el-table-column prop="owner_name" label="业主姓名" width="100" />
            <el-table-column prop="fee_item_name" label="费用项目" width="120" />
            <el-table-column label="计费周期" width="100">
              <template #default="scope">
                {{ scope.row.billing_year }}年{{ scope.row.billing_month }}月
              </template>
            </el-table-column>
            <el-table-column prop="paid_amount" label="已付金额" width="120">
              <template #default="scope">
                <span class="paid-text">¥{{ scope.row.paid_amount }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="paid_at" label="支付时间" width="160" />
            <el-table-column prop="has_invoice" label="开票状态" width="100">
              <template #default="scope">
                <el-tag :type="scope.row.has_invoice ? 'success' : 'warning'">
                  {{ scope.row.has_invoice ? '已开票' : '未开票' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="scope">
                <el-button 
                  v-if="!scope.row.has_invoice"
                  type="primary" 
                  link 
                  @click="handleInvoiceFromBill(scope.row)"
                >
                  开具发票
                </el-button>
                <el-button 
                  v-if="!scope.row.has_invoice"
                  type="success" 
                  link 
                  @click="handlePreviewInvoice(scope.row)"
                >
                  预览
                </el-button>
                <el-button 
                  v-else
                  type="info" 
                  link 
                  @click="handleViewBillInvoices(scope.row)"
                >
                  查看票据
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="batch-actions" v-if="selectedPendingBills.length > 0">
            <span>已选择 {{ selectedPendingBills.length }} 条记录</span>
            <el-button type="primary" @click="handleBatchInvoice">
              批量开票
            </el-button>
            <el-button @click="clearSelection">
              取消选择
            </el-button>
          </div>

          <el-pagination
            v-model:current-page="pendingPage"
            v-model:page-size="pendingPageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalPendingBills"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="loadPendingBills"
            @current-change="loadPendingBills"
            style="margin-top: 20px; justify-content: flex-end;"
          />
        </el-tab-pane>

        <el-tab-pane label="开票统计" name="stats">
          <el-row :gutter="20" style="margin-bottom: 20px;">
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-label">票据总数</div>
                <div class="stat-value">{{ invoiceStats.total_count || 0 }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-label">总金额</div>
                <div class="stat-value amount">¥{{ invoiceStats.total_amount || 0 }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-label">发票数量</div>
                <div class="stat-value">{{ invoiceStats.invoice_count || 0 }}</div>
              </el-card>
            </el-col>
            <el-col :span="6">
              <el-card class="stat-card">
                <div class="stat-label">收据数量</div>
                <div class="stat-value">{{ invoiceStats.receipt_count || 0 }}</div>
              </el-card>
            </el-col>
          </el-row>

          <el-card>
            <template #header>
              <span>开票统计</span>
            </template>
            <el-descriptions :column="2" border>
              <el-descriptions-item label="发票总金额">
                <span style="color: #409EFF; font-weight: bold;">¥{{ invoiceStats.invoice_amount || 0 }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="收据总金额">
                <span style="color: #67c23a; font-weight: bold;">¥{{ invoiceStats.receipt_amount || 0 }}</span>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="quickInvoiceVisible" title="快速开票" width="600px">
      <el-form :model="quickInvoiceForm" label-width="100px">
        <el-form-item label="选择账单">
          <el-select 
            v-model="quickInvoiceForm.bill_id" 
            placeholder="请选择账单（仅显示已支付账单）" 
            filterable
            style="width: 100%;"
            @change="handleQuickInvoiceBillChange"
          >
            <el-option 
              v-for="bill in quickInvoiceBills" 
              :key="bill.id" 
              :label="`${bill.bill_number} - ${bill.property_number} - ${bill.owner_name} - ¥${bill.paid_amount}`"
              :value="bill.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="票据类型">
          <el-select v-model="quickInvoiceForm.invoice_type" style="width: 100%;">
            <el-option label="收据" value="receipt" />
            <el-option label="发票" value="invoice" />
          </el-select>
        </el-form-item>
        <el-form-item label="发票抬头" v-if="quickInvoiceForm.invoice_type === 'invoice'">
          <el-input v-model="quickInvoiceForm.invoice_title" placeholder="请输入发票抬头（如：某某公司）" />
        </el-form-item>
        <el-form-item label="税号" v-if="quickInvoiceForm.invoice_type === 'invoice'">
          <el-input v-model="quickInvoiceForm.tax_number" placeholder="请输入税号" />
        </el-form-item>
        <el-form-item label="开票人">
          <el-input v-model="quickInvoiceForm.issuer" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="quickInvoiceVisible = false">取消</el-button>
        <el-button type="primary" @click="handleQuickInvoiceSubmit" :loading="quickInvoicing">
          确认开具
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="invoiceFormVisible" title="开具票据" width="500px">
      <el-form :model="invoiceForm" label-width="100px">
        <el-form-item label="票据类型">
          <el-select v-model="invoiceForm.invoice_type" style="width: 100%;">
            <el-option label="收据" value="receipt" />
            <el-option label="发票" value="invoice" />
          </el-select>
        </el-form-item>
        <el-form-item label="发票抬头" v-if="invoiceForm.invoice_type === 'invoice'">
          <el-input v-model="invoiceForm.invoice_title" placeholder="请输入发票抬头" />
        </el-form-item>
        <el-form-item label="税号" v-if="invoiceForm.invoice_type === 'invoice'">
          <el-input v-model="invoiceForm.tax_number" placeholder="请输入税号" />
        </el-form-item>
        <el-form-item label="开票人">
          <el-input v-model="invoiceForm.issuer" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="invoiceFormVisible = false">取消</el-button>
        <el-button type="primary" @click="handleInvoiceSubmit" :loading="invoicing">
          确认开具
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="batchInvoiceVisible" title="批量开票" width="500px">
      <el-alert 
        title="批量开票提示" 
        type="warning" 
        :closable="false"
        style="margin-bottom: 20px;"
      >
        已选择 {{ selectedPendingBills.length }} 条记录，将为这些账单统一开具票据。
      </el-alert>
      <el-form :model="batchInvoiceForm" label-width="100px">
        <el-form-item label="票据类型">
          <el-select v-model="batchInvoiceForm.invoice_type" style="width: 100%;">
            <el-option label="收据" value="receipt" />
            <el-option label="发票" value="invoice" />
          </el-select>
        </el-form-item>
        <el-form-item label="发票抬头" v-if="batchInvoiceForm.invoice_type === 'invoice'">
          <el-input v-model="batchInvoiceForm.invoice_title" placeholder="批量开票请输入统一的发票抬头" />
        </el-form-item>
        <el-form-item label="税号" v-if="batchInvoiceForm.invoice_type === 'invoice'">
          <el-input v-model="batchInvoiceForm.tax_number" placeholder="批量开票请输入统一的税号" />
        </el-form-item>
        <el-form-item label="开票人">
          <el-input v-model="batchInvoiceForm.issuer" placeholder="可选" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="batchInvoiceVisible = false">取消</el-button>
        <el-button type="primary" @click="handleBatchInvoiceSubmit" :loading="batchInvoicing">
          确认批量开票
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="previewVisible" title="发票预览" width="800px">
      <div class="invoice-preview" v-if="previewData">
        <div class="invoice-header">
          <div class="invoice-title">{{ previewData.invoice_type_name }}</div>
          <div class="invoice-number">票据编号：{{ previewData.bill_number }}</div>
        </div>
        
        <el-divider />
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="开票日期">
            {{ previewData.preview_date }}
          </el-descriptions-item>
          <el-descriptions-item label="计费周期">
            {{ previewData.billing_period }}
          </el-descriptions-item>
          <el-descriptions-item label="业主姓名" :span="2">
            {{ previewData.property_info?.owner_name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="房产编号" :span="2">
            {{ previewData.property_info?.property_number || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="房产地址">
            {{ previewData.property_info?.building }} {{ previewData.property_info?.unit }} {{ previewData.property_info?.room_number }}
          </el-descriptions-item>
          <el-descriptions-item label="建筑面积">
            {{ previewData.property_info?.area }} 平方米
          </el-descriptions-item>
          <el-descriptions-item label="费用项目">
            {{ previewData.fee_item_info?.name || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="计费标准">
            {{ previewData.fee_item_info?.billing_cycle === 'monthly' ? '按月' : previewData.fee_item_info?.billing_cycle === 'yearly' ? '按年' : '其他' }}
          </el-descriptions-item>
        </el-descriptions>

        <el-divider />

        <div class="amount-section">
          <div class="amount-row">
            <span class="amount-label">账单金额：</span>
            <span class="amount-value">¥{{ previewData.paid_info?.total_amount }}</span>
          </div>
          <div class="amount-row">
            <span class="amount-label">已付金额：</span>
            <span class="amount-value paid">¥{{ previewData.paid_info?.paid_amount }}</span>
          </div>
          <div class="amount-row total">
            <span class="amount-label">开票金额（大写）：</span>
            <span class="amount-value">{{ previewData.amount_cn }}</span>
          </div>
          <div class="amount-row total">
            <span class="amount-label">开票金额（小写）：</span>
            <span class="amount-value">¥{{ previewData.amount }}</span>
          </div>
        </div>

        <el-divider />

        <div class="invoice-footer">
          <div class="footer-item">
            <span>开票人：{{ invoiceForm.issuer || '系统' }}</span>
          </div>
          <div class="footer-item">
            <span>联系电话：{{ previewData.property_info?.owner_phone || '-' }}</span>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handlePrintPreview">
          <el-icon><Printer /></el-icon>
          打印预览
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="票据详情" width="600px">
      <el-descriptions :column="2" border v-if="selectedInvoice">
        <el-descriptions-item label="票据编号" :span="2">{{ selectedInvoice.invoice_number }}</el-descriptions-item>
        <el-descriptions-item label="票据类型">
          <el-tag :type="selectedInvoice.invoice_type === 'invoice' ? 'primary' : 'success'">
            {{ selectedInvoice.invoice_type === 'invoice' ? '发票' : '收据' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="票据状态">
          <el-tag :type="getStatusTag(selectedInvoice.status)">
            {{ getStatusLabel(selectedInvoice.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="票据金额">
          <span style="color: #f56c6c; font-weight: bold; font-size: 18px;">
            ¥{{ selectedInvoice.amount }}
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="开票人">{{ selectedInvoice.issuer || '-' }}</el-descriptions-item>
        <el-descriptions-item label="发票抬头" :span="2">{{ selectedInvoice.invoice_title || '-' }}</el-descriptions-item>
        <el-descriptions-item label="税号" :span="2">{{ selectedInvoice.tax_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="开票时间" :span="2">{{ selectedInvoice.issued_at || '-' }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ selectedInvoice.remark || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Printer } from '@element-plus/icons-vue'
import { invoiceApi } from '@/api'

const activeTab = ref('list')

const invoices = ref([])
const loading = ref(false)
const invoicing = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const totalInvoices = ref(0)

const pendingBills = ref([])
const pendingLoading = ref(false)
const pendingPage = ref(1)
const pendingPageSize = ref(20)
const totalPendingBills = ref(0)
const selectedPendingBills = ref([])

const invoiceStats = ref({})

const selectedInvoice = ref(null)
const previewData = ref(null)

const searchForm = reactive({
  status: '',
  invoice_type: ''
})

const pendingSearchForm = reactive({
  search: ''
})

const detailVisible = ref(false)
const previewVisible = ref(false)
const invoiceFormVisible = ref(false)
const quickInvoiceVisible = ref(false)
const batchInvoiceVisible = ref(false)

const quickInvoiceBills = ref([])

const invoiceForm = reactive({
  invoice_type: 'receipt',
  invoice_title: '',
  tax_number: '',
  issuer: ''
})

const quickInvoiceForm = reactive({
  bill_id: null,
  invoice_type: 'receipt',
  invoice_title: '',
  tax_number: '',
  issuer: ''
})

const batchInvoiceForm = reactive({
  invoice_type: 'receipt',
  invoice_title: '',
  tax_number: '',
  issuer: ''
})

const quickInvoicing = ref(false)
const batchInvoicing = ref(false)

const getStatusTag = (status) => {
  const map = {
    'pending': 'warning',
    'issued': 'success',
    'voided': 'danger'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    'pending': '待开具',
    'issued': '已开具',
    'voided': '已作废'
  }
  return map[status] || status
}

const handleTabChange = (tab) => {
  if (tab === 'list') {
    loadInvoices()
  } else if (tab === 'pending') {
    loadPendingBills()
  } else if (tab === 'stats') {
    loadInvoiceStats()
  }
}

const loadInvoices = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    if (searchForm.invoice_type) {
      params.invoice_type = searchForm.invoice_type
    }
    const res = await invoiceApi.getList(params)
    invoices.value = res.data
    totalInvoices.value = res.data.length
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const loadPendingBills = async () => {
  pendingLoading.value = true
  try {
    const params = {
      skip: (pendingPage.value - 1) * pendingPageSize.value,
      limit: pendingPageSize.value
    }
    if (pendingSearchForm.search) {
      params.search = pendingSearchForm.search
    }
    const res = await invoiceApi.getPendingBills(params)
    pendingBills.value = res.data.items
    totalPendingBills.value = res.data.total
  } catch (error) {
    console.error(error)
  } finally {
    pendingLoading.value = false
  }
}

const loadInvoiceStats = async () => {
  try {
    const res = await invoiceApi.getOverview()
    invoiceStats.value = res.data.summary || {}
  } catch (error) {
    console.error(error)
  }
}

const loadQuickInvoiceBills = async () => {
  try {
    const params = {
      skip: 0,
      limit: 100
    }
    const res = await invoiceApi.getPendingBills(params)
    quickInvoiceBills.value = res.data.items.filter(item => !item.has_invoice)
  } catch (error) {
    console.error(error)
  }
}

const handleQuickInvoice = () => {
  quickInvoiceForm.bill_id = null
  quickInvoiceForm.invoice_type = 'receipt'
  quickInvoiceForm.invoice_title = ''
  quickInvoiceForm.tax_number = ''
  quickInvoiceForm.issuer = ''
  loadQuickInvoiceBills()
  quickInvoiceVisible.value = true
}

const handleQuickInvoiceBillChange = async (billId) => {
  if (billId) {
    try {
      const res = await invoiceApi.getPreview(billId, quickInvoiceForm.invoice_type)
      previewData.value = res.data
    } catch (error) {
      console.error(error)
    }
  }
}

const handleQuickInvoiceSubmit = async () => {
  if (!quickInvoiceForm.bill_id) {
    ElMessage.warning('请选择账单')
    return
  }
  if (quickInvoiceForm.invoice_type === 'invoice' && !quickInvoiceForm.invoice_title) {
    ElMessage.warning('请输入发票抬头')
    return
  }
  
  quickInvoicing.value = true
  try {
    await invoiceApi.createFromBill(quickInvoiceForm.bill_id, {
      invoice_type: quickInvoiceForm.invoice_type,
      invoice_title: quickInvoiceForm.invoice_title || undefined,
      tax_number: quickInvoiceForm.tax_number || undefined,
      issuer: quickInvoiceForm.issuer || undefined
    })
    ElMessage.success('开票成功')
    quickInvoiceVisible.value = false
    loadInvoices()
    loadPendingBills()
  } catch (error) {
    console.error(error)
  } finally {
    quickInvoicing.value = false
  }
}

const handleInvoiceFromBill = (row) => {
  selectedInvoice.value = row
  invoiceForm.invoice_type = 'invoice'
  invoiceForm.invoice_title = ''
  invoiceForm.tax_number = ''
  invoiceForm.issuer = ''
  invoiceFormVisible.value = true
}

const handleInvoiceSubmit = async () => {
  if (invoiceForm.invoice_type === 'invoice' && !invoiceForm.invoice_title) {
    ElMessage.warning('请输入发票抬头')
    return
  }
  
  invoicing.value = true
  try {
    await invoiceApi.createFromBill(selectedInvoice.value.id, {
      invoice_type: invoiceForm.invoice_type,
      invoice_title: invoiceForm.invoice_title || undefined,
      tax_number: invoiceForm.tax_number || undefined,
      issuer: invoiceForm.issuer || undefined
    })
    ElMessage.success('开票成功')
    invoiceFormVisible.value = false
    loadInvoices()
    loadPendingBills()
  } catch (error) {
    console.error(error)
  } finally {
    invoicing.value = false
  }
}

const handlePreviewInvoice = async (row) => {
  try {
    const res = await invoiceApi.getPreview(row.id, 'invoice')
    previewData.value = res.data
    invoiceForm.invoice_type = 'invoice'
    invoiceForm.issuer = ''
    previewVisible.value = true
  } catch (error) {
    console.error(error)
  }
}

const handlePreview = async (row) => {
  try {
    const res = await invoiceApi.getPreview(row.bill_id, row.invoice_type)
    previewData.value = res.data
    invoiceForm.issuer = row.issuer || ''
    previewVisible.value = true
  } catch (error) {
    console.error(error)
  }
}

const handlePrintPreview = () => {
  ElMessage.info('打印功能正在开发中，您可以截图或复制内容进行打印')
}

const handlePendingSelectionChange = (selection) => {
  selectedPendingBills.value = selection.filter(item => !item.has_invoice)
}

const clearSelection = () => {
  selectedPendingBills.value = []
}

const handleBatchInvoice = () => {
  if (selectedPendingBills.value.length === 0) {
    ElMessage.warning('请选择需要开票的账单')
    return
  }
  batchInvoiceForm.invoice_type = 'invoice'
  batchInvoiceForm.invoice_title = ''
  batchInvoiceForm.tax_number = ''
  batchInvoiceForm.issuer = ''
  batchInvoiceVisible.value = true
}

const handleBatchInvoiceSubmit = async () => {
  if (batchInvoiceForm.invoice_type === 'invoice' && !batchInvoiceForm.invoice_title) {
    ElMessage.warning('批量开票请输入统一的发票抬头')
    return
  }
  
  batchInvoicing.value = true
  try {
    const billIds = selectedPendingBills.value.map(item => item.id)
    const res = await invoiceApi.batchIssue({
      bill_ids: billIds,
      invoice_type: batchInvoiceForm.invoice_type,
      invoice_title: batchInvoiceForm.invoice_title || undefined,
      tax_number: batchInvoiceForm.tax_number || undefined,
      issuer: batchInvoiceForm.issuer || undefined
    })
    
    const result = res.data.result
    if (result.fail_count > 0) {
      ElMessage.warning(`批量开票完成：成功 ${result.success_count} 张，失败 ${result.fail_count} 张`)
    } else {
      ElMessage.success(`批量开票完成：成功 ${result.success_count} 张`)
    }
    
    batchInvoiceVisible.value = false
    clearSelection()
    loadInvoices()
    loadPendingBills()
  } catch (error) {
    console.error(error)
  } finally {
    batchInvoicing.value = false
  }
}

const handleIssue = (row) => {
  selectedInvoice.value = row
  invoiceForm.invoice_type = row.invoice_type
  invoiceForm.invoice_title = row.invoice_title || ''
  invoiceForm.tax_number = row.tax_number || ''
  invoiceForm.issuer = row.issuer || ''
  invoiceFormVisible.value = true
}

const handleVoid = async (row) => {
  try {
    await ElMessageBox.confirm('确定要作废该票据吗？作废后不可恢复。', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await invoiceApi.void(row.id)
    ElMessage.success('票据已作废')
    loadInvoices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleDetail = (row) => {
  selectedInvoice.value = row
  detailVisible.value = true
}

const handleViewBillInvoices = async (row) => {
  try {
    const res = await invoiceApi.getByBill(row.id)
    if (res.data && res.data.length > 0) {
      selectedInvoice.value = res.data[0]
      detailVisible.value = true
    } else {
      ElMessage.info('该账单暂无票据')
    }
  } catch (error) {
    console.error(error)
  }
}

onMounted(() => {
  loadInvoices()
})
</script>

<style scoped>
.invoices {
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

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.amount-text {
  color: #f56c6c;
  font-weight: bold;
}

.paid-text {
  color: #67c23a;
  font-weight: bold;
}

.batch-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  background-color: #fdf6ec;
  border-radius: 4px;
  margin-top: 15px;
}

.stat-card {
  text-align: center;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-value.amount {
  color: #f56c6c;
}

.invoice-preview {
  padding: 20px;
}

.invoice-header {
  text-align: center;
  margin-bottom: 20px;
}

.invoice-title {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.invoice-number {
  font-size: 14px;
  color: #909399;
}

.amount-section {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.amount-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
}

.amount-row.total {
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
  margin-top: 10px;
}

.amount-label {
  font-size: 14px;
  color: #606266;
}

.amount-value {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.amount-value.paid {
  color: #67c23a;
}

.invoice-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 20px;
  color: #909399;
  font-size: 14px;
}
</style>
