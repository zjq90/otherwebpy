<template>
  <div class="physical-tests">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">体测数据</span>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          新增体测
        </el-button>
      </div>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="会员姓名">
          <el-input v-model="searchForm.member_name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="测试日期">
          <el-date-picker
            v-model="searchForm.date_range"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :icon="Search" @click="handleSearch">搜索</el-button>
          <el-button :icon="Refresh" @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 数据表格 -->
      <el-table :data="tableData" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="member_name" label="会员姓名" width="100" />
        <el-table-column prop="test_date" label="测试日期" width="120">
          <template #default="{ row }">
            {{ formatDate(row.test_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="height" label="身高(cm)" width="100" />
        <el-table-column prop="weight" label="体重(kg)" width="100" />
        <el-table-column prop="bmi" label="BMI" width="80">
          <template #default="{ row }">
            <el-tag :type="getBmiType(row.bmi)">
              {{ row.bmi }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="body_fat" label="体脂率(%)" width="100" />
        <el-table-column prop="muscle_mass" label="肌肉量(kg)" width="100" />
        <el-table-column prop="basal_metabolism" label="基础代谢" width="100" />
        <el-table-column prop="notes" label="备注" min-width="150" show-overflow-tooltip />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link :icon="Edit" @click="handleEdit(row)">编辑</el-button>
              <el-button type="danger" link :icon="Delete" @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
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
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑体测数据' : '新增体测数据'"
      width="600px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="会员" prop="member_id">
          <el-select
            v-model="form.member_id"
            placeholder="请选择会员"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="member in memberOptions"
              :key="member.id"
              :label="member.name"
              :value="member.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="测试日期" prop="test_date">
          <el-date-picker
            v-model="form.test_date"
            type="date"
            placeholder="请选择测试日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="身高(cm)">
              <el-input-number
                v-model="form.height"
                :min="0"
                :max="300"
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="体重(kg)">
              <el-input-number
                v-model="form.weight"
                :min="0"
                :max="500"
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="体脂率(%)">
              <el-input-number
                v-model="form.body_fat"
                :min="0"
                :max="100"
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="肌肉量(kg)">
              <el-input-number
                v-model="form.muscle_mass"
                :min="0"
                :max="200"
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="基础代谢">
          <el-input-number
            v-model="form.basal_metabolism"
            :min="0"
            :max="10000"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="form.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search, Refresh, Edit, Delete } from '@element-plus/icons-vue'
import {
  getPhysicalTests, createPhysicalTest, updatePhysicalTest, deletePhysicalTest
} from '@/api/archive'
import { getMemberList } from '@/api/member'
import dayjs from 'dayjs'

const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const searchForm = reactive({
  member_name: '',
  date_range: []
})

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0
})

const tableData = ref([])
const memberOptions = ref([])

const form = reactive({
  member_id: null,
  test_date: '',
  height: null,
  weight: null,
  body_fat: null,
  muscle_mass: null,
  basal_metabolism: null,
  notes: ''
})

const rules = {
  member_id: [
    { required: true, message: '请选择会员', trigger: 'change' }
  ],
  test_date: [
    { required: true, message: '请选择测试日期', trigger: 'change' }
  ]
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

const getBmiType = (bmi) => {
  if (!bmi) return 'info'
  if (bmi < 18.5) return 'warning'
  if (bmi < 24) return 'success'
  if (bmi < 28) return 'warning'
  return 'danger'
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await getPhysicalTests({
      page: pagination.page,
      page_size: pagination.pageSize
    })
    if (res.data) {
      tableData.value = res.data.items || []
      pagination.total = res.data.total || 0
    }
  } catch (error) {
    // 使用模拟数据
    tableData.value = [
      { id: 1, member_name: '张三', test_date: '2024-01-20', height: 175, weight: 75, bmi: 24.5, body_fat: 18.5, muscle_mass: 35.2, basal_metabolism: 1750, notes: '首次体测' },
      { id: 2, member_name: '李四', test_date: '2024-02-15', height: 165, weight: 58, bmi: 21.3, body_fat: 22.1, muscle_mass: 28.5, basal_metabolism: 1450, notes: '定期体测' },
      { id: 3, member_name: '王五', test_date: '2024-02-20', height: 175, weight: 73, bmi: 23.8, body_fat: 17.2, muscle_mass: 36.1, basal_metabolism: 1780, notes: '体脂率下降' }
    ]
    pagination.total = 3
  } finally {
    loading.value = false
  }
}

const fetchMembers = async () => {
  try {
    const res = await getMemberList({ page_size: 100 })
    if (res.data) {
      memberOptions.value = res.data.items || []
    }
  } catch (error) {
    memberOptions.value = [
      { id: 1, name: '张三' },
      { id: 2, name: '李四' },
      { id: 3, name: '王五' }
    ]
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchData()
}

const handleReset = () => {
  searchForm.member_name = ''
  searchForm.date_range = []
  handleSearch()
}

const resetForm = () => {
  form.member_id = null
  form.test_date = ''
  form.height = null
  form.weight = null
  form.body_fat = null
  form.muscle_mass = null
  form.basal_metabolism = null
  form.notes = ''
}

const handleAdd = () => {
  isEdit.value = false
  resetForm()
  fetchMembers()
  dialogVisible.value = true
}

const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(form, row)
  fetchMembers()
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该体测数据吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deletePhysicalTest(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (isEdit.value) {
      await updatePhysicalTest(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await createPhysicalTest(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchData()
  } catch (error) {
    ElMessage.error(isEdit.value ? '更新失败' : '创建失败')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.physical-tests {
  .search-form {
    margin-bottom: 20px;
    padding: 20px;
    background-color: #f5f7fa;
    border-radius: 4px;
  }

  .pagination-wrapper {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
