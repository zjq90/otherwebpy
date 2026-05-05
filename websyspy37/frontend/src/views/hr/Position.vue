<template>
  <div class="page-content">
    <el-card class="content-card">
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span style="font-weight: bold; font-size: 16px;">职位管理</span>
          <el-button type="primary" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增职位
          </el-button>
        </div>
      </template>

      <el-table :data="tableData" border stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="职位名称" width="150" />
        <el-table-column prop="code" label="职位编码" width="120" />
        <el-table-column prop="department_id" label="所属部门ID" width="120" />
        <el-table-column prop="level" label="职级" width="100" />
        <el-table-column prop="description" label="描述" min-width="200" />
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
  ElMessage.info('新增职位功能开发中')
}

const loadData = async () => {
  loading.value = true
  try {
    const result = await api.getPositions()
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
