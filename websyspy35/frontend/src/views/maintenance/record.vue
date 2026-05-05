<template>
  <div class="record-page">
    <div class="page-header">
      <span class="page-title">保养记录</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增记录
      </el-button>
    </div>
    
    <el-card class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="设备">
          <el-select v-model="searchForm.equipment_id" placeholder="请选择设备" clearable style="width: 200px;" @change="handleEquipmentChange">
            <el-option
              v-for="item in equipmentList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
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
        <el-form-item label="执行结果">
          <el-select v-model="searchForm.execution_result" placeholder="请选择结果" clearable>
            <el-option label="正常完成" value="正常完成" />
            <el-option label="部分完成" value="部分完成" />
            <el-option label="需延期" value="需延期" />
            <el-option label="需停修" value="需停修" />
          </el-select>
        </el-form-item>
        <el-form-item label="执行日期">
          <el-date-picker
            v-model="searchForm.dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 300px;"
          />
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
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="所属设备" width="150">
          <template #default="scope">
            {{ getEquipmentName(scope.row.equipment_id) }}
          </template>
        </el-table-column>
        <el-table-column prop="maintenance_type" label="保养类型" width="100" />
        <el-table-column prop="execution_date" label="执行日期" width="120" />
        <el-table-column prop="executor" label="执行人员" width="100" />
        <el-table-column prop="execution_result" label="执行结果" width="100">
          <template #default="scope">
            <el-tag :class="getResultClass(scope.row.execution_result)" size="small">
              {{ scope.row.execution_result }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="working_hours" label="工时(小时)" width="120" />
        <el-table-column prop="cost" label="费用" width="100">
          <template #default="scope">
            <span v-if="scope.row.cost">{{ scope.row.cost }} 元</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="保养内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="problems_found" label="发现问题" min-width="150" show-overflow-tooltip>
          <template #default="scope">
            <span v-if="scope.row.problems_found">{{ scope.row.problems_found }}</span>
            <span v-else class="text-muted">无</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleView(scope.row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button type="primary" link @click="handleEdit(scope.row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">
              <el-icon><Delete /></el-icon>
              删除
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
        style="margin-top: 15px;"
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
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="执行日期" prop="execution_date">
              <el-date-picker
                v-model="form.execution_date"
                type="date"
                placeholder="请选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="执行人员" prop="executor">
              <el-input v-model="form.executor" placeholder="请输入执行人员" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="执行结果" prop="execution_result">
              <el-select v-model="form.execution_result" placeholder="请选择结果" style="width: 100%;">
                <el-option label="正常完成" value="正常完成" />
                <el-option label="部分完成" value="部分完成" />
                <el-option label="需延期" value="需延期" />
                <el-option label="需停修" value="需停修" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="工时(小时)" prop="working_hours">
              <el-input-number v-model="form.working_hours" :min="0" :step="0.5" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="费用(元)" prop="cost">
              <el-input-number v-model="form.cost" :min="0" :precision="2" style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="关联任务">
              <el-select v-model="form.task_id" placeholder="选择关联任务(可选)" clearable style="width: 100%;">
                <el-option
                  v-for="item in taskList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="保养内容" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            placeholder="请输入保养内容详情"
          />
        </el-form-item>
        <el-form-item label="更换零件">
          <el-input
            v-model="form.parts_replaced"
            type="textarea"
            :rows="2"
            placeholder="请输入更换的零件(可选)"
          />
        </el-form-item>
        <el-form-item label="发现问题">
          <el-input
            v-model="form.problems_found"
            type="textarea"
            :rows="2"
            placeholder="请输入发现的问题(可选)"
          />
        </el-form-item>
        <el-form-item label="解决方案">
          <el-input
            v-model="form.solutions"
            type="textarea"
            :rows="2"
            placeholder="请输入解决方案(可选)"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.remark"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息(可选)"
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
      title="保养记录详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="所属设备">{{ getEquipmentName(detailForm.equipment_id) }}</el-descriptions-item>
        <el-descriptions-item label="保养类型">{{ detailForm.maintenance_type }}</el-descriptions-item>
        <el-descriptions-item label="执行日期">{{ detailForm.execution_date }}</el-descriptions-item>
        <el-descriptions-item label="执行人员">{{ detailForm.executor }}</el-descriptions-item>
        <el-descriptions-item label="执行结果">
          <el-tag :class="getResultClass(detailForm.execution_result)" size="small">
            {{ detailForm.execution_result }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="工时">{{ detailForm.working_hours }} 小时</el-descriptions-item>
        <el-descriptions-item label="费用">
          <span v-if="detailForm.cost">{{ detailForm.cost }} 元</span>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="关联任务">{{ detailForm.task_id ? '已关联' : '无' }}</el-descriptions-item>
        <el-descriptions-item label="保养内容" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.description }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="更换零件" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.parts_replaced || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="发现问题" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.problems_found || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="解决方案" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.solutions || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.remark || '无' }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ detailForm.created_at }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ detailForm.updated_at }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import {
  getMaintenanceRecordList, getMaintenanceRecord, createMaintenanceRecord,
  updateMaintenanceRecord, deleteMaintenanceRecord
} from '@/api/maintenance'
import { getEquipmentList } from '@/api/equipment'
import { getMaintenanceTaskList } from '@/api/maintenance'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const equipmentList = ref([])
const taskList = ref([])

