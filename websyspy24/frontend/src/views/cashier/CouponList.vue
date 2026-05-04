<template>
  <!-- 优惠券管理页面 -->
  <div class="coupon-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="优惠券码">
          <el-input
            v-model="searchForm.coupon_code"
            placeholder="请输入优惠券码"
            clearable
            @keyup.enter="handleSearch"
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="可用" value="available" />
            <el-option label="已使用" value="used" />
            <el-option label="已过期" value="expired" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.coupon_type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="代金券" value="cash" />
            <el-option label="折扣券" value="discount" />
            <el-option label="赠品券" value="gift" />
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
          新增优惠券
        </el-button>
        <el-button type="success" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>
    
    <!-- 优惠券列表 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
      >
        <el-table-column prop="coupon_code" label="优惠券码" width="150" />
        <el-table-column prop="name" label="优惠券名称" min-width="150" />
        <el-table-column prop="coupon_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getCouponType(row.coupon_type)" effect="light">
              {{ getCouponTypeName(row.coupon_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="面值/折扣" width="120">
          <template #default="{ row }">
            <template v-if="row.coupon_type === 'cash'">
              <span class="text-danger">¥{{ row.value }}</span>
            </template>
            <template v-else-if="row.coupon_type === 'discount'">
              <span class="text-warning">{{ row.value * 10 }}折</span>
            </template>
            <template v-else>
              <span class="text-success">赠品</span>
            </template>
          </template>
        </el-table-column>
        <el-table-column prop="min_amount" label="最低消费" width="100">
          <template #default="{ row }">
            <span v-if="row.min_amount > 0">¥{{ row.min_amount }}</span>
            <span v-else class="text-muted">无限制</span>
          </template>
        </el-table-column>
        <el-table-column prop="issue_time" label="发放时间" width="160">
          <template #default="{ row }">
            {{ row.issue_time ? formatDateTime(row.issue_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="expire_time" label="过期时间" width="160">
          <template #default="{ row }">
            <span :class="{ 'text-danger': isExpired(row.expire_time) }">
              {{ row.expire_time ? formatDateTime(row.expire_time) : '-' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="light">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              size="small" plain 
              @click="handleView(row)"
            >
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
    
    <!-- 新增优惠券弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      title="新增优惠券"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="couponFormRef"
        :model="couponForm"
        :rules="couponRules"
        label-width="100px"
      >
        <el-form-item label="优惠券码" prop="coupon_code">
          <el-input v-model="couponForm.coupon_code" placeholder="请输入优惠券码" />
        </el-form-item>
        <el-form-item label="优惠券名称" prop="name">
          <el-input v-model="couponForm.name" placeholder="请输入优惠券名称" />
        </el-form-item>
        <el-form-item label="优惠券类型" prop="coupon_type">
          <el-select v-model="couponForm.coupon_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="代金券" value="cash" />
            <el-option label="折扣券" value="discount" />
            <el-option label="赠品券" value="gift" />
          </el-select>
        </el-form-item>
        <el-form-item label="面值/折扣" prop="value">
          <el-input-number 
            v-model="couponForm.value" 
            :min="0" 
            :precision="2"
            style="width: 100%"
          />
          <div class="tip">
            代金券：填写金额；折扣券：填写0.1-0.95（如0.9表示9折）
          </div>
        </el-form-item>
        <el-form-item label="最低消费">
          <el-input-number 
            v-model="couponForm.min_amount" 
            :min="0" 
            :precision="2"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="过期时间" prop="expire_time">
          <el-date-picker
            v-model="couponForm.expire_time"
            type="datetime"
            placeholder="选择过期时间"
            value-format="YYYY-MM-DD HH:mm:ss"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="couponForm.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述"
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
    
    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="优惠券详情"
      width="400px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="优惠券码">
          {{ currentCoupon?.coupon_code }}
        </el-descriptions-item>
        <el-descriptions-item label="优惠券名称">
          {{ currentCoupon?.name }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="getCouponType(currentCoupon?.coupon_type)">
            {{ getCouponTypeName(currentCoupon?.coupon_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="面值">
          <template v-if="currentCoupon?.coupon_type === 'cash'">
            <span class="text-danger">¥{{ currentCoupon?.value }}</span>
          </template>
          <template v-else-if="currentCoupon?.coupon_type === 'discount'">
            <span class="text-warning">{{ currentCoupon?.value * 10 }}折</span>
          </template>
          <template v-else>
            赠品
          </template>
        </el-descriptions-item>
        <el-descriptions-item label="最低消费">
          ¥{{ currentCoupon?.min_amount || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="发放时间">
          {{ currentCoupon?.issue_time ? formatDateTime(currentCoupon.issue_time) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="过期时间">
          {{ currentCoupon?.expire_time ? formatDateTime(currentCoupon.expire_time) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentCoupon?.status)">
            {{ getStatusText(currentCoupon?.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="使用时间" v-if="currentCoupon?.used_time">
          {{ formatDateTime(currentCoupon.used_time) }}
        </el-descriptions-item>
        <el-descriptions-item label="描述">
          {{ currentCoupon?.description || '无' }}
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  coupon_code: '',
  status: '',
  coupon_type: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 弹窗相关
const dialogVisible = ref(false)
const submitLoading = ref(false)
const couponFormRef = ref<FormInstance>()

// 优惠券表单
const couponForm = reactive({
  coupon_code: '',
  name: '',
  coupon_type: 'cash',
  value: 0,
  min_amount: 0,
  expire_time: '',
  description: ''
})

// 详情相关
const detailDialogVisible = ref(false)
const currentCoupon = ref(null)

// 表单验证规则
const couponRules: FormRules = {
  coupon_code: [{ required: true, message: '请输入优惠券码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入优惠券名称', trigger: 'blur' }],
  coupon_type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  value: [{ required: true, message: '请输入面值', trigger: 'blur' }],
  expire_time: [{ required: true, message: '请选择过期时间', trigger: 'change' }]
}

// 获取优惠券类型
const getCouponType = (type) => {
  const map = {
    cash: 'danger',
    discount: 'warning',
    gift: 'success'
  }
  return map[type] || 'info'
}

const getCouponTypeName = (type) => {
  const map = {
    cash: '代金券',
    discount: '折扣券',
    gift: '赠品券'
  }
  return map[type] || type
}

// 获取状态类型
const getStatusType = (status) => {
  const map = {
    available: 'success',
    used: 'info',
    expired: 'danger'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    available: '可用',
    used: '已使用',
    expired: '已过期'
  }
  return map[status] || status
}

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 判断是否过期
const isExpired = (expireTime) => {
  if (!expireTime) return false
  return dayjs(expireTime).isBefore(dayjs())
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getCoupons({
      page: pagination.page,
      page_size: pagination.pageSize,
      coupon_code: searchForm.coupon_code || undefined,
      status: searchForm.status || undefined,
      coupon_type: searchForm.coupon_type || undefined
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
  searchForm.coupon_code = ''
  searchForm.status = ''
  searchForm.coupon_type = ''
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

// 新增优惠券
const handleAdd = () => {
  Object.assign(couponForm, {
    coupon_code: '',
    name: '',
    coupon_type: 'cash',
    value: 0,
    min_amount: 0,
    expire_time: '',
    description: ''
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!couponFormRef.value) return
  
  await couponFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        await api.createCoupon(couponForm)
        ElMessage.success('创建成功')
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

// 查看详情
const handleView = (row) => {
  currentCoupon.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.coupon-list {
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

.text-warning {
  color: #E6A23C;
  font-weight: bold;
}

.text-success {
  color: #67C23A;
  font-weight: bold;
}

.text-muted {
  color: #909399;
}

.tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
