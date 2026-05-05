<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">投诉反馈</span>
    </div>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="反馈类型">
          <el-select v-model="searchForm.feedback_type" placeholder="全部" clearable>
            <el-option label="投诉" :value="0" />
            <el-option label="建议" :value="1" />
            <el-option label="咨询" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="待处理" :value="0" />
            <el-option label="处理中" :value="1" />
            <el-option label="已处理" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">
            <el-icon><Refresh /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="table-container">
      <el-table :data="tableData" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="feedback_type" label="类型" align="center">
          <template #default="{ row }">
            <el-tag :type="typeMap[row.feedback_type]">
              {{ typeLabelMap[row.feedback_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="content" label="内容" min-width="300" show-overflow-tooltip />
        <el-table-column prop="contact" label="联系方式" width="120" />
        <el-table-column prop="status" label="状态" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]">
              {{ statusLabelMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right" align="center">
          <template #default="{ row }">
            <el-button 
              type="primary" 
              link 
              size="small" 
              @click="handleReply(row)"
              :disabled="row.status >= 2"
            >
              回复
            </el-button>
            <el-button type="info" link size="small" @click="handleView(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="fetchData"
          @current-change="fetchData"
        />
      </div>
    </el-card>
    
    <el-dialog v-model="replyVisible" title="回复反馈" width="600px">
      <el-descriptions :column="1" border class="mb-20">
        <el-descriptions-item label="标题">{{ currentFeedback.title }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="typeMap[currentFeedback.feedback_type]">
            {{ typeLabelMap[currentFeedback.feedback_type] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentFeedback.content }}</el-descriptions-item>
      </el-descriptions>
      
      <el-form label-width="80px">
        <el-form-item label="当前状态">
          <el-tag :type="statusTypeMap[currentFeedback.status]">
            {{ statusLabelMap[currentFeedback.status] }}
          </el-tag>
        </el-form-item>
        <el-form-item label="回复内容">
          <el-input
            v-model="replyForm.reply"
            type="textarea"
            :rows="4"
            placeholder="请输入回复内容"
          />
        </el-form-item>
        <el-form-item label="更新状态">
          <el-select v-model="replyForm.status" placeholder="请选择状态">
            <el-option label="处理中" :value="1" />
            <el-option label="已处理" :value="2" />
            <el-option label="已关闭" :value="3" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="replyVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmitReply">提交</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="detailVisible" title="反馈详情" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ currentFeedback.id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentFeedback.user_id }}</el-descriptions-item>
        <el-descriptions-item label="类型">
          <el-tag :type="typeMap[currentFeedback.feedback_type]">
            {{ typeLabelMap[currentFeedback.feedback_type] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="标题">{{ currentFeedback.title }}</el-descriptions-item>
        <el-descriptions-item label="内容">{{ currentFeedback.content }}</el-descriptions-item>
        <el-descriptions-item label="联系方式">{{ currentFeedback.contact || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="statusTypeMap[currentFeedback.status]">
            {{ statusLabelMap[currentFeedback.status] }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ formatDate(currentFeedback.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="回复内容" v-if="currentFeedback.reply">
          {{ currentFeedback.reply }}
        </el-descriptions-item>
        <el-descriptions-item label="回复时间" v-if="currentFeedback.reply_time">
          {{ formatDate(currentFeedback.reply_time) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import { getFeedbackList, updateFeedback } from '@/api'

const loading = ref(false)
const replyVisible = ref(false)
const detailVisible = ref(false)

const tableData = ref([])
const currentFeedback = ref({})

const searchForm = reactive({
  feedback_type: null,
  status: null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const replyForm = reactive({
  reply: '',
  status: 2
})

const typeMap = {
  0: 'danger',
  1: 'warning',
  2: 'info'
}

const typeLabelMap = {
  0: '投诉',
  1: '建议',
  2: '咨询'
}

const statusTypeMap = {
  0: 'danger',
  1: 'warning',
  2: 'success',
  3: 'info'
}

const statusLabelMap = {
  0: '待处理',
  1: '处理中',
  2: '已处理',
  3: '已关闭'
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    
    const res = await getFeedbackList(params)
    const data = res.data || {}
    tableData.value = data.list || []
    pagination.total = data.total || 0
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.feedback_type = null
  searchForm.status = null
  pagination.page = 1
  fetchData()
}

const handleReply = (row) => {
  currentFeedback.value = { ...row }
  replyForm.reply = row.reply || ''
  replyForm.status = row.status === 0 ? 1 : row.status
  replyVisible.value = true
}

const handleView = (row) => {
  currentFeedback.value = { ...row }
  detailVisible.value = true
}

const handleSubmitReply = async () => {
  try {
    const data = {
      reply: replyForm.reply,
      status: replyForm.status,
      reply_user_id: 1
    }
    
    await updateFeedback(currentFeedback.value.id, data)
    ElMessage.success('回复成功')
    replyVisible.value = false
    fetchData()
  } catch (error) {
    console.error('回复失败:', error)
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.search-form {
  .el-form-item {
    margin-right: 0;
  }
}

.mb-20 {
  margin-bottom: 20px;
}
</style>
