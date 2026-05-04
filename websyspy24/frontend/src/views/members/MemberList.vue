<template>
  <!-- 会员管理页面 -->
  <div class="member-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.keyword"
            placeholder="会员编号/姓名/手机号"
            clearable
            @keyup.enter="handleSearch"
            style="width: 250px"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="激活" value="active" />
            <el-option label="过期" value="expired" />
            <el-option label="暂停" value="suspended" />
          </el-select>
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
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增会员
        </el-button>
        <el-button type="success" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>
    
    <!-- 会员列表表格 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="member_no" label="会员编号" width="150" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="手机号" width="130" />
        <el-table-column prop="membership_type" label="会籍类型" width="100" />
        <el-table-column prop="membership_end" label="到期日期" width="120">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isExpired(row.membership_end) }">
              {{ row.membership_end }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="balance" label="账户余额" width="100">
          <template #default="{ row }">
            <span class="text-primary">¥{{ row.balance?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="light">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="success" size="small" plain @click="handleRecharge(row)">
              <el-icon><Money /></el-icon>
              充值
            </el-button>
            <el-button type="danger" size="small" plain @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>
              停用
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
    
    <!-- 新增/编辑会员弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="memberFormRef"
        :model="memberForm"
        :rules="memberRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="会员编号" prop="member_no">
              <el-input v-model="memberForm.member_no" placeholder="请输入会员编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="name">
              <el-input v-model="memberForm.name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="memberForm.phone" placeholder="请输入手机号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="身份证号">
              <el-input v-model="memberForm.id_card" placeholder="请输入身份证号" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="卡号">
              <el-input v-model="memberForm.card_no" placeholder="刷卡签到用卡号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="二维码">
              <el-input v-model="memberForm.qr_code" placeholder="扫码签到用二维码" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="会籍类型" prop="membership_type">
              <el-select v-model="memberForm.membership_type" placeholder="请选择会籍类型" style="width: 100%">
                <el-option label="月卡" value="月卡" />
                <el-option label="季卡" value="季卡" />
                <el-option label="年卡" value="年卡" />
                <el-option label="次卡" value="次卡" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="到期日期" prop="membership_end">
              <el-date-picker
                v-model="memberForm.membership_end"
                type="date"
                placeholder="选择到期日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="账户余额">
              <el-input-number v-model="memberForm.balance" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="memberForm.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="激活" value="active" />
                <el-option label="暂停" value="suspended" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="人脸数据">
          <el-input
            v-model="memberForm.face_data"
            type="textarea"
            :rows="2"
            placeholder="人脸特征数据（人脸识别签到用）"
          />
        </el-form-item>
        
        <el-form-item label="备注">
          <el-input
            v-model="memberForm.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 充值弹窗 -->
    <el-dialog
      v-model="rechargeDialogVisible"
      title="会员充值"
      width="450px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="会员编号">{{ currentMember?.member_no }}</el-descriptions-item>
        <el-descriptions-item label="会员姓名">{{ currentMember?.name }}</el-descriptions-item>
        <el-descriptions-item label="当前余额">
          <span class="text-primary">¥{{ currentMember?.balance?.toFixed(2) || '0.00' }}</span>
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider />
      
      <el-form label-width="100px">
        <el-form-item label="充值金额">
          <el-input-number v-model="rechargeForm.amount" :min="0" :precision="2" style="width: 200px" />
          <span style="margin-left: 10px">元</span>
        </el-form-item>
        <el-form-item label="赠送金额">
          <el-input-number v-model="rechargeForm.gift_amount" :min="0" :precision="2" style="width: 200px" />
          <span style="margin-left: 10px">元</span>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-radio-group v-model="rechargeForm.payment_method">
            <el-radio label="cash">现金</el-radio>
            <el-radio label="wechat">微信</el-radio>
            <el-radio label="alipay">支付宝</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="rechargeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleRechargeSubmit" :loading="rechargeLoading">
          确认充值
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 表格数据
const tableData = ref([])
const loading = ref(false)
const selectedRows = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  status: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 弹窗相关
const dialogVisible = ref(false)
const dialogTitle = ref('新增会员')
const isEdit = ref(false)
const submitLoading = ref(false)
const memberFormRef = ref<FormInstance>()

// 会员表单
const memberForm = reactive({
  member_no: '',
  name: '',
  phone: '',
  id_card: '',
  card_no: '',
  qr_code: '',
  face_data: '',
  membership_type: '月卡',
  membership_end: '',
  balance: 0,
  status: 'active',
  remarks: ''
})

// 表单验证规则
const memberRules: FormRules = {
  member_no: [{ required: true, message: '请输入会员编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  membership_type: [{ required: true, message: '请选择会籍类型', trigger: 'change' }],
  membership_end: [{ required: true, message: '请选择到期日期', trigger: 'change' }]
}

// 充值相关
const rechargeDialogVisible = ref(false)
const currentMember = ref(null)
const rechargeLoading = ref(false)
const rechargeForm = reactive({
  amount: 0,
  gift_amount: 0,
  payment_method: 'cash'
})

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    active: 'success',
    expired: 'warning',
    suspended: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const textMap = {
    active: '激活',
    expired: '过期',
    suspended: '暂停'
  }
  return textMap[status] || status
}

// 判断是否过期
const isExpired = (date) => {
  if (!date) return false
  return dayjs(date).isBefore(dayjs(), 'day')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getMembers({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword || undefined,
      status: searchForm.status || undefined
    })
    
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
  searchForm.keyword = ''
  searchForm.status = ''
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

// 选择变更
const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

// 新增会员
const handleAdd = () => {
  dialogTitle.value = '新增会员'
  isEdit.value = false
  // 重置表单
  Object.assign(memberForm, {
    member_no: '',
    name: '',
    phone: '',
    id_card: '',
    card_no: '',
    qr_code: '',
    face_data: '',
    membership_type: '月卡',
    membership_end: '',
    balance: 0,
    status: 'active',
    remarks: ''
  })
  dialogVisible.value = true
}

// 编辑会员
const handleEdit = (row) => {
  dialogTitle.value = '编辑会员'
  isEdit.value = true
  currentMember.value = row
  
  // 填充表单
  Object.assign(memberForm, {
    ...row,
    membership_end: row.membership_end
  })
  
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!memberFormRef.value) return
  
  await memberFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          // 更新
          await api.updateMember(currentMember.value.id, memberForm)
          ElMessage.success('更新成功')
        } else {
          // 新增
          await api.createMember(memberForm)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 删除/停用会员
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要停用法会员「${row.name}」吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.deleteMember(row.id)
      ElMessage.success('停用成功')
      loadData()
    } catch (error) {
      console.error('停用失败:', error)
    }
  }).catch(() => {})
}

// 充值
const handleRecharge = (row) => {
  currentMember.value = row
  rechargeForm.amount = 0
  rechargeForm.gift_amount = 0
  rechargeForm.payment_method = 'cash'
  rechargeDialogVisible.value = true
}

// 提交充值
const handleRechargeSubmit = async () => {
  if (rechargeForm.amount <= 0) {
    ElMessage.warning('请输入充值金额')
    return
  }
  
  rechargeLoading.value = true
  try {
    await api.memberRecharge(
      currentMember.value.id,
      rechargeForm.amount,
      rechargeForm.gift_amount,
      rechargeForm.payment_method,
      '管理员'
    )
    ElMessage.success('充值成功')
    rechargeDialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('充值失败:', error)
  } finally {
    rechargeLoading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.member-list {
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

.text-primary {
  color: #409EFF;
  font-weight: bold;
}

.text-danger {
  color: #F56C6C;
}
</style>
