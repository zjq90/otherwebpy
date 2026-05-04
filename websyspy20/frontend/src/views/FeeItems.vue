<template>
  <div class="fee-items">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>费用项目列表</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增费用项目
          </el-button>
        </div>
      </template>

      <el-table :data="feeItems" stripe style="width: 100%">
        <el-table-column prop="name" label="费用名称" width="150" />
        <el-table-column prop="code" label="费用编码" width="150" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="billingCycle" label="计费周期" width="120">
          <template #default="scope">
            <el-tag>{{ getBillingCycleLabel(scope.row.billing_cycle) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="billingType" label="计费类型" width="120">
          <template #default="scope">
            <el-tag type="info">{{ getBillingTypeLabel(scope.row.billing_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="unitPrice" label="单价(元)" width="100">
          <template #default="scope">
            <span class="price-text">¥{{ scope.row.unit_price }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="isActive" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button 
              type="primary" 
              link 
              @click="handleToggle(scope.row)"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-form-item label="费用名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入费用名称" />
        </el-form-item>
        <el-form-item label="费用编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入费用编码（如：PROPERTY_FEE）" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="计费周期" prop="billingCycle">
          <el-select v-model="form.billing_cycle" placeholder="请选择计费周期" style="width: 100%;">
            <el-option label="月付" value="monthly" />
            <el-option label="季付" value="quarterly" />
            <el-option label="半年付" value="half_yearly" />
            <el-option label="年付" value="yearly" />
            <el-option label="一次性" value="one_time" />
          </el-select>
        </el-form-item>
        <el-form-item label="计费类型" prop="billingType">
          <el-select v-model="form.billing_type" placeholder="请选择计费类型" style="width: 100%;">
            <el-option label="按面积计费" value="area" />
            <el-option label="按单位计费" value="unit" />
            <el-option label="固定金额" value="fixed" />
          </el-select>
        </el-form-item>
        <el-form-item label="单价(元)" prop="unitPrice">
          <el-input-number 
            v-model="form.unit_price" 
            :min="0" 
            :precision="2" 
            :step="0.1" 
            style="width: 100%;" 
          />
        </el-form-item>
        <el-form-item label="是否启用" prop="isActive">
          <el-switch v-model="form.is_active" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { feeItemApi } from '@/api'

const feeItems = ref([])
const dialogVisible = ref(false)
const loading = ref(false)
const formRef = ref(null)
const isEdit = ref(false)

const form = reactive({
  id: null,
  name: '',
  code: '',
  description: '',
  billing_cycle: 'monthly',
  billing_type: 'area',
  unit_price: 0,
  is_active: true
})

const rules = {
  name: [{ required: true, message: '请输入费用名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入费用编码', trigger: 'blur' }],
  billing_cycle: [{ required: true, message: '请选择计费周期', trigger: 'change' }],
  billing_type: [{ required: true, message: '请选择计费类型', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑费用项目' : '新增费用项目')

const getBillingCycleLabel = (value) => {
  const map = {
    monthly: '月付',
    quarterly: '季付',
    half_yearly: '半年付',
    yearly: '年付',
    one_time: '一次性'
  }
  return map[value] || value
}

const getBillingTypeLabel = (value) => {
  const map = {
    area: '按面积',
    unit: '按单位',
    fixed: '固定'
  }
  return map[value] || value
}

const loadData = async () => {
  try {
    const res = await feeItemApi.getList()
    feeItems.value = res.data
  } catch (error) {
    console.error(error)
  }
}

const resetForm = () => {
  form.id = null
  form.name = ''
  form.code = ''
  form.description = ''
  form.billing_cycle = 'monthly'
  form.billing_type = 'area'
  form.unit_price = 0
  form.is_active = true
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.name = row.name
  form.code = row.code
  form.description = row.description || ''
  form.billing_cycle = row.billing_cycle
  form.billing_type = row.billing_type
  form.unit_price = row.unit_price
  form.is_active = row.is_active
  dialogVisible.value = true
}

const handleToggle = async (row) => {
  const action = row.is_active ? '禁用' : '启用'
  try {
    await ElMessageBox.confirm(`确定要${action}该费用项目吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await feeItemApi.toggle(row.id)
    ElMessage.success(`${action}成功`)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
    }
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    if (isEdit.value) {
      await feeItemApi.update(form.id, {
        name: form.name,
        description: form.description,
        billing_cycle: form.billing_cycle,
        billing_type: form.billing_type,
        unit_price: form.unit_price,
        is_active: form.is_active
      })
      ElMessage.success('更新成功')
    } else {
      await feeItemApi.create({
        name: form.name,
        code: form.code,
        description: form.description,
        billing_cycle: form.billing_cycle,
        billing_type: form.billing_type,
        unit_price: form.unit_price,
        is_active: form.is_active
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.fee-items {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-text {
  color: #f56c6c;
  font-weight: bold;
}
</style>
