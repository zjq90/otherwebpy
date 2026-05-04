<template>
  <div class="test-generate">
    <div class="page-container">
      <div class="page-header">
        <span class="page-title">测试数据生成</span>
      </div>

      <el-alert
        title="测试数据生成说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        <template #default>
          <p>此功能用于生成测试数据，方便进行系统测试。</p>
          <ul>
            <li>• 生成单个会员：创建一个随机的会员信息</li>
            <li>• 批量生成会员：创建指定数量的会员及相关档案数据</li>
            <li>• 生成带档案的会员：创建包含体测数据、消费记录等档案的完整会员数据</li>
          </ul>
        </template>
      </el-alert>

      <el-row :gutter="24">
        <el-col :span="8">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>健康检查</span>
              </div>
            </template>
            <div class="action-content">
              <div class="status-display" v-if="healthStatus">
                <el-tag :type="healthStatus.status === 'ok' ? 'success' : 'danger'">
                  {{ healthStatus.status === 'ok' ? '服务正常' : '服务异常' }}
                </el-tag>
                <div class="status-detail">
                  <p>数据库: {{ healthStatus.database }}</p>
                  <p>时间: {{ formatDate(healthStatus.timestamp) }}</p>
                </div>
              </div>
              <el-button type="primary" @click="checkHealth" :loading="checkingHealth">
                检查服务状态
              </el-button>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>生成单个会员</span>
              </div>
            </template>
            <div class="action-content">
              <el-button type="success" @click="generateOneMember" :loading="generatingOne">
                生成单个会员
              </el-button>
              <div v-if="generatedMember" class="generated-info">
                <el-divider />
                <p><strong>姓名:</strong> {{ generatedMember.name }}</p>
                <p><strong>手机号:</strong> {{ generatedMember.phone }}</p>
                <p><strong>等级:</strong> {{ formatLevel(generatedMember.current_level) }}</p>
              </div>
            </div>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>批量生成会员</span>
              </div>
            </template>
            <div class="action-content">
              <el-form label-width="80px">
                <el-form-item label="数量">
                  <el-input-number v-model="batchCount" :min="1" :max="100" />
                </el-form-item>
                <el-form-item>
                  <el-button type="warning" @click="generateBatch" :loading="generatingBatch">
                    批量生成
                  </el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>操作日志</span>
            <el-button type="danger" link @click="clearLogs">清空日志</el-button>
          </div>
        </template>
        <div class="logs-container">
          <el-timeline>
            <el-timeline-item
              v-for="(log, index) in logs"
              :key="index"
              :type="log.type"
              :timestamp="log.time"
              placement="top"
            >
              <el-card>
                <h4>{{ log.title }}</h4>
                <p style="color: #606266; font-size: 14px;">{{ log.content }}</p>
              </el-card>
            </el-timeline-item>
            <el-timeline-item v-if="logs.length === 0" type="info">
              <el-card>暂无操作日志</el-card>
            </el-timeline-item>
          </el-timeline>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { healthCheck, generateTestData, generateTestMember } from '@/api/test'
import dayjs from 'dayjs'

const checkingHealth = ref(false)
const generatingOne = ref(false)
const generatingBatch = ref(false)

const healthStatus = ref(null)
const generatedMember = ref(null)
const batchCount = ref(10)
const logs = ref([])

const formatDate = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const formatLevel = (level) => {
  const levelMap = { 'bronze': '铜卡', 'silver': '银卡', 'gold': '金卡' }
  return levelMap[level] || level
}

const addLog = (title, content, type = 'info') => {
  logs.value.unshift({
    title,
    content,
    type,
    time: dayjs().format('YYYY-MM-DD HH:mm:ss')
  })
}

const clearLogs = () => {
  logs.value = []
}

const checkHealth = async () => {
  checkingHealth.value = true
  try {
    const res = await healthCheck()
    if (res.data) {
      healthStatus.value = res.data
      addLog('健康检查', `服务状态: ${res.data.status}, 数据库: ${res.data.database}`, 'success')
      ElMessage.success('服务正常')
    }
  } catch (error) {
    healthStatus.value = { status: 'error', database: '未知', timestamp: new Date().toISOString() }
    addLog('健康检查', '服务检查失败', 'danger')
    ElMessage.error('服务检查失败')
  } finally {
    checkingHealth.value = false
  }
}

const generateOneMember = async () => {
  generatingOne.value = true
  try {
    const res = await generateTestMember()
    if (res.data) {
      generatedMember.value = res.data.member
      addLog('生成会员', `成功创建会员: ${res.data.member.name} (${res.data.member.phone})`, 'success')
      ElMessage.success('会员创建成功')
    }
  } catch (error) {
    addLog('生成会员', '创建会员失败', 'danger')
    ElMessage.error('创建失败')
  } finally {
    generatingOne.value = false
  }
}

const generateBatch = async () => {
  generatingBatch.value = true
  try {
    const res = await generateTestData(batchCount.value)
    if (res.data) {
      addLog('批量生成', `成功创建 ${res.data.count} 个会员`, 'success')
      ElMessage.success(`成功创建 ${res.data.count} 个会员`)
    }
  } catch (error) {
    addLog('批量生成', '批量创建会员失败', 'danger')
    ElMessage.error('批量创建失败')
  } finally {
    generatingBatch.value = false
  }
}
</script>

<style lang="scss" scoped>
.test-generate {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .action-content {
    text-align: center;
    padding: 20px 0;

    .generated-info {
      text-align: left;
      margin-top: 15px;

      p {
        margin: 8px 0;
      }
    }
  }

  .status-display {
    margin-bottom: 15px;

    .status-detail {
      margin-top: 10px;
      text-align: left;
      padding: 0 20px;

      p {
        margin: 5px 0;
        color: #606266;
      }
    }
  }

  .logs-container {
    max-height: 400px;
    overflow-y: auto;
  }
}
</style>
