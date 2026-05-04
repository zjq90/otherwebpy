<template>
  <div class="course-list-page">
    <div class="page-header">
      <h2 class="page-title">课程列表</h2>
      <p class="page-desc">管理各类健身课程，支持团操课、私教课、定制课程等</p>
    </div>

    <div class="search-bar">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="课程类型">
          <el-select v-model="searchForm.course_type_id" placeholder="全部类型" clearable>
            <el-option
              v-for="item in courseTypeList"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="全部状态" clearable>
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
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
            新增课程
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <div class="table-container">
      <el-table :data="tableData" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="课程名称" width="180" />
        <el-table-column label="课程类型" width="120">
          <template #default="scope">
            <el-tag :type="getCourseTypeColor(scope.row.course_type_id)">
              {{ getCourseTypeName(scope.row.course_type_id) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="instructor" label="教练" width="120" />
        <el-table-column prop="duration" label="时长(分钟)" width="100" />
        <el-table-column prop="max_capacity" label="最大容量" width="100" />
        <el-table-column label="难度等级" width="120">
          <template #default="scope">
            <el-rate
              v-model="scope.row.difficulty_level"
              disabled
              show-text
              :texts="['入门', '初级', '中级', '高级', '专业']"
            />
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button type="primary" link @click="handleEdit(scope.row)">
              编辑
            </el-button>
            <el-button type="warning" link @click="handleView(scope.row)">
              详情
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
      width="700px"
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
            <el-form-item label="课程名称" prop="name">
              <el-input v-model="formData.name" placeholder="请输入课程名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="课程类型" prop="course_type_id">
              <el-select v-model="formData.course_type_id" placeholder="请选择课程类型" style="width: 100%">
                <el-option
                  v-for="item in courseTypeList"
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
            <el-form-item label="教练" prop="instructor">
              <el-input v-model="formData.instructor" placeholder="请输入教练名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="时长(分钟)" prop="duration">
              <el-input-number
                v-model="formData.duration"
                :min="1"
                style="width: 100%"
                placeholder="请输入时长"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="最大容量" prop="max_capacity">
              <el-input-number
                v-model="formData.max_capacity"
                :min="1"
                style="width: 100%"
                placeholder="请输入最大容量"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="难度等级">
              <el-rate
                v-model="formData.difficulty_level"
                show-text
                :texts="['入门', '初级', '中级', '高级', '专业']"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>课程详情</el-divider>
        <el-form-item label="适合人群">
          <el-input v-model="formData.suitable_for" placeholder="请输入适合人群描述" />
        </el-form-item>
        <el-form-item label="注意事项">
          <el-input
            v-model="formData.precautions"
            type="textarea"
            :rows="2"
            placeholder="请输入注意事项"
          />
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入课程描述"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="formData.is_active">
            <el-radio :value="true">启用</el-radio>
            <el-radio :value="false">禁用</el-radio>
          </el-radio-group>
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
      title="课程详情"
      width="500px"
    >
      <el-descriptions :column="1" border v-if="currentCourse">
        <el-descriptions-item label="课程名称">
          {{ currentCourse.name }}
        </el-descriptions-item>
        <el-descriptions-item label="课程类型">
          {{ getCourseTypeName(currentCourse.course_type_id) }}
        </el-descriptions-item>
        <el-descriptions-item label="教练">
          {{ currentCourse.instructor || '未指定' }}
        </el-descriptions-item>
        <el-descriptions-item label="时长">
          {{ currentCourse.duration }}分钟
        </el-descriptions-item>
        <el-descriptions-item label="最大容量">
          {{ currentCourse.max_capacity }}人
        </el-descriptions-item>
        <el-descriptions-item label="难度等级">
          <el-rate
            v-model="currentCourse.difficulty_level"
            disabled
            show-text
            :texts="['入门', '初级', '中级', '高级', '专业']"
          />
        </el-descriptions-item>
        <el-descriptions-item label="适合人群" v-if="currentCourse.suitable_for">
          {{ currentCourse.suitable_for }}
        </el-descriptions-item>
        <el-descriptions-item label="注意事项" v-if="currentCourse.precautions">
          {{ currentCourse.precautions }}
        </el-descriptions-item>
        <el-descriptions-item label="描述" v-if="currentCourse.description">
          {{ currentCourse.description }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="currentCourse.is_active ? 'success' : 'danger'">
            {{ currentCourse.is_active ? '启用' : '禁用' }}
          </el-tag>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { courseApi, courseTypeApi } from '@/api'

const loading = ref(false)
const tableData = ref([])
const courseTypeList = ref([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const dialogTitle = ref('新增课程')
const isEdit = ref(false)
const formRef = ref(null)
const currentCourse = ref(null)

const searchForm = reactive({
  course_type_id: null,
  is_active: null
})

const formData = reactive({
  name: '',
  course_type_id: null,
  instructor: '',
  duration: 60,
  max_capacity: 20,
  difficulty_level: 3,
  suitable_for: '',
  precautions: '',
  description: '',
  is_active: true
})

const formRules = {
  name: [
    { required: true, message: '请输入课程名称', trigger: 'blur' }
  ],
  course_type_id: [
    { required: true, message: '请选择课程类型', trigger: 'change' }
  ],
  duration: [
    { required: true, message: '请输入时长', trigger: 'blur' }
  ],
  max_capacity: [
    { required: true, message: '请输入最大容量', trigger: 'blur' }
  ]
}

const getCourseTypeName = (id) => {
  const type = courseTypeList.value.find(item => item.id === id)
  return type ? type.name : '未知'
}

const getCourseTypeColor = (id) => {
  const colors = {
    1: 'primary',
    2: 'success',
    3: 'warning'
  }
  return colors[id] || 'info'
}

const fetchCourseTypes = async () => {
  try {
    const data = await courseTypeApi.getList({ is_active: true })
    courseTypeList.value = data
  } catch (error) {
    console.error('获取课程类型失败:', error)
  }
}

const fetchData = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchForm.course_type_id !== null) {
      params.course_type_id = searchForm.course_type_id
    }
    if (searchForm.is_active !== null) {
      params.is_active = searchForm.is_active
    }
    const data = await courseApi.getList(params)
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
  searchForm.course_type_id = null
  searchForm.is_active = null
  fetchData()
}

const resetForm = () => {
  formData.name = ''
  formData.course_type_id = null
  formData.instructor = ''
  formData.duration = 60
  formData.max_capacity = 20
  formData.difficulty_level = 3
  formData.suitable_for = ''
  formData.precautions = ''
  formData.description = ''
  formData.is_active = true
}

const handleAdd = () => {
  isEdit.value = false
  dialogTitle.value = '新增课程'
  resetForm()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  dialogTitle.value = '编辑课程'
  formData.id = row.id
  formData.name = row.name
  formData.course_type_id = row.course_type_id
  formData.instructor = row.instructor || ''
  formData.duration = row.duration
  formData.max_capacity = row.max_capacity
  formData.difficulty_level = row.difficulty_level
  formData.suitable_for = row.suitable_for || ''
  formData.precautions = row.precautions || ''
  formData.description = row.description || ''
  formData.is_active = row.is_active
  dialogVisible.value = true
}

const handleView = (row) => {
  currentCourse.value = row
  detailDialogVisible.value = true
}

const handleSubmit = async () => {
  await formRef.value?.validate(async (valid) => {
    if (valid) {
      try {
        if (isEdit.value) {
          await courseApi.update(formData.id, formData)
          ElMessage.success('更新成功')
        } else {
          await courseApi.create(formData)
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

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除课程"${row.name}"吗？`,
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      await courseApi.delete(row.id)
      ElMessage.success('删除成功')
      fetchData()
    } catch (error) {
      console.error('删除失败:', error)
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchCourseTypes()
  fetchData()
})
</script>

<style scoped>
.course-list-page {
  height: 100%;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>
