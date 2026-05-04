<template>
  <div class="status-logs">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">状态变更日志</span>
      </div>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="会员姓名">
          <el-input v-model="searchForm.member_name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="原状态">
          <el-select v-model="searchForm.old_status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="active" />
            <el-option label="已冻结" value="frozen" />
            <el-option label="已注销" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="新状态">
          <el-select v-model="searchForm.new_status" placeholder="请选择状态" clearable>
            <el-option label="正常" value="active" />
            <el-option label="已冻结" value="frozen" />
            <el-option label="已注销" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 时间线展示 -->
      <el-timeline>
        <el-timeline-item
          v-for="(log, index) in logs"
          :key="log.id"
          :type="getLogType(log.new_status)"
          :timestamp="formatDate(log.created_at)"
          placement="top"
        >
          <el-card>
            <div class="log-header">
              <div class="log-title">
                <el-tag :class="`status-tag ${log.old_status}`" effect="plain" v-if="log.old_status">
                  {{ formatStatus(log.old_status) }}
                </el-tag>
                <el-icon :size="16" color="#409EFF"><Right /></el-icon>
                <el-tag :class="`status-tag ${log.new_status}`" effect="plain">
                  {{ formatStatus(log.new_status) }}
                </el-tag>
              </div>
              <div class="log-info">
                <el-tag size="small" type="info">{{ log.member_name || '未知会员' }}</el-tag>
                <span class="operator">操作人: {{ log.operator || '系统' }}</span>
              </div>
            </div>
            <el-divider style="margin: 12px 0;" />
            <div class="log-content">
              <p><strong>变更原因:</strong> {{ log.reason || '无' }}</p>
              <p v-if="log.notes"><strong>备注:</strong> {{ log.notes }}</p>
            </div>
          </el-card>
        </el-timeline-item>
      </el-timeline>

      <!-- 分页 -->
      <div class="pagination-wrapper" v-if="pagination.total > 0">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>

      <el-empty v-if="logs.length === 0 && !loading" description="暂无状态变更记录" />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search, Refresh, Right } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const loading = ref(false)

const searchForm = reactive({
  member_name: '',
  old_status: '',
  new_status: ''
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const logs = ref([])

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const formatStatus = (status) => {
  const statusMap = { 'active': '正常', 'frozen': '已冻结', 'cancelled': '已注销' }
  return statusMap[status] || status
}

const getLogType = (newStatus) => {
  const typeMap = {
    'active': 'success',
    'frozen': 'warning',
    'cancelled': 'danger'
  }
  return typeMap[newStatus] || 'info'
}

const fetchData = async () => {
  loading.value = true
  try {
    // 模拟数据
    logs.value = [
      {
        id: 1,
        member_name: '赵六',
        old_status: 'active',
        new_status: 'frozen',
        reason: '账户异常，暂时冻结',
        operator: '管理员',
        notes: '',
        created_at: '2024-02-15T10:30:00'
      },
      {
        id: 2,
        member_name: '张三',
        old_status: null,
        new_status: 'active',
        reason: '新会员注册',
        operator: '系统',
        notes: '线上注册',
        created_at: '2024-01-15T10:30:00'
      }
    ]
    pagination.total = 2
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.member_name = ''
  searchForm.old_status = ''
  searchForm.new_status = ''
  handleSearch()
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.status-logs {
  .search-form {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }

  .log-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .log-title {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .log-info {
      display: flex;
      align-items: center;
      gap: 15px;

      .operator {
        font-size: 14px;
        color: #909399;
      }
    }
  }

  .log-content {
    p {
      margin: 5px 0;
      font-size: 14px;
      color: #606266;
    }
  }

  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
