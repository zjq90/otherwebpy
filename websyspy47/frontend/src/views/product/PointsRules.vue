<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">积分规则</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增规则
      </el-button>
    </div>
    
    <el-alert
      title="积分规则说明"
      type="info"
      :closable="false"
      class="mb-20"
    >
      <template #default>
        <ul>
          <li><strong>基础积分</strong>：用户回收衣物时获得的基础积分奖励</li>
          <li><strong>额外奖励</strong>：满足特定条件时额外赠送的积分</li>
          <li><strong>计价方式</strong>：支持按件计价和按斤计价两种积分模式</li>
        </ul>
      </template>
    </el-alert>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="规则名称">
          <el-input v-model="searchForm.name" placeholder="请输入规则名称" clearable />
        </el-form-item>
        <el-form-item label="衣物分类">
          <el-select v-model="searchForm.category_id" placeholder="全部" clearable style="width: 150px">
            <el-option
              v-for="item in categoryList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="启用" :value="1" />
            <el-option label="禁用" :value="0" />
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
    </el-card>
    
    <el-card class="table-container">
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="name" label="规则名称" />
        <el-table-column prop="category_name" label="适用分类">
          <template #default="{ row }">
            {{ row.category_name || '全部分类' }}
          </template>
        </el-table-column>
        <el-table-column prop="pricing_type" label="计价方式" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="row.pricing_type === 0 ? 'primary' : 'success'">
              {{ pricingTypeMap[row.pricing_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="base_points" label="基础积分" align="center" width="100">
          <template #default="{ row }">
            <span style="color: #e6a23c; font-weight: 600;">{{ row.base_points || 0 }}</span>
            <span style="color: #909399;">积分</span>
          </template>
        </el-table-column>
        <el-table-column prop="extra_points" label="额外奖励" align="center" width="100">
          <template #default="{ row }">
            <span v-if="row.extra_points">
              <el-tag type="success">+{{ row.extra_points }}积分</el-tag>
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="extra_condition" label="奖励条件" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.extra_condition || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="valid_days" label="有效天数" align="center" width="100">
          <template #default="{ row }">
            {{ row.valid_days ? row.valid_days + '天' : '永久有效' }}
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" align="center" width="70" />
        <el-table-column prop="status" label="状态" align="center" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
              :disabled="row.status === 0"
            >
              禁用
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
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="规则名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入规则名称" />
        </el-form-item>
        <el-form-item label="适用分类">
          <el-select 
            v-model="form.category_id" 
            placeholder="选择适用分类（不选则适用全部）" 
            style="width: 100%"
            clearable
          >
            <el-option
              v-for="item in categoryList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="计价方式" prop="pricing_type">
          <el-radio-group v-model="form.pricing_type">
            <el-radio :value="0">按件计价</el-radio>
            <el-radio :value="1">按斤计价</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="基础积分" prop="base_points">
              <el-input-number 
                v-model="form.base_points" 
                :min="0" 
                :step="1"
                style="width: 100%"
              />
              <span class="form-tip">积分/件 或 积分/千克</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="额外奖励">
              <el-input-number 
                v-model="form.extra_points" 
                :min="0" 
                :step="1"
                style="width: 100%"
              />
              <span class="form-tip">额外赠送积分</span>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="奖励条件">
          <el-input 
            v-model="form.extra_condition" 
            placeholder="请输入额外奖励的条件，如：满5件额外奖励"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="有效天数">
              <el-input-number 
                v-model="form.valid_days" 
                :min="0" 
                :step="1"
                style="width: 100%"
              />
              <span class="form-tip">0表示永久有效</span>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" :max="999" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { 
  getPointsRuleList, 
  createPointsRule, 
  updatePointsRule, 
  getCategoryList
} from '@/api'

const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tableData = ref([])
const categoryList = ref([])

const searchForm = reactive({
  name: '',
  category_id: null,
  status: null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const form = reactive({
  name: '',
  category_id: null,
  pricing_type: 0,
  base_points: 0,
  extra_points: 0,
  extra_condition: '',
  valid_days: 0,
  sort_order: 0,
  status: 1,
  remark: ''
})

const rules = {
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' }
  ],
  pricing_type: [
    { required: true, message: '请选择计价方式', trigger: 'change' }
  ],
  base_points: [
    { required: true, message: '请输入基础积分', trigger: 'blur' }
  ]
}

const pricingTypeMap = {
  0: '按件计价',
  1: '按斤计价'
}

const statusMap = {
  0: '禁用',
  1: '启用'
}

const dialogTitle = ref('新增积分规则')

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const fetchCategories = async () => {
  try {
    const res = await getCategoryList(0, 1)
    categoryList.value = res.data || []
  } catch (error) {
    console.error('获取分类列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    const res = await getPointsRuleList(params)
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
  searchForm.name = ''
  searchForm.category_id = null
  searchForm.status = null
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增积分规则'
  form.name = ''
  form.category_id = null
  form.pricing_type = 0
  form.base_points = 0
  form.extra_points = 0
  form.extra_condition = ''
  form.valid_days = 0
  form.sort_order = 0
  form.status = 1
  form.remark = ''
  delete form.id
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑积分规则'
  form.id = row.id
  form.name = row.name
  form.category_id = row.category_id || null
  form.pricing_type = row.pricing_type
  form.base_points = row.base_points || 0
  form.extra_points = row.extra_points || 0
  form.extra_condition = row.extra_condition || ''
  form.valid_days = row.valid_days || 0
  form.sort_order = row.sort_order || 0
  form.status = row.status
  form.remark = row.remark || ''
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要禁用积分规则 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updatePointsRule(row.id, { status: 0 })
    ElMessage.success('禁用成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('禁用失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = { ...form }
        
        if (isEdit.value) {
          await updatePointsRule(form.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createPointsRule(submitData)
          ElMessage.success('创建成功')
        }
        
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('提交失败:', error)
      }
    }
  })
}

onMounted(() => {
  fetchCategories()
  fetchData()
})
</script>

<style lang="scss" scoped>
.search-form {
  .el-form-item {
    margin-right: 0;
  }
}

.mb-20 {
  margin-bottom: 20px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}
</style>
