<template>
  <div class="owners">
    <!-- 搜索栏 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="姓名">
          <el-input
            v-model="searchForm.name"
            placeholder="请输入姓名"
            clearable
          />
        </el-form-item>
        <el-form-item label="电话">
          <el-input
            v-model="searchForm.phone"
            placeholder="请输入电话"
            clearable
          />
        </el-form-item>
        <el-form-item label="类型">
          <el-select
            v-model="searchForm.is_owner"
            placeholder="请选择类型"
            clearable
          >
            <el-option label="业主" :value="true" />
            <el-option label="住户" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Plus" @click="handleAdd">新增业主</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card shadow="never">
      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" width="120" />
        <el-table-column prop="id_card" label="身份证号" width="200">
          <template #default="scope">
            {{ scope.row.id_card || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="联系电话" width="140" />
        <el-table-column prop="email" label="邮箱" width="180">
          <template #default="scope">
            {{ scope.row.email || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_owner" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_owner ? 'success' : 'primary'" size="small">
              {{ scope.row.is_owner ? '业主' : '住户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="家庭成员" width="100">
          <template #default="scope">
            <el-tag type="info" size="small">
              {{ scope.row.family_members?.length || 0 }}人
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="车辆" width="80">
          <template #default="scope">
            <el-tag type="info" size="small">
              {{ scope.row.vehicles?.length || 0 }}辆
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="scope">
            <div class="table-actions">
              <el-button type="primary" link :icon="View" @click="handleView(scope.row)">
                详情
              </el-button>
              <el-button type="primary" link :icon="Edit" @click="handleEdit(scope.row)">
                编辑
              </el-button>
              <el-button type="danger" link :icon="Delete" @click="handleDelete(scope.row)">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑业主信息' : '新增业主信息'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身份证号" prop="id_card">
              <el-input v-model="formData.id_card" placeholder="请输入身份证号" maxlength="18" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="联系电话" prop="phone">
              <el-input v-model="formData.phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="电子邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="请输入电子邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="类型" prop="is_owner">
              <el-select v-model="formData.is_owner" placeholder="请选择类型" style="width: 100%">
                <el-option label="业主" :value="true" />
                <el-option label="住户" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="联系地址" prop="address">
          <el-input v-model="formData.address" placeholder="请输入联系地址" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 详情对话框 -->
    <el-dialog
      v-model="detailVisible"
      title="业主/住户详情"
      width="800px"
    >
      <el-descriptions :column="2" border style="margin-bottom: 20px">
        <el-descriptions-item label="ID">{{ currentRow.id }}</el-descriptions-item>
        <el-descriptions-item label="姓名">{{ currentRow.name }}</el-descriptions-item>
        <el-descriptions-item label="身份证号">
          {{ currentRow.id_card || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="联系电话">
          {{ currentRow.phone || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="电子邮箱">
          {{ currentRow.email || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="currentRow.is_owner ? 'success' : 'primary'" size="small">
            {{ currentRow.is_owner ? '业主' : '住户' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="联系地址" :span="2">
          {{ currentRow.address || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ formatDate(currentRow.created_at) }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 家庭成员 -->
      <div class="detail-section">
        <div class="section-header">
          <span class="section-title">家庭成员</span>
          <el-button type="primary" link size="small" :icon="Plus" @click="showFamilyForm = true">
            添加成员
          </el-button>
        </div>
        <el-table
          v-if="currentRow.family_members?.length > 0"
          :data="currentRow.family_members"
          size="small"
          border
        >
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="relation" label="关系" />
          <el-table-column prop="phone" label="联系电话" />
          <el-table-column prop="gender" label="性别" />
          <el-table-column prop="is_emergency_contact" label="紧急联系人">
            <template #default="scope">
              <el-tag v-if="scope.row.is_emergency_contact" type="danger" size="small">是</el-tag>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="scope">
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDeleteFamilyMember(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无家庭成员" />
      </div>

      <!-- 车辆信息 -->
      <div class="detail-section">
        <div class="section-header">
          <span class="section-title">车辆信息</span>
          <el-button type="primary" link size="small" :icon="Plus" @click="showVehicleForm = true">
            添加车辆
          </el-button>
        </div>
        <el-table
          v-if="currentRow.vehicles?.length > 0"
          :data="currentRow.vehicles"
          size="small"
          border
        >
          <el-table-column prop="plate_number" label="车牌号" />
          <el-table-column prop="vehicle_type" label="车辆类型" />
          <el-table-column prop="brand" label="品牌" />
          <el-table-column prop="color" label="颜色" />
          <el-table-column prop="parking_space" label="停车位">
            <template #default="scope">
              {{ scope.row.parking_space || '-' }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="80">
            <template #default="scope">
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDeleteVehicle(scope.row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-else description="暂无车辆信息" />
      </div>

      <!-- 添加家庭成员表单 -->
      <el-dialog
        v-model="showFamilyForm"
        title="添加家庭成员"
        width="500px"
      >
        <el-form
          ref="familyFormRef"
          :model="familyFormData"
          :rules="familyFormRules"
          label-width="100px"
        >
          <el-form-item label="姓名" prop="name">
            <el-input v-model="familyFormData.name" placeholder="请输入姓名" />
          </el-form-item>
          <el-form-item label="关系" prop="relation">
            <el-select v-model="familyFormData.relation" placeholder="请选择关系" style="width: 100%">
              <el-option label="配偶" value="配偶" />
              <el-option label="子女" value="子女" />
              <el-option label="父母" value="父母" />
              <el-option label="兄弟姐妹" value="兄弟姐妹" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="联系电话" prop="phone">
            <el-input v-model="familyFormData.phone" placeholder="请输入联系电话" />
          </el-form-item>
          <el-form-item label="身份证号" prop="id_card">
            <el-input v-model="familyFormData.id_card" placeholder="请输入身份证号" />
          </el-form-item>
          <el-form-item label="性别" prop="gender">
            <el-radio-group v-model="familyFormData.gender">
              <el-radio label="男">男</el-radio>
              <el-radio label="女">女</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="紧急联系人" prop="is_emergency_contact">
            <el-switch v-model="familyFormData.is_emergency_contact" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showFamilyForm = false">取消</el-button>
          <el-button type="primary" :loading="familySubmitLoading" @click="handleAddFamilyMember">
            确定
          </el-button>
        </template>
      </el-dialog>

      <!-- 添加车辆表单 -->
      <el-dialog
        v-model="showVehicleForm"
        title="添加车辆信息"
        width="500px"
      >
        <el-form
          ref="vehicleFormRef"
          :model="vehicleFormData"
          :rules="vehicleFormRules"
          label-width="100px"
        >
          <el-form-item label="车牌号" prop="plate_number">
            <el-input v-model="vehicleFormData.plate_number" placeholder="请输入车牌号" />
          </el-form-item>
          <el-form-item label="车辆类型" prop="vehicle_type">
            <el-select v-model="vehicleFormData.vehicle_type" placeholder="请选择类型" style="width: 100%">
              <el-option label="轿车" value="轿车" />
              <el-option label="SUV" value="SUV" />
              <el-option label="MPV" value="MPV" />
              <el-option label="电动车" value="电动车" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>
          <el-form-item label="品牌" prop="brand">
            <el-input v-model="vehicleFormData.brand" placeholder="请输入品牌" />
          </el-form-item>
          <el-form-item label="颜色" prop="color">
            <el-select v-model="vehicleFormData.color" placeholder="请选择颜色" style="width: 100%">
              <el-option label="白色" value="白色" />
              <el-option label="黑色" value="黑色" />
              <el-option label="灰色" value="灰色" />
              <el-option label="银色" value="银色" />
              <el-option label="红色" value="红色" />
              <el-option label="蓝色" value="蓝色" />
            </el-select>
          </el-form-item>
          <el-form-item label="停车位" prop="parking_space">
            <el-input v-model="vehicleFormData.parking_space" placeholder="请输入停车位编号" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="showVehicleForm = false">取消</el-button>
          <el-button type="primary" :loading="vehicleSubmitLoading" @click="handleAddVehicle">
            确定
          </el-button>
        </template>
      </el-dialog>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ownerApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const currentRow = ref({})
const formRef = ref(null)

const searchForm = reactive({
  name: '',
  phone: '',
  is_owner: null
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const defaultFormData = {
  name: '',
  id_card: '',
  phone: '',
  email: '',
  address: '',
  is_owner: true
}

const formData = reactive({ ...defaultFormData })

// 正则表达式验证规则
const PHONE_PATTERN = /^1[3-9]\d{9}$/
const EMAIL_PATTERN = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
const ID_CARD_PATTERN = /^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/

// 通用验证函数
const validateChineseName = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请输入姓名'))
  } else if (value.trim().length < 2) {
    callback(new Error('姓名至少需要2个字符'))
  } else if (value.trim().length > 50) {
    callback(new Error('姓名不能超过50个字符'))
  } else {
    callback()
  }
}

const validatePhone = (rule, value, callback) => {
  if (value && value.trim() !== '') {
    if (!PHONE_PATTERN.test(value.trim())) {
      callback(new Error('手机号格式不正确，应为11位数字，以1开头'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

const validateEmail = (rule, value, callback) => {
  if (value && value.trim() !== '') {
    if (!EMAIL_PATTERN.test(value.trim())) {
      callback(new Error('邮箱格式不正确'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

const validateIdCard = (rule, value, callback) => {
  if (value && value.trim() !== '') {
    if (value.trim().length !== 18) {
      callback(new Error('身份证号必须是18位'))
    } else if (!ID_CARD_PATTERN.test(value.trim().toUpperCase())) {
      callback(new Error('身份证号格式不正确'))
    } else {
      callback()
    }
  } else {
    callback()
  }
}

const validateAddress = (rule, value, callback) => {
  if (value && value.length > 200) {
    callback(new Error('联系地址不能超过200个字符'))
  } else {
    callback()
  }
}

const validatePlateNumber = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请输入车牌号'))
  } else if (value.trim().length < 7 || value.trim().length > 8) {
    callback(new Error('车牌号长度不正确，应为7-8位'))
  } else {
    callback()
  }
}

const validateGender = (rule, value, callback) => {
  if (value && value !== '' && value !== '男' && value !== '女') {
    callback(new Error('性别只能是"男"或"女"'))
  } else {
    callback()
  }
}

const formRules = {
  name: [
    { required: true, validator: validateChineseName, trigger: 'blur' }
  ],
  id_card: [
    { validator: validateIdCard, trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ],
  email: [
    { validator: validateEmail, trigger: 'blur' }
  ],
  address: [
    { validator: validateAddress, trigger: 'blur' }
  ]
}

// 家庭成员相关
const showFamilyForm = ref(false)
const familyFormRef = ref(null)
const familySubmitLoading = ref(false)
const familyFormData = reactive({
  name: '',
  relation: '',
  phone: '',
  id_card: '',
  gender: '',
  is_emergency_contact: false
})

const familyFormRules = {
  name: [
    { required: true, validator: validateChineseName, trigger: 'blur' }
  ],
  phone: [
    { validator: validatePhone, trigger: 'blur' }
  ],
  id_card: [
    { validator: validateIdCard, trigger: 'blur' }
  ],
  gender: [
    { validator: validateGender, trigger: 'change' }
  ]
}

// 车辆相关
const showVehicleForm = ref(false)
const vehicleFormRef = ref(null)
const vehicleSubmitLoading = ref(false)
const vehicleFormData = reactive({
  plate_number: '',
  vehicle_type: '',
  brand: '',
  model: '',
  color: '',
  parking_space: ''
})

const vehicleFormRules = {
  plate_number: [
    { required: true, validator: validatePlateNumber, trigger: 'blur' }
  ]
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    if (searchForm.name) {
      params.name = searchForm.name
    }
    if (searchForm.phone) {
      params.phone = searchForm.phone
    }
    if (searchForm.is_owner !== null && searchForm.is_owner !== undefined) {
      params.is_owner = searchForm.is_owner
    }
    const res = await ownerApi.getList(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadData()
}

const handleReset = () => {
  searchForm.name = ''
  searchForm.phone = ''
  searchForm.is_owner = null
  pagination.page = 1
  loadData()
}

const resetForm = () => {
  Object.assign(formData, defaultFormData)
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const handleView = (row) => {
  currentRow.value = row
  detailVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  currentRow.value = row
  Object.assign(formData, row)
  dialogVisible.value = true
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除"${row.name}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await ownerApi.delete(row.id)
      ElMessage.success('删除成功')
      loadData()
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
          await ownerApi.update(currentRow.value.id, formData)
          ElMessage.success('更新成功')
        } else {
          await ownerApi.create(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 家庭成员操作
const resetFamilyForm = () => {
  Object.assign(familyFormData, {
    name: '',
    relation: '',
    phone: '',
    id_card: '',
    gender: '',
    is_emergency_contact: false
  })
}

const handleAddFamilyMember = async () => {
  if (!familyFormRef.value) return
  await familyFormRef.value.validate(async (valid) => {
    if (valid) {
      familySubmitLoading.value = true
      try {
        const res = await ownerApi.addFamilyMember(currentRow.value.id, familyFormData)
        if (!currentRow.value.family_members) {
          currentRow.value.family_members = []
        }
        currentRow.value.family_members.push(res)
        ElMessage.success('添加成功')
        showFamilyForm.value = false
        resetFamilyForm()
      } catch (error) {
        console.error('添加失败:', error)
      } finally {
        familySubmitLoading.value = false
      }
    }
  })
}

const handleDeleteFamilyMember = (member) => {
  ElMessageBox.confirm('确定要删除该家庭成员吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await ownerApi.deleteFamilyMember(member.id)
      const index = currentRow.value.family_members.findIndex(item => item.id === member.id)
      if (index > -1) {
        currentRow.value.family_members.splice(index, 1)
      }
      ElMessage.success('删除成功')
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

// 车辆操作
const resetVehicleForm = () => {
  Object.assign(vehicleFormData, {
    plate_number: '',
    vehicle_type: '',
    brand: '',
    model: '',
    color: '',
    parking_space: ''
  })
}

const handleAddVehicle = async () => {
  if (!vehicleFormRef.value) return
  await vehicleFormRef.value.validate(async (valid) => {
    if (valid) {
      vehicleSubmitLoading.value = true
      try {
        const res = await ownerApi.addVehicle(currentRow.value.id, vehicleFormData)
        if (!currentRow.value.vehicles) {
          currentRow.value.vehicles = []
        }
        currentRow.value.vehicles.push(res)
        ElMessage.success('添加成功')
        showVehicleForm.value = false
        resetVehicleForm()
      } catch (error) {
        console.error('添加失败:', error)
      } finally {
        vehicleSubmitLoading.value = false
      }
    }
  })
}

const handleDeleteVehicle = (vehicle) => {
  ElMessageBox.confirm('确定要删除该车辆信息吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await ownerApi.deleteVehicle(vehicle.id)
      const index = currentRow.value.vehicles.findIndex(item => item.id === vehicle.id)
      if (index > -1) {
        currentRow.value.vehicles.splice(index, 1)
      }
      ElMessage.success('删除成功')
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.owners {
  width: 100%;
}

.search-form {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.table-actions {
  display: flex;
  gap: 5px;
}

.detail-section {
  margin-top: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.section-title {
  font-size: 14px;
  font-weight: bold;
  color: #303133;
}
</style>
