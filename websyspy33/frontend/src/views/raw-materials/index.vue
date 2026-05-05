<template>
  <div class="raw-materials-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>原材料管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增原材料
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="关键词">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入原材料名称/编码"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="材料类型">
          <el-select v-model="searchForm.material_type" placeholder="请选择" clearable>
            <el-option label="水泥" value="水泥" />
            <el-option label="骨料" value="骨料" />
            <el-option label="外加剂" value="外加剂" />
            <el-option label="粉煤灰" value="粉煤灰" />
            <el-option label="矿渣粉" value="矿渣粉" />
            <el-option label="硅灰" value="硅灰" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
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
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe>
        <el-table-column prop="code" label="材料编码" width="130" />
        <el-table-column prop="name" label="材料名称" width="120" />
        <el-table-column prop="material_type" label="材料类型" width="100">
          <template #default="scope">
            <el-tag :type="getMaterialTypeTagType(scope.row.material_type)">
              {{ scope.row.material_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="specification" label="规格型号" width="150" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="supplier_name" label="供应商" min-width="150" show-overflow-tooltip />
        <el-table-column prop="description" label="描述" min-width="150" show-overflow-tooltip />
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
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料编码" prop="code">
              <el-input v-model="formData.code" placeholder="请输入材料编码" :disabled="isView" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="材料名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入材料名称" :disabled="isView" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="材料类型" prop="material_type">
              <el-select v-model="formData.material_type" placeholder="请选择" style="width: 100%" :disabled="isView">
                <el-option label="水泥" value="水泥" />
                <el-option label="骨料" value="骨料" />
                <el-option label="外加剂" value="外加剂" />
                <el-option label="粉煤灰" value="粉煤灰" />
                <el-option label="矿渣粉" value="矿渣粉" />
                <el-option label="硅灰" value="硅灰" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="规格型号" prop="specification">
              <el-input v-model="formData.specification" placeholder="请输入规格型号" :disabled="isView" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计量单位" prop="unit">
              <el-select v-model="formData.unit" placeholder="请选择" style="width: 100%" :disabled="isView">
                <el-option label="吨" value="吨" />
                <el-option label="kg" value="kg" />
                <el-option label="m³" value="m³" />
                <el-option label="袋" value="袋" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="供应商">
              <el-select v-model="formData.supplier_id" placeholder="请选择供应商" style="width: 100%" :disabled="isView">
                <el-option v-for="supplier in suppliers" :key="supplier.id" :label="supplier.name" :value="supplier.id" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="2"
            placeholder="请输入描述"
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

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const isView = ref(false)
const formRef = ref(null)
const suppliers = ref([])

const searchForm = reactive({
  keyword: '',
  material_type: '',
  status: null
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
  material_type: '水泥',
  specification: '',
  unit: '吨',
  supplier_id: null,
  description: '',
  status: true
})

const rules = {
  code: [{ required: true, message: '请输入材料编码', trigger: 'blur' }],
  name: [{ required: true, message: '请输入材料名称', trigger: 'blur' }],
  material_type: [{ required: true, message: '请选择材料类型', trigger: 'change' }],
  specification: [{ required: true, message: '请输入规格型号', trigger: 'blur' }],
  unit: [{ required: true, message: '请选择计量单位', trigger: 'change' }]
}

const dialogTitle = computed(() => {
  if (isView.value) return '查看原材料'
  return formData.id ? '编辑原材料' : '新增原材料'
})

const getMaterialTypeTagType = (type) => {
  const typeMap = {
    '水泥': 'primary',
    '骨料': 'success',
    '外加剂': 'warning',
    '粉煤灰': 'info',
    '矿渣粉': 'danger',
    '硅灰': ''
  }
  return typeMap[type] || ''
}

const fetchData = async () => {
  loading.value = true
  try {
    tableData.value = [
      {
        id: 1,
        code: 'MAT001',
        name: 'P.O 42.5水泥',
        material_type: '水泥',
        specification: 'P.O 42.5',
        unit: '吨',
        supplier_id: 1,
        supplier_name: '山水水泥有限公司',
        description: '普通硅酸盐水泥，强度等级42.5',
        status: true
      },
      {
        id: 2,
        code: 'MAT002',
        name: '碎石骨料',
        material_type: '骨料',
        specification: '5-20mm',
        unit: 'm³',
        supplier_id: 2,
        supplier_name: '海螺水泥集团',
        description: '优质碎石骨料，连续级配',
        status: true
      },
      {
        id: 3,
        code: 'MAT003',
        name: '聚羧酸减水剂',
        material_type: '外加剂',
        specification: 'PC-1000',
        unit: 'kg',
        supplier_id: 3,
        supplier_name: '华新水泥股份',
        description: '高效聚羧酸系减水剂',
        status: true
      }
    ]
    pagination.total = 3
    
    suppliers.value = [
      { id: 1, name: '山水水泥有限公司' },
      { id: 2, name: '海螺水泥集团' },
      { id: 3, name: '华新水泥股份' }
    ]
  } catch (error) {
    console.error('获取原材料数据失败:', error)
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
  searchForm.material_type = ''
  searchForm.status = null
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
  formData.material_type = '水泥'
  formData.specification = ''
  formData.unit = '吨'
  formData.supplier_id = null
  formData.description = ''
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
    `确定要删除原材料"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    ElMessage.success('删除成功')
    fetchData()
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      ElMessage.success('保存成功')
      dialogVisible.value = false
      fetchData()
    }
  })
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.raw-materials-container {
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
</style>
