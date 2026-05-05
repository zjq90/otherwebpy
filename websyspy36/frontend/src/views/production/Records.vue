<template>
  <div class="records-page">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <span>生产记录列表</span>
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
        <el-table-column prop="record_date" label="记录日期" width="120" />
        <el-table-column prop="total_production" label="总产量 (m³)" width="120">
          <template #default="scope">
            {{ scope.row.total_production?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="qualified_production" label="合格产量 (m³)" width="120">
          <template #default="scope">
            {{ scope.row.qualified_production?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="qualified_rate" label="合格率 (%)" width="100">
          <template #default="scope">
            {{ getQualifiedRate(scope.row).toFixed(1) }}%
          </template>
        </el-table-column>
        <el-table-column prop="batch_count" label="批次数量" width="100" />
        <el-table-column prop="working_hours" label="工作时长 (h)" width="120">
          <template #default="scope">
            {{ scope.row.working_hours?.toFixed(1) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="production_type" label="生产类型" width="100" />
        <el-table-column prop="remarks" label="备注" min-width="150" show-overflow-tooltip />
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="记录日期" prop="record_date">
          <el-date-picker
            v-model="form.record_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="总产量 (m³)" prop="total_production">
          <el-input-number v-model="form.total_production" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="合格产量 (m³)" prop="qualified_production">
          <el-input-number v-model="form.qualified_production" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="批次数量" prop="batch_count">
          <el-input-number v-model="form.batch_count" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="工作时长 (h)" prop="working_hours">
          <el-input-number v-model="form.working_hours" :min="0" :precision="1" style="width: 100%" />
        </el-form-item>
        <el-form-item label="生产类型" prop="production_type">
          <el-select v-model="form.production_type" placeholder="请选择生产类型" style="width: 100%">
            <el-option label="商砼" value="商砼" />
            <el-option label="预制件" value="预制件" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input v-model="form.remarks" type="textarea" :rows="3" placeholder="请输入备注" />
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
import { productionApi } from '@/api'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增生产记录')
const isEdit = ref(false)

const formRef = ref(null)
const tableData = ref([])

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
  total_production: 0,
  qualified_production: 0,
  batch_count: 0,
  working_hours: 0,
  production_type: '',
  remarks: ''
})

const rules = {
  record_date: [{ required: true, message: '请选择记录日期', trigger: 'change' }],
  total_production: [{ required: true, message: '请输入总产量', trigger: 'blur' }],
  qualified_production: [{ required: true, message: '请输入合格产量', trigger: 'blur' }]
}

const getQualifiedRate = (row) => {
  if (row.total_production > 0) {
    return (row.qualified_production / row.total_production) * 100
  }
  return 0
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
    
    const res = await productionApi.getProductionRecords(params)
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
  dialogTitle.value = '新增生产记录'
  Object.assign(form, {
    id: null,
    record_date: '',
    total_production: 0,
    qualified_production: 0,
    batch_count: 0,
    working_hours: 0,
    production_type: '',
    remarks: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑生产记录'
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
    
    await productionApi.deleteProductionRecord(row.id)
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
        if (isEdit.value) {
          await productionApi.updateProductionRecord(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await productionApi.createProductionRecord(form)
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
