<template>
  <div>
    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff">
              <el-icon :size="32"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_projects }}</div>
              <div class="stat-label">物业项目数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon :size="32"><House /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_properties }}</div>
              <div class="stat-label">房产总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_owners }}</div>
              <div class="stat-label">业主/住户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.vacant_properties }}</div>
              <div class="stat-label">空置房产</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 房产状态分布 -->
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">房产状态分布</span>
          </template>
          <div class="status-chart">
            <div class="status-item">
              <div class="status-info">
                <span class="status-dot" style="background: #e6a23c"></span>
                <span class="status-name">空置</span>
                <span class="status-count">{{ stats.vacant_properties }} 套</span>
              </div>
              <el-progress
                :percentage="getPercentage(stats.vacant_properties, stats.total_properties)"
                :color="'#e6a23c'"
                :stroke-width="10"
              />
            </div>
            <div class="status-item">
              <div class="status-info">
                <span class="status-dot" style="background: #409eff"></span>
                <span class="status-name">出租</span>
                <span class="status-count">{{ stats.rented_properties }} 套</span>
              </div>
              <el-progress
                :percentage="getPercentage(stats.rented_properties, stats.total_properties)"
                :color="'#409eff'"
                :stroke-width="10"
              />
            </div>
            <div class="status-item">
              <div class="status-info">
                <span class="status-dot" style="background: #67c23a"></span>
                <span class="status-name">自住</span>
                <span class="status-count">{{ stats.occupied_properties }} 套</span>
              </div>
              <el-progress
                :percentage="getPercentage(stats.occupied_properties, stats.total_properties)"
                :color="'#67c23a'"
                :stroke-width="10"
              />
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">快捷操作</span>
          </template>
          <div class="quick-actions">
            <router-link to="/property-projects">
              <el-button type="primary" size="large" :icon="OfficeBuilding">
                物业项目管理
              </el-button>
            </router-link>
            <router-link to="/properties">
              <el-button type="success" size="large" :icon="House">
                房产信息管理
              </el-button>
            </router-link>
            <router-link to="/owners">
              <el-button type="warning" size="large" :icon="User">
                业主/住户管理
              </el-button>
            </router-link>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { dashboardApi } from '@/api'

const stats = ref({
  total_projects: 0,
  total_properties: 0,
  total_owners: 0,
  vacant_properties: 0,
  rented_properties: 0,
  occupied_properties: 0
})

const getPercentage = (part, total) => {
  if (!total) return 0
  return Math.round((part / total) * 100)
}

const loadStats = async () => {
  try {
    const res = await dashboardApi.getStats()
    stats.value = res
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
}

.status-chart {
  padding: 10px 0;
}

.status-item {
  margin-bottom: 25px;
}

.status-item:last-child {
  margin-bottom: 0;
}

.status-info {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.status-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  margin-right: 10px;
}

.status-name {
  font-size: 14px;
  color: #606266;
}

.status-count {
  font-size: 14px;
  color: #909399;
  margin-left: auto;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 20px 0;
}

.quick-actions a {
  text-decoration: none;
}

.quick-actions .el-button {
  width: 100%;
  justify-content: center;
}
</style>
