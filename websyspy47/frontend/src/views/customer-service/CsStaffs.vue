<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">客服人员</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增客服
      </el-button>
    </div>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="searchForm.real_name" placeholder="请输入真实姓名" clearable />
        </el-form-item>
        <el-form-item label="分组">
          <el-select v-model="searchForm.group_type" placeholder="全部" clearable>
            <el-option label="售前客服" :value="0" />
            <el-option label="售后客服" :value="1" />
            <el-option label="投诉处理" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="在职" :value="1" />
            <el-option label="离职" :value="0" />
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
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="real_name" label="真实姓名" />
        <el-table-column prop="phone" label="联系电话" />
        <el-table-column prop="group_type" label="分组" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="groupTypeTagMap[row.group_type]">
              {{ groupTypeLabelMap[row.group_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_consultations" label="总咨询数" align="center" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.total_consultations || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="resolved_count" label="已解决数" align="center" width="100">
          <template #default="{ row }">
            <el-tag type="success">{{ row.resolved_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="avg_rating" label="平均评分" align="center" width="100">
          <template #default="{ row }">
            <el-rate 
              v-model="row.avg_rating" 
              disabled 
              :max="5" 
              :show-text="true"
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" align="center" width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'danger'">
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="入职时间" width="160">
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
              type="info" 
              link 
              size="small" 
              @click="handleViewConsultations(row)"
            >
              咨询记录
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
              :disabled="row.status === 0"
            >
              离职
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
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码" 
            show-password
          />
        </el-form-item>
        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="分组" prop="group_type">
          <el-radio-group v-model="form.group_type">
            <el-radio :value="0">售前客服</el-radio>
            <el-radio :value="1">售后客服</el-radio>
            <el-radio :value="2">投诉处理</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">在职</el-radio>
            <el-radio :value="0">离职</el-radio>
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
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { getCsStaffList, createCsStaff, updateCsStaff, deleteCsStaff } from '@/api'

const router = useRouter()

const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tableData = ref([])

const searchForm = reactive({
  username: '',
  real_name: '',
  group_type: null,
  status: null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const form = reactive({
  username: '',
  password: '',
  real_name: '',
  phone: '',
  email: '',
  group_type: 0,
  status: 1,
  remark: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ],
  group_type: [
    { required: true, message: '请选择分组', trigger: 'change' }
  ]
}

const statusMap = {
  0: '离职',
  1: '在职'
}

const groupTypeTagMap = {
  0: 'primary',
  1: 'success',
  2: 'warning'
}

const groupTypeLabelMap = {
  0: '售前客服',
  1: '售后客服',
  2: '投诉处理'
}

const dialogTitle = ref('新增客服人员')

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    const res = await getCsStaffList(params)
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
  searchForm.username = ''
  searchForm.real_name = ''
  searchForm.group_type = null
  searchForm.status = null
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增客服人员'
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.phone = ''
  form.email = ''
  form.group_type = 0
  form.status = 1
  form.remark = ''
  delete form.id
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑客服人员'
  form.id = row.id
  form.username = row.username
  form.real_name = row.real_name
  form.phone = row.phone || ''
  form.email = row.email || ''
  form.group_type = row.group_type
  form.status = row.status
  form.remark = row.remark || ''
  dialogVisible.value = true
}

const handleViewConsultations = (row) => {
  router.push({ 
    path: '/consultations', 
    query: { staff_id: row.id, staff_name: row.real_name } 
  })
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要将客服人员 "${row.real_name}" 标记为离职吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteCsStaff(row.id)
    ElMessage.success('操作成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
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
          delete submitData.password
          await updateCsStaff(form.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createCsStaff(submitData)
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
