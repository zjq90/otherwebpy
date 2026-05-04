<template>
  <div class="service-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>服务请求列表</span>
          <el-button type="primary" @click="goToCreate">
            <el-icon><Plus /></el-icon>
            提交新请求
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="服务类型">
          <el-select v-model="searchForm.service_type" placeholder="全部类型" clearable>
            <el-option label="报修" value="repair" />
            <el-option label="投诉" value="complaint" />
            <el-option label="咨询" value="consult" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="已派单" value="assigned" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-table :data="serviceList" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="service_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getServiceTypeTag(row.service_type)">
              {{ getServiceTypeText(row.service_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityTag(row.priority)">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="room_number" label="房间号" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="goToDetail(row.id)">查看</el-button>
            <el-button 
              v-if="userStore.isAdmin" 
              type="danger" 
              link 
              @click="handleDelete(row)"
            >
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
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { serviceApi } from '@/api/service'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const serviceList = ref([])

const searchForm = reactive({
  service_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const fetchServiceList = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.service_type) params.service_type = searchForm.service_type
    if (searchForm.status) params.status = searchForm.status
    
    const res = userStore.isAdmin 
      ? await serviceApi.getServiceRequests(params)
      : await serviceApi.getMyServiceRequests(params)
    
    serviceList.value = res || []
    pagination.total = res?.length || 0
  } catch (error) {
    console.error('获取服务列表失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchServiceList()
}

const handleReset = () => {
  searchForm.service_type = ''
  searchForm.status = ''
  pagination.page = 1
  fetchServiceList()
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  fetchServiceList()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchServiceList()
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该服务请求吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await serviceApi.deleteServiceRequest(row.id)
    ElMessage.success('删除成功')
    fetchServiceList()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const goToCreate = () => {
  router.push('/services/create')
}

const goToDetail = (id) => {
  router.push(`/services/${id}`)
}

const getServiceTypeText = (type) => {
  const map = { repair: '报修', complaint: '投诉', consult: '咨询' }
  return map[type] || type
}

const getServiceTypeTag = (type) => {
  const map = { repair: 'primary', complaint: 'danger', consult: 'info' }
  return map[type] || 'info'
}

const getStatusText = (status) => {
  const map = {
    pending: '待处理',
    assigned: '已派单',
    processing: '处理中',
    completed: '已完成',
    closed: '已关闭'
  }
  return map[status] || status
}

const getStatusTag = (status) => {
  const map = {
    pending: 'warning',
    assigned: 'info',
    processing: 'primary',
    completed: 'success',
    closed: 'info'
  }
  return map[status] || 'info'
}

const getPriorityText = (priority) => {
  const map = { 1: '普通', 2: '紧急', 3: '非常紧急' }
  return map[priority] || '普通'
}

const getPriorityTag = (priority) => {
  const map = { 1: 'info', 2: 'warning', 3: 'danger' }
  return map[priority] || 'info'
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchServiceList()
})
</script>

<style scoped>
.service-list {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}
</style>
