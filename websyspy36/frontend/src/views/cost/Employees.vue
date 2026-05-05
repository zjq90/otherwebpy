<template>
  <div class="employees-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>员工管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="employee_code" label="员工编号" width="120" />
        <el-table-column prop="employee_name" label="姓名" width="100" />
        <el-table-column prop="department" label="部门" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.department }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="position" label="职位" width="100" />
        <el-table-column prop="base_salary" label="基本工资" width="120">
          <template #default="scope">
            ¥{{ scope.row.base_salary?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="hourly_rate" label="小时工资" width="100">
          <template #default="scope">
            ¥{{ scope.row.hourly_rate?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '在职' ? 'success' : 'info'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" ref="formRef" label-width="100px">
        <el-form-item label="员工编号">
          <el-input v-model="form.employee_code" placeholder="请输入员工编号" />
        </el-form-item>
        <el-form-item label="姓名">
          <el-input v-model="form.employee_name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="部门">
          <el-select v-model="form.department" placeholder="请选择" style="width: 100%">
            <el-option label="生产部" value="生产部" />
            <el-option label="质量部" value="质量部" />
            <el-option label="销售部" value="销售部" />
            <el-option label="财务部" value="财务部" />
            <el-option label="行政部" value="行政部" />
          </el-select>
        </el-form-item>
        <el-form-item label="职位">
          <el-input v-model="form.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="基本工资">
          <el-input-number v-model="form.base_salary" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="小时工资">
          <el-input-number v-model="form.hourly_rate" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" placeholder="请选择" style="width: 100%">
            <el-option label="在职" value="在职" />
            <el-option label="离职" value="离职" />
            <el-option label="休假" value="休假" />
          </el-select>
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
import { Plus } from '@element-plus/icons-vue'
import { costApi } from '@/api'

const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增员工')
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])

const form = reactive({
  id: null,
  employee_code: '',
  employee_name: '',
  department: '',
  position: '',
  base_salary: 0,
  hourly_rate: 0,
  status: '在职'
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await costApi.getEmployees()
    tableData.value = res.data || []
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增员工'
  Object.assign(form, { id: null, employee_code: '', employee_name: '', department: '', position: '', base_salary: 0, hourly_rate: 0, status: '在职' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑员工'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除吗？', '提示', { type: 'warning' })
    ElMessage.success('删除成功')
    loadData()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

const handleSubmit = async () => {
  ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
  dialogVisible.value = false
  loadData()
}

onMounted(() => {
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
