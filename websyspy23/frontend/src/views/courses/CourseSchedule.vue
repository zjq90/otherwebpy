<template>
  <div class="course-schedule-page">
    <div class="page-header">
      <h2 class="page-title">课程排期</h2>
      <p class="page-desc">管理课程排期，支持时间冲突检测</p>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="日期">
          <el-date-picker
            v-model="searchForm.schedule_date"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="场地">
          <el-select v-model="searchForm.venue_id" placeholder="全部场地" clearable>
            <el-option
              v-for="item in venueList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="全部状态" clearable>
            <el-option label="已排班" value="scheduled" />
            <el-option label="已进行" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" @click="handleAdd">
            <el-icon><Plus /></el-icon>
            新增排期
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="course_name" label="课程名称" width="180" />
        <el-table-column prop="venue_name" label="场地" width="120" />
        <el-table-column prop="schedule_date" label="日期" width="120" />
        <el-table-column label="时间" width="180">
          <template #default="scope">
            {{ scope.row.start_time }} - {{ scope.row.end_time }}
          </template>
        </el-table-column>
        <el-table-column prop="instructor" label="教练" width="100" />
        <el-table-column label="预约情况" width="120">
          <template #default="scope">
            <el-progress
              :percentage="Math.round((scope.row.booked_count / scope.row.max_capacity) * 100)"
              :format="(percentage) => `${scope.row.booked_count}/${scope.row.max_capacity}`"
            />
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)" size="small">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link @click="handleView(scope.row)">
              详情
            </el-button>
            <el-button
              v-if="scope.row.status === 'scheduled'"
              type="danger"
              link
              @click="handleCancel(scope.row)"
            >
              取消
            </el-button>
            <el-button type="danger" link @click="handleDelete(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="课程" prop="course_id">
              <el-select
                v-model="formData.course_id"
                placeholder="请选择课程"
                style="width: 100%"
                @change="onCourseChange"
              >
                <el-option
                  v-for="item in courseList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="场地" prop="venue_id">
              <el-select
                v-model="formData.venue_id"
                placeholder="请选择场地"
                style="width: 100%"
              >
                <el-option
                  v-for="item in venueList"
                  :key="item.id"
                  :label="item.name"
                  :value="item.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="日期" prop="schedule_date">
              <el-date-picker
                v-model="formData.schedule_date"
                type="date"
                placeholder="选择日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="教练">
              <el-input v-model="formData.instructor" placeholder="请输入教练名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始时间" prop="start_time">
              <el-time-select
                v-model="formData.start_time"
                start="06:00"
                step="00:30"
                end="22:00"
                placeholder="开始时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束时间" prop="end_time">
              <el-time-select
                v-model="formData.end_time"
                start="06:00"
                step="00:30"
                end="22:30"
                placeholder="结束时间"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>其他设置</el-divider>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大预约人数" prop="max_capacity">
              <el-input-number
                v-model="formData.max_capacity"
                :min="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-select v-model="formData.status" style="width: 100%">
                <el-option label="已排班" value="scheduled" />
                <el-option label="已进行" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="2"
            placeholder="请输入备注信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="detailDialogVisible"
      title="排期详情"
      width="500px"
    >
      <el-descriptions :column="1" border v-if="currentSchedule">
        <el-descriptions-item label="课程名称">
          {{ currentSchedule.course_name }}
        </el-descriptions-item>
        <el-descriptions-item label="场地">
          {{ currentSchedule.venue_name }}
        </el-descriptions-item>
        <el-descriptions-item label="日期">
          {{ currentSchedule.schedule_date }}
        </el-descriptions-item>
        <el-descriptions-item label="时间">
          {{ currentSchedule.start_time }} - {{ currentSchedule.end_time }}
        </el-descriptions-item>
        <el-descriptions-item label="教练">
          {{ currentSchedule.instructor || '未指定' }}
        </el-descriptions-item>
        <el-descriptions-item label="最大容量">
          {{ currentSchedule.max_capacity }}人
        </el-descriptions-item>
        <el-descriptions-item label="已预约">
          {{ currentSchedule.booked_count }}人
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentSchedule.status)">
            {{ getStatusText(currentSchedule.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="备注" v-if="currentSchedule.notes">
          {{ currentSchedule.notes }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'
import { scheduleApi, courseApi, venueApi } from '@/api'

const loading = ref(false)
const tableData = ref([])
const courseList = ref([])
const venueList = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('新增排期')
const isEdit = ref(false)
const formRef = ref(null)
const currentSchedule = ref(null)

const searchForm = reactive({
  schedule_date: null,
  venue_id: null,
  status: null
})

const formData = reactive({
  course_id: null,
  venue_id: null,
  schedule_date: '',
  start_time: '',
  end_time: '',
  instructor: '',
  max_capacity: 20,
  status: 'scheduled',
  notes: ''
})

const formRules = {
  course_id: [
    { required: true, message: '请选择课程', trigger: 'change' }
  ],
  venue_id: [
    { required: true, message: '请选择场地', trigger: 'change' }
  ],
  schedule_date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ]
}

const getStatusType = (status) => {
  const types = {
    scheduled: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return types[status] || 'info'
}

const getStatusText = (status) => {
  const texts = {
    scheduled: '已排班',
    in_progress: '已进行',
    completed: '已完成',
    cancelled: '已取消'
  }
  return texts[status] || status
}

const fetchCourseList = async () => {
  try {
    const data = await courseApi.getList({ is_active: true })
    courseList.value = data
  } catch (error) {
    console.error('获取课程列表失败:', error)
  }
}

const fetchVenueList = async () => {
  try {
    const data = await venueApi.getList({ is_active: true })
    venueList.value = data
  } catch (error) {
    console.error('获取场地列表失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.schedule_date && searchForm.schedule_date.length === 2) {
      params.start_date = searchForm.schedule_date[0]
      params.end_date = searchForm.schedule_date[1]
    }
    if (searchForm.venue_id !== null) {
      params.venue_id = searchForm.venue_id
    }
    if (searchForm.status) {
      params.status = searchForm.status
    }
    const data = await scheduleApi.getList(params)
    tableData.value = data
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  fetchData()
}

const handleReset = () => {
  searchForm.schedule_date = null
  searchForm.venue_id = null
  searchForm.status = null
  fetchData()
}

const resetForm = () => {
  formData.course_id = null
  formData.venue_id = null
  formData.schedule_date = ''
  formData.start_time = ''
  formData.end_time = ''
  formData.instructor = ''
  formData.max_capacity = 20
  formData.status = 'scheduled'
  formData.notes = ''
}

const onCourseChange = (courseId) => {
  const course = courseList.value.find(item => item.id === courseId)
  if (course) {
    formData.max_capacity = course.max_capacity
    formData.instructor = course.instructor || ''
  }
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增排期'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑排期'
  formData.id = row.id
  formData.course_id = row.course_id
  formData.venue_id = row.venue_id
  formData.schedule_date = row.schedule_date
  formData.start_time = row.start_time
  formData.end_time = row.end_time
  formData.instructor = row.instructor || ''
  formData.max_capacity = row.max_capacity
  formData.status = row.status
  formData.notes = row.notes || ''
  dialogVisible.value = true
}

const handleView = (row) => {
  currentSchedule.value = row
  detailDialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await scheduleApi.update(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await scheduleApi.create(formData)
          ElMessage.success('创建成功')
        }
        dialogVisible.value = false
        fetchData()
      } catch (error) {
        if (error.response && error.response.data && error.response.data.detail) {
          ElMessage.error(error.response.data.detail)
        } else {
          console.error('提交失败:', error)
        }
      }
    }
  })
}

const handleCancel = (row) => {
  ElMessageBox.confirm(
    `确定要取消该排期吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await scheduleApi.update(row.id, { status: 'cancelled' })
      ElMessage.success('已取消')
      fetchData()
    } catch (error) {
      console.error('取消失败:', error)
    }
  }).catch(() => {})
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除该排期吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await scheduleApi.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchCourseList()
  fetchVenueList()
  fetchData()
})
</script>

<style scoped>
.course-schedule-page {
  height: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
