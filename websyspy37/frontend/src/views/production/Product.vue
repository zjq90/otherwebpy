<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">产品管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增产品
          </el-button>
        </div>
      </template>

      <!-- 搜索表单 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="产品编号">
          <el-input v-model="searchForm.product_no" placeholder="请输入产品编号" clearable />
        </el-form-item>
        <el-form-item label="产品名称">
          <el-input v-model="searchForm.name" placeholder="请输入产品名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="product_no" label="产品编号" width="120" />
        <el-table-column prop="name" label="产品名称" min-width="180" />
        <el-table-column prop="specification" label="规格型号" width="200" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="cost_price" label="成本价" width="120">
          <template #default="scope">
            ¥{{ scope.row.cost_price?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="selling_price" label="销售价" width="120">
          <template #default="scope">
            ¥{{ scope.row.selling_price?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link size="small" @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link size="small" @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
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
          layout="total, sizes, prev, pager, next, jumper"
          :total="pagination.total"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="产品编号" prop="product_no">
          <el-input v-model="form.product_no" placeholder="请输入产品编号" />
        </el-form-item>
        <el-form-item label="产品名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入产品名称" />
        </el-form-item>
        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="form.specification" placeholder="请输入规格型号" />
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-select v-model="form.unit" placeholder="请选择单位" style="width: 100%;">
            <el-option label="个" value="个" />
            <el-option label="台" value="台" />
            <el-option label="件" value="件" />
            <el-option label="套" value="套" />
            <el-option label="箱" value="箱" />
          </el-select>
        </el-form-item>
        <el-form-item label="成本价" prop="cost_price">
          <el-input-number v-model="form.cost_price" :precision="2" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="销售价" prop="selling_price">
          <el-input-number v-model="form.selling_price" :precision="2" :min="0" style="width: 100%;" />
        </el-form-item>
        <el-form-item label="产品描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入产品描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import validations from '@/utils/validations'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tableData = ref([])
const searchForm = reactive({
  product_no: '',
  name: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: null,
  product_no: '',
  name: '',
  specification: '',
  unit: '个',
  cost_price: 0,
  selling_price: 0,
  description: ''
})

const rules = {
  product_no: [
    { required: true, message: '请输入产品编号', trigger: 'blur' },
    validations.stringLengthRule(1, 50, '产品编号长度不能超过50个字符')
  ],
  name: validations.productNameRules,
  specification: [
    validations.stringLengthRule(0, 200, '规格型号长度不能超过200个字符')
  ],
  unit: [
    validations.stringLengthRule(0, 20, '单位长度不能超过20个字符')
  ],
  cost_price: validations.amountOptionalRules,
  selling_price: validations.amountOptionalRules,
  description: validations.descriptionRules
}

const dialogTitle = ref('新增产品')

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    
    const result = await api.getProducts(params)
    tableData.value = Array.isArray(result) ? result : []
    pagination.total = tableData.value.length
  } catch (error) {
    console.error('加载数据失败:', error)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  searchForm.product_no = ''
  searchForm.name = ''
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增产品'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑产品'
  resetForm()
  Object.assign(form, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除产品"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.deleteProduct(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const resetForm = () => {
  form.id = null
  form.product_no = ''
  form.name = ''
  form.specification = ''
  form.unit = '个'
  form.cost_price = 0
  form.selling_price = 0
  form.description = ''
  if (formRef.value) {
    formRef.value.resetFields()
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.updateProduct(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await api.createProduct(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(() => {
  loadData()
})
</script>
