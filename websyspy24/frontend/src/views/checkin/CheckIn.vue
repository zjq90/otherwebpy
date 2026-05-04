<template>
  <!-- 签到验证页面 -->
  <div class="checkin-page">
    <!-- 今日统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#409EFF"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ todayStats.total }}</div>
              <div class="stat-label">今日总签到</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#67C23A"><CircleCheck /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ todayStats.success }}</div>
              <div class="stat-label">签到成功</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#F56C6C"><CircleClose /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ todayStats.failed }}</div>
              <div class="stat-label">签到失败</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon :size="32" color="#E6A23C"><Timer /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ currentTime }}</div>
              <div class="stat-label">当前时间</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 签到验证区域 -->
    <el-row :gutter="20">
      <!-- 左侧：签到方式选择 -->
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>签到验证</span>
            </div>
          </template>
          
          <!-- 签到方式Tabs -->
          <el-tabs v-model="activeTab" class="checkin-tabs">
            <!-- 刷卡签到 -->
            <el-tab-pane label="刷卡签到" name="card">
              <div class="checkin-form">
                <el-empty :image-size="80" description="请刷卡或输入卡号" v-if="!cardMember" />
                <div v-else class="member-info">
                  <el-avatar :size="80" icon="UserFilled" />
                  <div class="info-detail">
                    <h3>{{ cardMember.name }}</h3>
                    <p>会员编号: {{ cardMember.member_no }}</p>
                    <p>会籍类型: {{ cardMember.membership_type }}</p>
                    <p>到期日期: {{ cardMember.membership_end }}</p>
                    <el-tag :type="cardMember.valid ? 'success' : 'danger'">
                      {{ cardMember.valid ? '会籍有效' : '会籍无效' }}
                    </el-tag>
                  </div>
                </div>
                <el-divider />
                <el-form label-width="100px">
                  <el-form-item label="卡号">
                    <el-input
                      v-model="cardNo"
                      placeholder="请输入卡号或刷卡"
                      @keyup.enter="handleCardCheckin"
                      style="width: 300px"
                    />
                  </el-form-item>
                  <el-form-item label="设备编号">
                    <el-input
                      v-model="deviceNo"
                      placeholder="请输入设备编号（可选）"
                      style="width: 300px"
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="handleCardCheckin" :loading="checkinLoading">
                      <el-icon><Check /></el-icon>
                      确认签到
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
            
            <!-- 扫码签到 -->
            <el-tab-pane label="扫码签到" name="qr">
              <div class="checkin-form">
                <el-empty :image-size="80" description="请扫描二维码或输入二维码内容" v-if="!qrMember" />
                <div v-else class="member-info">
                  <el-avatar :size="80" icon="UserFilled" />
                  <div class="info-detail">
                    <h3>{{ qrMember.name }}</h3>
                    <p>会员编号: {{ qrMember.member_no }}</p>
                    <p>会籍类型: {{ qrMember.membership_type }}</p>
                    <el-tag :type="qrMember.valid ? 'success' : 'danger'">
                      {{ qrMember.valid ? '会籍有效' : '会籍无效' }}
                    </el-tag>
                  </div>
                </div>
                <el-divider />
                <el-form label-width="120px">
                  <el-form-item label="二维码内容">
                    <el-input
                      v-model="qrCode"
                      type="textarea"
                      :rows="2"
                      placeholder="请输入二维码内容或扫描二维码"
                      style="width: 400px"
                    />
                  </el-form-item>
                  <el-form-item>
                    <el-button type="primary" @click="handleQRCheckin" :loading="checkinLoading">
                      <el-icon><Check /></el-icon>
                      扫码签到
                    </el-button>
                  </el-form-item>
                </el-form>
              </div>
            </el-tab-pane>
            
            <!-- 人脸识别签到 -->
            <el-tab-pane label="人脸识别" name="face">
              <div class="checkin-form">
                <el-empty :image-size="80" description="请对准摄像头进行人脸识别" v-if="!faceMember" />
                <div v-else class="member-info">
                  <el-avatar :size="80" icon="UserFilled" />
                  <div class="info-detail">
                    <h3>{{ faceMember.name }}</h3>
                    <p>会员编号: {{ faceMember.member_no }}</p>
                    <p>相似度: {{ faceMember.similarity }}%</p>
                    <el-tag :type="faceMember.valid ? 'success' : 'danger'">
                      {{ faceMember.valid ? '验证通过' : '验证失败' }}
                    </el-tag>
                  </div>
                </div>
                <el-divider />
                <div class="face-camera-area">
                  <div class="camera-placeholder">
                    <el-icon :size="64"><VideoCamera /></el-icon>
                    <p>摄像头区域（模拟）</p>
                  </div>
                  <el-form label-width="100px" style="margin-top: 20px">
                    <el-form-item label="人脸数据">
                      <el-input
                        v-model="faceData"
                        placeholder="请输入人脸特征数据（模拟）"
                        style="width: 300px"
                      />
                    </el-form-item>
                    <el-form-item>
                      <el-button type="primary" @click="handleFaceCheckin" :loading="checkinLoading">
                        <el-icon><VideoCamera /></el-icon>
                        人脸识别
                      </el-button>
                    </el-form-item>
                  </el-form>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <!-- 右侧：快速签到和最近签到 -->
      <el-col :span="10">
        <!-- 快速签到 -->
        <el-card class="quick-checkin-card">
          <template #header>
            <div class="card-header">
              <span>快速签到测试</span>
              <el-button type="text" size="small" @click="loadTestMembers">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-button>
            </div>
          </template>
          
          <el-form label-width="100px">
            <el-form-item label="选择会员">
              <el-select
                v-model="selectedMemberId"
                placeholder="请选择会员"
                filterable
                style="width: 100%"
              >
                <el-option
                  v-for="member in testMembers"
                  :key="member.id"
                  :label="`${member.name} (${member.member_no})`"
                  :value="member.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="签到方式">
              <el-radio-group v-model="quickCheckinType">
                <el-radio label="card">刷卡</el-radio>
                <el-radio label="qr">扫码</el-radio>
                <el-radio label="face">人脸识别</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleQuickCheckin" :loading="quickLoading" :disabled="!selectedMemberId">
                <el-icon><Timer /></el-icon>
                快速签到
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 签到结果提示 -->
        <el-card v-if="checkinResult" class="result-card">
          <el-alert
            :title="checkinResult.title"
            :type="checkinResult.type"
            :description="checkinResult.message"
            show-icon
            :closable="false"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import api from '@/api'

