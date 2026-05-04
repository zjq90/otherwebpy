<template>
  <div class="page-container">
    <div class="page-header">
      <span class="page-title">测试工具</span>
    </div>

    <!-- 系统统计 -->
    <div class="detail-section">
      <div class="detail-title">系统数据统计</div>
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align: center">
              <div style="font-size: 32px; font-weight: bold; color: #409eff">
                {{ stats.members.total || 0 }}
              </div>
              <div style="color: #909399; margin-top: 8px">会员总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align: center">
              <div style="font-size: 32px; font-weight: bold; color: #67c23a">
                {{ stats.member_cards.total || 0 }}
              </div>
              <div style="color: #909399; margin-top: 8px">会员卡总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align: center">
              <div style="font-size: 32px; font-weight: bold; color: #e6a23c">
                {{ stats.promotions.total || 0 }}
              </div>
              <div style="color: #909399; margin-top: 8px">活动总数</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card shadow="hover">
            <div style="text-align: center">
              <div style="font-size: 32px; font-weight: bold; color: #f56c6c">
                {{ stats.reminders.total || 0 }}
              </div>
              <div style="color: #909399; margin-top: 8px">提醒总数</div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-button type="primary" plain @click="loadStats" style="margin-top: 15px">
        <el-icon><Refresh /></el-icon>
        刷新统计
      </el-button>
    </div>

    <!-- 一键生成测试数据 -->
    <div class="detail-section">
      <div class="detail-title">一键生成测试数据</div>
      <el-form :inline="true" :model="quickForm">
        <el-form-item label="会员数量">
          <el-input-number v-model="quickForm.member_count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="generateAll" :loading="loading">
            <el-icon><MagicStick /></el-icon>
            一键生成所有测试数据
          </el-button>
        </el-form-item>
      </el-form>
      <el-text type="info" size="small">
        提示：此操作将生成会员、会员卡、促销活动、优惠券等完整测试数据
      </el-text>
    </div>

    <!-- 分步生成测试数据 -->
    <div class="detail-section">
      <div class="detail-title">分步生成测试数据</div>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>生成会员数据</span>
            </template>
            <el-form :inline="true" :model="memberForm">
              <el-form-item label="数量">
                <el-input-number v-model="memberForm.count" :min="1" :max="100" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="generateMembers" :loading="memberLoading">
                  生成会员
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>生成会员卡数据</span>
            </template>
            <el-form :inline="true" :model="cardForm">
              <el-form-item label="会员数">
                <el-input-number v-model="cardForm.member_count" :min="1" :max="50" />
              </el-form-item>
              <el-form-item label="每人卡数">
                <el-input-number v-model="cardForm.cards_per_member" :min="1" :max="3" />
              </el-form-item>
              <el-form-item>
                <el-button type="success" @click="generateMemberCards" :loading="cardLoading">
                  生成会员卡
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>

      <el-row :gutter="20" style="margin-top: 20px">
        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>生成促销活动数据</span>
            </template>
            <el-form :inline="true" :model="promotionForm">
              <el-form-item label="数量">
                <el-input-number v-model="promotionForm.count" :min="1" :max="10" />
              </el-form-item>
              <el-form-item>
                <el-button type="warning" @click="generatePromotions" :loading="promotionLoading">
                  生成活动
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <el-col :span="12">
          <el-card shadow="hover">
            <template #header>
              <span>生成即将到期的会员卡</span>
            </template>
            <el-form :inline="true" :model="expiringForm">
              <el-form-item label="数量">
                <el-input-number v-model="expiringForm.count" :min="1" :max="20" />
              </el-form-item>
              <el-form-item>
                <el-button type="danger" @click="generateExpiringCards" :loading="expiringLoading">
                  生成到期卡
                </el-button>
              </el-form-item>
            </el-form>
            <el-text type="info" size="small">
              提示：这些会员卡将在3天或7天后到期，用于测试续费提醒功能
            </el-text>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作结果日志 -->
    <div v-if="logs.length > 0" class="detail-section">
      <div class="detail-title">操作结果日志</div>
      <el-table :data="logs" border stripe size="small">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="action" label="操作" width="200" />
        <el-table-column prop="message" label="结果" min-width="300" />
        <el-table-column prop="type" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.type === 'success' ? 'success' : row.type === 'error' ? 'danger' : 'info'">
              {{ row.type === 'success' ? '成功' : row.type === 'error' ? '失败' : '信息' }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
      <el-button type="text" @click="clearLogs" style="margin-top: 10px">清空日志</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, MagicStick } from '@element-plus/icons-vue'
