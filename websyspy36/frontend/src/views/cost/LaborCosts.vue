<template>
  <div class="labor-costs-page">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <span>人工成本</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="searchForm.startDate"
            type="date"
            placeholder="选择开始日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="searchForm.endDate"
            type="date"
            placeholder="选择结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="record_date" label="日期" width="120" />
        <el-table-column prop="employee_name" label="员工" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.employee?.employee_name || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="working_hours" label="工作时长 (h)" width="120">
          <template #default="scope">
            {{ scope.row.working_hours?.toFixed(1) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="overtime_hours" label="加班时长 (h)" width="120">
          <template #default="scope">
            {{ scope.row.overtime_hours?.toFixed(1) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="hourly_rate" label="小时工资 (元)" width="120">
          <template #default="scope">
            ¥{{ scope.row.hourly_rate?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="total_labor_cost" label="人工成本 (元)" width="140">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold;">
              ¥{{ scope.row.total_labor_cost?.toFixed(2) || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="work_content" label="工作内容" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      
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
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="550px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="记录日期" prop="record_date">
          <el-date-picker
            v-model="form.record_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="员工" prop="employee_id">
          <el-select v-model="form.employee_id" placeholder="请选择员工" style="width: 100%">
            <el-option
              v-for="item in employeeList"
              :key="item.id"
              :label="item.employee_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="工作时长 (h)" prop="working_hours">
          <el-input-number v-model="form.working_hours" :min="0" :max="24" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="加班时长 (h)" prop="overtime_hours">
          <el-input-number v-model="form.overtime_hours" :min="0" :max="24" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="小时工资 (元)" prop="hourly_rate">
          <el-input-number v-model="form.hourly_rate" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="加班倍率" prop="overtime_rate">
          <el-input-number v-model="form.overtime_rate" :min="1" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="工作内容" prop="work_content">
          <el-input v-model="form.work_content" placeholder="请输入工作内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import { costApi } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增人工成本记录')
const isEdit = ref(false)

const formRef = ref(null)
const tableData = ref([])
const employeeList = ref([])

const searchForm = reactive({
  startDate: '',
  endDate: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: null,
  record_date: '',
  employee_id: null,
  working_hours: 0,
  overtime_hours: 0,
  hourly_rate: 0,
  overtime_rate: 1.5,
  total_labor_cost: 0,
  work_content: ''
})

const rules = {
  record_date: [{ required: true, message: '请选择记录日期', trigger: 'change' }],
  employee_id: [{ required: true, message: '请选择员工', trigger: 'change' }],
  working_hours: [{ required: true, message: '请输入工作时长', trigger: 'blur' }],
  hourly_rate: [{ required: true, message: '请输入小时工资', trigger: 'blur' }]
}

const loadEmployeeList = async () => {
  try {
    const res = await costApi.getEmployees()
    employeeList.value = res.data || []
  } catch (e) {
    console.error('加载员工列表失败:', e)
    employeeList.value = []
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    if (searchForm.startDate) {
      params.start_date = searchForm.startDate
    }
    if (searchForm.endDate) {
      params.end_date = searchForm.endDate
    }
    
    const res = await costApi.getLaborCosts(params)
    tableData.value = res.data || []
  } catch (e) {
    console.error('加载数据失败:', e)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.startDate = ''
  searchForm.endDate = ''
  pagination.page = 1
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增人工成本记录'
  Object.assign(form, {
    id: null,
    record_date: '',
    employee_id: null,
    working_hours: 0,
    overtime_hours: 0,
    hourly_rate: 0,
    overtime_rate: 1.5,
    total_labor_cost: 0,
    work_content: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑人工成本记录'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await costApi.deleteLaborCost(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') {
      console.error('删除失败:', e)
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitting.value = true
      try {
        form.total_labor_cost = form.working_hours * form.hourly_rate + form.overtime_hours * form.hourly_rate * form.overtime_rate
        
        if (isEdit.value) {
          await costApi.updateLaborCost(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await costApi.createLaborCost(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (e) {
        console.error('提交失败:', e)
        ElMessage.error('提交失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

onMounted(() => {
  loadEmployeeList()
  loadData()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
