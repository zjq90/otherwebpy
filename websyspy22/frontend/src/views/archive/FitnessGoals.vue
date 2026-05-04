<template>
  <div class="fitness-goals">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">运动目标</span>
        <el-button type="primary" :icon="Plus" @click="handleAdd">
          新增目标
        </el-button>
      </div>

      <!-- 统计卡片 -->
      <el-row :gutter="20" style="margin-bottom: 20px;">
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">总目标数</div>
              <div class="stat-value">{{ stats.total }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">进行中</div>
              <div class="stat-value" style="color: #e6a23c;">{{ stats.inProgress }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">已完成</div>
              <div class="stat-value" style="color: #67c23a;">{{ stats.completed }}</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card>
            <div class="stat-item">
              <div class="stat-label">完成率</div>
              <div class="stat-value">{{ stats.completionRate }}%</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 目标卡片展示 -->
      <el-row :gutter="20">
        <el-col :span="8" v-for="goal in goals" :key="goal.id">
          <el-card class="goal-card" :class="{ 'completed-card': goal.status === 'completed' }">
            <template #header>
              <div class="goal-header">
                <span class="goal-type">{{ goal.goal_type }}</span>
                <el-tag :type="goal.status === 'completed' ? 'success' : 'warning'">
                  {{ goal.status === 'completed' ? '已完成' : '进行中' }}
                </el-tag>
              </div>
            </template>
            
            <div class="goal-content">
              <p class="goal-description">{{ goal.description }}</p>
              
              <div class="goal-progress">
                <div class="progress-info">
                  <span>当前: {{ goal.current_value }}</span>
                  <span>目标: {{ goal.target_value }}</span>
                </div>
                <el-progress
                  :percentage="calculateProgress(goal)"
                  :status="goal.status === 'completed' ? 'success' : ''"
                />
              </div>

              <el-divider style="margin: 12px 0;" />
              
              <div class="goal-dates">
                <div>
                  <span class="label">开始日期:</span>
                  <span>{{ formatDate(goal.start_date) }}</span>
                </div>
                <div>
                  <span class="label">目标日期:</span>
                  <span>{{ formatDate(goal.target_date) }}</span>
                </div>
              </div>
            </div>

            <template #footer>
              <div class="goal-actions">
                <el-button size="small" type="primary" link @click="handleEdit(goal)">编辑</el-button>
                <el-button
                  v-if="goal.status !== 'completed'"
                  size="small"
                  type="success"
                  link
                  @click="handleComplete(goal)"
                >完成目标</el-button>
                <el-button size="small" type="danger" link @click="handleDelete(goal)">删除</el-button>
              </div>
            </template>
          </el-card>
        </el-col>
      </el-row>

      <el-empty v-if="goals.length === 0" description="暂无运动目标" />
    </div>

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑运动目标' : '新增运动目标'"
      width="500px"
    >
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="100px"
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
        <el-form-item label="目标类型" prop="goal_type">
          <el-select v-model="form.goal_type" placeholder="请选择目标类型" style="width: 100%">
            <el-option label="减重" value="减重" />
            <el-option label="增肌" value="增肌" />
            <el-option label="体脂率" value="体脂率" />
            <el-option label="耐力" value="耐力" />
            <el-option label="其他" value="其他" />
          </el-select>
        </el-form-item>
        <el-form-item label="目标描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="2"
            placeholder="请输入目标描述"
          />
        </el-form-item>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="目标值" prop="target_value">
              <el-input-number
                v-model="form.target_value"
                :min="0"
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="当前值">
              <el-input-number
                v-model="form.current_value"
                :min="0"
                :precision="1"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="开始日期" prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="请选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="目标日期" prop="target_date">
              <el-date-picker
                v-model="form.target_date"
                type="date"
                placeholder="请选择目标日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
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
import { Plus } from '@element-plus/icons-vue'
import { getMemberList } from '@/api/member'
import dayjs from 'dayjs'

const submitting = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)

const stats = reactive({
  total: 2,
  inProgress: 2,
  completed: 0,
  completionRate: 0
})

const goals = ref([])
const memberOptions = ref([])

const form = reactive({
  member_id: null,
  goal_type: '',
  description: '',
  target_value: 0,
  current_value: 0,
  start_date: '',
  target_date: '',
  status: 'in_progress'
})

const rules = {
  member_id: [
    { required: true, message: '请选择会员', trigger: 'change' }
  ],
  goal_type: [
    { required: true, message: '请选择目标类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入目标描述', trigger: 'blur' }
  ],
  target_value: [
    { required: true, message: '请输入目标值', trigger: 'blur' }
  ]
}

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD')
}

const calculateProgress = (goal) => {
  if (!goal.target_value || goal.target_value === 0) return 0
  const progress = (goal.current_value / goal.target_value) * 100
  return Math.min(Math.round(progress), 100)
}

const fetchData = async () => {
  // 模拟数据
  goals.value = [
    {
      id: 1,
      member_id: 1,
      member_name: '张三',
      goal_type: '减重',
      description: '三个月减重5kg',
      target_value: 70,
      current_value: 73,
      start_date: '2024-01-15',
      target_date: '2024-04-15',
      status: 'in_progress'
    },
    {
      id: 2,
      member_id: 1,
      member_name: '张三',
      goal_type: '增肌',
      description: '增加肌肉量2kg',
      target_value: 38,
      current_value: 36.1,
      start_date: '2024-02-01',
      target_date: '2024-05-01',
      status: 'in_progress'
    }
  ]
  
  stats.total = goals.value.length
  stats.inProgress = goals.value.filter(g => g.status === 'in_progress').length
  stats.completed = goals.value.filter(g => g.status === 'completed').length
  stats.completionRate = stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0
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

const resetForm = () => {
  form.member_id = null
  form.goal_type = ''
  form.description = ''
  form.target_value = 0
  form.current_value = 0
  form.start_date = ''
  form.target_date = ''
  form.status = 'in_progress'
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

const handleComplete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要标记该目标为已完成吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    row.status = 'completed'
    ElMessage.success('目标已完成')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该运动目标吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
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
    ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
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
.fitness-goals {
  .stat-item {
    text-align: center;

    .stat-label {
      font-size: 14px;
      color: #909399;
    }

    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      margin-top: 8px;
    }
  }

  .goal-card {
    margin-bottom: 20px;

    &.completed-card {
      opacity: 0.7;
    }

    :deep(.el-card__header) {
      padding: 12px 20px;
    }

    :deep(.el-card__footer) {
      padding: 10px 20px;
      background-color: #fafafa;
    }

    .goal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .goal-type {
        font-size: 16px;
        font-weight: 600;
        color: #409EFF;
      }
    }

    .goal-content {
      .goal-description {
        font-size: 14px;
        color: #606266;
        margin-bottom: 15px;
        line-height: 1.6;
      }

      .goal-progress {
        .progress-info {
          display: flex;
          justify-content: space-between;
          margin-bottom: 8px;
          font-size: 13px;
          color: #909399;
        }
      }

      .goal-dates {
        font-size: 13px;
        color: #909399;

        .label {
          margin-right: 5px;
        }

        div + div {
          margin-top: 5px;
        }
      }
    }

    .goal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }
  }
}
</style>