import { testApi } from '../api'

const loading = ref(false)
const memberLoading = ref(false)
const cardLoading = ref(false)
const promotionLoading = ref(false)
const expiringLoading = ref(false)

const logs = ref([])

const stats = ref({
  members: { total: 0 },
  member_cards: { total: 0 },
  promotions: { total: 0, active: 0 },
  reminders: { total: 0, pending: 0 }
})

const quickForm = reactive({
  member_count: 20
})

const memberForm = reactive({
  count: 10
})

const cardForm = reactive({
  member_count: 5,
  cards_per_member: 2
})

const promotionForm = reactive({
  count: 3
})

const expiringForm = reactive({
  count: 5
})

// 添加日志
const addLog = (action, message, type = 'info') => {
  logs.value.unshift({
    time: new Date().toLocaleString('zh-CN'),
    action,
    message,
    type
  })
}

// 清空日志
const clearLogs = () => {
  logs.value = []
}

// 加载统计数据
const loadStats = async () => {
  try {
    const data = await testApi.getStats()
    stats.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

// 一键生成所有测试数据
const generateAll = async () => {
  loading.value = true
  addLog('一键生成', '开始生成所有测试数据...', 'info')
  
  try {
    const result = await testApi.generateAll(quickForm.member_count)
    ElMessage.success('测试数据生成成功！')
    addLog('一键生成', result.message, 'success')
    loadStats()
  } catch (error) {
    addLog('一键生成', '生成失败: ' + (error.message || '未知错误'), 'error')
  } finally {
    loading.value = false
  }
}

// 生成会员
const generateMembers = async () => {
  memberLoading.value = true
  addLog('生成会员', `开始生成 ${memberForm.count} 个会员...`, 'info')
  
  try {
    const result = await testApi.generateMembers(memberForm.count)
    ElMessage.success(result.message)
    addLog('生成会员', result.message, 'success')
    loadStats()
  } catch (error) {
    addLog('生成会员', '生成失败: ' + (error.message || '未知错误'), 'error')
  } finally {
    memberLoading.value = false
  }
}

// 生成会员卡
const generateMemberCards = async () => {
  cardLoading.value = true
  addLog('生成会员卡', `开始为 ${cardForm.member_count} 个会员，每人 ${cardForm.cards_per_member} 张会员卡...`, 'info')
  
  try {
    const result = await testApi.generateMemberCards(
      cardForm.member_count,
      cardForm.cards_per_member
    )
    ElMessage.success(result.message)
    addLog('生成会员卡', result.message, 'success')
    loadStats()
  } catch (error) {
    addLog('生成会员卡', '生成失败: ' + (error.message || '未知错误'), 'error')
  } finally {
    cardLoading.value = false
  }
}

// 生成活动
const generatePromotions = async () => {
  promotionLoading.value = true
  addLog('生成活动', `开始生成 ${promotionForm.count} 个促销活动...`, 'info')
  
  try {
    const result = await testApi.generatePromotions(promotionForm.count)
    ElMessage.success(result.message)
    addLog('生成活动', result.message, 'success')
    loadStats()
  } catch (error) {
    addLog('生成活动', '生成失败: ' + (error.message || '未知错误'), 'error')
  } finally {
    promotionLoading.value = false
  }
}

// 生成即将到期的会员卡
const generateExpiringCards = async () => {
  expiringLoading.value = true
  addLog('生成到期卡', `开始生成 ${expiringForm.count} 张即将到期的会员卡...`, 'info')
  
  try {
    const result = await testApi.generateExpiringCards(expiringForm.count)
    ElMessage.success(result.message)
    addLog('生成到期卡', result.message, 'success')
    loadStats()
  } catch (error) {
    addLog('生成到期卡', '生成失败: ' + (error.message || '未知错误'), 'error')
  } finally {
    expiringLoading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>
