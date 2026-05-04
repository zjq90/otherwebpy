<template>
  <div class="home-page">
    <div class="page-header">
      <h2 class="page-title">欢迎使用会员管理系统</h2>
      <p class="page-desc">一站式会员管理、卡项管理、课程管理解决方案</p>
    </div>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stats-card card-1">
          <div class="stats-content">
            <div class="stats-info">
              <div class="stats-value">{{ stats.members }}</div>
              <div class="stats-label">会员总数</div>
            </div>
            <div class="stats-icon">
              <el-icon size="40"><User /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card card-2">
          <div class="stats-content">
            <div class="stats-info">
              <div class="stats-value">{{ stats.cards }}</div>
              <div class="stats-label">卡项数量</div>
            </div>
            <div class="stats-icon">
              <el-icon size="40"><CreditCard /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card card-3">
          <div class="stats-content">
            <div class="stats-info">
              <div class="stats-value">{{ stats.courses }}</div>
              <div class="stats-label">课程数量</div>
            </div>
            <div class="stats-icon">
              <el-icon size="40"><VideoCamera /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stats-card card-4">
          <div class="stats-content">
            <div class="stats-info">
              <div class="stats-value">{{ stats.schedules }}</div>
              <div class="stats-label">今日排期</div>
            </div>
            <div class="stats-icon">
              <el-icon size="40"><Calendar /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">快速操作</span>
          </template>
          <el-row :gutter="20">
            <el-col :span="12">
              <router-link to="/cards/list" class="quick-action">
                <el-card shadow="hover" class="action-card">
                  <div class="action-content">
                    <el-icon size="36" color="#409EFF"><CreditCard /></el-icon>
                    <span>卡项管理</span>
                  </div>
                </el-card>
              </router-link>
            </el-col>
            <el-col :span="12">
              <router-link to="/courses/schedules" class="quick-action">
                <el-card shadow="hover" class="action-card">
                  <div class="action-content">
                    <el-icon size="36" color="#67C23A"><Calendar /></el-icon>
                    <span>课程排期</span>
                  </div>
                </el-card>
              </router-link>
            </el-col>
            <el-col :span="12" style="margin-top: 20px;">
              <router-link to="/members/list" class="quick-action">
                <el-card shadow="hover" class="action-card">
                  <div class="action-content">
                    <el-icon size="36" color="#E6A23C"><User /></el-icon>
                    <span>会员管理</span>
                  </div>
                </el-card>
              </router-link>
            </el-col>
            <el-col :span="12" style="margin-top: 20px;">
              <router-link to="/venues" class="quick-action">
                <el-card shadow="hover" class="action-card">
                  <div class="action-content">
                    <el-icon size="36" color="#909399"><OfficeBuilding /></el-icon>
                    <span>场地管理</span>
                  </div>
                </el-card>
              </router-link>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-title">系统功能说明</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="卡项管理">
              支持年卡、月卡、次卡、储值卡、私教包等多种卡型，可自定义价格、有效期、包含权益、续费规则。
            </el-descriptions-item>
            <el-descriptions-item label="课程管理">
              支持团操课（瑜伽、动感单车）、私教课和定制课程的创建与排班，系统自动检测时间与场地冲突。
            </el-descriptions-item>
            <el-descriptions-item label="会员管理">
              支持会员信息管理、会员卡管理、课程预约等功能，完整的会员生命周期管理。
            </el-descriptions-item>
            <el-descriptions-item label="技术架构">
              后端：Python + FastAPI + SQLite + SQLAlchemy<br/>
              前端：Vue 3 + Element Plus + Axios
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { reactive } from 'vue'

const stats = reactive({
  members: 0,
  cards: 0,
  courses: 0,
  schedules: 0
})
</script>

<style scoped>
.home-page {
  height: 100%;
}

.stats-row {
  margin-bottom: 20px;
}

.stats-card {
  border-radius: 8px;
  overflow: hidden;
}

.stats-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stats-info {
  display: flex;
  flex-direction: column;
}

.stats-value {
  font-size: 32px;
  font-weight: bold;
  color: #fff;
}

.stats-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 8px;
}

.stats-icon {
  color: rgba(255, 255, 255, 0.3);
}

.card-1 {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-2 {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-3 {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.card-4 {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.card-title {
  font-size: 16px;
  font-weight: bold;
}

.quick-action {
  text-decoration: none;
  color: inherit;
}

.action-card {
  cursor: pointer;
}

.action-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 20px 0;
}

.action-content span {
  font-size: 14px;
  color: #606266;
}
</style>
