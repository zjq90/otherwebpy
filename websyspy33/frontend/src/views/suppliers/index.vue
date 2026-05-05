<template>
  <div class="suppliers-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>供应商管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增供应商
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入供应商名称/联系人"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="供应商类型">
          <el-select v-model="searchForm.supplier_type" placeholder="请选择" clearable>
            <el-option label="原材料供应商" value="原材料供应商" />
            <el-option label="设备供应商" value="设备供应商" />
            <el-option label="服务商" value="服务商" />
          </el-select>
        </el-form-item>
        <el-form-item label="评级等级">
          <el-select v-model="searchForm.rating_level" placeholder="请选择" clearable>
            <el-option label="A级" value="A级" />
            <el-option label="B级" value="B级" />
            <el-option label="C级" value="C级" />
            <el-option label="D级" value="D级" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="code" label="供应商编码" width="150" />
        <el-table-column prop="name" label="供应商名称" min-width="200" />
        <el-table-column prop="supplier_type" label="供应商类型" width="120" />
        <el-table-column prop="contact_person" label="联系人" width="100" />
        <el-table-column prop="phone" label="联系电话" width="130" />
        <el-table-column prop="address" label="地址" min-width="200" show-overflow-tooltip />
        <el-table-column prop="rating" label="评分" width="80">
          <template #default="scope">
            <span :class="getRatingClass(scope.row.rating)">
              {{ scope.row.rating }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="rating_level" label="等级" width="80">
          <template #default="scope">
            <el-tag :type="getRatingTagType(scope.row.rating_level)">
              {{ scope.row.rating_level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status ? 'success' : 'danger'">
              {{ scope.row.status ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="primary" link @click="handleView(scope.row)">
              查看
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="100px"
      >
        <el-form-item label="供应商编码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入供应商编码" :disabled="isView" />
        </el-form-item>
        <el-form-item label="供应商名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入供应商名称" :disabled="isView" />
        </el-form-item>
        <el-form-item label="供应商类型" prop="supplier_type">
          <el-select v-model="formData.supplier_type" placeholder="请选择" style="width: 100%" :disabled="isView">
            <el-option label="原材料供应商" value="原材料供应商" />
            <el-option label="设备供应商" value="设备供应商" />
            <el-option label="服务商" value="服务商" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系人" prop="contact_person">
          <el-input v-model="formData.contact_person" placeholder="请输入联系人" :disabled="isView" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="formData.phone" placeholder="请输入联系电话" :disabled="isView" />
        </el-form-item>
        <el-form-item label="地址" prop="address">
          <el-input
            v-model="formData.address"
            type="textarea"
            :rows="2"
            placeholder="请输入地址"
            :disabled="isView"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="formData.status" :disabled="isView">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <span v-if="!isView">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
        <span v-else>
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getSuppliers, createSupplier, updateSupplier, deleteSupplier } from '@/api/suppliers'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isView = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  keyword: '',
  supplier_type: '',
  rating_level: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const formData = reactive({
  id: null,
  code: '',
  name: '',
  supplier_type: '原材料供应商',
  contact_person: '',
  phone: '',
  address: '',
  status: true
})

const rules = {
  code: [{ required: true, message: '请输入供应商编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入供应商名称', trigger: 'blur' }],
  supplier_type: [{ required: true, message: '请选择供应商类型', trigger: 'change' }],
  contact_person: [{ required: true, message: '请输入联系人', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看供应商'
  return formData.id ? '编辑供应商' : '新增供应商'
})

const getRatingClass = (rating) => {
  if (rating >= 90) return 'text-green-600 font-bold'
  if (rating >= 75) return 'text-orange-600 font-bold'
  if (rating >= 60) return 'text-red-600 font-bold'
  return 'text-gray-600 font-bold'
}

const getRatingTagType = (level) => {
  const typeMap = {
    'A级': 'success',
    'B级': 'warning',
    'C级': 'danger',
    'D级': 'info'
  }
  return typeMap[level] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.pageSize,
      ...searchForm
    }
    const res = await getSuppliers(params)
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('获取供应商数据失败:', error)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.keyword = ''
  searchForm.supplier_type = ''
  searchForm.rating_level = ''
  handleSearch()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchData()
}

const resetForm = () => {
  formData.id = null
  formData.code = ''
  formData.name = ''
  formData.supplier_type = '原材料供应商'
  formData.contact_person = ''
  formData.phone = ''
  formData.address = ''
  formData.status = true
  formRef.value?.resetFields()
}

const handleAdd = () => {
  isView.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isView.value = false
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleView = (row) => {
  isView.value = true
  resetForm()
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除供应商"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteSupplier(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        if (formData.id) {
          await updateSupplier(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await createSupplier(formData)
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
  fetchData()
})
</script>

<style scoped>
.suppliers-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.text-green-600 {
  color: #67c23a;
}

.text-orange-600 {
  color: #e6a23c;
}

.text-red-600 {
  color: #f56c6c;
}

.text-gray-600 {
  color: #909399;
}

.font-bold {
  font-weight: bold;
}
</style>
