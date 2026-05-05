<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">回收人员管理</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增回收人员
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
        <el-form-item label="负责区域">
          <el-input v-model="searchForm.area" placeholder="请输入区域" clearable />
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
        <el-table-column prop="area" label="负责区域" />
        <el-table-column prop="total_orders" label="总订单数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">{{ row.total_orders || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="completed_orders" label="完成订单" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="success">{{ row.completed_orders || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="回收金额" width="120" align="center">
          <template #default="{ row }">
            <span style="color: #f56c6c; font-weight: 600;">¥{{ row.total_amount || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="performance_score" label="绩效评分" width="100" align="center">
          <template #default="{ row }">
            <el-progress 
              :percentage="row.performance_score || 0" 
              :color="getProgressColor(row.performance_score)"
              :stroke-width="8"
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
              type="warning" 
              link 
              size="small" 
              @click="handlePerformance(row)"
            >
              绩效
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
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="form.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="负责区域">
          <el-input v-model="form.area" placeholder="请输入负责区域" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">在职</el-radio>
            <el-radio :value="0">离职</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="3" placeholder="请输入备注" />
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
      v-model="performanceVisible"
      title="绩效考核记录"
      width="700px"
    >
      <el-descriptions :column="2" border class="mb-20">
        <el-descriptions-item label="姓名">{{ currentRecycler.real_name }}</el-descriptions-item>
        <el-descriptions-item label="用户名">{{ currentRecycler.username }}</el-descriptions-item>
        <el-descriptions-item label="负责区域">{{ currentRecycler.area || '-' }}</el-descriptions-item>
        <el-descriptions-item label="当前绩效分">{{ currentRecycler.performance_score || 0 }}</el-descriptions-item>
      </el-descriptions>
      
      <el-table :data="performanceData" v-loading="performanceLoading">
        <el-table-column prop="year_month" label="年月" width="120">
          <template #default="{ row }">
            {{ row.year }}年{{ row.month }}月
          </template>
        </el-table-column>
        <el-table-column prop="period_type" label="考核周期" align="center">
          <template #default="{ row }">
            {{ periodTypeMap[row.period_type] }}
          </template>
        </el-table-column>
        <el-table-column prop="order_count" label="订单数" align="center" />
        <el-table-column prop="completed_count" label="完成数" align="center" />
        <el-table-column prop="total_amount" label="回收金额" align="center">
          <template #default="{ row }">
            ¥{{ row.total_amount || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="score" label="评分" align="center">
          <template #default="{ row }">
            <el-tag :type="getScoreType(row.score)">{{ row.score }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="grade" label="等级" align="center">
          <template #default="{ row }">
            <el-tag :type="getGradeType(row.grade)">{{ gradeMap[row.grade] || row.grade }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="考核时间">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button type="primary" @click="handleAddPerformance">新增考核</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="addPerformanceVisible"
      title="新增绩效考核"
      width="500px"
    >
      <el-form :model="performanceForm" label-width="100px">
        <el-form-item label="考核周期">
          <el-radio-group v-model="performanceForm.period_type">
            <el-radio :value="0">月度</el-radio>
            <el-radio :value="1">季度</el-radio>
            <el-radio :value="2">年度</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="评分">
          <el-slider 
            v-model="performanceForm.score" 
            :min="0" 
            :max="100" 
            :show-tooltip="true"
          />
        </el-form-item>
        <el-form-item label="等级">
          <el-select v-model="performanceForm.grade" placeholder="请选择等级" style="width: 100%">
            <el-option label="优秀(A)" value="A" />
            <el-option label="良好(B)" value="B" />
            <el-option label="合格(C)" value="C" />
            <el-option label="待改进(D)" value="D" />
          </el-select>
        </el-form-item>
        <el-form-item label="考核意见">
          <el-input 
            v-model="performanceForm.comment" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入考核意见"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addPerformanceVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitPerformance">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { 
  getRecyclerList, 
  createRecycler, 
  updateRecycler, 
  deleteRecycler, 
  getPerformanceList,
  createPerformance
} from '@/api'

const loading = ref(false)
const dialogVisible = ref(false)
const performanceVisible = ref(false)
const addPerformanceVisible = ref(false)
const performanceLoading = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tableData = ref([])
const performanceData = ref([])
const currentRecycler = ref({})

const searchForm = reactive({
  username: '',
  real_name: '',
  area: '',
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
  id_card: '',
  area: '',
  status: 1,
  remark: ''
})

const performanceForm = reactive({
  period_type: 0,
  score: 80,
  grade: 'B',
  comment: ''
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  real_name: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' }
  ]
}

const statusMap = {
  0: '离职',
  1: '在职'
}

const periodTypeMap = {
  0: '月度',
  1: '季度',
  2: '年度'
}

const gradeMap = {
  'A': '优秀',
  'B': '良好',
  'C': '合格',
  'D': '待改进'
}

const dialogTitle = ref('新增回收人员')

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const getProgressColor = (score) => {
  if (!score) return '#909399'
  if (score >= 90) return '#67c23a'
  if (score >= 80) return '#409eff'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

const getScoreType = (score) => {
  if (!score) return 'info'
  if (score >= 90) return 'success'
  if (score >= 80) return 'primary'
  if (score >= 60) return 'warning'
  return 'danger'
}

const getGradeType = (grade) => {
  switch (grade) {
    case 'A': return 'success'
    case 'B': return 'primary'
    case 'C': return 'warning'
    case 'D': return 'danger'
    default: return 'info'
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    const res = await getRecyclerList(params)
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
  searchForm.area = ''
  searchForm.status = null
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增回收人员'
  form.username = ''
  form.password = ''
  form.real_name = ''
  form.phone = ''
  form.id_card = ''
  form.area = ''
  form.status = 1
  form.remark = ''
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑回收人员'
  form.username = row.username
  form.real_name = row.real_name
  form.phone = row.phone || ''
  form.id_card = row.id_card || ''
  form.area = row.area || ''
  form.status = row.status
  form.remark = row.remark || ''
  form.id = row.id
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要将回收人员 "${row.real_name}" 标记为离职吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteRecycler(row.id)
    ElMessage.success('操作成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('操作失败:', error)
    }
  }
}

const handlePerformance = async (row) => {
  currentRecycler.value = { ...row }
  performanceVisible.value = true
  performanceLoading.value = true
  
  try {
    const res = await getPerformanceList({ 
      page: 1, 
      page_size: 100, 
      recycler_id: row.id 
    })
    const data = res.data || {}
    performanceData.value = data.list || []
  } catch (error) {
    console.error('获取绩效记录失败:', error)
  } finally {
    performanceLoading.value = false
  }
}

const handleAddPerformance = () => {
  performanceForm.period_type = 0
  performanceForm.score = 80
  performanceForm.grade = 'B'
  performanceForm.comment = ''
  addPerformanceVisible.value = true
}

const handleSubmitPerformance = async () => {
  try {
    await createPerformance({
      recycler_id: currentRecycler.value.id,
      year: dayjs().year(),
      month: dayjs().month() + 1,
      ...performanceForm
    })
    ElMessage.success('考核记录添加成功')
    addPerformanceVisible.value = false
    handlePerformance(currentRecycler.value)
  } catch (error) {
    console.error('添加考核记录失败:', error)
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = { ...form }
        
        if (isEdit.value) {
          await updateRecycler(form.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createRecycler(submitData)
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
