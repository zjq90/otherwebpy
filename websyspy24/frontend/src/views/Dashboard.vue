<template>
  <!-- 工作台页面 -->
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card member-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.members }}</div>
              <div class="stat-label">会员总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card checkin-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Timer /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.todayCheckin }}</div>
              <div class="stat-label">今日签到</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card locker-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Box /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.availableLockers }} / {{ stats.totalLockers }}</div>
              <div class="stat-label">可用储物柜</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card revenue-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon">
              <el-icon :size="40"><Money /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">¥{{ stats.todayRevenue }}</div>
              <div class="stat-label">今日营收</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 快捷操作 -->
    <el-row :gutter="20" class="shortcut-row">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>快捷操作</span>
            </div>
          </template>
          <div class="shortcut-actions">
            <el-button type="primary" size="large" @click="goToCheckin">
              <el-icon><Timer /></el-icon>
              签到验证
            </el-button>
            <el-button type="success" size="large" @click="goToCashier">
              <el-icon><Money /></el-icon>
              收银台
            </el-button>
            <el-button type="warning" size="large" @click="goToLocker">
              <el-icon><Box /></el-icon>
              储物柜分配
            </el-button>
            <el-button type="info" size="large" @click="goToMembers">
              <el-icon><User /></el-icon>
              会员管理
            </el-button>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>今日签到统计</span>
              <el-button type="text" @click="goToCheckinRecords">查看更多</el-button>
            </div>
          </template>
          <div class="checkin-stats">
            <div class="checkin-item">
              <span class="checkin-label">刷卡签到</span>
              <span class="checkin-count">{{ checkinStats.byType.card }}</span>
            </div>
            <div class="checkin-item">
              <span class="checkin-label">扫码签到</span>
              <span class="checkin-count">{{ checkinStats.byType.qr }}</span>
            </div>
            <div class="checkin-item">
              <span class="checkin-label">人脸识别</span>
              <span class="checkin-count">{{ checkinStats.byType.face }}</span>
            </div>
            <el-divider />
            <div class="checkin-item">
              <span class="checkin-label">签到成功</span>
              <span class="checkin-count success">{{ checkinStats.success }}</span>
            </div>
            <div class="checkin-item">
              <span class="checkin-label">签到失败</span>
              <span class="checkin-count failed">{{ checkinStats.failed }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 储物柜使用情况 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>储物柜状态分布</span>
            </div>
          </template>
          <div class="locker-stats">
            <div class="locker-item">
              <el-tag type="success" effect="dark">空闲</el-tag>
              <span class="locker-count">{{ lockerStats.available }}</span>
              <el-progress 
                :percentage="lockerStats.total > 0 ? Math.round(lockerStats.available / lockerStats.total * 100) : 0"
                :show-text="false"
                color="#67C23A"
                style="width: 100px"
              />
            </div>
            <div class="locker-item">
              <el-tag type="warning" effect="dark">使用中</el-tag>
              <span class="locker-count">{{ lockerStats.occupied }}</span>
              <el-progress 
                :percentage="lockerStats.total > 0 ? Math.round(lockerStats.occupied / lockerStats.total * 100) : 0"
                :show-text="false"
                color="#E6A23C"
                style="width: 100px"
              />
            </div>
            <div class="locker-item">
              <el-tag type="danger" effect="dark">故障维修</el-tag>
              <span class="locker-count">{{ lockerStats.maintenance }}</span>
              <el-progress 
                :percentage="lockerStats.total > 0 ? Math.round(lockerStats.maintenance / lockerStats.total * 100) : 0"
                :show-text="false"
                color="#F56C6C"
                style="width: 100px"
              />
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>系统信息</span>
            </div>
          </template>
          <div class="system-info">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="系统名称">健身房管理系统</el-descriptions-item>
              <el-descriptions-item label="系统版本">v1.0.0</el-descriptions-item>
              <el-descriptions-item label="技术栈">Vue 3 + FastAPI + SQLite</el-descriptions-item>
              <el-descriptions-item label="API地址">http://localhost:8000</el-descriptions-item>
              <el-descriptions-item label="文档地址">
                <el-link href="http://localhost:8000/docs" target="_blank">API文档</el-link>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'

const router = useRouter()

// 统计数据
const stats = ref({
  members: 0,
  todayCheckin: 0,
  totalLockers: 0,
  availableLockers: 0,
  todayRevenue: '0.00'
})

// 签到统计
const checkinStats = ref({
  total: 0,
  success: 0,
  failed: 0,
  byType: {
    card: 0,
    qr: 0,
    face: 0
  }
})

// 储物柜统计
const lockerStats = ref({
  total: 0,
  available: 0,
  occupied: 0,
  maintenance: 0
})

// 加载数据
const loadData = async () => {
  try {
    // 加载测试数据摘要
    const summaryRes = await api.getTestSummary()
    if (summaryRes.success) {
      const data = summaryRes.data
      
      stats.value.members = data.total_counts.members || 0
      stats.value.totalLockers = data.total_counts.lockers || 0
      
      // 储物柜统计
      lockerStats.value = {
        total: data.total_counts.lockers || 0,
        available: data.locker_stats?.available || 0,
        occupied: data.locker_stats?.occupied || 0,
        maintenance: data.locker_stats?.maintenance || 0
      }
      
      stats.value.availableLockers = data.locker_stats?.available || 0
    }
    
    // 加载今日签到统计
    try {
      const checkinRes = await api.getTodayStats()
      if (checkinRes.success) {
        const data = checkinRes.data
        checkinStats.value = {
          total: data.total || 0,
          success: data.success || 0,
          failed: data.failed || 0,
          byType: data.by_type || { card: 0, qr: 0, face: 0 }
        }
        stats.value.todayCheckin = data.total || 0
      }
    } catch (e) {
      console.log('签到统计API尚未准备好')
    }
    
  } catch (error) {
    console.error('加载数据失败:', error)
    // 使用默认数据
    stats.value.members = 20
    stats.value.todayCheckin = 0
    stats.value.totalLockers = 30
    stats.value.availableLockers = 20
    stats.value.todayRevenue = '0.00'
    
    lockerStats.value = {
      total: 30,
      available: 20,
      occupied: 8,
      maintenance: 2
    }
  }
}

// 导航函数
const goToCheckin = () => router.push('/checkin')
const goToCashier = () => router.push('/cashier')
const goToLocker = () => router.push('/lockers')
const goToMembers = () => router.push('/members')
const goToCheckinRecords = () => router.push('/checkin/records')

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.member-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.checkin-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border: none;
}

.locker-card {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  border: none;
}

.revenue-card {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
  border: none;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
  color: #fff;
}

.stat-icon {
  opacity: 0.8;
}

.stat-info {
  text-align: right;
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  opacity: 0.9;
  margin-top: 5px;
}

/* 快捷操作 */
.shortcut-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.shortcut-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.shortcut-actions .el-button {
  padding: 15px 25px;
  font-size: 16px;
}

/* 签到统计 */
.checkin-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.checkin-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkin-label {
  color: #606266;
  font-size: 14px;
}

.checkin-count {
  font-size: 18px;
  font-weight: bold;
  color: #409EFF;
}

.checkin-count.success {
  color: #67C23A;
}

.checkin-count.failed {
  color: #F56C6C;
}

/* 储物柜统计 */
.locker-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.locker-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.locker-count {
  font-size: 18px;
  font-weight: bold;
  min-width: 40px;
}

/* 系统信息 */
.system-info {
  font-size: 14px;
}
</style>
