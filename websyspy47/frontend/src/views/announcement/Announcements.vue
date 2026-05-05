<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">公告管理</span>
      <el-button type="primary" @click="handleAdd">
        <el-icon><Plus /></el-icon>
        新增公告
      </el-button>
    </div>
    
    <el-card class="search-bar">
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="公告标题">
          <el-input v-model="searchForm.title" placeholder="请输入标题" clearable />
        </el-form-item>
        <el-form-item label="公告类型">
          <el-select v-model="searchForm.type" placeholder="全部" clearable>
            <el-option label="系统公告" :value="0" />
            <el-option label="活动公告" :value="1" />
            <el-option label="环保资讯" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部" clearable>
            <el-option label="草稿" :value="0" />
            <el-option label="已发布" :value="1" />
            <el-option label="已撤回" :value="2" />
          </el-select>
        </el-form-item>
        <el-form-item label="是否置顶">
          <el-select v-model="searchForm.is_top" placeholder="全部" clearable>
            <el-option label="是" :value="1" />
            <el-option label="否" :value="0" />
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
        <el-table-column prop="id" label="ID" width="60" align="center" />
        <el-table-column prop="title" label="公告标题" min-width="200">
          <template #default="{ row }">
            <div class="title-cell">
              <el-tag v-if="row.is_top === 1" type="danger" size="small" effect="dark" class="mr-5">置顶</el-tag>
              <span>{{ row.title }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="公告类型" align="center" width="100">
          <template #default="{ row }">
            <el-tag :type="typeTagMap[row.type]">
              {{ typeLabelMap[row.type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="summary" label="摘要" min-width="150" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.summary || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览次数" align="center" width="100">
          <template #default="{ row }">
            <el-tag type="info">{{ row.view_count || 0 }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" align="center" width="90">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]">
              {{ statusLabelMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publish_time" label="发布时间" width="160">
          <template #default="{ row }">
            {{ formatDate(row.publish_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleView(row)">
              预览
            </el-button>
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button 
              v-if="row.status === 0"
              type="success" 
              link 
              size="small" 
              @click="handlePublish(row)"
            >
              发布
            </el-button>
            <el-button 
              v-if="row.status === 1"
              type="warning" 
              link 
              size="small" 
              @click="handleRevoke(row)"
            >
              撤回
            </el-button>
            <el-button 
              type="danger" 
              link 
              size="small" 
              @click="handleDelete(row)"
              :disabled="row.status === 2"
            >
              删除
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
    
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="公告标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入公告标题" maxlength="100" show-word-limit />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="公告类型" prop="type">
              <el-select v-model="form.type" placeholder="请选择公告类型" style="width: 100%">
                <el-option label="系统公告" :value="0" />
                <el-option label="活动公告" :value="1" />
                <el-option label="环保资讯" :value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否置顶">
              <el-radio-group v-model="form.is_top">
                <el-radio :value="1">是</el-radio>
                <el-radio :value="0">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="封面图片">
          <el-input v-model="form.cover_image" placeholder="请输入封面图片URL" />
        </el-form-item>
        <el-form-item label="公告摘要">
          <el-input 
            v-model="form.summary" 
            type="textarea" 
            :rows="2" 
            placeholder="请输入公告摘要（不超过200字）"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="公告内容" prop="content">
          <el-input 
            v-model="form.content" 
            type="textarea" 
            :rows="8" 
            placeholder="请输入公告内容"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="排序">
              <el-input-number v-model="form.sort_order" :min="0" :max="999" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-radio-group v-model="form.status">
                <el-radio :value="0">草稿</el-radio>
                <el-radio :value="1">发布</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
    
    <el-dialog v-model="previewVisible" title="公告预览" width="700px">
      <div class="announcement-preview">
        <div class="preview-header">
          <h2>{{ currentAnnouncement.title }}</h2>
          <div class="preview-meta">
            <el-tag :type="typeTagMap[currentAnnouncement.type]">
              {{ typeLabelMap[currentAnnouncement.type] }}
            </el-tag>
            <span v-if="currentAnnouncement.is_top === 1" class="ml-10">
              <el-tag type="danger" effect="dark">置顶</el-tag>
            </span>
            <span class="ml-10">浏览次数: {{ currentAnnouncement.view_count || 0 }}</span>
            <span class="ml-10">发布时间: {{ formatDate(currentAnnouncement.publish_time) }}</span>
          </div>
        </div>
        <el-divider />
        <div class="preview-content" v-if="currentAnnouncement.cover_image">
          <el-image 
            :src="currentAnnouncement.cover_image" 
            fit="cover"
            style="width: 100%; max-height: 300px; border-radius: 8px;"
          />
        </div>
        <div class="preview-summary" v-if="currentAnnouncement.summary">
          <h4>摘要：</h4>
          <p>{{ currentAnnouncement.summary }}</p>
        </div>
        <div class="preview-body">
          <h4>内容：</h4>
          <div class="content-text">
            {{ currentAnnouncement.content }}
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { 
  getAnnouncementList, 
  createAnnouncement, 
  updateAnnouncement, 
  deleteAnnouncement,
  publishAnnouncement,
  getAnnouncementById
} from '@/api'

const loading = ref(false)
const dialogVisible = ref(false)
const previewVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const tableData = ref([])
const currentAnnouncement = ref({})

const searchForm = reactive({
  title: '',
  type: null,
  status: null,
  is_top: null
})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const form = reactive({
  title: '',
  type: 0,
  is_top: 0,
  cover_image: '',
  summary: '',
  content: '',
  sort_order: 0,
  status: 0
})

const rules = {
  title: [
    { required: true, message: '请输入公告标题', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择公告类型', trigger: 'change' }
  ],
  content: [
    { required: true, message: '请输入公告内容', trigger: 'blur' }
  ]
}

const typeTagMap = {
  0: 'primary',
  1: 'success',
  2: 'warning'
}

const typeLabelMap = {
  0: '系统公告',
  1: '活动公告',
  2: '环保资讯'
}

const statusTypeMap = {
  0: 'info',
  1: 'success',
  2: 'warning'
}

const statusLabelMap = {
  0: '草稿',
  1: '已发布',
  2: '已撤回'
}

const dialogTitle = ref('新增公告')

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
    
    const res = await getAnnouncementList(params)
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
  searchForm.title = ''
  searchForm.type = null
  searchForm.status = null
  searchForm.is_top = null
  pagination.page = 1
  fetchData()
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增公告'
  form.title = ''
  form.type = 0
  form.is_top = 0
  form.cover_image = ''
  form.summary = ''
  form.content = ''
  form.sort_order = 0
  form.status = 0
  delete form.id
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑公告'
  form.id = row.id
  form.title = row.title
  form.type = row.type
  form.is_top = row.is_top || 0
  form.cover_image = row.cover_image || ''
  form.summary = row.summary || ''
  form.content = row.content || ''
  form.sort_order = row.sort_order || 0
  form.status = row.status
  dialogVisible.value = true
}

const handleView = async (row) => {
  try {
    const res = await getAnnouncementById(row.id)
    currentAnnouncement.value = res.data || {}
    previewVisible.value = true
  } catch (error) {
    console.error('获取详情失败:', error)
  }
}

const handlePublish = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要发布公告 "${row.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await publishAnnouncement(row.id)
    ElMessage.success('发布成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('发布失败:', error)
    }
  }
}

const handleRevoke = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要撤回公告 "${row.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await updateAnnouncement(row.id, { status: 2 })
    ElMessage.success('撤回成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('撤回失败:', error)
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定要删除公告 "${row.title}" 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteAnnouncement(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
    }
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = { ...form }
        
        if (isEdit.value) {
          await updateAnnouncement(form.id, submitData)
          ElMessage.success('更新成功')
        } else {
          await createAnnouncement(submitData)
          ElMessage.success('创建成功')
        }
        
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        console.error('提交失败:', error)
      }
    }
  })
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

.title-cell {
  display: flex;
  align-items: center;
  
  .mr-5 {
    margin-right: 5px;
  }
}

.announcement-preview {
  .preview-header {
    text-align: center;
    
    h2 {
      margin-bottom: 15px;
      color: #303133;
    }
    
    .preview-meta {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      color: #909399;
      font-size: 14px;
      
      .ml-10 {
        margin-left: 10px;
      }
    }
  }
  
  .preview-summary,
  .preview-body {
    h4 {
      color: #606266;
      margin-bottom: 10px;
    }
    
    p {
      color: #606266;
      line-height: 1.8;
    }
  }
  
  .content-text {
    white-space: pre-wrap;
    line-height: 2;
    color: #303133;
  }
}
</style>
