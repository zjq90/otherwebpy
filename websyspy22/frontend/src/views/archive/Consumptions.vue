<template>
  <div class="consumptions">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">消费记录</span>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          新增记录
        </el-button>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">总消费金额</div>
              <div class="stat-value">¥{{ stats.totalAmount.toLocaleString() }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">总折扣金额</div>
              <div class="stat-value">¥{{ stats.totalDiscount.toLocaleString() }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">消费次数</div>
              <div class="stat-value">{{ stats.count }}次</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">本月消费</div>
              <div class="stat-value">¥{{ stats.monthAmount.toLocaleString() }}</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="会员姓名">
          <el-input v-model="searchForm.member_name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="消费类型">
          <el-select v-model="searchForm.type" placeholder="请选择类型" clearable>
            <el-option label="会员卡" value="会员卡" />
            <el-option label="私教课" value="私教课" />
            <el-option label="团课" value="团课" />
            <el-option label="营养品" value="营养品" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="消费日期">
          <el-date-picker
            v-model="searchForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="member_name" label="会员姓名" width="100" />
        <el-table-column prop="consumption_date" label="消费日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.consumption_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="consumption_type" label="消费类型" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.consumption_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="消费金额" width="120">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600;">
              ¥{{ (row.amount || 0).toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="discount_amount" label="折扣金额" width="100">
          <template #default="{ row }">
            <span v-if="row.discount_amount > 0" style="color: #67c23a;">
              -¥{{ (row.discount_amount || 0).toLocaleString() }}
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="payment_method" label="支付方式" width="100" />
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑消费记录' : '新增消费记录'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="会员" prop="member_id">
          <el-select
            v-model="form.member_id"
            placeholder="请选择会员"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="member in memberOptions"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="消费日期" prop="consumption_date">
          <el-date-picker
            v-model="form.consumption_date"
            type="date"
            placeholder="请选择消费日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="消费类型" prop="consumption_type">
          <el-select v-model="form.consumption_type" placeholder="请选择消费类型" style="width: 100%">
            <el-option label="会员卡" value="会员卡" />
            <el-option label="私教课" value="私教课" />
            <el-option label="团课" value="团课" />
            <el-option label="营养品" value="营养品" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="消费金额" prop="amount">
          <el-input-number
            v-model="form.amount"
            :min="0"
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="支付方式" prop="payment_method">
          <el-select v-model="form.payment_method" placeholder="请选择支付方式" style="width: 100%">
            <el-option label="微信支付" value="微信支付" />
            <el-option label="支付宝" value="支付宝" />
            <el-option label="现金" value="现金" />
            <el-option label="银行卡" value="银行卡" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import {
  getConsumptions, createConsumption, updateConsumption, deleteConsumption
} from '@/api/archive'
import { getMemberList } from '@/api/member'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  member_name: '',
  type: '',
  date_range: []
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const stats = reactive({
  totalAmount: 8500,
  totalDiscount: 350,
  count: 3,
  monthAmount: 3500
})

const tableData = ref([])
const memberOptions = ref([])

const form = reactive({
  member_id: null,
  consumption_date: '',
  consumption_type: '',
  amount: 0,
  payment_method: '',
  notes: ''
})

const rules = {
  member_id: [
    { required: true, message: '请选择会员', trigger: 'change' }
  ],
  consumption_date: [
    { required: true, message: '请选择消费日期', trigger: 'change' }
  ],
  consumption_type: [
    { required: true, message: '请选择消费类型', trigger: 'change' }
  ],
  amount: [
    { required: true, message: '请输入消费金额', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getConsumptions({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    if (res.data) {
      tableData.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    // 使用模拟数据
    tableData.value = [
      { id: 1, member_name: '张三', consumption_date: '2024-01-15', consumption_type: '会员卡', amount: 5000, discount_amount: 0, payment_method: '微信支付', notes: '办理年卡' },
      { id: 2, member_name: '张三', consumption_date: '2024-02-10', consumption_type: '私教课', amount: 3000, discount_amount: 300, payment_method: '支付宝', notes: '购买10节私教课' },
      { id: 3, member_name: '张三', consumption_date: '2024-03-05', consumption_type: '营养品', amount: 500, discount_amount: 50, payment_method: '现金', notes: '购买蛋白粉' }
    ]
    pagination.total = 3
  } finally {
    loading.value = false
  }
}

const fetchMembers = async () => {
  try {
    const res = await getMemberList({ page_size: 100 })
    if (res.data) {
      memberOptions.value = res.data.items || []
    }
  } catch (error) {
    memberOptions.value = [
      { id: 1, name: '张三' },
      { id: 2, name: '李四' },
      { id: 3, name: '王五' }
    ]
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.member_name = ''
  searchForm.type = ''
  searchForm.date_range = []
  handleSearch()
}

const resetForm = () => {
  form.member_id = null
  form.consumption_date = ''
  form.consumption_type = ''
  form.amount = 0
  form.payment_method = ''
  form.notes = ''
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  fetchMembers()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  fetchMembers()
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该消费记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteConsumption(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateConsumption(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createConsumption(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.consumptions {
  .stat-item {
    text-align: center;

    .stat-label {
      font-size: 14px;
      color: #909399;
    }

    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      margin-top: 8px;
    }
  }

  .search-form {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }

  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
