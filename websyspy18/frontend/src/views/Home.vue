/**
 * 首页
 * 显示系统概览和快捷入口
 */
<template>
  <div class="home-page">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6" v-for="item in statistics" :key="item.title">
        <el-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-content">
            <div class="stat-icon" :style="{ backgroundColor: item.color }">
              <el-icon :size="24"><component :is="item.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ item.value }}</div>
              <div class="stat-title">{{ item.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 快捷操作 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-header-title">快捷操作</span>
          </template>
          <el-row :gutter="15">
            <el-col :span="6" v-for="item in quickActions" :key="item.name">
              <div class="quick-item" @click="goTo(item.path)">
                <el-icon :size="32" :color="item.color"><component :is="item.icon" /></el-icon>
                <span class="quick-name">{{ item.name }}</span>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>

      <!-- 待办事项 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <span class="card-header-title">待办事项</span>
          </template>
          <el-table :data="todos" style="width: 100%" size="small">
            <el-table-column prop="title" label="事项" width="300" />
            <el-table-column prop="type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag :type="row.tagType" size="small">{{ row.type }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="priority" label="优先级" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.priority === '高'" type="danger" size="small">高</el-tag>
                <el-tag v-else-if="row.priority === '中'" type="warning" size="small">中</el-tag>
                <el-tag v-else type="info" size="small">低</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="deadline" label="截止日期" width="120" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 统计数据
const statistics = ref([
  { title: '设备总数', value: '12', icon: 'Tools', color: '#409EFF' },
  { title: '待审批申请', value: '3', icon: 'Document', color: '#E6A23C' },
  { title: '合同数', value: '8', icon: 'Notebook', color: '#67C23A' },
  { title: '待处理故障', value: '2', icon: 'Warning', color: '#F56C6C' }
])

// 快捷操作
const quickActions = ref([
  { name: '设备管理', icon: 'Tools', path: '/equipment/list', color: '#409EFF' },
  { name: '装修申请', icon: 'House', path: '/decoration/application', color: '#67C23A' },
  { name: '合同管理', icon: 'Notebook', path: '/contract/list', color: '#E6A23C' },
  { name: '故障维修', icon: 'Warning', path: '/equipment/fault', color: '#F56C6C' }
])

// 待办事项
const todos = ref([
  { title: 'A栋101室装修申请审批', type: '装修管理', tagType: 'success', priority: '高', deadline: '2024-01-15' },
  { title: '1号电梯月度巡检', type: '工程维保', tagType: 'primary', priority: '中', deadline: '2024-01-18' },
  { title: '消防水泵故障维修', type: '工程维保', tagType: 'danger', priority: '高', deadline: '2024-01-16' },
  { title: '保洁公司合同到期提醒', type: '合同管理', tagType: 'warning', priority: '中', deadline: '2024-01-20' }
])

// 路由跳转
const goTo = (path) => {
  router.push(path)
}
</script>

<style scoped>
.home-page {
  min-height: 100%;
}

.stat-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.stat-content {
  display: flex;
  align-items: center;
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
  margin-left: 15px;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

.card-header-title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.quick-item {
  text-align: center;
  padding: 20px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-item:hover {
  background-color: #f5f7fa;
}

.quick-name {
  display: block;
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
}
</style>
