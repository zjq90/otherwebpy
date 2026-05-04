<template>
  <div class="property-projects">
    <!-- 搜索栏 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目名称">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入项目名称"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Plus" @click="handleAdd">新增项目</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="项目名称" min-width="180" />
        <el-table-column prop="location" label="地理位置" min-width="200" />
        <el-table-column prop="total_buildings" label="楼栋数" width="100" />
        <el-table-column prop="total_houses" label="房屋总数" width="100" />
        <el-table-column prop="developer" label="开发商" min-width="150" />
        <el-table-column prop="built_year" label="建成年份" width="100" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <div class="table-actions">
              <el-button type="primary" link :icon="View" @click="handleView(scope.row)">
                查看
              </el-button>
              <el-button type="primary" link :icon="Edit" @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" link :icon="Delete" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑物业项目' : '新增物业项目'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="项目名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="地理位置" prop="location">
          <el-input v-model="formData.location" placeholder="请输入地理位置" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="楼栋总数" prop="total_buildings">
              <el-input-number
                v-model="formData.total_buildings"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="房屋总数" prop="total_houses">
              <el-input-number
                v-model="formData.total_houses"
                :min="0"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开发商" prop="developer">
              <el-input v-model="formData.developer" placeholder="请输入开发商" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="物业公司" prop="property_company">
              <el-input v-model="formData.property_company" placeholder="请输入物业公司" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="建成年份" prop="built_year">
              <el-input-number
                v-model="formData.built_year"
                :min="1900"
                :max="2100"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="项目描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="物业项目详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ currentRow.id }}</el-descriptions-item>
        <el-descriptions-item label="项目名称">{{ currentRow.name }}</el-descriptions-item>
        <el-descriptions-item label="地理位置" :span="2">
          {{ currentRow.location }}
        </el-descriptions-item>
        <el-descriptions-item label="楼栋总数">{{ currentRow.total_buildings }}</el-descriptions-item>
        <el-descriptions-item label="房屋总数">{{ currentRow.total_houses }}</el-descriptions-item>
        <el-descriptions-item label="开发商">{{ currentRow.developer || '-' }}</el-descriptions-item>
        <el-descriptions-item label="物业公司">{{ currentRow.property_company || '-' }}</el-descriptions-item>
        <el-descriptions-item label="建成年份">{{ currentRow.built_year || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(currentRow.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="项目描述" :span="2">
          {{ currentRow.description || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { propertyProjectApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const currentRow = ref({})
const formRef = ref(null)

const searchForm = reactive({
  name: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const defaultFormData = {
  name: '',
  location: '',
  total_buildings: 0,
  total_houses: 0,
  developer: '',
  property_company: '',
  built_year: null,
  description: ''
}

const formData = reactive({ ...defaultFormData })

const validateName = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请输入项目名称'))
  } else if (value.trim().length < 2) {
    callback(new Error('项目名称至少需要2个字符'))
  } else if (value.trim().length > 100) {
    callback(new Error('项目名称不能超过100个字符'))
  } else {
    callback()
  }
}

const validateLocation = (rule, value, callback) => {
  if (value && value.length > 200) {
    callback(new Error('地理位置不能超过200个字符'))
  } else {
    callback()
  }
}

const validateDescription = (rule, value, callback) => {
  if (value && value.length > 1000) {
    callback(new Error('项目描述不能超过1000个字符'))
  } else {
    callback()
  }
}

const validateDeveloper = (rule, value, callback) => {
  if (value && value.length > 100) {
    callback(new Error('开发商名称不能超过100个字符'))
  } else {
    callback()
  }
}

const formRules = {
  name: [
    { required: true, validator: validateName, trigger: 'blur' }
  ],
  location: [
    { validator: validateLocation, trigger: 'blur' }
  ],
  total_buildings: [
    { type: 'number', min: 0, max: 1000, message: '楼栋总数必须在0-1000之间', trigger: 'blur' }
  ],
  total_houses: [
    { type: 'number', min: 0, max: 100000, message: '房屋总数必须在0-100000之间', trigger: 'blur' }
  ],
  developer: [
    { validator: validateDeveloper, trigger: 'blur' }
  ],
  property_company: [
    { validator: validateDeveloper, trigger: 'blur' }
  ],
  built_year: [
    { type: 'number', min: 1900, max: 2100, message: '建成年份必须在1900-2100之间', trigger: 'blur' }
  ],
  description: [
    { validator: validateDescription, trigger: 'blur' }
  ]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    if (searchForm.name) {
      params.name = searchForm.name
    }
    const res = await propertyProjectApi.getList(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.name = ''
  pagination.page = 1
  loadData()
}

const resetForm = () => {
  Object.assign(formData, defaultFormData)
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleView = (row) => {
  currentRow.value = row
  detailVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentRow.value = row
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除项目"${row.name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await propertyProjectApi.delete(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await propertyProjectApi.update(currentRow.value.id, formData)
          ElMessage.success('更新成功')
        } else {
          await propertyProjectApi.create(formData)
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

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.property-projects {
  width: 100%;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 5px;
}
</style>
