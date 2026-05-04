<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff;">
              <el-icon :size="30"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.serviceRequests }}</div>
              <div class="stat-label">服务请求</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a;">
              <el-icon :size="30"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.pendingRequests }}</div>
              <div class="stat-label">待处理</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c;">
              <el-icon :size="30"><Calendar /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.activities }}</div>
              <div class="stat-label">社区活动</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c;">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.myRegistrations }}</div>
              <div class="stat-label">我的报名</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <el-row :gutter="20">
            <el-col :span="8">
              <router-link to="/services/create">
                <div class="action-card">
                  <el-icon :size="40" color="#409eff"><Edit /></el-icon>
                  <span>提交报修</span>
                </div>
              </router-link>
            </el-col>
            <el-col :span="8">
              <router-link to="/services">
                <div class="action-card">
                  <el-icon :size="40" color="#67c23a"><List /></el-icon>
                  <span>我的服务</span>
                </div>
              </router-link>
            </el-col>
            <el-col :span="8">
              <router-link to="/activities">
                <div class="action-card">
                  <el-icon :size="40" color="#e6a23c"><Calendar /></el-icon>
                  <span>社区活动</span>
                </div>
              </router-link>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最新活动</span>
              <router-link to="/activities">查看更多</router-link>
            </div>
          </template>
          <el-timeline v-if="recentActivities.length > 0">
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="formatDate(activity.start_time)"
              placement="top"
            >
              <el-card shadow="hover" class="timeline-card" @click="goToActivity(activity.id)">
                <div class="activity-title">{{ activity.title }}</div>
                <div class="activity-meta">
                  <el-tag size="small" :type="activity.is_featured ? 'warning' : 'info'">
                    {{ activity.is_featured ? '推荐' : '普通' }}
                  </el-tag>
                  <span class="activity-location">{{ activity.location }}</span>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无活动" />
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的服务请求</span>
              <router-link to="/services">查看更多</router-link>
            </div>
          </template>
          <el-table :data="myRecentServices" v-if="myRecentServices.length > 0" stripe>
            <el-table-column prop="title" label="标题" min-width="200" />
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
            <el-table-column prop="created_at" label="创建时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <router-link :to="`/services/${row.id}`">
                  <el-button type="primary" link>查看</el-button>
                </router-link>
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-else description="暂无服务请求" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { serviceApi } from '@/api/service'
import { activityApi } from '@/api/activity'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const stats = reactive({
  serviceRequests: 0,
  pendingRequests: 0,
  activities: 0,
  myRegistrations: 0
})

const recentActivities = ref([])
const myRecentServices = ref([])

const fetchData = async () => {
  try {
    const [servicesRes, activitiesRes, registrationsRes] = await Promise.all([
      userStore.isAdmin ? serviceApi.getServiceRequests() : serviceApi.getMyServiceRequests(),
      activityApi.getPublishedActivities({ limit: 5 }),
      activityApi.getMyRegistrations()
    ])
    
    stats.serviceRequests = servicesRes.length || 0
    stats.pendingRequests = servicesRes.filter(s => s.status === 'pending').length || 0
    stats.activities = activitiesRes.length || 0
    stats.myRegistrations = registrationsRes.length || 0
    
    recentActivities.value = activitiesRes.slice(0, 3)
    myRecentServices.value = servicesRes.slice(0, 5)
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
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

const goToActivity = (id) => {
  router.push(`/activities/${id}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  margin-bottom: 0;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header a {
  font-size: 14px;
  color: #409eff;
  text-decoration: none;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #dcdfe6;
  cursor: pointer;
  transition: all 0.3s;
}

.action-card:hover {
  border-color: #409eff;
  background: #ecf5ff;
}

.action-card span {
  margin-top: 12px;
  color: #606266;
  font-size: 14px;
}

a {
  text-decoration: none;
}

.timeline-card {
  cursor: pointer;
  transition: all 0.3s;
}

.timeline-card:hover {
  transform: translateX(5px);
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 8px;
}

.activity-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.activity-location {
  font-size: 12px;
  color: #909399;
}
</style>
