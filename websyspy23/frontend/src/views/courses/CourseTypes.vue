<template>
  <div class="course-types-page">
    <div class="page-header">
      <h2 class="page-title">课程类型管理</h2>
      <p class="page-desc">管理系统支持的课程类型，如团操课、私教课、定制课程等</p>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="课程类型名称" width="150" />
        <el-table-column prop="code" label="类型代码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="类型名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入课程类型名称" />
        </el-form-item>
        <el-form-item label="类型代码" prop="code">
          <el-input v-model="formData.code" placeholder="请输入类型代码" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">禁用</el-radio>
          </el-radio-group>
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
import { courseTypeApi } from '@/api'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新增课程类型')
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  is_active: null
})

const formData = reactive({
  name: '',
  code: '',
  description: '',
  is_active: true
})

const formRules = {
  name: [
    { required: true, message: '请输入课程类型名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入类型代码', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.is_active !== null) {
      params.is_active = searchForm.is_active
    }
    const data = await courseTypeApi.getList(params)
    tableData.value = data
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  searchForm.is_active = null
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增课程类型'
  formData.name = ''
  formData.code = ''
  formData.description = ''
  formData.is_active = true
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑课程类型'
  formData.name = row.name
  formData.code = row.code
  formData.description = row.description
  formData.is_active = row.is_active
  formData.id = row.id
  dialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await courseTypeApi.update(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await courseTypeApi.create(formData)
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

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除课程类型"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await courseTypeApi.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.course-types-page {
  height: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
