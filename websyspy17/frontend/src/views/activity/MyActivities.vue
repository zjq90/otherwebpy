<template>
  <div class="my-activities">
    <el-card>
      <template #header>
        <span>我的活动报名</span>
      </template>
      
      <el-table :data="registrationList" v-loading="loading" stripe style="width: 100%">
        <el-table-column prop="id" label="报名ID" width="80" />
        <el-table-column prop="activity_title" label="活动名称" min-width="200">
          <template #default="{ row }">
            <router-link :to="`/activities/${row.activity_id}`" style="color: #409eff; text-decoration: none;">
              {{ getActivityTitle(row.activity_id) }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="participant_name" label="参与者" width="120" />
        <el-table-column prop="participant_phone" label="联系电话" width="130" />
        <el-table-column prop="participant_count" label="参与人数" width="100">
          <template #default="{ row }">
            {{ row.participant_count }} 人
          </template>
        </el-table-column>
        <el-table-column prop="room_number" label="房间号" width="120">
          <template #default="{ row }">
            {{ row.room_number || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="is_attended" label="是否参加" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_attended ? 'success' : 'info'">
              {{ row.is_attended ? '已参加' : '未参加' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="报名时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button 
              type="danger" 
              link
              @click="handleCancel(row)"
            >
              取消报名
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="registrationList.length === 0 && !loading" description="暂无活动报名记录">
        <template #description>
          <p>您还没有报名任何活动</p>
          <el-button type="primary" @click="goToActivities">
            去看看活动
          </el-button>
        </template>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { activityApi } from '@/api/activity'

const router = useRouter()

const loading = ref(false)
const registrationList = ref([])
const activityMap = ref({})

const fetchRegistrations = async () => {
  loading.value = true
  try {
    registrationList.value = await activityApi.getMyRegistrations() || []
  } catch (error) {
    console.error('获取报名记录失败:', error)
  } finally {
    loading.value = false
  }
}

const getActivityTitle = (activityId) => {
  return activityMap.value[activityId] || `活动 #${activityId}`
}

const handleCancel = async (row) => {
  try {
    await ElMessageBox.confirm('确定要取消该活动的报名吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await activityApi.cancelRegistration(row.activity_id)
    ElMessage.success('已取消报名')
    fetchRegistrations()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('取消报名失败:', error)
    }
  }
}

const goToActivities = () => {
  router.push('/activities')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  fetchRegistrations()
})
</script>

<style scoped>
.my-activities {
  padding: 0;
}
</style>
