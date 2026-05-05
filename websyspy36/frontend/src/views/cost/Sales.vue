<template>
  <div class="sales-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>销售记录</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="sale_date" label="销售日期" width="120" />
        <el-table-column prop="sale_code" label="销售单号" width="140" />
        <el-table-column prop="customer_name" label="客户名称" width="150" show-overflow-tooltip />
        <el-table-column prop="concrete_type" label="混凝土类型" width="100">
          <template #default="scope">
            <el-tag type="primary" size="small">{{ scope.row.concrete_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="数量 (m³)" width="120">
          <template #default="scope">
            {{ scope.row.quantity?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="unit_price" label="单价 (元)" width="100">
          <template #default="scope">
            ¥{{ scope.row.unit_price?.toFixed(2) || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="总金额 (元)" width="140">
          <template #default="scope">
            <span style="color: #f56c6c; font-weight: bold;">
              ¥{{ scope.row.total_amount?.toFixed(2) || 0 }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="delivery_location" label="交货地点" width="120" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">{{ scope.row.status }}</el-tag>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" ref="formRef" label-width="100px">
        <el-form-item label="销售日期">
          <el-date-picker
            v-model="form.sale_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="销售单号">
          <el-input v-model="form.sale_code" placeholder="自动生成" disabled />
        </el-form-item>
        <el-form-item label="客户名称">
          <el-input v-model="form.customer_name" placeholder="请输入客户名称" />
        </el-form-item>
        <el-form-item label="混凝土类型">
          <el-select v-model="form.concrete_type" placeholder="请选择" style="width: 100%">
            <el-option label="C20" value="C20" />
            <el-option label="C25" value="C25" />
            <el-option label="C30" value="C30" />
            <el-option label="C35" value="C35" />
            <el-option label="C40" value="C40" />
            <el-option label="C45" value="C45" />
          </el-select>
        </el-form-item>
        <el-form-item label="数量 (m³)">
          <el-input-number v-model="form.quantity" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="单价 (元)">
          <el-input-number v-model="form.unit_price" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="交货地点">
          <el-input v-model="form.delivery_location" placeholder="请输入交货地点" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" placeholder="请选择" style="width: 100%">
            <el-option label="已确认" value="已确认" />
            <el-option label="已发货" value="已发货" />
            <el-option label="已收款" value="已收款" />
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
const dialogTitle = ref('新增销售记录')
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])

const form = reactive({
  id: null,
  sale_date: '',
  sale_code: '',
  customer_name: '',
  concrete_type: '',
  quantity: 0,
  unit_price: 0,
  total_amount: 0,
  delivery_location: '',
  status: '已确认'
})

const getStatusTagType = (status) => {
  const map = { '已确认': 'info', '已发货': 'warning', '已收款': 'success' }
  return map[status] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await costApi.getSalesRecords()
    tableData.value = res.data || []
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增销售记录'
  Object.assign(form, { id: null, sale_date: '', sale_code: '', customer_name: '', concrete_type: '', quantity: 0, unit_price: 0, total_amount: 0, delivery_location: '', status: '已确认' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑销售记录'
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
