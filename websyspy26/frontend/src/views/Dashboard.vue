<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon size="40"><User /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">会员总数</div>
          <div class="stat-value">{{ stats.members.total || 0 }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon size="40"><Wallet /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">会员卡总数</div>
          <div class="stat-value">{{ stats.member_cards.total || 0 }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon size="40"><Present /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">进行中活动</div>
          <div class="stat-value">{{ stats.promotions.active || 0 }}</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <el-icon size="40"><Bell /></el-icon>
        </div>
        <div class="stat-info">
          <div class="stat-title">待发送提醒</div>
          <div class="stat-value">{{ stats.reminders.pending || 0 }}</div>
        </div>
      </div>
    </div>

    <!-- 快捷操作 -->
    <div class="page-container" style="margin-top: 20px">
      <div class="page-header">
        <span class="page-title">快捷操作</span>
      </div>
      <div style="display: flex; gap: 15px; flex-wrap: wrap">
        <el-button type="primary" size="large" @click="goToMembers">
          <el-icon><User /></el-icon>
          会员管理
        </el-button>
        <el-button type="success" size="large" @click="goToPromotions">
          <el-icon><Present /></el-icon>
          促销活动
        </el-button>
        <el-button type="warning" size="large" @click="goToReminders">
          <el-icon><Bell /></el-icon>
          续费提醒
        </el-button>
        <el-button type="info" size="large" @click="goToTest">
          <el-icon><Tools /></el-icon>
          测试工具
        </el-button>
      </div>
    </div>

    <!-- 系统信息 -->
    <div class="page-container" style="margin-top: 20px">
      <div class="page-header">
        <span class="page-title">系统信息</span>
      </div>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="系统名称">会员管理系统</el-descriptions-item>
        <el-descriptions-item label="版本号">1.0.0</el-descriptions-item>
        <el-descriptions-item label="后端技术">FastAPI + SQLite</el-descriptions-item>
        <el-descriptions-item label="前端技术">Vue 3 + Element Plus</el-descriptions-item>
        <el-descriptions-item label="API文档">
          <el-link href="/api/docs" target="_blank">/api/docs</el-link>
        </el-descriptions-item>
        <el-descriptions-item label="健康状态">
          <el-tag type="success">正常运行</el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, 
  Wallet, 
  Present, 
  Bell, 
  Tools 
} from '@element-plus/icons-vue'
import { testApi } from '../api'

const router = useRouter()

const stats = ref({
  members: { total: 0 },
  member_cards: { total: 0 },
  promotions: { active: 0, total: 0 },
  reminders: { pending: 0, total: 0 }
})

// 获取统计数据
const loadStats = async () => {
  try {
    const data = await testApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('获取统计数据失败:', error)
  }
}

// 导航
const goToMembers = () => router.push('/members')
const goToPromotions = () => router.push('/promotions')
const goToReminders = () => router.push('/reminders')
const goToTest = () => router.push('/test')

onMounted(() => {
  loadStats()
})
</script>
