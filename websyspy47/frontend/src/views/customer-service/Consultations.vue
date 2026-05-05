<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">咨询记录</span>
      <span v-if="staffFilter" class="filter-info">
        筛选：客服人员 <el-tag type="primary">{{ staffFilter }}</el-tag>
        <el-button link size="small" @click="clearFilter">清除筛选</el-button>
      </span>
    </div>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="咨询类型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable>
            <el-option label="产品咨询" :value="0" />
            <el-option label="订单问题" :value="1" />
            <el-option label="积分兑换" :value="2" />
            <el-option label="投诉建议" :value="3" />
            <el-option label="其他" :value="4" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待处理" :value="0" />
            <el-option label="处理中" :value="1" />
            <el-option label="已解决" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item label="用户">
          <el-input v-model="searchForm.user_name" placeholder="用户名/手机号" clearable />
        </el-form-item>
        <el-form-item label="客服">
          <el-select v-model="searchForm.staff_id" placeholder="全部" clearable style="width: 120px">
            <el-option
              v-for="item in staffList"
              :key="item.id"
              :label="item.real_name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="创建时间">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 240px"
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
    </el-card>
    
    <el-card class="table-container">
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="user_name" label="用户" />
        <el-table-column prop="user_phone" label="用户电话" width="120" />
        <el-table-column prop="staff_name" label="客服人员" width="100">
          <template #default="{ row }">
            {{ row.staff_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="type" label="咨询类型" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="typeTagMap[row.type]">
              {{ typeLabelMap[row.type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="subject" label="咨询主题" min-width="150" show-overflow-tooltip />
        <el-table-column prop="message_count" label="消息数" align="center" width="80">
          <template #default="{ row }">
            <el-tag type="info">{{ row.message_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="评分" align="center" width="100">
          <template #default="{ row }">
            <el-rate 
              v-if="row.rating"
              v-model="row.rating" 
              disabled 
              :max="5" 
              :show-text="true"
            />
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]">
              {{ statusLabelMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button 
              v-if="row.status === 0"
              type="warning" 
              link 
              size="small" 
              @click="handleAssign(row)"
            >
              分配
            </el-button>
            <el-button 
              v-if="row.status === 2"
              type="success" 
              link 
              size="small" 
              @click="handleClose(row)"
            >
              关闭
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="detailVisible" title="咨询详情" width="700px">
      <el-descriptions :column="2" border class="mb-20">
        <el-descriptions-item label="咨询编号">{{ currentConsultation.id }}</el-descriptions-item>
        <el-descriptions-item label="咨询类型">
          <el-tag :type="typeTagMap[currentConsultation.type]">
            {{ typeLabelMap[currentConsultation.type] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="咨询主题">{{ currentConsultation.subject || '-' }}</el-descriptions-item>
        <el-descriptions-item label="当前状态">
          <el-tag :type="statusTypeMap[currentConsultation.status]">
            {{ statusLabelMap[currentConsultation.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="用户姓名">{{ currentConsultation.user_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentConsultation.user_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="客服人员">{{ currentConsultation.staff_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="用户评分" v-if="currentConsultation.rating">
          <el-rate 
            v-model="currentConsultation.rating" 
            disabled 
            :max="5" 
            :show-text="true"
          />
        </el-descriptions-item>
        <el-descriptions-item label="创建时间" :span="2">{{ formatDate(currentConsultation.created_at) }}</el-descriptions-item>
      </el-descriptions>
      
      <el-divider content-position="left">咨询消息</el-divider>
      <div class="message-list" v-if="messages.length > 0">
        <div 
          v-for="msg in messages" 
          :key="msg.id" 
          class="message-item"
          :class="{ 'is-user': msg.sender_type === 0, 'is-staff': msg.sender_type === 1 }"
        >
          <div class="message-header">
            <el-tag :type="msg.sender_type === 0 ? 'info' : 'primary'" size="small">
              {{ msg.sender_type === 0 ? '用户' : '客服' }}
            </el-tag>
            <span class="sender-name">{{ msg.sender_name || '系统' }}</span>
            <span class="send-time">{{ formatDate(msg.created_at) }}</span>
          </div>
          <div class="message-content">
            <p>{{ msg.content }}</p>
          </div>
        </div>
      </div>
      <el-empty v-else description="暂无消息记录" />
      
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
    
    <el-dialog v-model="assignVisible" title="分配客服" width="500px">
      <el-form label-width="100px">
        <el-form-item label="当前咨询">
          <span>{{ currentConsultation.subject }}</span>
        </el-form-item>
        <el-form-item label="选择客服">
          <el-select 
            v-model="selectedStaffId" 
            placeholder="请选择客服人员" 
            style="width: 100%"
          >
            <el-option
              v-for="item in staffList"
              :key="item.id"
              :label="item.real_name + ' (' + groupTypeLabelMap[item.group_type] + ')'"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="assignVisible = false">取消</el-button>
          <el-button type="primary" @click="handleConfirmAssign">确认分配</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { 
  getConsultationList, 
  getConsultationById, 
  getConsultationMessages,
  updateConsultation,
  getCsStaffList
} from '@/api'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const detailVisible = ref(false)
const assignVisible = ref(false)

const tableData = ref([])
const messages = ref([])
const staffList = ref([])
const currentConsultation = ref({})
const dateRange = ref([])
const selectedStaffId = ref(null)

const staffFilter = computed(() => {
  if (route.query.staff_name) {
    return route.query.staff_name
  }
  return null
})

const searchForm = reactive({
  type: null,
  status: null,
  user_name: '',
  staff_id: null,
  start_date: '',
  end_date: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const typeTagMap = {
  0: 'info',
  1: 'primary',
  2: 'success',
  3: 'warning',
  4: 'info'
}

const typeLabelMap = {
  0: '产品咨询',
  1: '订单问题',
  2: '积分兑换',
  3: '投诉建议',
  4: '其他'
}

const statusTypeMap = {
  0: 'warning',
  1: 'primary',
  2: 'success',
  3: 'info'
}

const statusLabelMap = {
  0: '待处理',
  1: '处理中',
  2: '已解决',
  3: '已关闭'
}

const groupTypeLabelMap = {
  0: '售前客服',
  1: '售后客服',
  2: '投诉处理'
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const clearFilter = () => {
  router.push({ path: '/consultations', query: {} })
  searchForm.staff_id = null
  fetchData()
}

const fetchStaffList = async () => {
  try {
    const res = await getCsStaffList({ page: 1, page_size: 1000, status: 1 })
    const data = res.data || {}
    staffList.value = data.list || []
  } catch (error) {
    console.error('获取客服列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    if (route.query.staff_id) {
      params.staff_id = parseInt(route.query.staff_id)
    }
    
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dayjs(dateRange.value[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(dateRange.value[1]).format('YYYY-MM-DD')
    }
    
    const res = await getConsultationList(params)
    const data = res.data || {}
    tableData.value = data.list || []
    pagination.total = data.total || 0
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
  searchForm.type = null
  searchForm.status = null
  searchForm.user_name = ''
  searchForm.staff_id = null
  dateRange.value = []
  pagination.page = 1
  fetchData()
}

const handleView = async (row) => {
  try {
    const res = await getConsultationById(row.id)
    currentConsultation.value = res.data || {}
    
    const msgRes = await getConsultationMessages(row.id)
    messages.value = msgRes.data || []
    
    detailVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
  }
}

const handleAssign = (row) => {
  currentConsultation.value = { ...row }
  selectedStaffId.value = null
  fetchStaffList()
  assignVisible.value = true
}

const handleConfirmAssign = async () => {
  if (!selectedStaffId.value) {
    ElMessage.warning('请选择客服人员')
    return
  }
  
  try {
    await updateConsultation(currentConsultation.value.id, {
      staff_id: selectedStaffId.value,
      status: 1
    })
    ElMessage.success('分配成功')
    assignVisible.value = false
    fetchData()
  } catch (error) {
    console.error('分配失败:', error)
  }
}

const handleClose = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要关闭此咨询吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updateConsultation(row.id, { status: 3 })
    ElMessage.success('关闭成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('关闭失败:', error)
    }
  }
}

onMounted(() => {
  fetchStaffList()
  fetchData()
})
</script>

<style lang="scss" scoped>
.search-form {
  .el-form-item {
    margin-right: 0;
  }
}

.filter-info {
  font-size: 14px;
  color: #606266;
}

.message-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  
  .message-item {
    margin-bottom: 15px;
    padding: 12px;
    background: #fff;
    border-radius: 8px;
    border-left: 4px solid #909399;
    
    &.is-user {
      border-left-color: #909399;
    }
    
    &.is-staff {
      border-left-color: #409eff;
    }
    
    .message-header {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      
      .sender-name {
        margin-left: 8px;
        font-weight: 600;
        color: #303133;
      }
      
      .send-time {
        margin-left: auto;
        font-size: 12px;
        color: #909399;
      }
    }
    
    .message-content {
      p {
        margin: 0;
        line-height: 1.6;
        color: #606266;
      }
    }
  }
}
</style>
