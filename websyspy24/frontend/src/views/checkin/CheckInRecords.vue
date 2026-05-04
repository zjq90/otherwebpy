<template>
  <!-- 签到记录页面 -->
  <div class="checkin-records">
    <!-- 搜索和操作栏 -->
    <el-card class="search-card">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="会员ID">
          <el-input
            v-model="searchForm.member_id"
            placeholder="请输入会员ID"
            clearable
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="签到方式">
          <el-select v-model="searchForm.check_in_type" placeholder="全部方式" clearable style="width: 120px">
            <el-option label="刷卡" value="card" />
            <el-option label="扫码" value="qr" />
            <el-option label="人脸识别" value="face" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable style="width: 120px">
            <el-option label="成功" value="success" />
            <el-option label="失败" value="failed" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="searchForm.start_date"
            type="date"
            placeholder="开始日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="searchForm.end_date"
            type="date"
            placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 150px"
          />
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
        <el-button type="success" @click="loadData">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
    </el-card>
    
    <!-- 签到记录表格 -->
    <el-card class="table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="member_name" label="会员姓名" width="100">
          <template #default="{ row }">
            {{ row.member_name || '未知' }}
          </template>
        </el-table-column>
        <el-table-column prop="member_no" label="会员编号" width="120">
          <template #default="{ row }">
            {{ row.member_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="check_in_type" label="签到方式" width="120">
          <template #default="{ row }">
            <el-tag :type="getCheckInType(row.check_in_type)" effect="light">
              {{ getCheckInTypeName(row.check_in_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="device_no" label="设备编号" width="120">
          <template #default="{ row }">
            {{ row.device_no || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="check_in_time" label="签到时间" width="160">
          <template #default="{ row }">
            {{ row.check_in_time ? formatDateTime(row.check_in_time) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'success' ? 'success' : 'danger'" effect="light">
              {{ row.status === 'success' ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fail_reason" label="失败原因" min-width="200">
          <template #default="{ row }">
            <span v-if="row.status === 'failed'" class="text-danger">
              {{ row.fail_reason || '未知原因' }}
            </span>
            <span v-else class="text-success">-</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" plain @click="handleView(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 分页 -->
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
    
    <!-- 详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="签到详情"
      width="500px"
    >
      <el-descriptions :column="1" border>
        <el-descriptions-item label="签到记录ID">
          {{ currentCheckIn?.id }}
        </el-descriptions-item>
        <el-descriptions-item label="会员姓名">
          {{ currentCheckIn?.member_name || '未知' }}
        </el-descriptions-item>
        <el-descriptions-item label="会员编号">
          {{ currentCheckIn?.member_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="签到方式">
          <el-tag :type="getCheckInType(currentCheckIn?.check_in_type)">
            {{ getCheckInTypeName(currentCheckIn?.check_in_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="设备编号">
          {{ currentCheckIn?.device_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="签到时间">
          {{ currentCheckIn?.check_in_time ? formatDateTime(currentCheckIn.check_in_time) : '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="签到状态">
          <el-tag :type="currentCheckIn?.status === 'success' ? 'success' : 'danger'">
            {{ currentCheckIn?.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="失败原因" v-if="currentCheckIn?.status === 'failed'">
          <span class="text-danger">{{ currentCheckIn?.fail_reason || '未知原因' }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="验证详情" v-if="currentCheckIn?.verification_details">
          <pre>{{ JSON.stringify(currentCheckIn.verification_details, null, 2) }}</pre>
        </el-descriptions-item>
      </el-descriptions>
      
      <template #footer>
        <el-button @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 表格数据
const tableData = ref([])
const loading = ref(false)

// 搜索表单
const searchForm = reactive({
  member_id: '',
  check_in_type: '',
  status: '',
  start_date: '',
  end_date: ''
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

// 详情相关
const detailDialogVisible = ref(false)
const currentCheckIn = ref(null)

// 获取签到方式类型
const getCheckInType = (type) => {
  const map = {
    card: 'primary',
    qr: 'success',
    face: 'warning'
  }
  return map[type] || 'info'
}

const getCheckInTypeName = (type) => {
  const map = {
    card: '刷卡',
    qr: '扫码',
    face: '人脸识别'
  }
  return map[type] || type
}

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      member_id: searchForm.member_id ? parseInt(searchForm.member_id) : undefined,
      check_in_type: searchForm.check_in_type || undefined,
      status: searchForm.status || undefined,
      start_date: searchForm.start_date || undefined,
      end_date: searchForm.end_date || undefined
    }
    
    const res = await api.getCheckins(params)
    
    tableData.value = res.items || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  searchForm.member_id = ''
  searchForm.check_in_type = ''
  searchForm.status = ''
  searchForm.start_date = ''
  searchForm.end_date = ''
  pagination.page = 1
  loadData()
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

// 查看详情
const handleView = (row) => {
  currentCheckIn.value = row
  detailDialogVisible.value = true
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.checkin-records {
  padding: 0;
}

.search-card {
  margin-bottom: 20px;
}

.action-bar {
  display: flex;
  gap: 10px;
}

.table-card {
  padding: 0;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  padding: 20px;
}

.text-danger {
  color: #F56C6C;
}

.text-success {
  color: #67C23A;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 12px;
  color: #606266;
}
</style>
