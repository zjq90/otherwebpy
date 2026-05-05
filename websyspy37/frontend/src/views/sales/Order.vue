<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">订单管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增订单
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="order_no" label="订单编号" width="200" />
        <el-table-column prop="customer_id" label="客户ID" width="100" />
        <el-table-column prop="total_amount" label="订单金额" width="120">
          <template #default="scope">
            ¥{{ scope.row.total_amount?.toFixed(2) || '0.00' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
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
import { ref, reactive, onMounted } from 'vue'
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

const getStatusType = (status) => {
  switch (status) {
    case '已完成':
      return 'success'
    case '已取消':
      return 'danger'
    case '已发货':
      return 'warning'
    default:
      return 'info'
  }
}

const handleAdd = () => {
  ElMessage.info('新增订单功能开发中')
}

const loadData = async () => {
  loading.value = true
  try {
    const result = await api.getOrders()
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
