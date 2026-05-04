<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">首页概览</h2>
      <el-button type="primary" @click="handleGenerateTestData">
        <el-icon><Plus /></el-icon>
        生成测试数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <el-row :gutter="20" style="margin-bottom: 20px;">
      <el-col :span="6">
        <div class="stat-card blue">
          <div class="stat-title">总教练数</div>
          <div class="stat-value">{{ stats.coachCount }}</div>
          <div class="stat-unit">位</div>
          <div class="stat-trend up">
            <el-icon><TrendCharts /></el-icon>
            <span>在职教练: {{ stats.activeCoachCount }}</span>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card green">
          <div class="stat-title">总会员数</div>
          <div class="stat-value">{{ stats.memberCount }}</div>
          <div class="stat-unit">位</div>
          <div class="stat-trend up">
            <el-icon><TrendCharts /></el-icon>
            <span>有效会员: {{ stats.activeMemberCount }}</span>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card orange">
          <div class="stat-title">今日课时</div>
          <div class="stat-value">{{ stats.todayLessons }}</div>
          <div class="stat-unit">节</div>
          <div class="stat-trend up">
            <el-icon><TrendCharts /></el-icon>
            <span>本月累计: {{ stats.monthLessons }} 节</span>
          </div>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="stat-card purple">
          <div class="stat-title">本月收入</div>
          <div class="stat-value">¥{{ formatNumber(stats.monthRevenue) }}</div>
          <div class="stat-unit">元</div>
          <div class="stat-trend up">
            <el-icon><TrendCharts /></el-icon>
            <span>教练提成: ¥{{ formatNumber(stats.monthCommission) }}</span>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <el-card style="margin-bottom: 20px;">
      <template #header>
        <span>快捷操作</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="4">
          <el-button type="primary" plain style="width: 100%; height: 60px;" @click="$router.push('/coach/list')">
            <el-icon :size="20"><UserFilled /></el-icon>
            <div style="margin-top: 5px;">教练管理</div>
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button type="success" plain style="width: 100%; height: 60px;" @click="$router.push('/member/list')">
            <el-icon :size="20"><Team /></el-icon>
            <div style="margin-top: 5px;">会员管理</div>
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button type="warning" plain style="width: 100%; height: 60px;" @click="$router.push('/lesson/records')">
            <el-icon :size="20"><Calendar /></el-icon>
            <div style="margin-top: 5px;">课时记录</div>
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button type="danger" plain style="width: 100%; height: 60px;" @click="$router.push('/member/packages')">
            <el-icon :size="20"><ShoppingCart /></el-icon>
            <div style="margin-top: 5px;">课程包管理</div>
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button type="info" plain style="width: 100%; height: 60px;" @click="$router.push('/performance')">
            <el-icon :size="20"><DataAnalysis /></el-icon>
            <div style="margin-top: 5px;">业绩追踪</div>
          </el-button>
        </el-col>
        <el-col :span="4">
          <el-button type="primary" plain style="width: 100%; height: 60px;" @click="$router.push('/test')">
            <el-icon :size="20"><Tools /></el-icon>
            <div style="margin-top: 5px;">测试工具</div>
          </el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 最近课时记录 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>最近课时记录</span>
            <el-button text type="primary" style="float: right;" @click="$router.push('/lesson/records')">
              查看全部
            </el-button>
          </template>
          <el-table :data="recentLessons" style="width: 100%" v-loading="loading">
            <el-table-column prop="record_no" label="记录编号" width="180" />
            <el-table-column prop="lesson_date" label="上课日期" width="120" />
            <el-table-column prop="start_time" label="开始时间" width="100" />
            <el-table-column prop="hours_used" label="课时" width="80">
              <template #default="scope">
                {{ scope.row.hours_used }} 小时
              </template>
            </el-table-column>
            <el-table-column prop="lesson_type" label="课程类型" width="100" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ scope.row.status }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>系统状态</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="API服务状态">
              <el-tag type="success">运行正常</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="数据库连接">
              <el-tag type="success">已连接</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="当前时间">
              {{ currentTime }}
            </el-descriptions-item>
            <el-descriptions-item label="API文档">
              <el-link href="http://localhost:8000/api/docs" target="_blank" type="primary">
                查看API文档
              </el-link>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 生成测试数据对话框 -->
    <el-dialog v-model="generateDialogVisible" title="生成测试数据" width="500px">
      <el-form :model="generateForm" label-width="120px">
        <el-form-item label="教练数量">
          <el-input-number v-model="generateForm.coachCount" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="会员数量">
          <el-input-number v-model="generateForm.memberCount" :min="1" :max="50" />
        </el-form-item>
        <el-form-item label="课程包/会员">
          <el-input-number v-model="generateForm.packagePerMember" :min="1" :max="5" />
        </el-form-item>
        <el-form-item label="课时/课程包">
          <el-input-number v-model="generateForm.lessonsPerPackage" :min="1" :max="20" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="generateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmGenerateData" :loading="generating">
          确认生成
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '@/api'

