<template>
  <div class="page-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <span class="page-title">续费提醒管理</span>
      <div style="display: flex; gap: 10px">
        <el-button type="primary" @click="generateReminders">
          <el-icon><Plus /></el-icon>
          生成到期提醒
        </el-button>
        <el-button type="success" @click="sendPendingReminders">
          <el-icon><Promotion /></el-icon>
          发送待发送提醒
        </el-button>
      </div>
    </div>

    <!-- 搜索区域 -->
    <div class="search-area">
      <div class="search-row">
        <el-select v-model="searchForm.reminder_type" placeholder="提醒类型" clearable style="width: 150px">
          <el-option label="到期前7天" value="seven_days" />
          <el-option label="到期前3天" value="three_days" />
        </el-select>
        <el-select v-model="searchForm.status" placeholder="提醒状态" clearable style="width: 150px">
          <el-option label="待发送" value="pending" />
          <el-option label="已发送" value="sent" />
          <el-option label="发送失败" value="failed" />
          <el-option label="已续费" value="renewed" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
        <el-button @click="resetSearch">
          <el-icon><Refresh /></el-icon>
          重置
        </el-button>
      </div>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" v-loading="loading" border stripe>
      <el-table-column prop="reminder_type" label="提醒类型" width="120">
        <template #default="{ row }">
          <el-tag>{{ getReminderTypeText(row.reminder_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="channel" label="发送渠道" width="100">
        <template #default="{ row }">
          {{ getChannelText(row.channel) }}
        </template>
      </el-table-column>
      <el-table-column prop="scheduled_time" label="计划发送时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.scheduled_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="sent_time" label="实际发送时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.sent_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <span class="status-tag" :class="getStatusClass(row.status)">
            {{ getStatusText(row.status) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="renewal_method" label="续费方式" width="120">
        <template #default="{ row }">
          {{ getRenewalMethodText(row.renewal_method) }}
        </template>
      </el-table-column>
      <el-table-column prop="renewed_at" label="续费时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.renewed_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="message_content" label="消息内容" min-width="200" show-overflow-tooltip />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <div class="action-buttons">
            <el-button 
              type="primary" 
              link 
              @click="markAsSent(row)" 
              :disabled="row.status !== 'pending'"
            >
              标记已发送
            </el-button>
            <el-button 
              type="success" 
              link 
              @click="markAsRenewed(row, 'offline')" 
              :disabled="row.status === 'renewed'"
            >
              到店续费
            </el-button>
            <el-button 
              type="warning" 
              link 
              @click="markAsRenewed(row, 'online')" 
              :disabled="row.status === 'renewed'"
            >
              线上续费
            </el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div style="margin-top: 20px; text-align: right">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Promotion } from '@element-plus/icons-vue'
import { reminderApi } from '../../api'

const loading = ref(false)

const tableData = ref([])

const searchForm = reactive({
  reminder_type: '',
  status: ''
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

// 获取提醒类型显示文本
const getReminderTypeText = (type) => {
  const map = {
    seven_days: '到期前7天',
    three_days: '到期前3天'
  }
  return map[type] || type
}

// 获取渠道显示文本
const getChannelText = (channel) => {
  const map = {
    sms: '短信',
    wechat: '微信',
    app: 'APP推送',
    email: '邮件'
  }
  return map[channel] || channel
}

// 获取状态显示文本
const getStatusText = (status) => {
  const map = {
    pending: '待发送',
    sent: '已发送',
    failed: '发送失败',
    renewed: '已续费'
  }
  return map[status] || status
}

// 获取状态样式类
const getStatusClass = (status) => {
  const map = {
    pending: 'status-pending',
    sent: 'status-sent',
    failed: 'status-inactive',
    renewed: 'status-renewed'
  }
  return map[status] || ''
}

// 获取续费方式显示文本
const getRenewalMethodText = (method) => {
  if (!method) return '-'
  const map = {
    offline: '到店续费',
    online: '线上续费'
  }
  return map[method] || method
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size
    }
    if (searchForm.reminder_type) params.reminder_type = searchForm.reminder_type
    if (searchForm.status) params.status = searchForm.status

    const data = await reminderApi.getList(params)
    tableData.value = data.items
    pagination.total = data.total
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadData()
}

// 重置搜索
const resetSearch = () => {
  searchForm.reminder_type = ''
  searchForm.status = ''
  pagination.page = 1
  loadData()
}

// 生成到期提醒
const generateReminders = async () => {
  try {
    await ElMessageBox.confirm('确定要为即将到期的会员卡生成提醒吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    const result = await reminderApi.generateForExpiring()
    ElMessage.success(result.message)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('生成提醒失败:', error)
    }
  }
}

// 发送待发送提醒
const sendPendingReminders = async () => {
  try {
    await ElMessageBox.confirm('确定要发送所有待发送的提醒吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    const result = await reminderApi.sendPending()
    ElMessage.success(result.message)
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发送提醒失败:', error)
    }
  }
}

// 标记已发送
const markAsSent = async (row) => {
  try {
    await ElMessageBox.confirm('确定要标记为已发送吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await reminderApi.markAsSent(row.id)
    ElMessage.success('标记成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('标记失败:', error)
    }
  }
}

// 标记已续费
const markAsRenewed = async (row, method) => {
  try {
    const methodText = method === 'offline' ? '到店续费' : '线上续费'
    await ElMessageBox.confirm(`确定要标记为${methodText}吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    await reminderApi.markAsRenewed(row.id, method)
    ElMessage.success('标记成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('标记失败:', error)
    }
  }
}

onMounted(() => {
  loadData()
})
</script>