const searchForm = reactive({
  equipment_id: null,
  maintenance_type: '',
  execution_result: '',
  dateRange: []
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const defaultForm = {
  equipment_id: null,
  maintenance_type: '',
  execution_date: '',
  executor: '',
  execution_result: '正常完成',
  working_hours: 1,
  cost: 0,
  task_id: null,
  description: '',
  parts_replaced: '',
  problems_found: '',
  solutions: '',
  remark: ''
}

const form = reactive({ ...defaultForm })
const detailForm = reactive({ ...defaultForm })

const rules = {
  equipment_id: [{ required: true, message: '请选择所属设备', trigger: 'change' }],
  maintenance_type: [{ required: true, message: '请选择保养类型', trigger: 'change' }],
  execution_date: [{ required: true, message: '请选择执行日期', trigger: 'change' }],
  executor: [{ required: true, message: '请输入执行人员', trigger: 'blur' }],
  execution_result: [{ required: true, message: '请选择执行结果', trigger: 'change' }],
  description: [{ required: true, message: '请输入保养内容', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑保养记录' : '新增保养记录')

const getEquipmentName = (id) => {
  const item = equipmentList.value.find(e => e.id === id)
  return item ? item.name : '-'
}

const getResultClass = (result) => {
  const classMap = {
    '正常完成': 'status-tag completed',
    '部分完成': 'status-tag warning',
    '需延期': 'status-tag overdue',
    '需停修': 'status-tag danger'
  }
  return classMap[result] || 'status-tag normal'
}

const fetchEquipmentList = async () => {
  try {
    const res = await getEquipmentList({ limit: 1000 })
    equipmentList.value = res
  } catch (error) {
    console.error('获取设备列表失败:', error)
  }
}

const fetchTaskList = async () => {
  try {
    const res = await getMaintenanceTaskList({ limit: 1000 })
    taskList.value = res
  } catch (error) {
    console.error('获取任务列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      order_by: 'execution_date',
      order_dir: 'desc'
    }
    
    if (searchForm.equipment_id) {
      params.equipment_id = searchForm.equipment_id
    }
    if (searchForm.maintenance_type) {
      params.maintenance_type = searchForm.maintenance_type
    }
    if (searchForm.execution_result) {
      params.execution_result = searchForm.execution_result
    }
    if (searchForm.dateRange && searchForm.dateRange.length === 2) {
      params.start_date = searchForm.dateRange[0]
      params.end_date = searchForm.dateRange[1]
    }
    
    const res = await getMaintenanceRecordList(params)
    tableData.value = res || []
    pagination.total = 100
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleEquipmentChange = () => {
  // 可以根据设备过滤任务
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  Object.assign(searchForm, {
    equipment_id: null,
    maintenance_type: '',
    execution_result: '',
    dateRange: []
  })
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  Object.assign(form, {
    ...defaultForm,
    execution_date: new Date().toISOString().split('T')[0]
  })
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

const handleDelete = (row) => {
  ElMessageBox.confirm('确定要删除该保养记录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await deleteMaintenanceRecord(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await updateMaintenanceRecord(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createMaintenanceRecord(form)
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

onMounted(() => {
  fetchEquipmentList()
  fetchTaskList()
  fetchData()
})
</script>

<style lang="scss" scoped>
.record-page {
  padding: 20px;
  
  .page-header {
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    .page-title {
      font-size: 18px;
      font-weight: 600;
      margin-right: 20px;
    }
  }
  
  .text-muted {
    color: #909399;
  }
}
</style>
