<template>
  <div class="member-detail">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">会员详情</span>
        <div class="header-actions">
          <el-button :icon="Edit" @click="$router.push(`/members/edit/${memberId}`)">编辑</el-button>
          <el-button :icon="ArrowLeft" @click="$router.back()">返回</el-button>
        </div>
      </div>

      <div v-loading="loading">
        <!-- 基本信息卡片 -->
        <el-card class="info-card">
          <template #header>
            <div class="card-header">
              <span>基本信息</span>
              <div class="status-tags">
                <el-tag :class="`level-tag ${member.current_level?.toLowerCase()}`" effect="plain">
                  {{ formatLevel(member.current_level) }}
                </el-tag>
                <el-tag :class="`status-tag ${member.status}`" effect="plain">
                  {{ formatStatus(member.status) }}
                </el-tag>
              </div>
            </div>
          </template>
          
          <el-descriptions :column="4" border>
            <el-descriptions-item label="姓名">{{ member.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="手机号">{{ member.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ formatGender(member.gender) }}</el-descriptions-item>
            <el-descriptions-item label="邮箱">{{ member.email || '-' }}</el-descriptions-item>
            
            <el-descriptions-item label="身份证号">{{ member.id_card || '-' }}</el-descriptions-item>
            <el-descriptions-item label="出生日期">{{ member.birth_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="注册渠道">{{ formatChannel(member.registration_channel) }}</el-descriptions-item>
            <el-descriptions-item label="注册日期">{{ formatDate(member.registration_date) }}</el-descriptions-item>
            
            <el-descriptions-item label="紧急联系人">{{ member.emergency_contact || '-' }}</el-descriptions-item>
            <el-descriptions-item label="紧急电话">{{ member.emergency_phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="联系地址" :span="2">{{ member.address || '-' }}</el-descriptions-item>
            
            <el-descriptions-item label="总消费金额">¥{{ (member.total_consumption || 0).toLocaleString() }}</el-descriptions-item>
            <el-descriptions-item label="健身次数">{{ member.workout_count || 0 }}次</el-descriptions-item>
            <el-descriptions-item label="是否实名认证">
              <el-tag :type="member.is_verified ? 'success' : 'info'">
                {{ member.is_verified ? '已认证' : '未认证' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="注册时间">{{ formatDate(member.created_at) }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 健康状况卡片 -->
        <el-card class="info-card" style="margin-top: 20px;">
          <template #header>
            <span>健康状况</span>
          </template>
          
          <el-descriptions :column="4" border>
            <el-descriptions-item label="身高">{{ member.height ? member.height + 'cm' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="体重">{{ member.weight ? member.weight + 'kg' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="BMI">{{ calculateBMI(member.height, member.weight) }}</el-descriptions-item>
            <el-descriptions-item label="血型">{{ member.blood_type || '-' }}</el-descriptions-item>
            
            <el-descriptions-item label="过敏史">
              <el-tag :type="member.has_allergies ? 'danger' : 'info'">
                {{ member.has_allergies ? '有' : '无' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="过敏详情" :span="3">{{ member.allergy_details || '无' }}</el-descriptions-item>
            
            <el-descriptions-item label="既往病史" :span="4">{{ member.medical_history || '无' }}</el-descriptions-item>
            <el-descriptions-item label="健康备注" :span="4">{{ member.health_remarks || '无' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 快捷操作 -->
        <el-card class="info-card" style="margin-top: 20px;">
          <template #header>
            <span>快捷操作</span>
          </template>
          
          <div class="quick-actions">
            <el-button type="primary" @click="addPhysicalTest">
              <template #icon><Document /></template>
              添加体测数据
            </el-button>
            <el-button type="success" @click="addConsumption">
              <template #icon><Wallet /></template>
              添加消费记录
            </el-button>
            <el-button type="warning" @click="addCourse">
              <template #icon><Calendar /></template>
              记录课程参与
            </el-button>
            
            <el-divider direction="vertical" />
            
            <el-button
              v-if="member.status === 'active'"
              type="warning"
              @click="handleFreeze"
            >
              <template #icon><Lock /></template>
              冻结账户
            </el-button>
            <el-button
              v-if="member.status === 'frozen'"
              type="success"
              @click="handleUnfreeze"
            >
              <template #icon><Unlock /></template>
              解冻账户
            </el-button>
            <el-button
              v-if="member.status !== 'cancelled'"
              type="danger"
              @click="handleDelete"
            >
              <template #icon><Delete /></template>
              注销账户
            </el-button>
          </div>
        </el-card>

        <!-- 档案标签页 -->
        <el-card class="info-card" style="margin-top: 20px;">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="体测记录" name="physical">
              <el-table :data="physicalTests" stripe>
                <el-table-column prop="test_date" label="测试日期" width="120">
                  <template #default="{ row }">
                    {{ formatDate(row.test_date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="height" label="身高(cm)" width="100" />
                <el-table-column prop="weight" label="体重(kg)" width="100" />
                <el-table-column prop="bmi" label="BMI" width="80" />
                <el-table-column prop="body_fat" label="体脂率(%)" width="100" />
                <el-table-column prop="muscle_mass" label="肌肉量(kg)" width="100" />
                <el-table-column prop="basal_metabolism" label="基础代谢" width="100" />
                <el-table-column prop="notes" label="备注" />
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="消费记录" name="consumption">
              <el-table :data="consumptions" stripe>
                <el-table-column prop="consumption_date" label="消费日期" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.consumption_date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="consumption_type" label="消费类型" width="120">
                  <template #default="{ row }">
                    <el-tag size="small">{{ row.consumption_type }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="amount" label="消费金额" width="120">
                  <template #default="{ row }">
                    ¥{{ (row.amount || 0).toLocaleString() }}
                  </template>
                </el-table-column>
                <el-table-column prop="discount_amount" label="折扣金额" width="120">
                  <template #default="{ row }">
                    ¥{{ (row.discount_amount || 0).toLocaleString() }}
                  </template>
                </el-table-column>
                <el-table-column prop="payment_method" label="支付方式" width="100" />
                <el-table-column prop="notes" label="备注" />
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="运动目标" name="goal">
              <el-table :data="fitnessGoals" stripe>
                <el-table-column prop="goal_type" label="目标类型" width="120" />
                <el-table-column prop="description" label="目标描述" width="200" />
                <el-table-column prop="target_value" label="目标值" width="100" />
                <el-table-column prop="current_value" label="当前值" width="100" />
                <el-table-column prop="start_date" label="开始日期" width="120">
                  <template #default="{ row }">
                    {{ formatDate(row.start_date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="target_date" label="目标日期" width="120">
                  <template #default="{ row }">
                    {{ formatDate(row.target_date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="status" label="状态" width="100">
                  <template #default="{ row }">
                    <el-tag :type="row.status === 'completed' ? 'success' : 'warning'">
                      {{ row.status === 'completed' ? '已完成' : '进行中' }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="课程参与" name="course">
              <el-table :data="courses" stripe>
                <el-table-column prop="course_name" label="课程名称" width="150" />
                <el-table-column prop="course_date" label="参与日期" width="150">
                  <template #default="{ row }">
                    {{ formatDate(row.course_date) }}
                  </template>
                </el-table-column>
                <el-table-column prop="instructor" label="教练" width="100" />
                <el-table-column prop="duration_minutes" label="时长(分钟)" width="100" />
                <el-table-column prop="calories_burned" label="消耗卡路里" width="100" />
                <el-table-column prop="notes" label="备注" />
              </el-table>
            </el-tab-pane>
            
            <el-tab-pane label="状态变更日志" name="log">
              <el-table :data="statusLogs" stripe>
                <el-table-column prop="old_status" label="原状态" width="120">
                  <template #default="{ row }">
                    <el-tag :class="`status-tag ${row.old_status}`" effect="plain">
                      {{ formatStatus(row.old_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="new_status" label="新状态" width="120">
                  <template #default="{ row }">
                    <el-tag :class="`status-tag ${row.new_status}`" effect="plain">
                      {{ formatStatus(row.new_status) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="reason" label="变更原因" />
                <el-table-column prop="operator" label="操作人" width="120" />
                <el-table-column prop="created_at" label="操作时间" width="180">
                  <template #default="{ row }">
                    {{ formatDate(row.created_at) }}
                  </template>
                </el-table-column>
              </el-table>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Edit, ArrowLeft, Document, Wallet, Calendar, Lock, Unlock, Delete
} from '@element-plus/icons-vue'
import {
  getMemberDetail, freezeMember, unfreezeMember, deleteMember, getStatusLogs
} from '@/api/member'
import {
  getMemberPhysicalTests, getMemberConsumptions, getMemberFitnessGoals, getMemberCourseParticipations
} from '@/api/archive'
import dayjs from 'dayjs'

const route = useRoute()

const loading = ref(false)
const activeTab = ref('physical')
const memberId = computed(() => route.params.id)

const member = ref({})
const physicalTests = ref([])
const consumptions = ref([])
const fitnessGoals = ref([])
const courses = ref([])
const statusLogs = ref([])

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

const formatGender = (value) => {
  const genderMap = { 'male': '男', 'female': '女' }
  return genderMap[value] || '-'
}

const formatChannel = (value) => {
  const channelMap = { 'online': '线上', 'offline': '线下' }
  return channelMap[value] || '-'
}

const formatStatus = (status) => {
  const statusMap = { 'active': '正常', 'frozen': '已冻结', 'cancelled': '已注销' }
  return statusMap[status] || status
}

const formatLevel = (level) => {
  const levelMap = { 'bronze': '铜卡', 'silver': '银卡', 'gold': '金卡' }
  return levelMap[level] || level
}

const calculateBMI = (height, weight) => {
  if (!height || !weight) return '-'
  const bmi = weight / ((height / 100) ** 2)
  return bmi.toFixed(1)
}

const fetchData = async () => {
  loading.value = true
  try {
    const [memberRes, physicalRes, consumptionRes, goalRes, courseRes, logRes] = await Promise.all([
      getMemberDetail(memberId.value),
      getMemberPhysicalTests(memberId.value),
      getMemberConsumptions(memberId.value),
      getMemberFitnessGoals(memberId.value),
      getMemberCourseParticipations(memberId.value),
      getStatusLogs(memberId.value)
    ])
    
    if (memberRes.data) member.value = memberRes.data
    if (physicalRes.data) physicalTests.value = physicalRes.data || []
    if (consumptionRes.data) consumptions.value = consumptionRes.data || []
    if (goalRes.data) fitnessGoals.value = goalRes.data || []
    if (courseRes.data) courses.value = courseRes.data || []
    if (logRes.data) statusLogs.value = logRes.data || []
  } catch (error) {
    // 使用模拟数据
    member.value = {
      id: 1,
      name: '张三',
      phone: '13800138001',
      gender: 'male',
      email: 'zhangsan@example.com',
      id_card: '110101199001011234',
      birth_date: '1990-01-01',
      registration_channel: 'online',
      registration_date: '2024-01-15',
      emergency_contact: '张父',
      emergency_phone: '13900139001',
      address: '北京市朝阳区XXX街道XXX号',
      height: 175,
      weight: 75,
      blood_type: 'A',
      has_allergies: false,
      allergy_details: '',
      medical_history: '',
      health_remarks: '',
      current_level: 'silver',
      status: 'active',
      total_consumption: 8500,
      workout_count: 45,
      is_verified: true,
      created_at: '2024-01-15T10:30:00'
    }
    
    physicalTests.value = [
      { test_date: '2024-01-20', height: 175, weight: 75, bmi: 24.5, body_fat: 18.5, muscle_mass: 35.2, basal_metabolism: 1750, notes: '首次体测' },
      { test_date: '2024-02-20', height: 175, weight: 73, bmi: 23.8, body_fat: 17.2, muscle_mass: 36.1, basal_metabolism: 1780, notes: '体脂率下降' }
    ]
    
    consumptions.value = [
      { consumption_date: '2024-01-15', consumption_type: '会员卡', amount: 5000, discount_amount: 0, payment_method: '微信支付', notes: '办理年卡' },
      { consumption_date: '2024-02-10', consumption_type: '私教课', amount: 3000, discount_amount: 300, payment_method: '支付宝', notes: '购买10节私教课' },
      { consumption_date: '2024-03-05', consumption_type: '营养品', amount: 500, discount_amount: 50, payment_method: '现金', notes: '购买蛋白粉' }
    ]
    
    fitnessGoals.value = [
      { goal_type: '减重', description: '三个月减重5kg', target_value: 70, current_value: 73, start_date: '2024-01-15', target_date: '2024-04-15', status: 'in_progress' },
      { goal_type: '增肌', description: '增加肌肉量2kg', target_value: 38, current_value: 36.1, start_date: '2024-02-01', target_date: '2024-05-01', status: 'in_progress' }
    ]
    
    courses.value = [
      { course_name: '动感单车', course_date: '2024-01-20', instructor: '王教练', duration_minutes: 45, calories_burned: 350, notes: '强度适中' },
      { course_name: '力量训练', course_date: '2024-01-22', instructor: '李教练', duration_minutes: 60, calories_burned: 400, notes: '腿部训练' },
      { course_name: '瑜伽', course_date: '2024-01-25', instructor: '张教练', duration_minutes: 60, calories_burned: 200, notes: '放松训练' }
    ]
    
    statusLogs.value = [
      { old_status: null, new_status: 'active', reason: '新会员注册', operator: '系统', created_at: '2024-01-15T10:30:00' }
    ]
  } finally {
    loading.value = false
  }
}

const addPhysicalTest = () => {
  ElMessage.info('添加体测数据功能')
}

const addConsumption = () => {
  ElMessage.info('添加消费记录功能')
}

const addCourse = () => {
  ElMessage.info('记录课程参与功能')
}

const handleFreeze = async () => {
  try {
    await ElMessageBox.confirm(`确定要冻结会员「${member.value.name}」的账户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await freezeMember(memberId.value, '管理员冻结')
    ElMessage.success('账户已冻结')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('冻结失败')
    }
  }
}

const handleUnfreeze = async () => {
  try {
    await ElMessageBox.confirm(`确定要解冻会员「${member.value.name}」的账户吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    await unfreezeMember(memberId.value, '管理员解冻')
    ElMessage.success('账户已解冻')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('解冻失败')
    }
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm(`确定要注销会员「${member.value.name}」的账户吗？此操作不可恢复。`, '警告', {
      confirmButtonText: '确定注销',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteMember(memberId.value)
    ElMessage.success('账户已注销')
    fetchData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('注销失败')
    }
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style lang="scss" scoped>
.member-detail {
  .info-card {
    :deep(.el-card__header) {
      padding: 15px 20px;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .status-tags {
      display: flex;
      gap: 10px;
    }
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }

  .quick-actions {
    display: flex;
    align-items: center;
    gap: 15px;
    flex-wrap: wrap;
  }
}
</style>
