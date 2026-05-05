<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">分类管理</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增分类
      </el-button>
    </div>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="分类名称">
          <el-input v-model="searchForm.name" placeholder="请输入分类名称" clearable />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-select v-model="searchForm.parent_id" placeholder="全部" clearable style="width: 150px">
            <el-option label="顶级分类" :value="0" />
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
      <el-table :data="tableData" v-loading="loading" row-key="id" style="width: 100%" :tree-props="{ children: 'children' }">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="name" label="分类名称" />
        <el-table-column prop="code" label="分类编码" />
        <el-table-column prop="parent_name" label="上级分类">
          <template #default="{ row }">
            {{ row.parent_name || '顶级分类' }}
          </template>
        </el-table-column>
        <el-table-column prop="level" label="层级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)">
              {{ row.level === 1 ? '一级' : row.level === 2 ? '二级' : '三级' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sort_order" label="排序" width="80" align="center" />
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
        <el-table-column label="操作" width="200" fixed="right" align="center">
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
            <el-button 
              type="success" 
              link 
              size="small" 
              @click="handleAddSub(row)"
              v-if="row.level < 3"
            >
              子分类
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码">
          <el-input v-model="form.code" placeholder="请输入分类编码" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-tree-select
            v-model="form.parent_id"
            :data="treeData"
            :props="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="请选择上级分类"
            :default-expand-all="true"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="请输入图标名称或URL" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入分类描述" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">启用</el-radio>
            <el-radio :value="0">禁用</el-radio>
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
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { getCategoryList, createCategory, updateCategory, deleteCategory } from '@/api'

const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tableData = ref([])
const categoryList = ref([])

const searchForm = reactive({
  name: '',
  parent_id: null,
  status: null
})

const form = reactive({
  name: '',
  code: '',
  parent_id: 0,
  sort_order: 0,
  icon: '',
  description: '',
  status: 1
})

const rules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' }
  ]
}

const statusMap = {
  0: '禁用',
  1: '启用'
}

const dialogTitle = ref('新增分类')

const treeData = computed(() => {
  const data = [{ id: 0, name: '顶级分类' }]
  return data.concat(categoryList.value || [])
})

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const getLevelType = (level) => {
  switch (level) {
    case 1: return 'primary'
    case 2: return 'success'
    case 3: return 'warning'
    default: return 'info'
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      parent_id: searchForm.parent_id === null ? 0 : searchForm.parent_id,
      status: searchForm.status
    }
    
    const res = await getCategoryList(params.parent_id, params.status)
    let data = res.data || []
    
    if (searchForm.name) {
      data = data.filter(item => item.name.includes(searchForm.name))
    }
    
    tableData.value = data
    categoryList.value = data
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
  searchForm.name = ''
  searchForm.parent_id = null
  searchForm.status = null
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增分类'
  form.name = ''
  form.code = ''
  form.parent_id = 0
  form.sort_order = 0
  form.icon = ''
  form.description = ''
  form.status = 1
  delete form.id
  dialogVisible.value = true
}

const handleAddSub = (row) => {
  isEdit.value = false
  dialogTitle.value = '新增子分类'
  form.name = ''
  form.code = ''
  form.parent_id = row.id
  form.sort_order = 0
  form.icon = ''
  form.description = ''
  form.status = 1
  delete form.id
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑分类'
  form.id = row.id
  form.name = row.name
  form.code = row.code || ''
  form.parent_id = row.parent_id || 0
  form.sort_order = row.sort_order || 0
  form.icon = row.icon || ''
  form.description = row.description || ''
  form.status = row.status
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要禁用分类 "${row.name}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteCategory(row.id)
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
          await updateCategory(form.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createCategory(submitData)
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

<style lang="scss" scoped>
.search-form {
  .el-form-item {
    margin-right: 0;
  }
}
</style>
