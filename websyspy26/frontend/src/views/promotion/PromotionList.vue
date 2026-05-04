<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <span class="page-title">促销活动管理</span>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新增活动
      </el-button>
    </div>

    <!-- 搜索区域 -->
    <div class="search-area">
      <div class="search-row">
        <el-input
          v-model="searchForm.keyword"
          placeholder="搜索活动名称"
          clearable
          style="width: 250px"
          @keyup.enter="handleSearch"
        />
        <el-select v-model="searchForm.type" placeholder="活动类型" clearable style="width: 150px">
          <el-option label="限时折扣" value="discount" />
          <el-option label="满减券" value="full_reduction" />
          <el-option label="体验券" value="experience" />
        </el-select>
        <el-select v-model="searchForm.status" placeholder="活动状态" clearable style="width: 150px">
          <el-option label="草稿" value="draft" />
          <el-option label="进行中" value="active" />
          <el-option label="已结束" value="ended" />
          <el-option label="已取消" value="cancelled" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" v-loading="loading" border stripe>
      <el-table-column prop="name" label="活动名称" min-width="200" />
      <el-table-column prop="type" label="活动类型" width="120">
        <template #default="{ row }">
          <el-tag :type="getTypeTagType(row.type)">{{ getTypeText(row.type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="优惠信息" min-width="200">
        <template #default="{ row }">
          {{ getPromotionInfo(row) }}
        </template>
      </el-table-column>
      <el-table-column prop="target_type" label="目标用户" width="120">
        <template #default="{ row }">
          {{ getTargetTypeText(row.target_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="total_quantity" label="发放数量" width="100" />
      <el-table-column prop="used_quantity" label="已使用" width="100" />
      <el-table-column prop="valid_from" label="开始时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.valid_from) }}
        </template>
      </el-table-column>
      <el-table-column prop="valid_to" label="结束时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.valid_to) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusTagType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button type="primary" link @click="viewDetail(row)">详情</el-button>
            <el-button type="primary" link @click="generateCoupons(row)" :disabled="row.status !== 'draft'">
              生成优惠券
            </el-button>
            <el-button type="success" link @click="distribute(row)" :disabled="row.status !== 'active'">
              定向发放
            </el-button>
            <el-button type="primary" link @click="startPromotion(row)" :disabled="row.status !== 'draft'">
              开始
            </el-button>
            <el-button type="warning" link @click="endPromotion(row)" :disabled="row.status !== 'active'">
              结束
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 20px; text-align: right">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>

    <!-- 新增对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新增促销活动"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="活动名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入活动名称" />
        </el-form-item>
        <el-form-item label="活动类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择活动类型" style="width: 100%" @change="handleTypeChange">
            <el-option label="限时折扣" value="discount" />
            <el-option label="满减券" value="full_reduction" />
            <el-option label="体验券" value="experience" />
          </el-select>
        </el-form-item>
        <el-form-item label="活动描述">
          <el-input v-model="form.description" type="textarea" placeholder="请输入活动描述" :rows="3" />
        </el-form-item>
        
        <!-- 限时折扣 -->
        <el-form-item v-if="form.type === 'discount'" label="折扣率" prop="discount_rate">
          <el-slider v-model="form.discount_rate" :min="0.1" :max="1" :step="0.1" :show-tooltip="true">
            <template #tooltip="{ value }">
              {{ (value * 10).toFixed(1) }}折
            </template>
          </el-slider>
          <span style="margin-left: 15px; color: #409eff">
            {{ form.discount_rate ? (form.discount_rate * 10).toFixed(1) + '折' : '' }}
          </span>
        </el-form-item>
        
        <!-- 满减券 -->
        <el-form-item v-if="form.type === 'full_reduction'" label="满减条件">
          <el-col :span="10">
            <el-form-item prop="full_amount">
              <el-input-number v-model="form.full_amount" :min="0" :precision="2" placeholder="满多少" />
            </el-form-item>
          </el-col>
          <el-col :span="4" style="text-align: center">减</el-col>
          <el-col :span="10">
            <el-form-item prop="reduction_amount">
              <el-input-number v-model="form.reduction_amount" :min="0" :precision="2" placeholder="减多少" />
            </el-form-item>
          </el-col>
        </el-form-item>
        
        <!-- 体验券 -->
        <el-form-item v-if="form.type === 'experience'" label="体验券金额" prop="experience_amount">
          <el-input-number v-model="form.experience_amount" :min="0" :precision="2" placeholder="请输入体验券金额" />
        </el-form-item>
        
        <el-form-item label="活动时间" prop="valid_from">
          <el-date-picker
            v-model="dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
            style="width: 100%"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="发放总量" prop="total_quantity">
          <el-input-number v-model="form.total_quantity" :min="1" />
        </el-form-item>
        <el-form-item label="每人限领" prop="per_member_limit">
          <el-input-number v-model="form.per_member_limit" :min="1" />
        </el-form-item>
        <el-form-item label="目标用户" prop="target_type">
          <el-select v-model="form.target_type" placeholder="请选择目标用户" style="width: 100%">
            <el-option label="全部会员" value="all" />
            <el-option label="沉睡会员" value="sleeping" />
            <el-option label="高价值客户" value="high_value" />
            <el-option label="指定会员" value="specific" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh } from '@element-plus/icons-vue'
import { promotionApi } from '../../api'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)

const tableData = ref([])
const dateRange = ref([])

const searchForm = reactive({
  keyword: '',
  type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const form = reactive({
  name: '',
  type: '',
  description: '',
  discount_rate: 0.8,
  full_amount: null,
  reduction_amount: null,
  experience_amount: null,
  valid_from: null,
  valid_to: null,
  total_quantity: 100,
  per_member_limit: 1,
  target_type: 'all',
  status: 'draft'
})

const rules = {
  name: [{ required: true, message: '请输入活动名称', trigger: 'blur' }],
  type: [{ required: true, message: '请选择活动类型', trigger: 'change' }],
  discount_rate: [{ required: true, message: '请设置折扣率', trigger: 'change' }],
  full_amount: [{ required: true, message: '请设置满减条件', trigger: 'blur' }],
  reduction_amount: [{ required: true, message: '请设置减免金额', trigger: 'blur' }],
  experience_amount: [{ required: true, message: '请设置体验券金额', trigger: 'blur' }]
}

// 获取类型显示文本
const getTypeText = (type) => {
  const map = {
    discount: '限时折扣',
    full_reduction: '满减券',
    experience: '体验券'
  }
  return map[type] || type
}

// 获取类型标签类型
const getTypeTagType = (type) => {
  const map = {
    discount: 'primary',
    full_reduction: 'success',
    experience: 'warning'
  }
  return map[type] || ''
}

// 获取优惠信息
const getPromotionInfo = (row) => {
  if (row.type === 'discount') {
    return `${(row.discount_rate * 10).toFixed(1)}折`
  } else if (row.type === 'full_reduction') {
    return `满${row.full_amount}减${row.reduction_amount}`
  } else if (row.type === 'experience') {
    return `体验券${row.experience_amount}元`
  }
  return '-'
}

// 获取目标用户显示文本
const getTargetTypeText = (type) => {
  const map = {
    all: '全部会员',
    sleeping: '沉睡会员',
    high_value: '高价值客户',
    specific: '指定会员'
  }
  return map[type] || type
}

// 获取状态显示文本
const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    active: '进行中',
    ended: '已结束',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const map = {
    draft: 'info',
    active: 'success',
    ended: 'warning',
    cancelled: 'danger'
  }
  return map[status] || ''
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    if (searchForm.type) params.type = searchForm.type
    if (searchForm.status) params.status = searchForm.status

    const data = await promotionApi.getList(params)
    tableData.value = data.items
    pagination.total = data.total
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.keyword = ''
  searchForm.type = ''
  searchForm.status = ''
  pagination.page = 1
  loadData()
}

// 类型变更处理
const handleTypeChange = () => {
  form.discount_rate = 0.8
  form.full_amount = null
  form.reduction_amount = null
  form.experience_amount = null
}

// 打开新增对话框
const openCreateDialog = () => {
  form.name = ''
  form.type = ''
  form.description = ''
  form.discount_rate = 0.8
  form.full_amount = null
  form.reduction_amount = null
  form.experience_amount = null
  form.valid_from = null
  form.valid_to = null
  form.total_quantity = 100
  form.per_member_limit = 1
  form.target_type = 'all'
  form.status = 'draft'
  dateRange.value = []
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (dateRange.value && dateRange.value.length === 2) {
    form.valid_from = dateRange.value[0]
    form.valid_to = dateRange.value[1]
  }

  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    await promotionApi.create(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitLoading.value = false
  }
}

// 生成优惠券
const generateCoupons = async (row) => {
  try {
    await ElMessageBox.confirm('确定要为该活动生成优惠券吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    const result = await promotionApi.generateCoupons(row.id, row.total_quantity)
    ElMessage.success(`成功生成 ${result.created_count} 张优惠券`)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成优惠券失败:', error)
    }
  }
}

// 定向发放
const distribute = async (row) => {
  try {
    await ElMessageBox.confirm('确定要定向发放优惠券吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    const result = await promotionApi.distribute(row.id)
    ElMessage.success(result.message)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发放失败:', error)
    }
  }
}

// 开始活动
const startPromotion = async (row) => {
  try {
    await ElMessageBox.confirm('确定要开始该活动吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await promotionApi.start(row.id)
    ElMessage.success('活动已开始')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('开始活动失败:', error)
    }
  }
}

// 结束活动
const endPromotion = async (row) => {
  try {
    await ElMessageBox.confirm('确定要结束该活动吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await promotionApi.end(row.id)
    ElMessage.success('活动已结束')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('结束活动失败:', error)
    }
  }
}

// 删除
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该活动吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await promotionApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

// 查看详情
const viewDetail = (row) => {
  router.push(`/promotions/${row.id}`)
}

onMounted(() => {
  loadData()
})
</script>
