<template>
  <!-- 商品管理页面 -->
  <div class="product-list">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.keyword"
            placeholder="商品编码/名称"
            clearable
            @keyup.enter="handleSearch"
            style="width: 250px"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearch" />
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.category" placeholder="全部分类" clearable style="width: 120px">
            <el-option label="饮品" value="饮品" />
            <el-option label="食品" value="食品" />
            <el-option label="装备" value="装备" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="上架" value="active" />
            <el-option label="下架" value="inactive" />
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
          新增商品
        </el-button>
        <el-button type="success" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>
    
    <!-- 商品列表表格 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="50" />
        <el-table-column prop="product_code" label="商品编码" width="120" />
        <el-table-column prop="name" label="商品名称" min-width="180" />
        <el-table-column prop="category" label="分类" width="100" />
        <el-table-column prop="price" label="售价" width="100">
          <template #default="{ row }">
            <span class="text-primary">¥{{ row.price?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="cost_price" label="成本价" width="100">
          <template #default="{ row }">
            <span class="text-muted">¥{{ row.cost_price?.toFixed(2) || '0.00' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存" width="100">
          <template #default="{ row }">
            <span :class="{ 'text-danger': row.stock_quantity < 10 }">
              {{ row.stock_quantity }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'" effect="light">
              {{ row.status === 'active' ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button 
              :type="row.status === 'active' ? 'warning' : 'success'" 
              size="small" plain 
              @click="handleToggleStatus(row)"
            >
              <el-icon>{{ row.status === 'active' ? 'Close' : 'Check' }}</el-icon>
              {{ row.status === 'active' ? '下架' : '上架' }}
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
    
    <!-- 新增/编辑商品弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="productFormRef"
        :model="productForm"
        :rules="productRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="商品编码" prop="product_code">
              <el-input v-model="productForm.product_code" placeholder="请输入商品编码" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="商品名称" prop="name">
              <el-input v-model="productForm.name" placeholder="请输入商品名称" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="分类" prop="category">
              <el-select v-model="productForm.category" placeholder="请选择分类" style="width: 100%">
                <el-option label="饮品" value="饮品" />
                <el-option label="食品" value="食品" />
                <el-option label="装备" value="装备" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="单位">
              <el-input v-model="productForm.unit" placeholder="请输入单位（如：瓶、份、件）" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="售价" prop="price">
              <el-input-number v-model="productForm.price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="成本价">
              <el-input-number v-model="productForm.cost_price" :min="0" :precision="2" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="库存" prop="stock_quantity">
              <el-input-number v-model="productForm.stock_quantity" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="productForm.status" placeholder="请选择状态" style="width: 100%">
                <el-option label="上架" value="active" />
                <el-option label="下架" value="inactive" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="商品描述">
          <el-input
            v-model="productForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入商品描述"
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
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import api from '@/api'

// 表格数据
const tableData = ref([])
const loading = ref(false)
const selectedRows = ref([])

// 搜索表单
const searchForm = reactive({
  keyword: '',
  category: '',
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
const dialogTitle = ref('新增商品')
const isEdit = ref(false)
const submitLoading = ref(false)
const productFormRef = ref<FormInstance>()

// 商品表单
const productForm = reactive({
  product_code: '',
  name: '',
  category: '饮品',
  price: 0,
  cost_price: 0,
  stock_quantity: 0,
  unit: '件',
  status: 'active',
  description: ''
})

// 表单验证规则
const productRules: FormRules = {
  product_code: [{ required: true, message: '请输入商品编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入售价', trigger: 'blur' }],
  stock_quantity: [{ required: true, message: '请输入库存', trigger: 'blur' }]
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getProducts({
      page: pagination.page,
      page_size: pagination.pageSize,
      keyword: searchForm.keyword || undefined,
      category: searchForm.category || undefined,
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
  searchForm.category = ''
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

// 新增商品
const handleAdd = () => {
  dialogTitle.value = '新增商品'
  isEdit.value = false
  // 重置表单
  Object.assign(productForm, {
    product_code: '',
    name: '',
    category: '饮品',
    price: 0,
    cost_price: 0,
    stock_quantity: 0,
    unit: '件',
    status: 'active',
    description: ''
  })
  dialogVisible.value = true
}

// 编辑商品
const handleEdit = (row) => {
  dialogTitle.value = '编辑商品'
  isEdit.value = true
  
  // 填充表单
  Object.assign(productForm, {
    ...row,
    price: row.price || 0,
    cost_price: row.cost_price || 0,
    stock_quantity: row.stock_quantity || 0
  })
  
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!productFormRef.value) return
  
  await productFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await api.updateProduct(selectedRows.value[0]?.id || productForm.id, productForm)
          ElMessage.success('更新成功')
        } else {
          await api.createProduct(productForm)
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

// 切换上下架状态
const handleToggleStatus = async (row) => {
  const action = row.status === 'active' ? '下架' : '上架'
  
  ElMessageBox.confirm(
    `确定要${action}商品「${row.name}」吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.updateProduct(row.id, {
        status: row.status === 'active' ? 'inactive' : 'active'
      })
      ElMessage.success(`${action}成功`)
      loadData()
    } catch (error) {
      console.error('操作失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.product-list {
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

.text-muted {
  color: #909399;
}

.text-danger {
  color: #F56C6C;
  font-weight: bold;
}
</style>
