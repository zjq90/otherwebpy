<template>
  <view class="detail-container">
    <view class="loading-state" v-if="loading">
      <view class="loading-icon">
        <text class="loading-text">⏳</text>
      </view>
      <text class="loading-title">加载中...</text>
    </view>
    
    <view v-else class="content">
      <view class="info-card">
        <view class="card-header">
          <view class="info-row">
            <text class="inspection-no">{{ inspectionData.inspection_no || '-' }}</text>
          </view>
          <view class="status-tag" :class="inspectionData.status">
            <text class="status-text">{{ inspectionData.status || '合格' }}</text>
          </view>
        </view>
        
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">原材料</text>
            <text class="info-value">{{ (inspectionData.material && inspectionData.material.material_name) || '-' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">批次号</text>
            <text class="info-value">{{ inspectionData.batch_no || '-' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">检验日期</text>
            <text class="info-value">{{ formatDate(inspectionData.inspection_date) }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">检验员</text>
            <text class="info-value">{{ inspectionData.inspector_name || '-' }}</text>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="materialType === 'cement'">
        <view class="section-title">
          <text class="title-text">水泥检验指标</text>
        </view>
        <view class="index-list">
          <view class="index-item">
            <text class="index-label">3天抗压强度</text>
            <text class="index-value">{{ inspectionData.cement_strength_3d || '-' }} MPa</text>
          </view>
          <view class="index-item">
            <text class="index-label">28天抗压强度</text>
            <text class="index-value">{{ inspectionData.cement_strength_28d || '-' }} MPa</text>
          </view>
          <view class="index-item">
            <text class="index-label">安定性</text>
            <text class="index-value">{{ inspectionData.soundness || '-' }}</text>
          </view>
          <view class="index-item">
            <text class="index-label">细度</text>
            <text class="index-value">{{ inspectionData.cement_fineness || '-' }} %</text>
          </view>
          <view class="index-item">
            <text class="index-label">凝结时间</text>
            <text class="index-value">{{ inspectionData.setting_time || '-' }} min</text>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="materialType === 'aggregate'">
        <view class="section-title">
          <text class="title-text">骨料检验指标</text>
        </view>
        <view class="index-list">
          <view class="index-item">
            <text class="index-label">级配情况</text>
            <text class="index-value">{{ inspectionData.grading || '-' }}</text>
          </view>
          <view class="index-item">
            <text class="index-label">含泥量</text>
            <text class="index-value">{{ inspectionData.mud_content || '-' }} %</text>
          </view>
          <view class="index-item">
            <text class="index-label">针片状含量</text>
            <text class="index-value">{{ inspectionData.flaky_content || '-' }} %</text>
          </view>
          <view class="index-item">
            <text class="index-label">含水率</text>
            <text class="index-value">{{ inspectionData.water_content || '-' }} %</text>
          </view>
          <view class="index-item">
            <text class="index-label">杂质含量</text>
            <text class="index-value">{{ inspectionData.impurity_content || '-' }} %</text>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="materialType === 'admixture'">
        <view class="section-title">
          <text class="title-text">外加剂检验指标</text>
        </view>
        <view class="index-list">
          <view class="index-item">
            <text class="index-label">减水率</text>
            <text class="index-value">{{ inspectionData.water_reduction_rate || '-' }} %</text>
          </view>
          <view class="index-item">
            <text class="index-label">氯离子含量</text>
            <text class="index-value">{{ inspectionData.chloride_content || '-' }} %</text>
          </view>
          <view class="index-item">
            <text class="index-label">含气量</text>
            <text class="index-value">{{ inspectionData.air_content || '-' }} %</text>
          </view>
          <view class="index-item">
            <text class="index-label">含水率</text>
            <text class="index-value">{{ inspectionData.water_content || '-' }} %</text>
          </view>
        </view>
      </view>
      
      <view class="section-card">
        <view class="section-title">
          <text class="title-text">检验结论</text>
        </view>
        <view class="conclusion-box">
          <text class="conclusion-text">{{ inspectionData.conclusion || '暂无结论' }}</text>
        </view>
      </view>
      
      <view class="section-card">
        <view class="section-title">
          <text class="title-text">检验报告附件</text>
        </view>
        <view class="attachment-list">
          <view class="attachment-item" v-for="(item, index) in attachments" :key="index">
            <view class="attachment-icon">
              <text class="icon-text">📄</text>
            </view>
            <view class="attachment-info">
              <text class="attachment-name">{{ item.name }}</text>
              <text class="attachment-size">{{ item.size }}</text>
            </view>
            <view class="attachment-arrow">
              <text class="arrow-text">›</text>
            </view>
          </view>
          <view class="empty-attach" v-if="attachments.length === 0">
            <text class="empty-text">暂无附件</text>
          </view>
        </view>
      </view>
      
      <view class="bottom-space"></view>
    </view>
    
    <view class="bottom-bar" v-if="inspectionData.status === '合格'">
      <view class="action-btn secondary" @click="goToRecheck">
        <text class="btn-text">复检</text>
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      loading: true,
      inspectionId: null,
      inspectionData: {},
      materialType: '',
      attachments: []
    }
  },
  onLoad(options) {
    if (options.id) {
      this.inspectionId = options.id
      this.loadDetail()
    }
  },
  methods: {
    async loadDetail() {
      this.loading = true
      
      try {
        const res = await request.get('/api/inspections/' + this.inspectionId)
        
        if (res.code === 200) {
          this.inspectionData = res.data
          if (res.data.material && res.data.material.material_type) {
            this.materialType = res.data.material.material_type
          }
        }
      } catch (err) {
        console.error('加载检验详情失败:', err)
        this.loadMockData()
      } finally {
        this.loading = false
      }
    },
    
    loadMockData() {
      this.inspectionData = {
        id: 1,
        inspection_no: 'INS20260505123456',
        batch_no: 'BATCH-001',
        status: '合格',
        material: {
          material_name: 'P.O42.5普通硅酸盐水泥',
          material_type: 'cement'
        },
        inspection_date: '2026-05-05T10:00:00',
        inspector_name: '张三',
        cement_strength_3d: 28.5,
        cement_strength_28d: 52.3,
        soundness: '合格',
        cement_fineness: 2.5,
        setting_time: 120,
        conclusion: '各项检验指标均符合GB175-2007《通用硅酸盐水泥》标准要求，判定为合格。'
      }
      this.materialType = 'cement'
    },
    
    formatDate(dateStr) {
      if (!dateStr) return '-'
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return year + '-' + month + '-' + day
    },
    
    goToRecheck() {
      uni.navigateTo({
        url: '/pages/inspection/inspection-form'
      })
    }
  }
}
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 120rpx;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;
}

.loading-icon {
  width: 120rpx;
  height: 120rpx;
  background: #e3f2fd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.loading-text {
  font-size: 48rpx;
}

.loading-title {
  font-size: 28rpx;
  color: #666;
}

.content {
  padding-bottom: 40rpx;
}

.info-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.inspection-no {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.status-tag {
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.status-tag.合格 {
  background: #e8f5e9;
}

.status-tag.禁用 {
  background: #ffebee;
}

.status-text {
  font-size: 24rpx;
}

.合格 .status-text {
  color: #2e7d32;
}

.禁用 .status-text {
  color: #c62828;
}

.info-list {
  padding-top: 20rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 26rpx;
  color: #999;
}

.info-value {
  font-size: 26rpx;
  color: #333;
}

.section-card {
  background: #fff;
  margin: 0 20rpx 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
}

.section-title {
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
  margin-bottom: 16rpx;
}

.title-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.index-list {
  margin-top: 8rpx;
}

.index-item {
  display: flex;
  justify-content: space-between;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.index-item:last-child {
  border-bottom: none;
}

.index-label {
  font-size: 26rpx;
  color: #666;
}

.index-value {
  font-size: 26rpx;
  color: #333;
  font-weight: 500;
}

.conclusion-box {
  padding: 8rpx 0;
}

.conclusion-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.8;
}

.attachment-list {
  margin-top: 8rpx;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.attachment-item:last-child {
  border-bottom: none;
}

.attachment-icon {
  width: 64rpx;
  height: 64rpx;
  background: #e3f2fd;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.icon-text {
  font-size: 32rpx;
}

.attachment-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.attachment-name {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 4rpx;
}

.attachment-size {
  font-size: 22rpx;
  color: #999;
}

.attachment-arrow {
  padding: 0 8rpx;
}

.arrow-text {
  font-size: 36rpx;
  color: #ccc;
}

.empty-attach {
  text-align: center;
  padding: 20rpx 0;
}

.empty-text {
  font-size: 26rpx;
  color: #999;
}

.bottom-space {
  height: 40rpx;
}

.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 24rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
  width: 100%;
  height: 88rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.action-btn.secondary {
  background: #f5f5f5;
}

.btn-text {
  font-size: 30rpx;
  font-weight: 500;
  color: #666;
}
</style>
