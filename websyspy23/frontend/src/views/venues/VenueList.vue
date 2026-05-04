<template>
  <div class="venue-list-page">
    <div class="page-header">
      <h2 class="page-title">场地管理</h2>
      <p class="page-desc">管理健身场地信息，如瑜伽室、动感单车室等</p>
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
            新增场地
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="场地名称" width="180" />
        <el-table-column prop="code" label="场地代码" width="120" />
        <el-table-column prop="capacity" label="容纳人数" width="100" />
        <el-table-column prop="location" label="位置" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link @click="handleView(scope.row)">
              详情
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
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="场地名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入场地名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场地代码" prop="code">
              <el-input v-model="formData.code" placeholder="请输入场地代码" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="容纳人数" prop="capacity">
              <el-input-number
                v-model="formData.capacity"
                :min="1"
                style="width: 100%"
                placeholder="请输入容纳人数"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="位置">
              <el-input v-model="formData.location" placeholder="请输入位置" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="设施配置">
          <el-input
            v-model="formData.facilities"
            type="textarea"
            :rows="2"
            placeholder="请输入设施配置"
          />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入场地描述"
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

    <el-dialog
      v-model="detailDialogVisible"
      title="场地详情"
      width="500px"
    >
      <el-descriptions :column="1" border v-if="currentVenue">
        <el-descriptions-item label="场地名称">
          {{ currentVenue.name }}
        </el-descriptions-item>
        <el-descriptions-item label="场地代码">
          {{ currentVenue.code }}
        </el-descriptions-item>
        <el-descriptions-item label="容纳人数">
          {{ currentVenue.capacity }}人
        </el-descriptions-item>
        <el-descriptions-item label="位置">
          {{ currentVenue.location || '未指定' }}
        </el-descriptions-item>
        <el-descriptions-item label="设施配置" v-if="currentVenue.facilities">
          {{ currentVenue.facilities }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" v-if="currentVenue.description">
          {{ currentVenue.description }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentVenue.is_active ? 'success' : 'danger'">
            {{ currentVenue.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { venueApi } from '@/api'

const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('新增场地')
const isEdit = ref(false)
const formRef = ref(null)
const currentVenue = ref(null)

const searchForm = reactive({
  is_active: null
})

const formData = reactive({
  name: '',
  code: '',
  capacity: 20,
  location: '',
  facilities: '',
  description: '',
  is_active: true
})

const formRules = {
  name: [
    { required: true, message: '请输入场地名称', trigger: 'blur' }
  ],
  code: [
    { required: true, message: '请输入场地代码', trigger: 'blur' }
  ],
  capacity: [
    { required: true, message: '请输入容纳人数', trigger: 'blur' }
  ]
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.is_active !== null) {
      params.is_active = searchForm.is_active
    }
    const data = await venueApi.getList(params)
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

const resetForm = () => {
  formData.name = ''
  formData.code = ''
  formData.capacity = 20
  formData.location = ''
  formData.facilities = ''
  formData.description = ''
  formData.is_active = true
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增场地'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑场地'
  formData.id = row.id
  formData.name = row.name
  formData.code = row.code
  formData.capacity = row.capacity
  formData.location = row.location || ''
  formData.facilities = row.facilities || ''
  formData.description = row.description || ''
  formData.is_active = row.is_active
  dialogVisible.value = true
}

const handleView = (row) => {
  currentVenue.value = row
  detailDialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await venueApi.update(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await venueApi.create(formData)
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
    `确定要删除场地"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await venueApi.delete(row.id)
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
.venue-list-page {
  height: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
