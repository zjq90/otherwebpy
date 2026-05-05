<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">账户管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增账户
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="账户名称" width="150" />
        <el-table-column prop="account_no" label="账户号" width="200" />
        <el-table-column prop="bank_name" label="开户行" width="150" />
        <el-table-column prop="balance" label="余额" width="120">
          <template #default="scope">
            <span style="color: #409eff; font-weight: bold;">
              ¥{{ scope.row.balance?.toFixed(2) || '0.00' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.status === '启用' ? 'success' : 'danger'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { Plus } from '@element-plus/icons-vue'

const loading = ref(false)
const tableData = ref([])

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const handleAdd = () => {
  ElMessage.info('新增账户功能开发中')
}

const loadData = async () => {
  loading.value = true
  try {
    const result = await api.getAccounts()
    tableData.value = Array.isArray(result) ? result : []
  } catch (error) {
    console.error('加载数据失败:', error)
    tableData.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
