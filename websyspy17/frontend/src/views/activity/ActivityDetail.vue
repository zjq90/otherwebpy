<template>
  <div class="activity-detail">
    <el-card v-loading="loading">
      <template #header>
        <div class="card-header">
          <span>活动详情</span>
          <el-button @click="goBack">
            <el-icon><ArrowLeft /></el-icon>
            返回列表
          </el-button>
        </div>
      </template>
      
      <div class="activity-header-section">
        <div class="activity-title-section">
          <h1>{{ activityDetail.title }}</h1>
          <div class="activity-tags">
            <el-tag :type="getStatusTag(activityDetail.status)" size="large">
              {{ getStatusText(activityDetail.status) }}
            </el-tag>
            <el-tag :type="getTypeTag(activityDetail.activity_type)" size="large">
              {{ getTypeText(activityDetail.activity_type) }}
            </el-tag>
            <el-tag v-if="activityDetail.is_featured" type="warning" size="large" effect="dark">
              推荐活动
            </el-tag>
          </div>
        </div>
      </div>
      
      <el-divider />
      
      <el-descriptions :column="2" border>
        <el-descriptions-item label="活动时间">
          <div class="time-info">
            <p><strong>开始：</strong>{{ formatDateTime(activityDetail.start_time) }}</p>
            <p><strong>结束：</strong>{{ formatDateTime(activityDetail.end_time) }}</p>
            <p v-if="activityDetail.registration_deadline">
              <strong>报名截止：</strong>{{ formatDateTime(activityDetail.registration_deadline) }}
            </p>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="活动地点">
          {{ activityDetail.location || '待定' }}
        </el-descriptions-item>
        <el-descriptions-item label="参与人数">
          <el-progress 
            :percentage="participationPercent" 
            :status="participationStatus"
          />
          <span style="display: block; margin-top: 8px; color: #909399;">
            已报名 {{ activityDetail.current_participants || 0 }} 人
            <span v-if="activityDetail.max_participants"> / 最多 {{ activityDetail.max_participants }} 人</span>
            <span v-else> / 不限人数</span>
          </span>
        </el-descriptions-item>
        <el-descriptions-item label="联系方式">
          <p>{{ activityDetail.contact_name || '待定' }}</p>
          <p>{{ activityDetail.contact_phone || '待定' }}</p>
        </el-descriptions-item>
        <el-descriptions-item label="浏览次数" :span="2">
          {{ activityDetail.views_count || 0 }} 次
        </el-descriptions-item>
      </el-descriptions>
      
      <el-divider content-position="left">活动描述</el-divider>
      
      <div class="activity-description">
        {{ activityDetail.description || '暂无活动描述' }}
      </div>
      
      <el-divider content-position="left">操作</el-divider>
      
      <div class="action-section">
        <template v-if="isRegistrationOpen">
          <template v-if="!isRegistered">
            <el-button 
              type="primary" 
              size="large"
              @click="showRegisterDialog = true"
            >
              <el-icon><Plus /></el-icon>
              立即报名
            </el-button>
          </template>
          <template v-else>
            <el-button 
              type="success" 
              size="large"
              disabled
            >
              <el-icon><Check /></el-icon>
              已报名
            </el-button>
            <el-button 
              type="danger"
              size="large"
              @click="handleCancelRegistration"
            >
              取消报名
            </el-button>
          </template>
        </template>
        <template v-else>
          <el-button 
            type="info" 
            size="large"
            disabled
          >
            {{ isRegistrationClosed ? '报名已结束' : '报名未开始' }}
          </el-button>
        </template>
        
        <template v-if="userStore.isAdmin">
          <el-button 
            v-if="activityDetail.status === 'draft'"
            type="primary"
            @click="handlePublish"
          >
            发布活动
          </el-button>
          <el-button 
            v-if="activityDetail.status === 'registration_open'"
            type="warning"
            @click="handleCloseRegistration"
          >
            关闭报名
          </el-button>
        </template>
      </div>
    </el-card>
    
    <el-dialog 
      v-model="showRegisterDialog" 
      title="活动报名" 
      width="500px"
    >
      <el-form 
        ref="registerFormRef"
        :model="registerForm" 
        :rules="registerRules"
        label-width="100px"
      >
        <el-form-item label="参与者姓名" prop="participant_name">
          <el-input v-model="registerForm.participant_name" placeholder="请输入参与者姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="participant_phone">
          <el-input v-model="registerForm.participant_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="参与人数" prop="participant_count">
          <el-input-number 
            v-model="registerForm.participant_count" 
            :min="1"
            style="width: 100%;"
          />
        </el-form-item>
        <el-form-item label="房间号" prop="room_number">
          <el-input v-model="registerForm.room_number" placeholder="请输入房间号（可选）" />
        </el-form-item>
        <el-form-item label="备注" prop="remarks">
          <el-input 
            v-model="registerForm.remarks" 
            type="textarea"
            :rows="3"
            placeholder="备注信息（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showRegisterDialog = false">取消</el-button>
        <el-button type="primary" :loading="registerLoading" @click="handleRegister">确认报名</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { activityApi } from '@/api/activity'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const registerLoading = ref(false)
