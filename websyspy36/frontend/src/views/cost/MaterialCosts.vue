<template>
  <div class="material-costs-page">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <span>原材料成本</span>
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
        <el-table-column prop="material_name" label="原材料" width="120">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.material?.material_name || '-' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="consumption_quantity" label="消耗量" width="120">
          <template #default="scope">
            {{ scope.row.consumption_quantity?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价 (元)" width="100">
          <template #default="scope">
            ¥{{ scope.row.unit_price?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="total_cost" label="总成本 (元)" width="120">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold;">
              ¥{{ scope.row.total_cost?.toFixed(2) || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="production_batch" label="生产批次" width="180" show-overflow-tooltip />
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
        <el-form-item label="原材料" prop="material_id">
          <el-select v-model="form.material_id" placeholder="请选择原材料" style="width: 100%">
            <el-option
              v-for="item in materialList"
              :key="item.id"
              :label="item.material_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="消耗量" prop="consumption_quantity">
          <el-input-number v-model="form.consumption_quantity" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价 (元)" prop="unit_price">
          <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="生产批次" prop="production_batch">
          <el-input v-model="form.production_batch" placeholder="请输入生产批次" />
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
const dialogTitle = ref('新增原材料成本记录')
const isEdit = ref(false)

const formRef = ref(null)
const tableData = ref([])
const materialList = ref([])

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
  material_id: null,
  consumption_quantity: 0,
  unit_price: 0,
  total_cost: 0,
  production_batch: ''
})

const rules = {
  record_date: [{ required: true, message: '请选择记录日期', trigger: 'change' }],
  material_id: [{ required: true, message: '请选择原材料', trigger: 'change' }],
  consumption_quantity: [{ required: true, message: '请输入消耗量', trigger: 'blur' }],
  unit_price: [{ required: true, message: '请输入单价', trigger: 'blur' }]
}

const loadMaterialList = async () => {
  try {
    const res = await costApi.getMaterials()
    materialList.value = res.data || []
  } catch (e) {
    console.error('加载原材料列表失败:', e)
    materialList.value = []
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
    
    const res = await costApi.getMaterialCosts(params)
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
  dialogTitle.value = '新增原材料成本记录'
  Object.assign(form, {
    id: null,
    record_date: '',
    material_id: null,
    consumption_quantity: 0,
    unit_price: 0,
    total_cost: 0,
    production_batch: ''
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑原材料成本记录'
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
    
    await costApi.deleteMaterialCost(row.id)
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
        form.total_cost = form.consumption_quantity * form.unit_price
        
        if (isEdit.value) {
          await costApi.updateMaterialCost(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await costApi.createMaterialCost(form)
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
  loadMaterialList()
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
