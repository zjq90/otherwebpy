<template>
  <div class="equipment-page">
    <div class="page-header">
      <span class="page-title">设备列表</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增设备
      </el-button>
    </div>
    
    <el-card class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="设备编号">
          <el-input v-model="searchForm.keyword" placeholder="请输入设备编号或名称" clearable />
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="searchForm.equipment_type" placeholder="请选择设备类型" clearable>
            <el-option label="搅拌主机" value="搅拌主机" />
            <el-option label="皮带秤" value="皮带秤" />
            <el-option label="空压机" value="空压机" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="运行中" value="运行中" />
            <el-option label="停机" value="停机" />
            <el-option label="维护中" value="维护中" />
            <el-option label="故障" value="故障" />
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
        <el-table-column prop="equipment_code" label="设备编号" width="120" />
        <el-table-column prop="name" label="设备名称" width="150" />
        <el-table-column prop="equipment_type" label="设备类型" width="120" />
        <el-table-column prop="model" label="设备型号" width="120" />
        <el-table-column prop="manufacturer" label="生产厂家" width="120" />
        <el-table-column prop="location" label="安装位置" min-width="150" show-overflow-tooltip />
        <el-table-column prop="status" label="设备状态" width="100">
          <template #default="scope">
            <el-tag :class="getStatusClass(scope.row.status)" size="small">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="responsible_person" label="负责人" width="100" />
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
            <el-form-item label="设备编号" prop="equipment_code">
              <el-input v-model="form.equipment_code" placeholder="请输入设备编号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入设备名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="设备类型" prop="equipment_type">
              <el-select v-model="form.equipment_type" placeholder="请选择设备类型" style="width: 100%;">
                <el-option label="搅拌主机" value="搅拌主机" />
                <el-option label="皮带秤" value="皮带秤" />
                <el-option label="空压机" value="空压机" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备型号" prop="model">
              <el-input v-model="form.model" placeholder="请输入设备型号" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="生产厂家" prop="manufacturer">
              <el-input v-model="form.manufacturer" placeholder="请输入生产厂家" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备规格" prop="specification">
              <el-input v-model="form.specification" placeholder="请输入设备规格" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="出厂日期" prop="production_date">
              <el-date-picker
                v-model="form.production_date"
                type="date"
                placeholder="请选择出厂日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="投入使用日期" prop="installation_date">
              <el-date-picker
                v-model="form.installation_date"
                type="date"
                placeholder="请选择投入使用日期"
                value-format="YYYY-MM-DD"
                style="width: 100%;"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="安装位置" prop="location">
              <el-input v-model="form.location" placeholder="请输入安装位置" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="设备状态" prop="status">
              <el-select v-model="form.status" placeholder="请选择设备状态" style="width: 100%;">
                <el-option label="运行中" value="运行中" />
                <el-option label="停机" value="停机" />
                <el-option label="维护中" value="维护中" />
                <el-option label="故障" value="故障" />
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
            <el-form-item label="联系电话" prop="contact_phone">
              <el-input v-model="form.contact_phone" placeholder="请输入联系电话" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
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
      title="设备详情"
      width="700px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="设备编号">{{ detailForm.equipment_code }}</el-descriptions-item>
        <el-descriptions-item label="设备名称">{{ detailForm.name }}</el-descriptions-item>
        <el-descriptions-item label="设备类型">{{ detailForm.equipment_type }}</el-descriptions-item>
        <el-descriptions-item label="设备型号">{{ detailForm.model }}</el-descriptions-item>
        <el-descriptions-item label="生产厂家">{{ detailForm.manufacturer }}</el-descriptions-item>
        <el-descriptions-item label="设备规格">{{ detailForm.specification }}</el-descriptions-item>
        <el-descriptions-item label="出厂日期">{{ detailForm.production_date }}</el-descriptions-item>
        <el-descriptions-item label="投入使用日期">{{ detailForm.installation_date }}</el-descriptions-item>
        <el-descriptions-item label="安装位置">{{ detailForm.location }}</el-descriptions-item>
        <el-descriptions-item label="设备状态">
          <el-tag :class="getStatusClass(detailForm.status)" size="small">
            {{ detailForm.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="负责人">{{ detailForm.responsible_person }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ detailForm.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">{{ detailForm.description }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Search, Refresh, View, Edit, Delete
} from '@element-plus/icons-vue'
import {
  getEquipmentList, getEquipment, createEquipment, updateEquipment, deleteEquipment
} from '@/api/equipment'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  keyword: '',
  equipment_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])

const defaultForm = {
  equipment_code: '',
  name: '',
  equipment_type: '',
  model: '',
  specification: '',
  manufacturer: '',
  production_date: '',
  installation_date: '',
  location: '',
  status: '运行中',
  responsible_person: '',
  contact_phone: '',
  description: ''
}

const form = reactive({ ...defaultForm })
const detailForm = reactive({ ...defaultForm })

const rules = {
  equipment_code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  equipment_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }]
}

const dialogTitle = computed(() => isEdit.value ? '编辑设备' : '新增设备')

const getStatusClass = (status) => {
  const classMap = {
    '运行中': 'status-tag running',
    '停机': 'status-tag stopped',
    '维护中': 'status-tag maintenance',
    '故障': 'status-tag fault'
  }
  return classMap[status] || 'status-tag normal'
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...searchForm
    }
    if (!params.keyword) delete params.keyword
    if (!params.equipment_type) delete params.equipment_type
    if (!params.status) delete params.status
    
    const res = await getEquipmentList(params)
    tableData.value = res
    // 暂时使用假数据长度，实际需要后端返回total
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
    keyword: '',
    equipment_type: '',
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
    `确定要删除设备 "${row.name}" 吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await deleteEquipment(row.id)
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
          await updateEquipment(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await createEquipment(form)
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
