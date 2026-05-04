<template>
  <div class="properties">
    <!-- 搜索栏 -->
    <el-card shadow="never" style="margin-bottom: 20px">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目">
          <el-select
            v-model="searchForm.project_id"
            placeholder="请选择项目"
            clearable
            style="width: 200px"
          >
            <el-option
              v-for="item in projectList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="楼栋号">
          <el-input
            v-model="searchForm.building_number"
            placeholder="请输入楼栋号"
            clearable
          />
        </el-form-item>
        <el-form-item label="房间号">
          <el-input
            v-model="searchForm.room_number"
            placeholder="请输入房间号"
            clearable
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select
            v-model="searchForm.status"
            placeholder="请选择状态"
            clearable
          >
            <el-option label="空置" value="vacant" />
            <el-option label="出租" value="rented" />
            <el-option label="自住" value="occupied" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
          <el-button type="success" :icon="Plus" @click="handleAdd">新增房产</el-button>
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
        <el-table-column prop="building_number" label="楼栋号" width="100" />
        <el-table-column prop="room_number" label="房间号" width="100" />
        <el-table-column prop="floor" label="楼层" width="80">
          <template #default="scope">
            {{ scope.row.floor }} / {{ scope.row.total_floors }}
          </template>
        </el-table-column>
        <el-table-column prop="house_type" label="户型" width="120" />
        <el-table-column prop="area" label="面积(㎡)" width="100">
          <template #default="scope">
            {{ scope.row.area }}
          </template>
        </el-table-column>
        <el-table-column prop="property_type" label="产权性质" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="orientation" label="朝向" width="80" />
        <el-table-column prop="decoration" label="装修" width="80" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <div class="table-actions">
              <el-button type="primary" link :icon="View" @click="handleView(scope.row)">
                查看
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
      :title="isEdit ? '编辑房产信息' : '新增房产信息'"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="所属项目" prop="project_id">
          <el-select
            v-model="formData.project_id"
            placeholder="请选择项目"
            style="width: 100%"
          >
            <el-option
              v-for="item in projectList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="楼栋号" prop="building_number">
              <el-input v-model="formData.building_number" placeholder="楼栋号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="房间号" prop="room_number">
              <el-input v-model="formData.room_number" placeholder="房间号" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="户型" prop="house_type">
              <el-select v-model="formData.house_type" placeholder="选择户型" style="width: 100%">
                <el-option label="一室一厅" value="一室一厅" />
                <el-option label="两室一厅" value="两室一厅" />
                <el-option label="两室两厅" value="两室两厅" />
                <el-option label="三室一厅" value="三室一厅" />
                <el-option label="三室两厅" value="三室两厅" />
                <el-option label="四室两厅" value="四室两厅" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="当前楼层" prop="floor">
              <el-input-number v-model="formData.floor" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="总楼层" prop="total_floors">
              <el-input-number v-model="formData.total_floors" :min="1" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="建筑面积" prop="area">
              <el-input-number
                v-model="formData.area"
                :min="0"
                :precision="2"
                style="width: 100%"
              >
                <template #suffix>㎡</template>
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="产权性质" prop="property_type">
              <el-select v-model="formData.property_type" placeholder="选择产权" style="width: 100%">
                <el-option label="商品房" value="商品房" />
                <el-option label="经济适用房" value="经济适用房" />
                <el-option label="回迁房" value="回迁房" />
                <el-option label="公房" value="公房" />
                <el-option label="私房" value="私房" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="状态" prop="status">
              <el-select v-model="formData.status" placeholder="选择状态" style="width: 100%">
                <el-option label="空置" value="vacant" />
                <el-option label="出租" value="rented" />
                <el-option label="自住" value="occupied" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="朝向" prop="orientation">
              <el-select v-model="formData.orientation" placeholder="选择朝向" style="width: 100%">
                <el-option label="南北通透" value="南北通透" />
                <el-option label="朝南" value="朝南" />
                <el-option label="朝北" value="朝北" />
                <el-option label="朝东" value="朝东" />
                <el-option label="朝西" value="朝西" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="装修情况" prop="decoration">
              <el-select v-model="formData.decoration" placeholder="选择装修" style="width: 100%">
                <el-option label="毛坯" value="毛坯" />
                <el-option label="简装" value="简装" />
                <el-option label="中装" value="中装" />
                <el-option label="精装" value="精装" />
                <el-option label="豪装" value="豪装" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="使用面积" prop="usable_area">
              <el-input-number
                v-model="formData.usable_area"
                :min="0"
                :precision="2"
                style="width: 100%"
              >
                <template #suffix>㎡</template>
              </el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注" prop="remarks">
          <el-input
            v-model="formData.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
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
      title="房产详情"
      width="600px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ currentRow.id }}</el-descriptions-item>
        <el-descriptions-item label="房间号">
          {{ currentRow.building_number }}栋 {{ currentRow.room_number }}
        </el-descriptions-item>
        <el-descriptions-item label="楼层">
          {{ currentRow.floor }} / {{ currentRow.total_floors }}层
        </el-descriptions-item>
        <el-descriptions-item label="户型">{{ currentRow.house_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="建筑面积">{{ currentRow.area || '-' }} ㎡</el-descriptions-item>
        <el-descriptions-item label="使用面积">{{ currentRow.usable_area || '-' }} ㎡</el-descriptions-item>
        <el-descriptions-item label="产权性质">{{ currentRow.property_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentRow.status)" size="small">
            {{ getStatusText(currentRow.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="朝向">{{ currentRow.orientation || '-' }}</el-descriptions-item>
        <el-descriptions-item label="装修">{{ currentRow.decoration || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">
          {{ formatDate(currentRow.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="备注" :span="2">
          {{ currentRow.remarks || '-' }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { propertyApi, propertyProjectApi } from '@/api'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const projectList = ref([])
const dialogVisible = ref(false)
const detailVisible = ref(false)
const isEdit = ref(false)
const currentRow = ref({})
const formRef = ref(null)

const searchForm = reactive({
  project_id: null,
  building_number: '',
  room_number: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0
})

const defaultFormData = {
  project_id: null,
  building_number: '',
  room_number: '',
  floor: 1,
  total_floors: 1,
  house_type: '',
  area: 0,
  usable_area: 0,
  property_type: '',
  status: 'vacant',
  orientation: '',
  decoration: '',
  remarks: ''
}

const formData = reactive({ ...defaultFormData })

const validateBuildingNumber = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请输入楼栋号'))
  } else if (value.trim().length > 20) {
    callback(new Error('楼栋号不能超过20个字符'))
  } else {
    callback()
  }
}

const validateRoomNumber = (rule, value, callback) => {
  if (!value || value.trim() === '') {
    callback(new Error('请输入房间号'))
  } else if (value.trim().length > 20) {
    callback(new Error('房间号不能超过20个字符'))
  } else {
    callback()
  }
}

const validateArea = (rule, value, callback) => {
  if (value !== null && value !== undefined && (value < 0 || value > 100000)) {
    callback(new Error('面积必须在0-100000平方米之间'))
  } else {
    callback()
  }
}

const validateUsableArea = (rule, value, callback) => {
  if (value !== null && value !== undefined && (value < 0 || value > 100000)) {
    callback(new Error('使用面积必须在0-100000平方米之间'))
  } else if (value !== null && value !== undefined && formData.area !== null && formData.area !== undefined && value > formData.area) {
    callback(new Error('使用面积不能大于建筑面积'))
  } else {
    callback()
  }
}

const validateFloor = (rule, value, callback) => {
  if (value !== null && value !== undefined && (value < 1 || value > 500)) {
    callback(new Error('楼层必须在1-500层之间'))
  } else {
    callback()
  }
}

const validateRemarks = (rule, value, callback) => {
  if (value && value.length > 500) {
    callback(new Error('备注不能超过500个字符'))
  } else {
    callback()
  }
}

const formRules = {
  project_id: [
    { required: true, message: '请选择所属项目', trigger: 'change' }
  ],
  building_number: [
    { required: true, validator: validateBuildingNumber, trigger: 'blur' }
  ],
  room_number: [
    { required: true, validator: validateRoomNumber, trigger: 'blur' }
  ],
  floor: [
    { validator: validateFloor, trigger: 'blur' }
  ],
  total_floors: [
    { validator: validateFloor, trigger: 'blur' }
  ],
  area: [
    { validator: validateArea, trigger: 'blur' }
  ],
  usable_area: [
    { validator: validateUsableArea, trigger: 'blur' }
  ],
  remarks: [
    { validator: validateRemarks, trigger: 'blur' }
  ]
}

const statusMap = {
  vacant: { text: '空置', type: 'warning' },
  rented: { text: '出租', type: 'primary' },
  occupied: { text: '自住', type: 'success' }
}

const getStatusText = (status) => statusMap[status]?.text || status
const getStatusType = (status) => statusMap[status]?.type || 'info'

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const loadProjectList = async () => {
  try {
    const res = await propertyProjectApi.getList({ limit: 1000 })
    projectList.value = res.items
  } catch (error) {
    console.error('加载项目列表失败:', error)
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize
    }
    if (searchForm.project_id) {
      params.project_id = searchForm.project_id
    }
    if (searchForm.building_number) {
      params.building_number = searchForm.building_number
    }
    if (searchForm.room_number) {
      params.room_number = searchForm.room_number
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    const res = await propertyApi.getList(params)
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
  searchForm.project_id = null
  searchForm.building_number = ''
  searchForm.room_number = ''
  searchForm.status = ''
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
  ElMessageBox.confirm(`确定要删除房产"${row.building_number}栋${row.room_number}"吗？`, '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      await propertyApi.delete(row.id)
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
          await propertyApi.update(currentRow.value.id, formData)
          ElMessage.success('更新成功')
        } else {
          await propertyApi.create(formData)
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

onMounted(() => {
  loadProjectList()
  loadData()
})
</script>

<style scoped>
.properties {
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
</style>
