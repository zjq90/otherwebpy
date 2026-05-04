<template>
  <div class="page-container">
    <!-- 返回按钮 -->
    <div style="margin-bottom: 20px">
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
    </div>

    <!-- 会员详情 -->
    <div v-if="member" class="detail-section">
      <div class="detail-title">基本信息</div>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">会员编号：</span>
          <span class="detail-value">{{ member.member_no }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">姓名：</span>
          <span class="detail-value">{{ member.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">手机号：</span>
          <span class="detail-value">{{ member.phone }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">邮箱：</span>
          <span class="detail-value">{{ member.email || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">性别：</span>
          <span class="detail-value">{{ member.gender || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">生日：</span>
          <span class="detail-value">{{ member.birthday || '-' }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">会员等级：</span>
          <span class="detail-value">
            <el-tag :type="getLevelTagType(member.level)">{{ getLevelText(member.level) }}会员</el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">会员状态：</span>
          <span class="detail-value">
            <span class="status-tag" :class="getStatusClass(member.status)">
              {{ getStatusText(member.status) }}
            </span>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">累计消费：</span>
          <span class="detail-value">¥{{ member.total_consumption?.toFixed(2) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">当前积分：</span>
          <span class="detail-value">{{ member.points }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">最后消费：</span>
          <span class="detail-value">{{ formatDateTime(member.last_consumption_time) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">注册时间：</span>
          <span class="detail-value">{{ formatDateTime(member.created_at) }}</span>
        </div>
        <div class="detail-item" style="grid-column: span 2">
          <span class="detail-label">地址：</span>
          <span class="detail-value">{{ member.address || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- 会员卡列表 -->
    <div class="detail-section">
      <div class="detail-title">会员卡信息</div>
      <el-table :data="memberCards" border stripe>
        <el-table-column prop="card_no" label="卡号" width="180" />
        <el-table-column prop="card_type" label="卡类型" width="100" />
        <el-table-column prop="balance" label="余额" width="100">
          <template #default="{ row }">
            ¥{{ row.balance?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_amount" label="累计充值" width="120">
          <template #default="{ row }">
            ¥{{ row.total_amount?.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="valid_from" label="有效期开始" width="120" />
        <el-table-column prop="valid_to" label="有效期结束" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '有效' : row.status === 'renewed' ? '已续费' : '已过期' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="openRenewDialog(row)">续费</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 续费对话框 -->
    <el-dialog
      v-model="renewDialogVisible"
      title="会员卡续费"
      width="400px"
    >
      <el-form :model="renewForm" label-width="100px">
        <el-form-item label="当前卡号">
          <el-input :value="currentCard?.card_no" disabled />
        </el-form-item>
        <el-form-item label="当前有效期">
          <el-input :value="`${currentCard?.valid_from} 至 ${currentCard?.valid_to}`" disabled />
        </el-form-item>
        <el-form-item label="续费天数" prop="renew_days">
          <el-select v-model="renewForm.renew_days" placeholder="请选择" style="width: 100%">
            <el-option :label="30 + '天（月卡）'" :value="30" />
            <el-option :label="90 + '天（季卡）'" :value="90" />
            <el-option :label="180 + '天（半年卡）'" :value="180" />
            <el-option :label="365 + '天（年卡）'" :value="365" />
          </el-select>
        </el-form-item>
        <el-form-item label="续费金额" prop="amount">
          <el-input-number v-model="renewForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item label="续费方式" prop="method">
          <el-select v-model="renewForm.method" placeholder="请选择" style="width: 100%">
            <el-option label="到店续费" value="offline" />
            <el-option label="线上续费" value="online" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="renewDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="renewLoading" @click="handleRenew">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { memberApi } from '../../api'

const route = useRoute()
const router = useRouter()

const member = ref(null)
const memberCards = ref([])
const renewDialogVisible = ref(false)
const currentCard = ref(null)
const renewLoading = ref(false)

const renewForm = reactive({
  renew_days: 30,
  amount: 0,
  method: 'offline'
})

// 获取等级显示文本
const getLevelText = (level) => {
  const map = {
    bronze: '青铜',
    silver: '白银',
    gold: '黄金',
    platinum: '铂金',
    diamond: '钻石'
  }
  return map[level] || level
}

// 获取等级标签类型
const getLevelTagType = (level) => {
  const map = {
    bronze: 'info',
    silver: '',
    gold: 'warning',
    platinum: 'primary',
    diamond: 'danger'
  }
  return map[level] || ''
}

// 获取状态显示文本
const getStatusText = (status) => {
  const map = {
    active: '活跃',
    sleeping: '沉睡',
    inactive: '不活跃'
  }
  return map[status] || status
}

// 获取状态样式类
const getStatusClass = (status) => {
  const map = {
    active: 'status-active',
    sleeping: 'status-sleeping',
    inactive: 'status-inactive'
  }
  return map[status] || ''
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载会员详情
const loadMember = async () => {
  try {
    const memberId = route.params.id
    member.value = await memberApi.getById(memberId)
  } catch (error) {
    console.error('加载会员详情失败:', error)
  }
}

// 加载会员卡
const loadMemberCards = async () => {
  try {
    const memberId = route.params.id
    memberCards.value = await memberApi.getCards(memberId)
  } catch (error) {
    console.error('加载会员卡失败:', error)
  }
}

// 返回
const goBack = () => {
  router.push('/members')
}

// 打开续费对话框
const openRenewDialog = (card) => {
  currentCard.value = card
  renewForm.renew_days = 30
  renewForm.amount = 0
  renewForm.method = 'offline'
  renewDialogVisible.value = true
}

// 续费
const handleRenew = async () => {
  if (!renewForm.amount || renewForm.amount <= 0) {
    ElMessage.warning('请输入续费金额')
    return
  }

  renewLoading.value = true
  try {
    await memberApi.renewCard(currentCard.value.id, {
      renew_days: renewForm.renew_days,
      amount: renewForm.amount,
      method: renewForm.method
    })
    ElMessage.success('续费成功')
    renewDialogVisible.value = false
    loadMemberCards()
  } catch (error) {
    console.error('续费失败:', error)
  } finally {
    renewLoading.value = false
  }
}

onMounted(() => {
  loadMember()
  loadMemberCards()
})
</script>
