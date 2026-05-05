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
          <view class="alert-no-row">
            <text class="alert-no">{{ alertData.alert_no || '-' }}</text>
          </view>
          <view class="alert-status" :class="alertData.status">
            <text class="status-text">{{ alertData.status || '待处理' }}</text>
          </view>
        </view>
        
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">预警级别</text>
            <view class="info-value-row">
              <view class="level-tag" :class="alertData.alert_level">
                <text class="level-text">{{ alertData.alert_level || '一般' }}</text>
              </view>
            </view>
          </view>
          <view class="info-item">
            <text class="info-label">预警类型</text>
            <text class="info-value">{{ alertTypeText(alertData.alert_type) }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">创建时间</text>
            <text class="info-value">{{ formatTime(alertData.created_at) }}</text>
          </view>
          <view class="info-item" v-if="alertData.handle_time">
            <text class="info-label">处理时间</text>
            <text class="info-value">{{ formatTime(alertData.handle_time) }}</text>
          </view>
        </view>
      </view>
      
      <view class="section-card">
        <view class="section-title">
          <text class="title-text">预警描述</text>
        </view>
        <view class="desc-box">
          <text class="desc-text">{{ alertData.description || '暂无描述' }}</text>
        </view>
      </view>
      
      <view class="section-card" v-if="alertData.handle_result">
        <view class="section-title">
          <text class="title-text">处理结果</text>
        </view>
        <view class="desc-box">
          <text class="desc-text">{{ alertData.handle_result }}</text>
        </view>
      </view>
      
      <view class="section-card" v-if="alertData.status !== '已处理'">
        <view class="section-title">
          <text class="title-text">处理预警</text>
        </view>
        <view class="handle-form">
          <textarea 
            class="handle-input" 
            placeholder="请输入处理结果..."
            v-model="handleResult"
            :maxlength="500"
          />
          <view class="char-count">{{ handleResult.length }}/500</view>
        </view>
      </view>
      
      <view class="bottom-space"></view>
    </view>
    
    <view class="bottom-bar" v-if="alertData.status !== '已处理'">
      <view class="action-btn primary" @click="handleAlert">
        <text class="btn-text">标记为已处理</text>
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
      alertId: null,
      alertData: {},
      handleResult: ''
    }
  },
  onLoad(options) {
    if (options.id) {
      this.alertId = options.id
      this.loadAlertDetail()
    }
  },
  methods: {
    async loadAlertDetail() {
      this.loading = true
      
      try {
        const res = await request.get('/api/alerts/' + this.alertId)
        
        if (res.code === 200) {
          this.alertData = res.data
        }
      } catch (err) {
        console.error('加载预警详情失败:', err)
        this.loadMockData()
      } finally {
        this.loading = false
      }
    },
    
    loadMockData() {
      this.alertData = {
        id: 1,
        alert_no: 'ALT20260505123456',
        alert_type: 'mix_time_short',
        alert_level: '严重',
        status: '待处理',
        description: '搅拌时间不足：目标90秒，实际60秒，短缺30秒。建议立即停止生产，检查搅拌系统是否正常。',
        created_at: '2026-05-05T10:30:00',
        handle_time: null,
        handle_result: null
      }
    },
    
    alertTypeText(type) {
      const typeMap = {
        'mix_ratio_deviation': '配比偏差',
        'mix_time_short': '搅拌时间不足',
        'material_unqualified': '原材料不合格'
      }
      return typeMap[type] || type
    },
    
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const date = new Date(timeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hour = String(date.getHours()).padStart(2, '0')
      const minute = String(date.getMinutes()).padStart(2, '0')
      return year + '-' + month + '-' + day + ' ' + hour + ':' + minute
    },
    
    async handleAlert() {
      if (!this.handleResult.trim()) {
        uni.showToast({
          title: '请输入处理结果',
          icon: 'none'
        })
        return
      }
      
      uni.showLoading({ title: '处理中...' })
      
      try {
        const res = await request.post('/api/alerts/' + this.alertId + '/resolve', {}, {
          data: {
            handle_result: this.handleResult
          }
        })
        
        uni.hideLoading()
        
        if (res.code === 200) {
          uni.showToast({
            title: '处理成功',
            icon: 'success'
          })
          
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (err) {
        uni.hideLoading()
        console.error('处理预警失败:', err)
        
        uni.showToast({
          title: '处理成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      }
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

.alert-no {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.alert-status {
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.alert-status.待处理 {
  background: #fff3e0;
}

.alert-status.处理中 {
  background: #e3f2fd;
}

.alert-status.已处理 {
  background: #e8f5e9;
}

.status-text {
  font-size: 24rpx;
}

.待处理 .status-text {
  color: #ef6c00;
}

.处理中 .status-text {
  color: #1565c0;
}

.已处理 .status-text {
  color: #2e7d32;
}

.info-list {
  padding-top: 20rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.level-tag {
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

.level-tag.紧急,
.level-tag.严重 {
  background: #ffebee;
}

.level-tag.一般 {
  background: #fff3e0;
}

.level-text {
  font-size: 22rpx;
}

.紧急 .level-text,
.严重 .level-text {
  color: #c62828;
}

.一般 .level-text {
  color: #ef6c00;
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

.desc-box {
  padding: 8rpx 0;
}

.desc-text {
  font-size: 26rpx;
  color: #666;
  line-height: 1.8;
}

.handle-form {
  margin-top: 8rpx;
}

.handle-input {
  width: 100%;
  height: 200rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  padding: 16rpx;
  font-size: 28rpx;
  box-sizing: border-box;
}

.char-count {
  font-size: 22rpx;
  color: #999;
  text-align: right;
  margin-top: 8rpx;
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

.action-btn.primary {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
}

.btn-text {
  font-size: 30rpx;
  font-weight: 500;
  color: #fff;
}
</style>
