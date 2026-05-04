<template>
  <div class="activity-list">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>社区活动</span>
          <el-button 
            v-if="userStore.isAdmin" 
            type="primary" 
            @click="goToCreate"
          >
            <el-icon><Plus /></el-icon>
            创建活动
          </el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="活动类型">
          <el-select v-model="searchForm.activity_type" placeholder="全部类型" clearable>
            <el-option label="节日活动" value="festival" />
            <el-option label="邻里互动" value="neighbor_interaction" />
            <el-option label="体育活动" value="sports" />
            <el-option label="文化活动" value="cultural" />
            <el-option label="公益活动" value="charity" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否推荐">
          <el-select v-model="searchForm.is_featured" placeholder="全部" clearable>
            <el-option label="推荐活动" :value="true" />
            <el-option label="普通活动" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
      
      <el-row :gutter="20">
        <el-col :span="8" v-for="activity in activityList" :key="activity.id">
          <el-card 
            class="activity-card" 
            shadow="hover"
            @click="goToDetail(activity.id)"
          >
            <template #header>
              <div class="activity-header">
                <span class="activity-title">{{ activity.title }}</span>
                <el-tag 
                  v-if="activity.is_featured" 
                  type="warning"
                  size="small"
                >
                  推荐
                </el-tag>
              </div>
            </template>
            
            <div class="activity-content">
              <p class="activity-desc">{{ activity.description || '暂无描述' }}</p>
              
              <el-divider />
              
              <div class="activity-meta">
                <div class="meta-item">
                  <el-icon><Calendar /></el-icon>
                  <span>{{ formatDate(activity.start_time) }}</span>
                </div>
                <div class="meta-item">
                  <el-icon><Location /></el-icon>
                  <span>{{ activity.location || '待定' }}</span>
                </div>
                <div class="meta-item">
                  <el-icon><User /></el-icon>
                  <span>{{ activity.current_participants || 0 }}/{{ activity.max_participants || '不限' }}人</span>
                </div>
              </div>
              
              <div class="activity-footer">
                <el-tag :type="getStatusTag(activity.status)" size="small">
                  {{ getStatusText(activity.status) }}
                </el-tag>
                <el-tag :type="getTypeTag(activity.activity_type)" size="small">
                  {{ getTypeText(activity.activity_type) }}
                </el-tag>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-empty v-if="activityList.length === 0" description="暂无活动" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { activityApi } from '@/api/activity'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const activityList = ref([])

const searchForm = reactive({
  activity_type: '',
  is_featured: null
})

const fetchActivityList = async () => {
  try {
    const params = {}
    if (searchForm.activity_type) params.activity_type = searchForm.activity_type
    if (searchForm.is_featured !== null) params.is_featured = searchForm.is_featured
    
    const res = userStore.isAdmin
      ? await activityApi.getActivities(params)
      : await activityApi.getPublishedActivities(params)
    
    activityList.value = res || []
  } catch (error) {
    console.error('获取活动列表失败:', error)
  }
}

const handleSearch = () => {
  fetchActivityList()
}

const handleReset = () => {
  searchForm.activity_type = ''
  searchForm.is_featured = null
  fetchActivityList()
}

const goToCreate = () => {
  router.push('/activities/create')
}

const goToDetail = (id) => {
  router.push(`/activities/${id}`)
}

const getTypeText = (type) => {
  const map = {
    festival: '节日活动',
    neighbor_interaction: '邻里互动',
    sports: '体育活动',
    cultural: '文化活动',
    charity: '公益活动',
    other: '其他'
  }
  return map[type] || type
}

const getTypeTag = (type) => {
  const map = {
    festival: 'danger',
    neighbor_interaction: 'success',
    sports: 'primary',
    cultural: 'warning',
    charity: '',
    other: 'info'
  }
  return map[type] || 'info'
}

const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    published: '已发布',
    registration_open: '报名中',
    registration_closed: '报名结束',
    ongoing: '进行中',
    completed: '已结束',
    cancelled: '已取消'
  }
  return map[status] || status
}

const getStatusTag = (status) => {
  const map = {
    draft: 'info',
    published: 'warning',
    registration_open: 'success',
    registration_closed: '',
    ongoing: 'primary',
    completed: 'info',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchActivityList()
})
</script>

<style scoped>
.activity-list {
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

.activity-card {
  margin-bottom: 20px;
  cursor: pointer;
  transition: all 0.3s;
}

.activity-card:hover {
  transform: translateY(-5px);
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-title {
  font-weight: bold;
  font-size: 16px;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-content {
  padding: 0;
}

.activity-desc {
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

.activity-meta {
  margin: 12px 0;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 13px;
  margin-bottom: 8px;
}

.activity-footer {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
</style>