// 当前时间
const currentTime = ref('')
let timeInterval = null

// 今日统计
const todayStats = reactive({
  total: 0,
  success: 0,
  failed: 0
})

// 签到相关
const activeTab = ref('card')
const checkinLoading = ref(false)
const quickLoading = ref(false)
const deviceNo = ref('')

// 刷卡签到
const cardNo = ref('')
const cardMember = ref(null)

// 扫码签到
const qrCode = ref('')
const qrMember = ref(null)

// 人脸识别
const faceData = ref('')
const faceMember = ref(null)

// 快速签到
const testMembers = ref([])
const selectedMemberId = ref(null)
const quickCheckinType = ref('card')

// 签到结果
const checkinResult = ref(null)

// 加载今日统计
const loadTodayStats = async () => {
  try {
    const res = await api.getTodayStats()
    if (res.success) {
      todayStats.total = res.data.total || 0
      todayStats.success = res.data.success || 0
      todayStats.failed = res.data.failed || 0
    }
  } catch (error) {
    console.error('加载统计失败:', error)
  }
}

// 加载测试会员
const loadTestMembers = async () => {
  try {
    const res = await api.getQuickTestData()
    if (res.success) {
      testMembers.value = res.data.active_members || []
    }
  } catch (error) {
    console.error('加载测试数据失败:', error)
  }
}

// 刷卡签到
const handleCardCheckin = async () => {
  if (!cardNo.value.trim()) {
    ElMessage.warning('请输入卡号')
    return
  }
  
  checkinLoading.value = true
  try {
    const res = await api.verifyCheckin({
      check_in_type: 'card',
      identifier: cardNo.value.trim(),
      device_no: deviceNo.value || undefined
    })
    
    if (res.success) {
      // 签到成功
      checkinResult.value = {
        title: '签到成功',
        type: 'success',
        message: `会员 ${res.data.member_name} 签到成功！`
      }
      
      // 显示会员信息
      cardMember.value = {
        name: res.data.member_name,
        member_no: res.data.member_no,
        membership_type: res.data.membership_type,
        membership_end: res.data.membership_end,
        valid: true
      }
      
      ElMessage.success('签到成功')
      loadTodayStats()
    } else {
      // 签到失败
      checkinResult.value = {
        title: '签到失败',
        type: 'error',
        message: res.message || '签到失败，请重试'
      }
      
      cardMember.value = {
        valid: false
      }
      
      ElMessage.error(res.message || '签到失败')
    }
  } catch (error) {
    console.error('签到失败:', error)
    ElMessage.error('签到失败，请稍后重试')
  } finally {
    checkinLoading.value = false
  }
}

