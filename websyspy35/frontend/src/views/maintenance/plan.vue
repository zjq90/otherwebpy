<template>
  <div class="plan-page">
    <div class="page-header">
      <span class="page-title">保养计划</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增计划
      </el-button>
    </div>
    
    <el-card class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="保养类型">
          <el-select v-model="searchForm.maintenance_type" placeholder="请选择类型" clearable>
            <el-option label="日常保养" value="日常保养" />
            <el-option label="月度保养" value="月度保养" />
            <el-option label="季度保养" value="季度保养" />
            <el-option label="年度保养" value="年度保养" />
          </el-select>
        </el-form-item>
        <el-form-item label="计划状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="启用" value="启用" />
            <el-option label="禁用" value="禁用" />
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
        <el-table-column prop="plan_code" label="计划编号" width="120" />
        <el-table-column prop="name" label="计划名称" width="200" />
        <el-table-column prop="maintenance_type" label="保养类型" width="120" />
        <el-table-column prop="cycle_description" label="执行周期" width="120" />
        <el-table-column prop="cycle_days" label="周期(天)" width="100" align="center" />
        <el-table-column prop="estimated_hours" label="预计耗时(小时)" width="120" align="center" />
        <el-table-column prop="responsible_person" label="负责人" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :class="scope.row.status === '启用' ? 'status-tag normal' : 'status-tag stopped'" size="small">
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
            <el-form-item label="计划编号" prop="plan_code">
              <el-input v-model="form.plan_code" placeholder="请输入计划编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="计划名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入计划名称" />
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
            <el-form-item label="执行周期(天)" prop="cycle_days">
              <el-input-number v-model="form.cycle_days" :min="1" style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="周期描述" prop="cycle_description">
              <el-input v-model="form.cycle_description" placeholder="如：每日一次" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="预计耗时(小时)" prop="estimated_hours">
              <el-input-number v-model="form.estimated_hours" :min="0" :step="0.5" style="width: 100%;" />
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
            <el-form-item label="计划状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%;">
                <el-option label="启用" value="启用" />
                <el-option label="禁用" value="禁用" />
              </el-select>
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
      title="计划详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="计划编号">{{ detailForm.plan_code }}</el-descriptions-item>
        <el-descriptions-item label="计划名称">{{ detailForm.name }}</el-descriptions-item>
        <el-descriptions-item label="保养类型">{{ detailForm.maintenance_type }}</el-descriptions-item>
        <el-descriptions-item label="执行周期">{{ detailForm.cycle_description }}</el-descriptions-item>
        <el-descriptions-item label="周期(天)">{{ detailForm.cycle_days }}天</el-descriptions-item>
        <el-descriptions-item label="预计耗时">{{ detailForm.estimated_hours }}小时</el-descriptions-item>
        <el-descriptions-item label="负责人">{{ detailForm.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :class="detailForm.status === '启用' ? 'status-tag normal' : 'status-tag stopped'" size="small">
            {{ detailForm.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="保养内容" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.content }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="保养标准" :span="2">
          <div style="white-space: pre-wrap;">{{ detailForm.standard }}</div>
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailForm.description }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, View, Edit, Delete } from '@element-plus/icons-vue'
import {
  getMaintenancePlanList, getMaintenancePlan, createMaintenancePlan,
  updateMaintenancePlan, deleteMaintenancePlan
} from '@/api/maintenance'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  maintenance_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const defaultForm = {
  plan_code: '',
  name: '',
  maintenance_type: '',
  cycle_days: 30,
  cycle_description: '',
  estimated_hours: 1,
  responsible_person: '',
  status: '启用',
  content: '',
  standard: '',
  description: ''
}

const form = reactive({ ...defaultForm })
const detailForm = reactive({ ...defaultForm })

const rules = {
  plan_code: [{ required: true, message: '请输入计划编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  maintenance_type: [{ required: true, message: '请选择保养类型', trigger: 'change' }],
  cycle_days: [{ required: true, message: '请输入执行周期', trigger: 'blur' }],
  content: [{ required: true, message: '请输入保养内容', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑计划' : '新增计划')

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    }
    if (!params.maintenance_type) delete params.maintenance_type
    if (!params.status) delete params.status
    
    const res = await getMaintenancePlanList(params)
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
    maintenance_type: '',
    status: ''
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

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除计划 "${row.name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteMaintenancePlan(row.id)
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
          await updateMaintenancePlan(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createMaintenancePlan(form)
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
  fetchData()
})
</script>
