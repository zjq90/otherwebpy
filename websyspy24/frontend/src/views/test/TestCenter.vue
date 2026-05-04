<template>
  <!-- 测试中心页面 -->
  <div class="test-center">
    <!-- 顶部介绍 -->
    <el-card class="intro-card">
      <template #header>
        <span>测试中心</span>
      </template>
      <div class="intro-content">
        <el-alert
          title="系统测试说明"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>本页面提供系统功能测试工具，包括：</p>
            <ul>
              <li>一键生成测试数据（会员、商品、储物柜、优惠券等）</li>
              <li>查看系统数据统计</li>
              <li>快速测试各功能模块</li>
            </ul>
          </template>
        </el-alert>
      </div>
    </el-card>

    <el-row :gutter="20">
      <!-- 左侧：测试操作 -->
      <el-col :span="8">
        <el-card class="test-card">
          <template #header>
            <span>测试操作</span>
          </template>
          
          <div class="test-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="generateTestData" 
              :loading="generateLoading"
              style="width: 100%; margin-bottom: 15px"
            >
              <el-icon><MagicStick /></el-icon>
              一键生成测试数据
            </el-button>
            
            <el-button 
              type="success" 
              @click="loadSummary" 
              :loading="summaryLoading"
              style="width: 100%; margin-bottom: 15px"
            >
              <el-icon><DataAnalysis /></el-icon>
              刷新数据统计
            </el-button>
            
            <el-button 
              type="warning" 
              @click="loadQuickTestData" 
              :loading="quickTestLoading"
              style="width: 100%"
            >
              <el-icon><View /></el-icon>
              查看测试数据详情
            </el-button>
          </div>
          
          <el-divider />
          
          <div class="quick-test">
            <div class="section-title">快速测试入口</div>
            <el-button 
              type="primary" 
              plain 
              @click="goToPage('/checkin')"
              style="width: 100%; margin-bottom: 10px"
            >
              <el-icon><Timer /></el-icon>
              测试签到功能
            </el-button>
            <el-button 
              type="success" 
              plain 
              @click="goToPage('/cashier')"
              style="width: 100%; margin-bottom: 10px"
            >
              <el-icon><Money /></el-icon>
              测试收银功能
            </el-button>
            <el-button 
              type="warning" 
              plain 
              @click="goToPage('/lockers')"
              style="width: 100%"
            >
              <el-icon><Box /></el-icon>
              测试储物柜功能
            </el-button>
          </div>
        </el-card>
      </el-col>

      <!-- 右侧：数据统计 -->
      <el-col :span="16">
        <el-card class="stats-card">
          <template #header>
            <div class="card-header">
              <span>系统数据统计</span>
              <el-tag :type="summaryData ? 'success' : 'info'">
                {{ summaryData ? '已加载' : '未加载' }}
              </el-tag>
            </div>
          </template>
          
          <el-empty v-if="!summaryData" description="点击「刷新数据统计」按钮加载数据" />
          
          <div v-else>
            <!-- 统计卡片 -->
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-item" shadow="hover">
                  <div class="stat-icon member">
                    <el-icon :size="32"><User /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ summaryData.members?.total || 0 }}</div>
                    <div class="stat-label">会员总数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-item" shadow="hover">
                  <div class="stat-icon product">
                    <el-icon :size="32"><Goods /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ summaryData.products?.total || 0 }}</div>
                    <div class="stat-label">商品总数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-item" shadow="hover">
                  <div class="stat-icon locker">
                    <el-icon :size="32"><Box /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ summaryData.lockers?.total || 0 }}</div>
                    <div class="stat-label">储物柜总数</div>
                  </div>
                </el-card>
              </el-col>
              <el-col :span="6">
                <el-card class="stat-item" shadow="hover">
                  <div class="stat-icon order">
                    <el-icon :size="32"><List /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ summaryData.orders?.total || 0 }}</div>
                    <div class="stat-label">订单总数</div>
                  </div>
                </el-card>
              </el-col>
            </el-row>

            <el-divider />

            <!-- 详细统计 -->
            <el-row :gutter="20">
              <!-- 会员统计 -->
              <el-col :span="12">
                <div class="detail-section">
                  <div class="section-title">会员详情</div>
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="激活会员">
                      <span class="text-success">{{ summaryData.members?.active || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="过期会员">
                      <span class="text-warning">{{ summaryData.members?.expired || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="暂停会员">
                      <span class="text-danger">{{ summaryData.members?.suspended || 0 }}</span>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-col>

              <!-- 储物柜统计 -->
              <el-col :span="12">
                <div class="detail-section">
                  <div class="section-title">储物柜详情</div>
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="空闲储物柜">
                      <span class="text-success">{{ summaryData.lockers?.available || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="使用中">
                      <span class="text-warning">{{ summaryData.lockers?.occupied || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="故障">
                      <span class="text-danger">{{ summaryData.lockers?.maintenance || 0 }}</span>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-col>
            </el-row>

            <el-divider />

            <!-- 商品和优惠券统计 -->
            <el-row :gutter="20">
              <!-- 商品统计 -->
              <el-col :span="12">
                <div class="detail-section">
                  <div class="section-title">商品详情</div>
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="上架商品">
                      <span class="text-success">{{ summaryData.products?.active || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="下架商品">
                      <span class="text-muted">{{ summaryData.products?.inactive || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="总库存">
                      <span class="text-primary">{{ summaryData.products?.total_stock || 0 }}</span>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-col>

              <!-- 优惠券统计 -->
              <el-col :span="12">
                <div class="detail-section">
                  <div class="section-title">优惠券详情</div>
                  <el-descriptions :column="1" border size="small">
                    <el-descriptions-item label="可用优惠券">
                      <span class="text-success">{{ summaryData.coupons?.available || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="已使用">
                      <span class="text-info">{{ summaryData.coupons?.used || 0 }}</span>
                    </el-descriptions-item>
                    <el-descriptions-item label="已过期">
                      <span class="text-danger">{{ summaryData.coupons?.expired || 0 }}</span>
                    </el-descriptions-item>
                  </el-descriptions>
                </div>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 测试数据详情弹窗 -->
    <el-dialog
      v-model="testDataDialogVisible"
      title="测试数据详情"
      width="800px"
    >
      <el-empty v-if="!quickTestData" description="加载中..." />
      
      <div v-else>
        <el-tabs v-model="activeTab">
          <!-- 活跃会员 -->
          <el-tab-pane label="活跃会员" name="members">
            <el-table :data="quickTestData.active_members || []" border size="small">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="member_no" label="会员编号" width="120" />
              <el-table-column prop="name" label="姓名" width="100" />
              <el-table-column prop="phone" label="手机号" width="130" />
              <el-table-column prop="membership_type" label="会籍类型" width="100" />
              <el-table-column prop="membership_end" label="到期日期" width="120" />
              <el-table-column prop="balance" label="余额" width="100">
                <template #default="{ row }">
                  <span class="text-primary">¥{{ row.balance?.toFixed(2) || '0.00' }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 可用储物柜 -->
          <el-tab-pane label="可用储物柜" name="lockers">
            <el-table :data="quickTestData.available_lockers || []" border size="small">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="locker_no" label="储物柜编号" width="120" />
              <el-table-column prop="location" label="位置" width="150" />
              <el-table-column prop="locker_type" label="类型" width="100" />
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag type="success" size="small">空闲</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 可用优惠券 -->
          <el-tab-pane label="可用优惠券" name="coupons">
            <el-table :data="quickTestData.available_coupons || []" border size="small">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="coupon_code" label="优惠券码" width="150" />
              <el-table-column prop="name" label="名称" min-width="150" />
              <el-table-column prop="coupon_type" label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.coupon_type === 'cash' ? 'danger' : row.coupon_type === 'discount' ? 'warning' : 'success'" size="small">
                    {{ row.coupon_type === 'cash' ? '代金券' : row.coupon_type === 'discount' ? '折扣券' : '赠品券' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="value" label="面值/折扣" width="120">
                <template #default="{ row }">
                  <span v-if="row.coupon_type === 'cash'" class="text-danger">¥{{ row.value }}</span>
                  <span v-else-if="row.coupon_type === 'discount'" class="text-warning">{{ row.value * 10 }}折</span>
                  <span v-else class="text-success">赠品</span>
                </template>
              </el-table-column>
              <el-table-column prop="min_amount" label="最低消费" width="100">
                <template #default="{ row }">
                  ¥{{ row.min_amount || 0 }}
                </template>
              </el-table-column>
              <el-table-column prop="expire_time" label="过期时间" width="160">
                <template #default="{ row }">
                  {{ row.expire_time ? formatDateTime(row.expire_time) : '-' }}
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import api from '@/api'

const router = useRouter()

// 加载状态
const generateLoading = ref(false)
const summaryLoading = ref(false)
const quickTestLoading = ref(false)

// 数据
const summaryData = ref(null)
const quickTestData = ref(null)
const testDataDialogVisible = ref(false)
const activeTab = ref('members')

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return '-'
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 生成测试数据
const generateTestData = async () => {
  generateLoading.value = true
  try {
    const res = await api.generateTestData()
    if (res.success) {
      ElMessage.success('测试数据生成成功！')
      loadSummary()
    } else {
      ElMessage.error(res.message || '生成失败')
    }
  } catch (error) {
    console.error('生成测试数据失败:', error)
    ElMessage.error('生成测试数据失败')
  } finally {
    generateLoading.value = false
  }
}

// 加载统计数据
const loadSummary = async () => {
  summaryLoading.value = true
  try {
    const res = await api.getTestSummary()
    if (res.success) {
      summaryData.value = res.data
    }
  } catch (error) {
    console.error('加载统计失败:', error)
    ElMessage.error('加载统计失败')
  } finally {
    summaryLoading.value = false
  }
}

// 加载快速测试数据
const loadQuickTestData = async () => {
  quickTestLoading.value = true
  try {
    const res = await api.getQuickTestData()
    if (res.success) {
      quickTestData.value = res.data
      testDataDialogVisible.value = true
    }
  } catch (error) {
    console.error('加载测试数据失败:', error)
    ElMessage.error('加载测试数据失败')
  } finally {
    quickTestLoading.value = false
  }
}

// 跳转到页面
const goToPage = (path) => {
  router.push(path)
}

onMounted(() => {
  loadSummary()
})
</script>

<style scoped>
.test-center {
  padding: 0;
}

/* 介绍卡片 */
.intro-card {
  margin-bottom: 20px;
}

.intro-content {
  padding: 10px 0;
}

/* 测试操作卡片 */
.test-card {
  min-height: 400px;
}

.test-actions {
  margin-bottom: 10px;
}

.quick-test {
  margin-top: 10px;
}

.section-title {
  font-weight: bold;
  margin-bottom: 10px;
  color: #303133;
}

/* 统计卡片 */
.stats-card {
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 统计项 */
.stat-item {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-item:hover {
  transform: translateY(-3px);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-icon.member {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.stat-icon.product {
  background: linear-gradient(135deg, #67C23A, #85ce61);
}

.stat-icon.locker {
  background: linear-gradient(135deg, #E6A23C, #ebb563);
}

.stat-icon.order {
  background: linear-gradient(135deg, #F56C6C, #f78989);
}

.stat-info {
  margin-top: 15px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 5px;
}

/* 详情区域 */
.detail-section {
  margin-top: 10px;
}

/* 文本样式 */
.text-primary {
  color: #409EFF;
  font-weight: bold;
}

.text-success {
  color: #67C23A;
  font-weight: bold;
}

.text-warning {
  color: #E6A23C;
  font-weight: bold;
}

.text-danger {
  color: #F56C6C;
  font-weight: bold;
}

.text-info {
  color: #909399;
  font-weight: bold;
}

.text-muted {
  color: #C0C4CC;
}
</style>
