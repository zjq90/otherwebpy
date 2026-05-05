<template>
  <div class="points-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>监测点位</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="point_code" label="点位编号" width="120" />
        <el-table-column prop="point_name" label="点位名称" width="150" />
        <el-table-column prop="location" label="位置描述" min-width="180" show-overflow-tooltip />
        <el-table-column prop="monitoring_type" label="监测类型" width="100">
          <template #default="scope">
            <el-tag :type="getTypeTagType(scope.row.monitoring_type)">
              {{ scope.row.monitoring_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="equipment_model" label="设备型号" width="120" />
        <el-table-column prop="installation_date" label="安装日期" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '正常' ? 'success' : 'danger'">
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
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="550px">
      <el-form :model="form" ref="formRef" label-width="100px">
        <el-form-item label="点位编号">
          <el-input v-model="form.point_code" placeholder="请输入点位编号" />
        </el-form-item>
        <el-form-item label="点位名称">
          <el-input v-model="form.point_name" placeholder="请输入点位名称" />
        </el-form-item>
        <el-form-item label="位置描述">
          <el-input v-model="form.location" placeholder="请输入位置描述" />
        </el-form-item>
        <el-form-item label="监测类型">
          <el-select v-model="form.monitoring_type" placeholder="请选择" style="width: 100%">
            <el-option label="粉尘" value="粉尘" />
            <el-option label="噪音" value="噪音" />
            <el-option label="废水" value="废水" />
          </el-select>
        </el-form-item>
        <el-form-item label="设备型号">
          <el-input v-model="form.equipment_model" placeholder="请输入设备型号" />
        </el-form-item>
        <el-form-item label="安装日期">
          <el-date-picker
            v-model="form.installation_date"
            type="date"
            placeholder="选择日期"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" placeholder="请选择" style="width: 100%">
            <el-option label="正常" value="正常" />
            <el-option label="故障" value="故障" />
            <el-option label="维护中" value="维护中" />
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
import { environmentApi } from '@/api'

const loading = ref(false)
const dialogVisible = ref(false)
const dialogTitle = ref('新增监测点位')
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])

const form = reactive({
  id: null,
  point_code: '',
  point_name: '',
  location: '',
  monitoring_type: '',
  equipment_model: '',
  installation_date: '',
  status: '正常'
})

const getTypeTagType = (type) => {
  const map = { '粉尘': 'warning', '噪音': 'info', '废水': 'success' }
  return map[type] || 'info'
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await environmentApi.getMonitoringPoints()
    tableData.value = res.data || []
  } catch (e) {
    tableData.value = []
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增监测点位'
  Object.assign(form, { id: null, point_code: '', point_name: '', location: '', monitoring_type: '', equipment_model: '', installation_date: '', status: '正常' })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑监测点位'
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
