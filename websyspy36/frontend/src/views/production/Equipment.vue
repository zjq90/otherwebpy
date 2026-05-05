<template>
  <div class="equipment-page">
    <el-card class="card-container">
      <template #header>
        <div class="card-header">
          <span>设备管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="设备类型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable>
            <el-option label="搅拌机" value="搅拌机" />
            <el-option label="运输车" value="运输车" />
            <el-option label="泵车" value="泵车" />
            <el-option label="装载机" value="装载机" />
          </el-select>
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
        <el-table-column prop="equipment_code" label="设备编号" width="120" />
        <el-table-column prop="equipment_name" label="设备名称" width="150" />
        <el-table-column prop="equipment_type" label="设备类型" width="100" />
        <el-table-column prop="specification" label="规格型号" width="120" />
        <el-table-column prop="max_capacity" label="最大产能" width="100">
          <template #default="scope">
            {{ scope.row.max_capacity?.toFixed(2) || 0 }} m³
          </template>
        </el-table-column>
        <el-table-column prop="manufacturer" label="制造商" width="120" />
        <el-table-column prop="purchase_date" label="购买日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '正常' ? 'success' : 'warning'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
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
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="设备编号" prop="equipment_code">
          <el-input v-model="form.equipment_code" placeholder="请输入设备编号" />
        </el-form-item>
        <el-form-item label="设备名称" prop="equipment_name">
          <el-input v-model="form.equipment_name" placeholder="请输入设备名称" />
        </el-form-item>
        <el-form-item label="设备类型" prop="equipment_type">
          <el-select v-model="form.equipment_type" placeholder="请选择设备类型" style="width: 100%">
            <el-option label="搅拌机" value="搅拌机" />
            <el-option label="运输车" value="运输车" />
            <el-option label="泵车" value="泵车" />
            <el-option label="装载机" value="装载机" />
          </el-select>
        </el-form-item>
        <el-form-item label="规格型号" prop="specification">
          <el-input v-model="form.specification" placeholder="请输入规格型号" />
        </el-form-item>
        <el-form-item label="最大产能 (m³)" prop="max_capacity">
          <el-input-number v-model="form.max_capacity" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="制造商" prop="manufacturer">
          <el-input v-model="form.manufacturer" placeholder="请输入制造商" />
        </el-form-item>
        <el-form-item label="购买日期" prop="purchase_date">
          <el-date-picker
            v-model="form.purchase_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="form.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="正常" value="正常" />
            <el-option label="维修中" value="维修中" />
            <el-option label="停用" value="停用" />
          </el-select>
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
const dialogTitle = ref('新增设备')
const isEdit = ref(false)

const formRef = ref(null)
const tableData = ref([])

const searchForm = reactive({
  type: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const form = reactive({
  id: null,
  equipment_code: '',
  equipment_name: '',
  equipment_type: '',
  specification: '',
  max_capacity: 0,
  manufacturer: '',
  purchase_date: '',
  status: '正常'
})

const rules = {
  equipment_code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  equipment_name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  equipment_type: [{ required: true, message: '请选择设备类型', trigger: 'change' }]
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await productionApi.getEquipment()
    tableData.value = res.data || []
    pagination.total = tableData.value.length
  } catch (e) {
    console.error('加载数据失败:', e)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadData()
}

const handleReset = () => {
  searchForm.type = ''
  loadData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增设备'
  Object.assign(form, {
    id: null,
    equipment_code: '',
    equipment_name: '',
    equipment_type: '',
    specification: '',
    max_capacity: 0,
    manufacturer: '',
    purchase_date: '',
    status: '正常'
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑设备'
  Object.assign(form, { ...row })
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该设备吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await productionApi.deleteEquipment(row.id)
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
          await productionApi.updateEquipment(form.id, form)
          ElMessage.success('更新成功')
        } else {
          await productionApi.createEquipment(form)
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
}

const handleCurrentChange = (page) => {
  pagination.page = page
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
