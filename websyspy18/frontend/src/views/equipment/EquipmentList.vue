/**
 * 设备台账页面
 * 设备列表管理，支持增删改查
 */
<template>
  <div class="page-container">
    <!-- 搜索栏 -->
    <el-form :inline="true" class="search-bar">
      <el-form-item label="设备类别">
        <el-select v-model="searchForm.category" placeholder="请选择" clearable style="width: 150px">
          <el-option label="电梯" value="电梯" />
          <el-option label="水泵" value="水泵" />
          <el-option label="空调" value="空调" />
          <el-option label="发电机" value="发电机" />
        </el-select>
      </el-form-item>
      <el-form-item label="设备状态">
        <el-select v-model="searchForm.status" placeholder="请选择" clearable style="width: 150px">
          <el-option label="正常" value="正常" />
          <el-option label="故障" value="故障" />
          <el-option label="维修中" value="维修中" />
          <el-option label="报废" value="报废" />
        </el-select>
      </el-form-item>
      <el-form-item label="关键词">
        <el-input v-model="searchForm.keyword" placeholder="设备名称/编号" clearable style="width: 200px" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>查询
        </el-button>
        <el-button @click="handleReset">
          <el-icon><Refresh /></el-icon>重置
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 操作栏 -->
    <div class="page-header">
      <span class="page-title">设备列表</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>新增设备
      </el-button>
    </div>

    <!-- 数据表格 -->
    <div class="table-container">
      <el-table :data="tableData" v-loading="loading" stripe border>
        <el-table-column prop="code" label="设备编号" width="120" />
        <el-table-column prop="name" label="设备名称" width="150" />
        <el-table-column prop="category" label="设备类别" width="100" />
        <el-table-column prop="model" label="型号" width="150" />
        <el-table-column prop="manufacturer" label="生产厂家" width="150" />
        <el-table-column prop="location" label="安装位置" width="180" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" size="small">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">
              <el-icon><Edit /></el-icon>编辑
            </el-button>
            <el-button type="primary" link @click="handleView(row)">
              <el-icon><View /></el-icon>详情
            </el-button>
            <el-button type="danger" link @click="handleDelete(row)">
              <el-icon><Delete /></el-icon>删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑设备' : '新增设备'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备编号" prop="code">
              <el-input v-model="form.code" placeholder="请输入设备编号" :disabled="isEdit" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备类别" prop="category">
              <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
                <el-option label="电梯" value="电梯" />
                <el-option label="水泵" value="水泵" />
                <el-option label="空调" value="空调" />
                <el-option label="发电机" value="发电机" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择" style="width: 100%">
                <el-option label="正常" value="正常" />
                <el-option label="故障" value="故障" />
                <el-option label="维修中" value="维修中" />
                <el-option label="报废" value="报废" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="form.model" placeholder="请输入型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="生产厂家">
              <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购买日期">
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="保修到期">
              <el-date-picker
                v-model="form.warranty_expiry"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="安装位置">
          <el-input v-model="form.location" placeholder="请输入安装位置" />
        </el-form-item>
        <el-form-item label="设备描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入设备描述" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible" title="设备详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="设备编号">{{ detailData.code }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ detailData.name }}</el-descriptions-item>
        <el-descriptions-item label="设备类别">{{ detailData.category }}</el-descriptions-item>
        <el-descriptions-item label="设备状态">
          <el-tag :type="getStatusTagType(detailData.status)" size="small">
            {{ detailData.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="型号">{{ detailData.model }}</el-descriptions-item>
        <el-descriptions-item label="生产厂家">{{ detailData.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="购买日期">{{ detailData.purchase_date }}</el-descriptions-item>
        <el-descriptions-item label="保修到期">{{ detailData.warranty_expiry }}</el-descriptions-item>
        <el-descriptions-item label="安装位置">{{ detailData.location }}</el-descriptions-item>
        <el-descriptions-item label="设备描述" :span="2">{{ detailData.description }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getEquipmentList,
  createEquipment,
  updateEquipment,
  deleteEquipment
} from '@/api/equipment'

// 加载状态
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)

// 搜索表单
const searchForm = reactive({
  category: '',
  status: '',
  keyword: ''
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 0
})

// 表格数据
const tableData = ref([])

// 表单数据
const form = reactive({
  id: null,
  code: '',
  name: '',
  category: '',
  model: '',
  manufacturer: '',
  purchase_date: '',
  warranty_expiry: '',
  location: '',
  status: '正常',
  description: ''
})

// 详情数据
const detailData = reactive({
  code: '',
  name: '',
  category: '',
  status: '',
  model: '',
  manufacturer: '',
  purchase_date: '',
  warranty_expiry: '',
  location: '',
  description: ''
})

// 表单验证规则
const rules = {
  code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  category: [{ required: true, message: '请选择设备类别', trigger: 'change' }]
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const map = {
    '正常': 'success',
    '故障': 'danger',
    '维修中': 'warning',
    '报废': 'info'
  }
  return map[status] || 'info'
}

// 获取数据
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.currentPage - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    }
    // 清理空值
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })
    
    const res = await getEquipmentList(params)
    tableData.value = res
    // 模拟总数，实际应该从API获取
    pagination.total = res.length + 10
  } catch (error) {
    console.error('获取设备列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 查询
const handleSearch = () => {
  pagination.currentPage = 1
  fetchData()
}

// 重置
const handleReset = () => {
  searchForm.category = ''
  searchForm.status = ''
  searchForm.keyword = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, {
    id: null,
    code: '',
    name: '',
    category: '',
    model: '',
    manufacturer: '',
    purchase_date: '',
    warranty_expiry: '',
    location: '',
    status: '正常',
    description: ''
  })
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  dialogVisible.value = true
}

// 查看详情
const handleView = (row) => {
  Object.assign(detailData, row)
  detailVisible.value = true
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除设备 "${row.name}" 吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteEquipment(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

// 提交
const handleSubmit = async () => {
  submitting.value = true
  try {
    if (isEdit.value) {
      await updateEquipment(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createEquipment(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    submitting.value = false
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchData()
})
</script>
