<template>
  <!-- 储物柜管理页面 -->
  <div class="locker-list">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="30" color="#409EFF"><Box /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total }}</div>
              <div class="stat-label">储物柜总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="30" color="#67C23A"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.available }}</div>
              <div class="stat-label">空闲</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="30" color="#E6A23C"><Clock /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.occupied }}</div>
              <div class="stat-label">使用中</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="30" color="#F56C6C"><Warning /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.maintenance }}</div>
              <div class="stat-label">故障维修</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="储物柜编号">
          <el-input
            v-model="searchForm.locker_no"
            placeholder="请输入储物柜编号"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="空闲" value="available" />
            <el-option label="使用中" value="occupied" />
            <el-option label="故障维修" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.locker_type" placeholder="全部类型" clearable style="width: 120px">
            <el-option label="小型" value="small" />
            <el-option label="中型" value="medium" />
            <el-option label="大型" value="large" />
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
      
      <el-divider />
      
      <div class="action-bar">
        <el-button type="primary" @click="handleAdd">
          <el-icon><Plus /></el-icon>
          新增储物柜
        </el-button>
        <el-button type="success" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>
    
    <!-- 储物柜列表 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
      >
        <el-table-column prop="locker_no" label="储物柜编号" width="120">
          <template #default="{ row }">
            <span class="locker-no">{{ row.locker_no }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="location" label="位置" width="150" />
        <el-table-column prop="locker_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.locker_type)">
              {{ getTypeText(row.locker_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" effect="light">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status_updated_at" label="状态更新时间" width="180">
          <template #default="{ row }">
            {{ row.status_updated_at ? formatTime(row.status_updated_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="remarks" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              plain
              @click="handleEdit(row)"
            >
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'available'"
              type="success"
              size="small"
              plain
              @click="handleAssign(row)"
            >
              <el-icon><Share /></el-icon>
              分配
            </el-button>
            <el-button
              v-if="row.status === 'occupied'"
              type="warning"
              size="small"
              plain
              @click="handleReturn(row)"
            >
              <el-icon><Back /></el-icon>
              归还
            </el-button>
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
    
    <!-- 新增/编辑储物柜弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      destroy-on-close
    >
      <el-form
        ref="lockerFormRef"
        :model="lockerForm"
        :rules="lockerRules"
        label-width="100px"
      >
        <el-form-item label="储物柜编号" prop="locker_no">
          <el-input v-model="lockerForm.locker_no" placeholder="如：A001、B023" />
        </el-form-item>
        <el-form-item label="位置">
          <el-input v-model="lockerForm.location" placeholder="如：一楼A区" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="lockerForm.locker_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="小型" value="small" />
            <el-option label="中型" value="medium" />
            <el-option label="大型" value="large" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="lockerForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option label="空闲" value="available" />
            <el-option label="使用中" value="occupied" />
            <el-option label="故障维修" value="maintenance" />
          </el-select>
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="lockerForm.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 分配储物柜弹窗 -->
    <el-dialog
      v-model="assignDialogVisible"
      title="分配储物柜"
      width="450px"
    >
      <el-form label-width="100px">
        <el-form-item label="储物柜编号">
          <el-input :value="currentLocker?.locker_no" disabled />
        </el-form-item>
        <el-form-item label="位置">
          <el-input :value="currentLocker?.location" disabled />
        </el-form-item>
        <el-divider />
        <el-form-item label="选择会员">
          <el-select
            v-model="assignForm.member_id"
            placeholder="请选择会员"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="member in testMembers"
              :key="member.id"
              :label="`${member.name} (${member.member_no})`"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="分配方式">
          <el-radio-group v-model="assignForm.assign_type">
            <el-radio label="auto">自动分配</el-radio>
            <el-radio label="manual">手动选择</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="assignForm.password" placeholder="可选，自动生成" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleAssignSubmit" :loading="assignLoading">
          确认分配
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 统计数据
const stats = reactive({
  total: 0,
  available: 0,
  occupied: 0,
  maintenance: 0
})

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  locker_no: '',
  status: '',
  locker_type: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 弹窗相关
const dialogVisible = ref(false)
const dialogTitle = ref('新增储物柜')
const isEdit = ref(false)
const submitLoading = ref(false)
const lockerFormRef = ref<FormInstance>()

// 储物柜表单
const lockerForm = reactive({
  locker_no: '',
  location: '',
  locker_type: 'medium',
  status: 'available',
  remarks: ''
})

// 表单验证规则
const lockerRules: FormRules = {
  locker_no: [{ required: true, message: '请输入储物柜编号', trigger: 'blur' }]
}

// 分配相关
const assignDialogVisible = ref(false)
const currentLocker = ref(null)
const testMembers = ref([])
const assignLoading = ref(false)
const assignForm = reactive({
  member_id: null,
  locker_id: null,
  assign_type: 'manual',
  password: ''
})

// 辅助函数
const getStatusTagType = (status) => {
  const typeMap = {
    available: 'success',
    occupied: 'warning',
    maintenance: 'danger'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const textMap = {
    available: '空闲',
    occupied: '使用中',
    maintenance: '故障维修'
  }
  return textMap[status] || status
}

const getTypeTagType = (type) => {
  const typeMap = {
    small: 'info',
    medium: 'primary',
    large: 'warning'
  }
  return typeMap[type] || 'info'
}

const getTypeText = (type) => {
  const textMap = {
    small: '小型',
    medium: '中型',
    large: '大型'
  }
  return textMap[type] || type
}

const formatTime = (time) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await api.getLockerStats()
    if (res.success) {
      const data = res.data
      stats.total = data.by_status?.available + data.by_status?.occupied + data.by_status?.maintenance || 0
      stats.available = data.by_status?.available || 0
      stats.occupied = data.by_status?.occupied || 0
      stats.maintenance = data.by_status?.maintenance || 0
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 加载列表数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await api.getLockers({
      page: pagination.page,
      page_size: pagination.pageSize,
      locker_no: searchForm.locker_no || undefined,
      status: searchForm.status || undefined,
      locker_type: searchForm.locker_type || undefined
    })
    
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 加载测试会员
const loadTestMembers = async () => {
  try {
    const res = await api.getQuickTestData()
    if (res.success) {
      testMembers.value = res.data.active_members || []
    }
  } catch (error) {
    console.error('加载测试数据失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
  loadStats()
}

// 重置
const handleReset = () => {
  searchForm.locker_no = ''
  searchForm.status = ''
  searchForm.locker_type = ''
  pagination.page = 1
  loadData()
  loadStats()
}

// 分页变更
const handleSizeChange = (size) => {
  pagination.pageSize = size
  loadData()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  loadData()
}

// 新增储物柜
const handleAdd = () => {
  dialogTitle.value = '新增储物柜'
  isEdit.value = false
  Object.assign(lockerForm, {
    locker_no: '',
    location: '',
    locker_type: 'medium',
    status: 'available',
    remarks: ''
  })
  dialogVisible.value = true
}

// 编辑储物柜
const handleEdit = (row) => {
  dialogTitle.value = '编辑储物柜'
  isEdit.value = true
  currentLocker.value = row
  Object.assign(lockerForm, {
    locker_no: row.locker_no,
    location: row.location,
    locker_type: row.locker_type,
    status: row.status,
    remarks: row.remarks || ''
  })
  dialogVisible.value = true
}

// 提交表单
const handleSubmit = async () => {
  if (!lockerFormRef.value) return
  
  await lockerFormRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (isEdit.value) {
          await api.updateLocker(currentLocker.value.id, lockerForm)
          ElMessage.success('更新成功')
        } else {
          await api.createLocker(lockerForm)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        loadData()
        loadStats()
      } catch (error) {
        console.error('提交失败:', error)
      } finally {
        submitLoading.value = false
      }
    }
  })
}

// 分配储物柜
const handleAssign = (row) => {
  currentLocker.value = row
  assignForm.locker_id = row.id
  assignForm.member_id = null
  assignForm.assign_type = 'manual'
  assignForm.password = ''
  assignDialogVisible.value = true
}

// 提交分配
const handleAssignSubmit = async () => {
  if (!assignForm.member_id) {
    ElMessage.warning('请选择会员')
    return
  }
  
  assignLoading.value = true
  try {
    const res = await api.assignLocker(assignForm)
    if (res.success) {
      ElMessage.success('分配成功')
      assignDialogVisible.value = false
      loadData()
      loadStats()
    } else {
      ElMessage.error(res.message || '分配失败')
    }
  } catch (error) {
    console.error('分配失败:', error)
    ElMessage.error('分配失败')
  } finally {
    assignLoading.value = false
  }
}

// 归还储物柜
const handleReturn = async (row) => {
  // 先获取该储物柜的使用记录
  try {
    const res = await api.getActiveUsages({ page: 1, page_size: 100 })
    
    // 找到对应的使用记录
    const usage = res.items?.find(item => item.locker_id === row.id)
    
    if (!usage) {
      ElMessage.warning('未找到该储物柜的使用记录')
      return
    }
    
    ElMessageBox.confirm(
      `确定要归还储物柜「${row.locker_no}」吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    ).then(async () => {
      try {
        await api.returnLocker({
          member_id: usage.member_id,
          locker_id: row.id
        })
        ElMessage.success('归还成功')
        loadData()
        loadStats()
      } catch (error) {
        console.error('归还失败:', error)
        ElMessage.error('归还失败')
      }
    }).catch(() => {})
  } catch (error) {
    console.error('查询使用记录失败:', error)
    ElMessage.error('查询使用记录失败')
  }
}

onMounted(() => {
  loadStats()
  loadData()
  loadTestMembers()
})
</script>

<style scoped>
.locker-list {
  padding: 0;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 搜索卡片 */
.search-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  gap: 10px;
}

/* 表格卡片 */
.table-card {
  padding: 0;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
}

.locker-no {
  font-weight: bold;
  color: #409EFF;
}
</style>
