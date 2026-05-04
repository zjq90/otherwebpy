<template>
  <div class="service-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>服务请求详情</span>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="ID">{{ serviceDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="服务类型">
          <el-tag :type="getServiceTypeTag(serviceDetail.service_type)">
            {{ getServiceTypeText(serviceDetail.service_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="状态" :span="2">
          <el-tag :type="getStatusTag(serviceDetail.status)" size="large">
            {{ getStatusText(serviceDetail.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标题" :span="2">{{ serviceDetail.title }}</el-descriptions-item>
        <el-descriptions-item label="详细描述" :span="2">
          {{ serviceDetail.description || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="优先级">
          <el-tag :type="getPriorityTag(serviceDetail.priority)">
            {{ getPriorityText(serviceDetail.priority) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="房间号">{{ serviceDetail.room_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="具体位置">{{ serviceDetail.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系人">{{ serviceDetail.contact_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ serviceDetail.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDateTime(serviceDetail.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatDateTime(serviceDetail.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="完成时间">{{ formatDateTime(serviceDetail.completed_at) || '-' }}</el-descriptions-item>
      </el-descriptions>
      
      <el-divider content-position="left">操作</el-divider>
      
      <el-space>
        <template v-if="userStore.isAdmin || serviceDetail.assignee_id === userStore.user?.id">
          <el-button 
            v-if="serviceDetail.status === 'pending'" 
            type="primary"
            @click="showAssignDialog = true"
          >
            派单
          </el-button>
          <el-button 
            v-if="serviceDetail.status === 'assigned'" 
            type="primary"
            @click="handleStatusChange('processing')"
          >
            开始处理
          </el-button>
          <el-button 
            v-if="serviceDetail.status === 'processing'" 
            type="success"
            @click="handleStatusChange('completed')"
          >
            完成处理
          </el-button>
        </template>
        <el-button 
          v-if="!userStore.isAdmin && serviceDetail.status === 'completed'" 
          type="primary"
          @click="handleStatusChange('closed')"
        >
          确认关闭
        </el-button>
      </el-space>
      
      <el-divider content-position="left">处理进度</el-divider>
      
      <el-timeline>
        <el-timeline-item
          v-for="progress in progressList"
          :key="progress.id"
          :timestamp="formatDateTime(progress.created_at)"
          placement="top"
        >
          <el-card>
            <h4>{{ progress.action }}</h4>
            <p style="color: #606266; margin: 0;">{{ progress.description }}</p>
            <p v-if="progress.from_status" style="color: #909399; margin: 8px 0 0; font-size: 12px;">
              状态变更: {{ getStatusText(progress.from_status) }} → {{ getStatusText(progress.to_status) }}
            </p>
          </el-card>
        </el-timeline-item>
      </el-timeline>
      <el-empty v-if="progressList.length === 0" description="暂无进度记录" />
    </el-card>
    
    <el-dialog v-model="showAssignDialog" title="派单" width="400px">
      <el-form :model="assignForm" label-width="80px">
        <el-form-item label="分配给">
          <el-select v-model="assignForm.assignee_id" placeholder="请选择处理人" style="width: 100%;">
            <el-option 
              v-for="user in propertyUsers" 
              :key="user.id" 
              :label="`${user.real_name || user.username} (${user.role === 'admin' ? '管理员' : '物业人员'})`"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAssignDialog = false">取消</el-button>
        <el-button type="primary" :loading="assignLoading" @click="handleAssign">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { serviceApi } from '@/api/service'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const assignLoading = ref(false)
const showAssignDialog = ref(false)

const serviceDetail = ref({})
const progressList = ref([])
const propertyUsers = ref([])

const assignForm = reactive({
  assignee_id: null
})

const fetchDetail = async () => {
  const id = route.params.id
  if (!id) return
  
  loading.value = true
  try {
    serviceDetail.value = await serviceApi.getServiceRequestById(id)
    progressList.value = await serviceApi.getServiceProgress(id)
  } catch (error) {
    console.error('获取详情失败:', error)
  } finally {
    loading.value = false
  }
}

const handleStatusChange = async (newStatus) => {
  try {
    await serviceApi.updateServiceStatus(route.params.id, newStatus)
    ElMessage.success('状态更新成功')
    fetchDetail()
  } catch (error) {
    console.error('状态更新失败:', error)
  }
}

const handleAssign = async () => {
  if (!assignForm.assignee_id) {
    ElMessage.warning('请选择处理人')
    return
  }
  
  assignLoading.value = true
  try {
    await serviceApi.assignServiceRequest(route.params.id, assignForm.assignee_id)
    ElMessage.success('派单成功')
    showAssignDialog.value = false
    fetchDetail()
  } catch (error) {
    console.error('派单失败:', error)
  } finally {
    assignLoading.value = false
  }
}

const goBack = () => {
  router.back()
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
  fetchDetail()
})
</script>

<style scoped>
.service-detail {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
