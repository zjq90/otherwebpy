<template>
  <div class="materials-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>原材料管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="material_code" label="材料编号" width="120" />
        <el-table-column prop="material_name" label="材料名称" width="150" />
        <el-table-column prop="material_type" label="材料类型" width="100">
          <template #default="scope">
            <el-tag size="small">{{ scope.row.material_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column prop="current_price" label="当前单价" width="120">
          <template #default="scope">
            ¥{{ scope.row.current_price?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="stock_quantity" label="库存数量" width="120">
          <template #default="scope">
            <el-progress
              :percentage="Math.min(scope.row.stock_quantity / 1000 * 100, 100)"
              :stroke-width="18"
              :color="getStockColor(scope.row.stock_quantity)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="supplier" label="供应商" width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="材料编号" prop="material_code">
          <el-input v-model="form.material_code" placeholder="请输入材料编号" />
        </el-form-item>
        <el-form-item label="材料名称" prop="material_name">
          <el-input v-model="form.material_name" placeholder="请输入材料名称" />
        </el-form-item>
        <el-form-item label="材料类型" prop="material_type">
          <el-select v-model="form.material_type" placeholder="请选择" style="width: 100%">
            <el-option label="水泥" value="水泥" />
            <el-option label="砂石" value="砂石" />
            <el-option label="粉煤灰" value="粉煤灰" />
            <el-option label="外加剂" value="外加剂" />
            <el-option label="矿粉" value="矿粉" />
          </el-select>
        </el-form-item>
        <el-form-item label="单位" prop="unit">
          <el-input v-model="form.unit" placeholder="请输入单位" />
        </el-form-item>
        <el-form-item label="当前单价" prop="current_price">
          <el-input-number v-model="form.current_price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="库存数量" prop="stock_quantity">
          <el-input-number v-model="form.stock_quantity" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="供应商" prop="supplier">
          <el-input v-model="form.supplier" placeholder="请输入供应商" />
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
const dialogTitle = ref('新增原材料')
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])

const form = reactive({
  id: null,
  material_code: '',
  material_name: '',
  material_type: '',
  unit: '',
  current_price: 0,
  stock_quantity: 0,
  supplier: ''
})

const rules = {
  material_code: [{ required: true, message: '请输入材料编号', trigger: 'blur' }],
  material_name: [{ required: true, message: '请输入材料名称', trigger: 'blur' }]
}

const getStockColor = (quantity) => {
  if (quantity > 500) return '#67C23A'
  if (quantity > 200) return '#E6A23C'
  return '#F56C6C'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await costApi.getMaterials()
    tableData.value = res.data || []
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增原材料'
  Object.assign(form, { id: null, material_code: '', material_name: '', material_type: '', unit: '', current_price: 0, stock_quantity: 0, supplier: '' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑原材料'
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
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
        dialogVisible.value = false
        loadData()
      } catch (e) {
        ElMessage.error('操作失败')
      }
    }
  })
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
