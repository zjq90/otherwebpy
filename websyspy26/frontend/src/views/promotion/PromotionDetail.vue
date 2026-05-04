<template>
  <div class="page-container">
    <!-- 返回按钮 -->
    <div style="margin-bottom: 20px">
      <el-button @click="goBack">
        <el-icon><ArrowLeft /></el-icon>
        返回列表
      </el-button>
    </div>

    <!-- 活动详情 -->
    <div v-if="promotion" class="detail-section">
      <div class="detail-title">活动信息</div>
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">活动名称：</span>
          <span class="detail-value">{{ promotion.name }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">活动类型：</span>
          <span class="detail-value">
            <el-tag :type="getTypeTagType(promotion.type)">{{ getTypeText(promotion.type) }}</el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">活动状态：</span>
          <span class="detail-value">
            <el-tag :type="getStatusTagType(promotion.status)">
              {{ getStatusText(promotion.status) }}
            </el-tag>
          </span>
        </div>
        <div class="detail-item">
          <span class="detail-label">优惠信息：</span>
          <span class="detail-value">{{ getPromotionInfo(promotion) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">目标用户：</span>
          <span class="detail-value">{{ getTargetTypeText(promotion.target_type) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">发放总量：</span>
          <span class="detail-value">{{ promotion.total_quantity }} 张</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">已使用：</span>
          <span class="detail-value">{{ promotion.used_quantity }} 张</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">每人限领：</span>
          <span class="detail-value">{{ promotion.per_member_limit }} 张</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">开始时间：</span>
          <span class="detail-value">{{ formatDateTime(promotion.valid_from) }}</span>
        </div>
        <div class="detail-item">
          <span class="detail-label">结束时间：</span>
          <span class="detail-value">{{ formatDateTime(promotion.valid_to) }}</span>
        </div>
        <div class="detail-item" style="grid-column: span 2">
          <span class="detail-label">活动描述：</span>
          <span class="detail-value">{{ promotion.description || '-' }}</span>
        </div>
      </div>
    </div>

    <!-- 优惠券列表 -->
    <div class="detail-section">
      <div class="detail-title">优惠券列表</div>
      <el-table :data="coupons" border stripe>
        <el-table-column prop="coupon_no" label="优惠券编号" width="220" />
        <el-table-column prop="name" label="优惠券名称" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getCouponStatusTagType(row.status)">
              {{ getCouponStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="valid_from" label="有效期开始" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.valid_from) }}
          </template>
        </el-table-column>
        <el-table-column prop="valid_to" label="有效期结束" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.valid_to) }}
          </template>
        </el-table-column>
        <el-table-column prop="claimed_at" label="领取时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.claimed_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="used_at" label="使用时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.used_at) }}
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'
import { promotionApi } from '../../api'

const route = useRoute()
const router = useRouter()

const promotion = ref(null)
const coupons = ref([])

// 获取类型显示文本
const getTypeText = (type) => {
  const map = {
    discount: '限时折扣',
    full_reduction: '满减券',
    experience: '体验券'
  }
  return map[type] || type
}

// 获取类型标签类型
const getTypeTagType = (type) => {
  const map = {
    discount: 'primary',
    full_reduction: 'success',
    experience: 'warning'
  }
  return map[type] || ''
}

// 获取优惠信息
const getPromotionInfo = (row) => {
  if (row.type === 'discount') {
    return `${(row.discount_rate * 10).toFixed(1)}折`
  } else if (row.type === 'full_reduction') {
    return `满${row.full_amount}减${row.reduction_amount}`
  } else if (row.type === 'experience') {
    return `体验券${row.experience_amount}元`
  }
  return '-'
}

// 获取目标用户显示文本
const getTargetTypeText = (type) => {
  const map = {
    all: '全部会员',
    sleeping: '沉睡会员',
    high_value: '高价值客户',
    specific: '指定会员'
  }
  return map[type] || type
}

// 获取状态显示文本
const getStatusText = (status) => {
  const map = {
    draft: '草稿',
    active: '进行中',
    ended: '已结束',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const map = {
    draft: 'info',
    active: 'success',
    ended: 'warning',
    cancelled: 'danger'
  }
  return map[status] || ''
}

// 获取优惠券状态显示文本
const getCouponStatusText = (status) => {
  const map = {
    available: '可用',
    claimed: '已领取',
    used: '已使用',
    expired: '已过期'
  }
  return map[status] || status
}

// 获取优惠券状态标签类型
const getCouponStatusTagType = (status) => {
  const map = {
    available: 'success',
    claimed: 'warning',
    used: 'info',
    expired: 'danger'
  }
  return map[status] || ''
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 加载活动详情
const loadPromotion = async () => {
  try {
    const promotionId = route.params.id
    promotion.value = await promotionApi.getById(promotionId)
  } catch (error) {
    console.error('加载活动详情失败:', error)
  }
}

// 加载优惠券
const loadCoupons = async () => {
  try {
    const promotionId = route.params.id
    coupons.value = await promotionApi.getCoupons(promotionId)
  } catch (error) {
    console.error('加载优惠券失败:', error)
  }
}

// 返回
const goBack = () => {
  router.push('/promotions')
}

onMounted(() => {
  loadPromotion()
  loadCoupons()
})
</script>
