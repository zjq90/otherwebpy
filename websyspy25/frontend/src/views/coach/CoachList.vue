<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">教练列表</h2>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增教练
      </el-button>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="教练姓名">
          <el-input v-model="searchForm.name" placeholder="请输入教练姓名" clearable />
        </el-form-item>
        <el-form-item label="手机号码">
          <el-input v-model="searchForm.phone" placeholder="请输入手机号码" clearable />
        </el-form-item>
        <el-form-item label="教练级别">
          <el-select v-model="searchForm.level" placeholder="请选择级别" clearable>
            <el-option label="初级" value="初级" />
            <el-option label="中级" value="中级" />
            <el-option label="高级" value="高级" />
            <el-option label="金牌" value="金牌" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="在职" value="在职" />
            <el-option label="离职" value="离职" />
            <el-option label="休假" value="休假" />
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
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" style="width: 100%" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="教练姓名" width="120" />
      <el-table-column prop="gender" label="性别" width="80" />
      <el-table-column prop="phone" label="手机号码" width="140" />
      <el-table-column prop="level" label="级别" width="100">
        <template #default="scope">
          <el-tag :type="getLevelType(scope.row.level)">
            {{ scope.row.level }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="expertise" label="擅长领域" min-width="150" />
      <el-table-column prop="hourly_rate" label="课时费率" width="100">
        <template #default="scope">
          ¥{{ scope.row.hourly_rate }}
        </template>
      </el-table-column>
      <el-table-column prop="commission_rate" label="提成比例" width="100">
        <template #default="scope">
          {{ scope.row.commission_rate }}%
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag :type="getStatusType(scope.row.status)">
            {{ scope.row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="hire_date" label="入职日期" width="120" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="scope">
          <el-button type="primary" link size="small" @click="handleView(scope.row)">
            查看
          </el-button>
          <el-button type="primary" link size="small" @click="handleEdit(scope.row)">
            编辑
          </el-button>
          <el-button type="danger" link size="small" @click="handleDelete(scope.row)">
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
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="教练姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入教练姓名" />
        </el-form-item>
        <el-form-item label="性别" prop="gender">
          <el-radio-group v-model="form.gender">
            <el-radio label="男">男</el-radio>
            <el-radio label="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号码" />
        </el-form-item>
        <el-form-item label="身份证号" prop="id_card">
          <el-input v-model="form.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="住址">
          <el-input v-model="form.address" placeholder="请输入住址" />
        </el-form-item>
        <el-form-item label="入职日期" prop="hire_date">
          <el-date-picker
            v-model="form.hire_date"
            type="date"
            placeholder="选择入职日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="教练级别" prop="level">
          <el-select v-model="form.level" placeholder="请选择级别">
            <el-option label="初级" value="初级" />
            <el-option label="中级" value="中级" />
            <el-option label="高级" value="高级" />
            <el-option label="金牌" value="金牌" />
          </el-select>
        </el-form-item>
        <el-form-item label="擅长领域">
          <el-select
            v-model="expertiseList"
            multiple
            placeholder="请选择擅长领域"
            style="width: 100%"
            @change="handleExpertiseChange"
          >
            <el-option label="减脂" value="减脂" />
            <el-option label="增肌" value="增肌" />
            <el-option label="康复" value="康复" />
            <el-option label="塑形" value="塑形" />
            <el-option label="普拉提" value="普拉提" />
            <el-option label="瑜伽" value="瑜伽" />
            <el-option label="拳击" value="拳击" />
            <el-option label="拉伸" value="拉伸" />
          </el-select>
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input
            v-model="form.bio"
            type="textarea"
            :rows="3"
            placeholder="请输入个人简介"
          />
        </el-form-item>
        <el-form-item label="课时费率" prop="hourly_rate">
          <el-input-number v-model="form.hourly_rate" :min="0" :precision="2" />
          <span style="margin-left: 10px;">元/小时</span>
        </el-form-item>
        <el-form-item label="提成比例" prop="commission_rate">
          <el-input-number v-model="form.commission_rate" :min="0" :max="100" :precision="1" />
          <span style="margin-left: 10px;">%</span>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="在职" value="在职" />
            <el-option label="离职" value="离职" />
            <el-option label="休假" value="休假" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="教练详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="教练姓名">{{ currentRow.name }}</el-descriptions-item>
        <el-descriptions-item label="性别">{{ currentRow.gender }}</el-descriptions-item>
        <el-descriptions-item label="手机号码">{{ currentRow.phone }}</el-descriptions-item>
        <el-descriptions-item label="身份证号">{{ currentRow.id_card || '-' }}</el-descriptions-item>
        <el-descriptions-item label="邮箱">{{ currentRow.email || '-' }}</el-descriptions-item>
        <el-descriptions-item label="住址">{{ currentRow.address || '-' }}</el-descriptions-item>
        <el-descriptions-item label="教练级别">
          <el-tag :type="getLevelType(currentRow.level)">{{ currentRow.level }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRow.status)">{{ currentRow.status }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="擅长领域">{{ currentRow.expertise || '-' }}</el-descriptions-item>
        <el-descriptions-item label="入职日期">{{ currentRow.hire_date }}</el-descriptions-item>
        <el-descriptions-item label="课时费率">¥{{ currentRow.hourly_rate }}/小时</el-descriptions-item>
        <el-descriptions-item label="提成比例">{{ currentRow.commission_rate }}%</el-descriptions-item>
        <el-descriptions-item label="个人简介" :span="2">
          {{ currentRow.bio || '暂无' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const formRef = ref(null)
const currentRow = ref({})
const expertiseList = ref([])

const isEdit = ref(false)
const dialogTitle = computed(() => isEdit.value ? '编辑教练' : '新增教练')

const searchForm = reactive({
  name: '',
  phone: '',
  level: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const form = reactive({
  name: '',
  gender: '男',
  phone: '',
  id_card: '',
  email: '',
  address: '',
  hire_date: new Date().toISOString().split('T')[0],
  level: '初级',
  expertise: '',
  bio: '',
  hourly_rate: 100,
  commission_rate: 30,
  status: '在职'
})

const rules = {
  name: [{ required: true, message: '请输入教练姓名', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  phone: [
    { required: true, message: '请输入手机号码', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
  ],
  level: [{ required: true, message: '请选择教练级别', trigger: 'change' }],
  hourly_rate: [{ required: true, message: '请输入课时费率', trigger: 'blur' }],
  commission_rate: [{ required: true, message: '请输入提成比例', trigger: 'blur' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }]
}

// 获取级别标签类型
const getLevelType = (level) => {
  const typeMap = {
    '初级': 'info',
    '中级': 'warning',
    '高级': 'primary',
    '金牌': 'success'
  }
  return typeMap[level] || 'info'
}

// 获取状态标签类型
const getStatusType = (status) => {
  const typeMap = {
    '在职': 'success',
    '离职': 'danger',
    '休假': 'warning'
  }
  return typeMap[status] || 'info'
}

// 处理擅长领域变化
const handleExpertiseChange = (val) => {
  form.expertise = val.join(',')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...searchForm
    }
    // 清除空值参数
    Object.keys(params).forEach(key => {
      if (params[key] === '' || params[key] === null || params[key] === undefined) {
        delete params[key]
      }
    })
    
    const res = await api.coach.getList(params)
    tableData.value = res.data || []
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
  searchForm.name = ''
  searchForm.phone = ''
  searchForm.level = ''
  searchForm.status = ''
  handleSearch()
}

// 新增
const handleAdd = () => {
  isEdit.value = false
  // 重置表单
  form.name = ''
  form.gender = '男'
  form.phone = ''
  form.id_card = ''
  form.email = ''
  form.address = ''
  form.hire_date = new Date().toISOString().split('T')[0]
  form.level = '初级'
  form.expertise = ''
  form.bio = ''
  form.hourly_rate = 100
  form.commission_rate = 30
  form.status = '在职'
  expertiseList.value = []
  dialogVisible.value = true
}

// 编辑
const handleEdit = (row) => {
  isEdit.value = true
  currentRow.value = row
  // 填充表单
  Object.assign(form, row)
  if (row.expertise) {
    expertiseList.value = row.expertise.split(',')
  } else {
    expertiseList.value = []
  }
  dialogVisible.value = true
}

// 查看
const handleView = (row) => {
  currentRow.value = row
  detailDialogVisible.value = true
}

// 删除
const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除教练「${row.name}」吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await api.coach.delete(row.id)
      ElMessage.success('删除成功')
      loadData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

// 提交
const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        if (isEdit.value) {
          await api.coach.update(currentRow.value.id, form)
          ElMessage.success('更新成功')
        } else {
          await api.coach.create(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitting.value = false
      }
    }
  })
}

// 分页变化
const handleSizeChange = (val) => {
  pagination.pageSize = val
  loadData()
}

const handleCurrentChange = (val) => {
  pagination.page = val
  loadData()
}

onMounted(() => {
  loadData()
})
</script>
