<template>
  <div class="properties">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>房产列表</span>
          <div class="header-actions">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索业主姓名/房产编号"
              style="width: 250px; margin-right: 10px;"
              clearable
              @keyup.enter="loadData"
            />
            <el-button type="primary" @click="loadData">
              <el-icon><Search /></el-icon>
              搜索
            </el-button>
            <el-button type="primary" @click="handleAdd" style="margin-left: 10px;">
              <el-icon><Plus /></el-icon>
              新增房产
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="properties" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="property_number" label="房产编号" width="150" />
        <el-table-column prop="building" label="楼栋" width="100" />
        <el-table-column prop="unit" label="单元" width="80" />
        <el-table-column prop="room_number" label="房间号" width="100" />
        <el-table-column prop="area" label="面积(㎡)" width="100" />
        <el-table-column prop="property_type" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="getPropertyTypeTag(scope.row.property_type)">
              {{ scope.row.property_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="owner_name" label="业主姓名" width="100" />
        <el-table-column prop="owner_phone" label="联系电话" width="130" />
        <el-table-column prop="is_occupied" label="入住状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_occupied ? 'success' : 'info'">
              {{ scope.row.is_occupied ? '已入住' : '空置' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleViewBills(scope.row)">
              账单
            </el-button>
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="房产编号" prop="property_number">
              <el-input v-model="form.property_number" placeholder="如：1-1-0101" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="房产类型" prop="property_type">
              <el-select v-model="form.property_type" placeholder="请选择" style="width: 100%;">
                <el-option label="住宅" value="住宅" />
                <el-option label="商铺" value="商铺" />
                <el-option label="车位" value="车位" />
                <el-option label="写字楼" value="写字楼" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="楼栋号" prop="building">
              <el-input v-model="form.building" placeholder="如：1号楼" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="单元号" prop="unit">
              <el-input v-model="form.unit" placeholder="如：1单元" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="房间号" prop="room_number">
              <el-input v-model="form.room_number" placeholder="如：0101" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="建筑面积" prop="area">
              <el-input-number
                v-model="form.area"
                :min="0"
                :precision="2"
                :step="1"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="入住日期" prop="move_in_date">
              <el-date-picker
                v-model="form.move_in_date"
                type="date"
                placeholder="选择日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>业主信息</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="业主姓名" prop="owner_name">
              <el-input v-model="form.owner_name" placeholder="请输入业主姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="owner_phone">
              <el-input v-model="form.owner_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="身份证号">
          <el-input v-model="form.owner_id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入住状态">
              <el-switch v-model="form.is_occupied" active-text="已入住" inactive-text="空置" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch v-model="form.is_active" active-text="启用" inactive-text="禁用" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" :rows="2" placeholder="请输入备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="billsDialogVisible" title="房产账单" width="900px">
      <el-table :data="propertyBills" stripe style="width: 100%">
        <el-table-column prop="bill_number" label="账单编号" width="180" />
        <el-table-column label="费用项目" width="120">
          <template #default="scope">
            {{ scope.row.fee_item_info?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="billing_year" label="年份" width="80">
          <template #default="scope">
            {{ scope.row.billing_year }}年
          </template>
        </el-table-column>
        <el-table-column prop="billing_month" label="月份" width="80">
          <template #default="scope">
            {{ scope.row.billing_month }}月
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="账单金额" width="100">
          <template #default="scope">
            <span class="amount-text">¥{{ scope.row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="paid_amount" label="已付金额" width="100">
          <template #default="scope">
            <span class="paid-text">¥{{ scope.row.paid_amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTag(scope.row.status)">
              {{ getStatusLabel(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="120" />
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { propertyApi, billApi } from '@/api'

const properties = ref([])
const propertyBills = ref([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const billsDialogVisible = ref(false)
const formRef = ref(null)
const isEdit = ref(false)
const searchKeyword = ref('')

const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)

const form = reactive({
  id: null,
  property_number: '',
  building: '',
  unit: '',
  room_number: '',
  area: 0,
  property_type: '住宅',
  owner_name: '',
  owner_phone: '',
  owner_id_card: '',
  is_occupied: true,
  move_in_date: null,
  is_active: true,
  remark: ''
})

const rules = {
  property_number: [{ required: true, message: '请输入房产编号', trigger: 'blur' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑房产' : '新增房产')

const getPropertyTypeTag = (type) => {
  const map = {
    '住宅': 'primary',
    '商铺': 'success',
    '车位': 'warning',
    '写字楼': 'info'
  }
  return map[type] || 'primary'
}

const getStatusTag = (status) => {
  const map = {
    'pending': 'warning',
    'partial': 'info',
    'paid': 'success',
    'overdue': 'danger',
    'cancelled': 'info'
  }
  return map[status] || 'info'
}

const getStatusLabel = (status) => {
  const map = {
    'pending': '待缴费',
    'partial': '部分缴费',
    'paid': '已缴费',
    'overdue': '逾期',
    'cancelled': '已取消'
  }
  return map[status] || status
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchKeyword.value) {
      params.owner_name = searchKeyword.value
    }
    const res = await propertyApi.getList(params)
    properties.value = res.data
    total.value = res.data.length
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = null
  form.property_number = ''
  form.building = ''
  form.unit = ''
  form.room_number = ''
  form.area = 0
  form.property_type = '住宅'
  form.owner_name = ''
  form.owner_phone = ''
  form.owner_id_card = ''
  form.is_occupied = true
  form.move_in_date = null
  form.is_active = true
  form.remark = ''
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  form.id = row.id
  form.property_number = row.property_number
  form.building = row.building || ''
  form.unit = row.unit || ''
  form.room_number = row.room_number || ''
  form.area = row.area
  form.property_type = row.property_type
  form.owner_name = row.owner_name || ''
  form.owner_phone = row.owner_phone || ''
  form.owner_id_card = row.owner_id_card || ''
  form.is_occupied = row.is_occupied
  form.move_in_date = row.move_in_date
  form.is_active = row.is_active
  form.remark = row.remark || ''
  dialogVisible.value = true
}

const handleViewBills = async (row) => {
  try {
    const res = await billApi.getByProperty(row.id)
    propertyBills.value = res.data
    billsDialogVisible.value = true
  } catch (error) {
    console.error(error)
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = { ...form }
    
    if (isEdit.value) {
      await propertyApi.update(form.id, data)
      ElMessage.success('更新成功')
    } else {
      await propertyApi.create(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } catch (error) {
    console.error(error)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.properties {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
}

.amount-text {
  color: #f56c6c;
  font-weight: bold;
}

.paid-text {
  color: #67c23a;
  font-weight: bold;
}
</style>
