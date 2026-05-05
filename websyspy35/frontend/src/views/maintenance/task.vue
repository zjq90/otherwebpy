<template>
  <div class="task-page">
    <div class="page-header">
      <span class="page-title">保养任务</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增任务
      </el-button>
    </div>
    
    <el-card class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="设备">
          <el-select v-model="searchForm.equipment_id" placeholder="请选择设备" clearable style="width: 200px;">
            <el-option
              v-for="item in equipmentList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="任务状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待执行" value="待执行" />
            <el-option label="执行中" value="执行中" />
            <el-option label="已完成" value="已完成" />
            <el-option label="已逾期" value="已逾期" />
            <el-option label="已取消" value="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item label="保养类型">
          <el-select v-model="searchForm.maintenance_type" placeholder="请选择类型" clearable>
            <el-option label="日常保养" value="日常保养" />
            <el-option label="月度保养" value="月度保养" />
            <el-option label="季度保养" value="季度保养" />
            <el-option label="年度保养" value="年度保养" />
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
    
    <el-card>
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="task_code" label="任务编号" width="140" />
        <el-table-column prop="name" label="任务名称" width="200" show-overflow-tooltip />
        <el-table-column prop="maintenance_type" label="保养类型" width="100" />
        <el-table-column label="所属设备" width="150">
          <template #default="scope">
            {{ getEquipmentName(scope.row.equipment_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="plan_date" label="计划日期" width="120" />
        <el-table-column prop="actual_date" label="实际日期" width="120">
          <template #default="scope">
            {{ scope.row.actual_date || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="responsible_person" label="负责人" width="100" />
        <el-table-column prop="executor" label="执行人员" width="100">
          <template #default="scope">
            {{ scope.row.executor || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :class="getStatusClass(scope.row.status)" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="primary" link v-if="scope.row.status !== '已完成'" @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="success" link v-if="scope.row.status === '待执行' || scope.row.status === '执行中'" @click="handleComplete(scope.row)">
              <el-icon><Check /></el-icon>
              完成
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="fetchData"
        @current-change="fetchData"
      />
    </el-card>
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="任务编号" prop="task_code">
              <el-input v-model="form.task_code" placeholder="请输入任务编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任务名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入任务名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="保养类型" prop="maintenance_type">
              <el-select v-model="form.maintenance_type" placeholder="请选择类型" style="width: 100%;">
                <el-option label="日常保养" value="日常保养" />
                <el-option label="月度保养" value="月度保养" />
                <el-option label="季度保养" value="季度保养" />
                <el-option label="年度保养" value="年度保养" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="所属设备" prop="equipment_id">
              <el-select v-model="form.equipment_id" placeholder="请选择设备" style="width: 100%;">
                <el-option
                  v-for="item in equipmentList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="计划执行日期" prop="plan_date">
              <el-date-picker
                v-model="form.plan_date"
                type="date"
                placeholder="请选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="任务状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
                <el-option label="待执行" value="待执行" />
                <el-option label="执行中" value="执行中" />
                <el-option label="已完成" value="已完成" />
                <el-option label="已逾期" value="已逾期" />
                <el-option label="已取消" value="已取消" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="负责人" prop="responsible_person">
              <el-input v-model="form.responsible_person" placeholder="请输入负责人" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="执行人员" prop="executor">
              <el-input v-model="form.executor" placeholder="请输入执行人员" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="保养内容" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="4"
            placeholder="请输入保养内容"
          />
        </el-form-item>
        <el-form-item label="保养标准" prop="standard">
          <el-input
            v-model="form.standard"
            type="textarea"
            :rows="3"
            placeholder="请输入保养标准"
          />
        </el-form-item>
        <el-form-item label="备注" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="detailVisible"
      title="任务详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务编号">{{ detailForm.task_code }}</el-descriptions-item>
        <el-descriptions-item label="任务名称">{{ detailForm.name }}</el-descriptions-item>
        <el-descriptions-item label="保养类型">{{ detailForm.maintenance_type }}</el-descriptions-item>
        <el-descriptions-item label="所属设备">{{ getEquipmentName(detailForm.equipment_id) }}</el-descriptions-item>
        <el-descriptions-item label="计划日期">{{ detailForm.plan_date }}</el-descriptions-item>
        <el-descriptions-item label="实际日期">{{ detailForm.actual_date || '-' }}</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ detailForm.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="执行人员">{{ detailForm.executor || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :class="getStatusClass(detailForm.status)" size="small">
            {{ detailForm.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="完成情况">{{ detailForm.completion_status || '-' }}</el-descriptions-item>
        <el-descriptions-item label="保养内容" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.content }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="保养标准" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.standard }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailForm.description }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
    
    <el-dialog
      v-model="completeVisible"
      title="完成任务"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="completeFormRef"
        :model="completeForm"
        :rules="completeRules"
        label-width="100px"
      >
        <el-form-item label="实际日期" prop="actual_date">
          <el-date-picker
            v-model="completeForm.actual_date"
            type="date"
            placeholder="请选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="执行人员" prop="executor">
          <el-input v-model="completeForm.executor" placeholder="请输入执行人员" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="completeVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitComplete" :loading="completeLoading">
            确定
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Check } from '@element-plus/icons-vue'
import {
  getMaintenanceTaskList, getMaintenanceTask, createMaintenanceTask,
  updateMaintenanceTask, completeMaintenanceTask
} from '@/api/maintenance'
import { getEquipmentList } from '@/api/equipment'

const loading = ref(false)
const submitLoading = ref(false)
const completeLoading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const completeVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const completeFormRef = ref(null)

const equipmentList = ref([])

const searchForm = reactive({
  equipment_id: null,
  status: '',
  maintenance_type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const defaultForm = {
  task_code: '',
  name: '',
  maintenance_type: '',
  equipment_id: null,
  plan_date: '',
  actual_date: '',
  content: '',
  standard: '',
  responsible_person: '',
  executor: '',
  status: '待执行',
  description: ''
}

const form = reactive({ ...defaultForm })
const detailForm = reactive({ ...defaultForm })
const currentTaskId = ref(null)

const completeForm = reactive({
  actual_date: '',
  executor: ''
})

const rules = {
  task_code: [{ required: true, message: '请输入任务编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  maintenance_type: [{ required: true, message: '请选择保养类型', trigger: 'change' }],
  equipment_id: [{ required: true, message: '请选择所属设备', trigger: 'change' }],
  plan_date: [{ required: true, message: '请选择计划日期', trigger: 'change' }],
  content: [{ required: true, message: '请输入保养内容', trigger: 'blur' }]
}

const completeRules = {
  actual_date: [{ required: true, message: '请选择实际日期', trigger: 'change' }],
  executor: [{ required: true, message: '请输入执行人员', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑任务' : '新增任务')

const getStatusClass = (status) => {
  const classMap = {
    '待执行': 'status-tag pending',
    '执行中': 'status-tag executing',
    '已完成': 'status-tag completed',
    '已逾期': 'status-tag overdue',
    '已取消': 'status-tag cancelled'
  }
  return classMap[status] || 'status-tag normal'
}

const getEquipmentName = (id) => {
  const item = equipmentList.value.find(e => e.id === id)
  return item ? item.name : '-'
}

const fetchEquipmentList = async () => {
  try {
    const res = await getEquipmentList({ limit: 1000 })
    equipmentList.value = res
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    }
    if (!params.equipment_id) delete params.equipment_id
    if (!params.status) delete params.status
    if (!params.maintenance_type) delete params.maintenance_type
    
    const res = await getMaintenanceTaskList(params)
    tableData.value = res
    pagination.total = 100
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
  Object.assign(searchForm, {
    equipment_id: null,
    status: '',
    maintenance_type: ''
  })
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, defaultForm)
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleView = (row) => {
  Object.assign(detailForm, { ...row })
  detailVisible.value = true
}

const handleComplete = (row) => {
  currentTaskId.value = row.id
  Object.assign(completeForm, {
    actual_date: new Date().toISOString().split('T')[0],
    executor: ''
  })
  completeVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateMaintenanceTask(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createMaintenanceTask(form)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleSubmitComplete = async () => {
  if (!completeFormRef.value) return
  
  await completeFormRef.value.validate(async (valid) => {
    if (valid) {
      completeLoading.value = true
      try {
        await completeMaintenanceTask(currentTaskId.value, completeForm)
        ElMessage.success('任务已完成')
        completeVisible.value = false
        fetchData()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        completeLoading.value = false
      }
    }
  })
}

onMounted(() => {
  fetchEquipmentList()
  fetchData()
})
</script>