// 扫码签到
const handleQRCheckin = async () => {
  if (!qrCode.value.trim()) {
    ElMessage.warning('请输入二维码内容')
    return
  }
  
  checkinLoading.value = true
  try {
    const res = await api.verifyCheckin({
      check_in_type: 'qr',
      identifier: qrCode.value.trim(),
      device_no: deviceNo.value || undefined
    })
    
    if (res.success) {
      checkinResult.value = {
        title: '扫码成功',
        type: 'success',
        message: `会员 ${res.data.member_name} 签到成功！`
      }
      
      qrMember.value = {
        name: res.data.member_name,
        member_no: res.data.member_no,
        membership_type: res.data.membership_type,
        valid: true
      }
      
      ElMessage.success('扫码签到成功')
      loadTodayStats()
    } else {
      checkinResult.value = {
        title: '扫码失败',
        type: 'error',
        message: res.message || '扫码失败，请重试'
      }
      
      qrMember.value = { valid: false }
      ElMessage.error(res.message || '扫码失败')
    }
  } catch (error) {
    console.error('扫码失败:', error)
    ElMessage.error('扫码签到失败')
  } finally {
    checkinLoading.value = false
  }
}

// 人脸识别签到
const handleFaceCheckin = async () => {
  if (!faceData.value.trim()) {
    ElMessage.warning('请输入人脸数据')
    return
  }
  
  checkinLoading.value = true
  try {
    const res = await api.verifyCheckin({
      check_in_type: 'face',
      identifier: faceData.value.trim(),
      device_no: deviceNo.value || undefined
    })
    
    if (res.success) {
      checkinResult.value = {
        title: '验证通过',
        type: 'success',
        message: `会员 ${res.data.member_name} 人脸识别签到成功！`
      }
      
      faceMember.value = {
        name: res.data.member_name,
        member_no: res.data.member_no,
        similarity: 95 + Math.floor(Math.random() * 5),
        valid: true
      }
      
      ElMessage.success('人脸识别签到成功')
      loadTodayStats()
    } else {
      checkinResult.value = {
        title: '验证失败',
        type: 'error',
        message: res.message || '人脸识别失败，请重试'
      }
      
      faceMember.value = { valid: false }
      ElMessage.error(res.message || '人脸识别失败')
    }
  } catch (error) {
    console.error('人脸识别失败:', error)
    ElMessage.error('人脸识别签到失败')
  } finally {
    checkinLoading.value = false
  }
}

// 快速签到
const handleQuickCheckin = async () => {
  if (!selectedMemberId.value) {
    ElMessage.warning('请选择会员')
    return
  }
  
  quickLoading.value = true
  try {
    const res = await api.quickCheckin(selectedMemberId.value, quickCheckinType.value)
    
    if (res.success) {
      checkinResult.value = {
        title: '快速签到成功',
        type: 'success',
        message: `会员 ${res.data.member_name} 签到成功！`
      }
      
      ElMessage.success('快速签到成功')
      loadTodayStats()
    } else {
      checkinResult.value = {
        title: '快速签到失败',
        type: 'error',
        message: res.message || '签到失败'
      }
      
      ElMessage.error(res.message || '签到失败')
    }
  } catch (error) {
    console.error('快速签到失败:', error)
    ElMessage.error('快速签到失败')
  } finally {
    quickLoading.value = false
  }
}

// 更新时间
const updateTime = () => {
  currentTime.value = dayjs().format('HH:mm:ss')
}

onMounted(() => {
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
  
  loadTodayStats()
  loadTestMembers()
})

onUnmounted(() => {
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})
</script>

<style scoped>
.checkin-page {
  padding: 0;
}

/* 统计卡片 */
.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 卡片头部 */
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

/* 签到表单 */
.checkin-form {
  min-height: 350px;
}

.member-info {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.info-detail h3 {
  margin: 0 0 10px 0;
  font-size: 20px;
  color: #303133;
}

.info-detail p {
  margin: 5px 0;
  color: #606266;
}

/* 人脸识别区域 */
.face-camera-area {
  text-align: center;
}

.camera-placeholder {
  width: 280px;
  height: 200px;
  margin: 0 auto;
  background: #303133;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #909399;
}

.camera-placeholder p {
  margin-top: 10px;
}

/* 快速签到卡片 */
.quick-checkin-card {
  margin-bottom: 20px;
}

/* 结果卡片 */
.result-card {
  margin-bottom: 20px;
}
</style>