const showRegisterDialog = ref(false)
const registerFormRef = ref(null)

const activityDetail = ref({})
const isRegistered = ref(false)

const registerForm = reactive({
  participant_name: '',
  participant_phone: '',
  participant_count: 1,
  room_number: '',
  remarks: ''
})

const registerRules = {
  participant_name: [
    { required: true, message: '请输入参与者姓名', trigger: 'blur' }
  ],
  participant_phone: [
    { required: true, message: '请输入联系电话', trigger: 'blur' }
  ]
}

const isRegistrationOpen = computed(() => {
  return activityDetail.value.status === 'registration_open' || 
         activityDetail.value.status === 'published'
})

const isRegistrationClosed = computed(() => {
  return activityDetail.value.status === 'registration_closed' ||
         activityDetail.value.status === 'completed' ||
         activityDetail.value.status === 'cancelled'
})

const participationPercent = computed(() => {
  if (!activityDetail.value.max_participants) return 0
  const current = activityDetail.value.current_participants || 0
  const max = activityDetail.value.max_participants
  return Math.min(Math.round((current / max) * 100), 100)
})

const participationStatus = computed(() => {
  if (!activityDetail.value.max_participants) return null
  const current = activityDetail.value.current_participants || 0
  const max = activityDetail.value.max_participants
  if (current >= max) return 'exception'
  if (current >= max * 0.8) return 'warning'
  return null
})

const fetchDetail = async () => {
  const id = route.params.id
  if (!id) return
  
  loading.value = true
  try {
    activityDetail.value = await activityApi.getActivityById(id)
    
    if (userStore.isLoggedIn) {
      const myRegistrations = await activityApi.getMyRegistrations()
      isRegistered.value = myRegistrations.some(r => r.activity_id === parseInt(id))
    }
    
    if (userStore.user) {
      registerForm.participant_name = userStore.user.real_name || ''
      registerForm.room_number = userStore.user.room_number || ''
      registerForm.participant_phone = userStore.user.phone || ''
    }
  } catch (error) {
    console.error('获取活动详情失败:', error)
  } finally {
    loading.value = false
  }
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  await registerFormRef.value.validate(async (valid) => {
    if (valid) {
      registerLoading.value = true
      try {
        await activityApi.registerActivity(route.params.id, registerForm)
        ElMessage.success('报名成功！')
        showRegisterDialog.value = false
        isRegistered.value = true
        fetchDetail()
      } catch (error) {
        console.error('报名失败:', error)
      } finally {
        registerLoading.value = false
      }
    }
  })
}

const handleCancelRegistration = async () => {
  try {
    await ElMessageBox.confirm('确定要取消报名吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await activityApi.cancelRegistration(route.params.id)
    ElMessage.success('已取消报名')
    isRegistered.value = false
    fetchDetail()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消报名失败:', error)
    }
  }
}

const handlePublish = async () => {
  try {
    await activityApi.publishActivity(route.params.id)
    ElMessage.success('发布成功！')
    fetchDetail()
  } catch (error) {
    console.error('发布失败:', error)
  }
}

const handleCloseRegistration = async () => {
  try {
    await activityApi.closeRegistration(route.params.id)
    ElMessage.success('已关闭报名')
    fetchDetail()
  } catch (error) {
    console.error('关闭报名失败:', error)
  }
}

const goBack = () => {
  router.back()
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
.activity-detail {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.activity-header-section {
  text-align: center;
  padding: 20px 0;
}

.activity-title-section h1 {
  margin: 0 0 16px;
  font-size: 24px;
  color: #303133;
}

.activity-tags {
  display: flex;
  justify-content: center;
  gap: 12px;
}

.time-info p {
  margin: 8px 0;
  color: #606266;
}

.activity-description {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
  line-height: 1.8;
  color: #606266;
  white-space: pre-wrap;
}

.action-section {
  display: flex;
  gap: 12px;
  align-items: center;
}
</style>
