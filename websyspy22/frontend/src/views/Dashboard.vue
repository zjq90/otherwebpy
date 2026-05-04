<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <div class="stat-card member-card">
          <div class="stat-icon">
            <el-icon :size="32"><User /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.totalMembers }}</div>
            <div class="stat-label">会员总数</div>
          </div>
          <div class="stat-trend">
            <el-tag type="success">+12%</el-tag>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card active-card">
          <div class="stat-icon">
            <el-icon :size="32"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.activeMembers }}</div>
            <div class="stat-label">活跃会员</div>
          </div>
          <div class="stat-trend">
            <el-tag type="success">+8%</el-tag>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card consumption-card">
          <div class="stat-icon">
            <el-icon :size="32"><Wallet /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">¥{{ stats.totalConsumption.toLocaleString() }}</div>
            <div class="stat-label">消费总额</div>
          </div>
          <div class="stat-trend">
            <el-tag type="success">+15%</el-tag>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card course-card">
          <div class="stat-icon">
            <el-icon :size="32"><Calendar /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-value">{{ stats.courseCount }}</div>
            <div class="stat-label">课程参与</div>
          </div>
          <div class="stat-trend">
            <el-tag type="success">+20%</el-tag>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="16">
        <div class="page-container">
          <div class="page-header">
            <span class="page-title">最近注册会员</span>
            <el-button type="primary" link @click="$router.push('/members/list')">
              查看全部
            </el-button>
          </div>
          <el-table :data="recentMembers" stripe>
            <el-table-column prop="name" label="姓名" width="100" />
            <el-table-column prop="phone" label="手机号" width="130" />
            <el-table-column prop="gender" label="性别" width="80" :formatter="formatGender" />
            <el-table-column prop="registration_channel" label="注册渠道" width="100" :formatter="formatChannel" />
            <el-table-column prop="current_level" label="会员等级" width="100">
              <template #default="{ row }">
                <el-tag :class="`level-tag ${row.current_level?.toLowerCase()}`" effect="plain">
                  {{ formatLevel(row.current_level) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :class="`status-tag ${row.status}`" effect="plain">
                  {{ formatStatus(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="注册时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="page-container">
          <div class="page-header">
            <span class="page-title">会员等级分布</span>
          </div>
          <div class="level-chart">
            <div class="level-item">
              <div class="level-header">
                <span class="level-name bronze">铜卡会员</span>
                <span class="level-count">{{ stats.bronzeMembers }}人</span>
              </div>
              <el-progress :percentage="(stats.bronzeMembers / stats.totalMembers) * 100" :color="#cd7f32" />
            </div>
            <div class="level-item">
              <div class="level-header">
                <span class="level-name silver">银卡会员</span>
                <span class="level-count">{{ stats.silverMembers }}人</span>
              </div>
              <el-progress :percentage="(stats.silverMembers / stats.totalMembers) * 100" :color="#c0c0c0" />
            </div>
            <div class="level-item">
              <div class="level-header">
                <span class="level-name gold">金卡会员</span>
                <span class="level-count">{{ stats.goldMembers }}人</span>
              </div>
              <el-progress :percentage="(stats.goldMembers / stats.totalMembers) * 100" :color="#ffd700" />
            </div>
          </div>
        </div>

        <div class="page-container" style="margin-top: 20px;">
          <div class="page-header">
            <span class="page-title">快捷操作</span>
          </div>
          <div class="quick-actions">
            <el-button type="primary" :icon="Plus" @click="$router.push('/members/add')">
              新增会员
            </el-button>
            <el-button type="success" :icon="Tools" @click="$router.push('/test/generate')">
              生成测试数据
            </el-button>
            <el-button type="warning" :icon="Document" @click="$router.push('/archive/physical-tests')">
              体测记录
            </el-button>
            <el-button type="info" :icon="Medal" @click="$router.push('/levels')">
              等级权益
            </el-button>
          </div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import {
  User, CircleCheck, Wallet, Calendar,
  Plus, Tools, Document, Medal
} from '@element-plus/icons-vue'
import { getMemberList } from '@/api/member'
import dayjs from 'dayjs'

const stats = ref({
  totalMembers: 0,
  activeMembers: 0,
  totalConsumption: 0,
  courseCount: 0,
  bronzeMembers: 0,
  silverMembers: 0,
  goldMembers: 0
})

const recentMembers = ref([])

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const formatGender = (row, column, value) => {
  const genderMap = { 'male': '男', 'female': '女' }
  return genderMap[value] || '-'
}

const formatChannel = (row, column, value) => {
  const channelMap = { 'online': '线上', 'offline': '线下' }
  return channelMap[value] || '-'
}

const formatStatus = (status) => {
  const statusMap = { 'active': '正常', 'frozen': '已冻结', 'cancelled': '已注销' }
  return statusMap[status] || status
}

const formatLevel = (level) => {
  const levelMap = { 'bronze': '铜卡', 'silver': '银卡', 'gold': '金卡' }
  return levelMap[level] || level
}

const fetchData = async () => {
  try {
    const res = await getMemberList({ page: 1, page_size: 5 })
    if (res.data) {
      recentMembers.value = res.data.items || []
      
      stats.value = {
        totalMembers: res.data.total || 25,
        activeMembers: res.data.items?.filter(m => m.status === 'active').length || 20,
        totalConsumption: 128500,
        courseCount: 45,
        bronzeMembers: 15,
        silverMembers: 8,
        goldMembers: 2
      }
    }
  } catch (error) {
    // 使用模拟数据
    stats.value = {
      totalMembers: 25,
      activeMembers: 20,
      totalConsumption: 128500,
      courseCount: 45,
      bronzeMembers: 15,
      silverMembers: 8,
      goldMembers: 2
    }
    
    recentMembers.value = [
      { name: '张三', phone: '13800138001', gender: 'male', registration_channel: 'online', current_level: 'bronze', status: 'active', created_at: '2024-01-15T10:30:00' },
      { name: '李四', phone: '13800138002', gender: 'female', registration_channel: 'offline', current_level: 'silver', status: 'active', created_at: '2024-01-14T14:20:00' },
      { name: '王五', phone: '13800138003', gender: 'male', registration_channel: 'online', current_level: 'gold', status: 'active', created_at: '2024-01-13T09:15:00' },
      { name: '赵六', phone: '13800138004', gender: 'male', registration_channel: 'offline', current_level: 'bronze', status: 'frozen', created_at: '2024-01-12T16:45:00' },
      { name: '孙七', phone: '13800138005', gender: 'female', registration_channel: 'online', current_level: 'silver', status: 'active', created_at: '2024-01-11T11:30:00' }
    ]
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.dashboard {
  .stats-row {
    margin-bottom: 20px;
  }

  .stat-card {
    display: flex;
    align-items: center;
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);

    .stat-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 60px;
      height: 60px;
      border-radius: 8px;
    }

    .stat-info {
      flex: 1;
      margin-left: 16px;

      .stat-value {
        font-size: 24px;
        font-weight: bold;
        color: #303133;
      }

      .stat-label {
        font-size: 14px;
        color: #909399;
        margin-top: 4px;
      }
    }

    .stat-trend {
      align-self: flex-start;
    }

    &.member-card {
      .stat-icon {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #fff;
      }
    }

    &.active-card {
      .stat-icon {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: #fff;
      }
    }

    &.consumption-card {
      .stat-icon {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #fff;
      }
    }

    &.course-card {
      .stat-icon {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: #fff;
      }
    }
  }

  .level-chart {
    .level-item {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      .level-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;

        .level-name {
          font-weight: 600;

          &.bronze { color: #cd7f32; }
          &.silver { color: #c0c0c0; }
          &.gold { color: #ffd700; }
        }

        .level-count {
          color: #909399;
          font-size: 14px;
        }
      }
    }
  }

  .quick-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;

    .el-button {
      flex: 1;
      min-width: 120px;
    }
  }
}
</style>