const loading = ref(false)
const generateDialogVisible = ref(false)
const generating = ref(false)
const currentTime = ref('')

const stats = reactive({
  coachCount: 0,
  activeCoachCount: 0,
  memberCount: 0,
  activeMemberCount: 0,
  todayLessons: 0,
  monthLessons: 0,
  monthRevenue: 0,
  monthCommission: 0
})

const recentLessons = ref([])

const generateForm = reactive({
  coachCount: 5,
  memberCount: 15,
  packagePerMember: 2,
  lessonsPerPackage: 8
})

// 获取当前时间
const updateTime = () => {
  currentTime.value = new Date().toLocaleString('zh-CN')
}

// 获取状态类型
const getStatusType = (status) => {
  const typeMap = {
    '已完成': 'success',
    '已预约': 'primary',
    '已取消': 'info',
    '已缺席': 'danger'
  }
  return typeMap[status] || 'info'
}

// 格式化数字
const formatNumber = (num) => {
  if (!num) return '0'
  return num.toLocaleString()
}

// 加载统计数据
const loadStats = async () => {
  loading.value = true
  try {
    // 获取教练列表统计
    const coachRes = await api.coach.getList({ page: 1, page_size: 1 })
    stats.coachCount = coachRes.total || 0
    
    // 获取会员列表统计
    const memberRes = await api.member.getList({ page: 1, page_size: 1 })
    stats.memberCount = memberRes.total || 0
    
    // 获取课时记录统计
    const lessonRes = await api.lesson.getList({ page: 1, page_size: 10 })
    recentLessons.value = lessonRes.data || []
    
    // 模拟统计数据（实际应调用统计API）
    stats.activeCoachCount = stats.coachCount
    stats.activeMemberCount = stats.memberCount
    stats.todayLessons = Math.floor(Math.random() * 10)
    stats.monthLessons = Math.floor(Math.random() * 100) + 50
    stats.monthRevenue = Math.floor(Math.random() * 50000) + 10000
    stats.monthCommission = Math.floor(stats.monthRevenue * 0.3)
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
}

// 打开生成测试数据对话框
const handleGenerateTestData = () => {
  ElMessageBox.confirm(
    '生成测试数据将创建模拟的教练、会员、课程包和课时记录。是否继续？',
    '提示',
    {
      confirmButtonText: '继续',
      cancelButtonText: '取消',
      type: 'info'
    }
  ).then(() => {
    generateDialogVisible.value = true
  }).catch(() => {})
}

// 确认生成测试数据
const confirmGenerateData = async () => {
  generating.value = true
  try {
    await api.test.generateAll({
      coach_count: generateForm.coachCount,
      member_count: generateForm.memberCount,
      package_per_member: generateForm.packagePerMember,
      lessons_per_package: generateForm.lessonsPerPackage
    })
    ElMessage.success('测试数据生成成功！')
    generateDialogVisible.value = false
    loadStats()
  } catch (error) {
    ElMessage.error('生成测试数据失败')
  } finally {
    generating.value = false
  }
}

onMounted(() => {
  loadStats()
  updateTime()
  setInterval(updateTime, 1000)
})
</script>
