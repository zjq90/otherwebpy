<template>
  <view class="container">
    <view class="filter-section">
      <view class="filter-row">
        <view class="filter-label">开始日期:</view>
        <picker 
          mode="date" 
          :value="startDate" 
          @change="onStartDateChange"
        >
          <view class="picker-text">{{ startDate }} ▼</view>
        </picker>
      </view>
      <view class="filter-row">
        <view class="filter-label">结束日期:</view>
        <picker 
          mode="date" 
          :value="endDate" 
          @change="onEndDateChange"
        >
          <view class="picker-text">{{ endDate }} ▼</view>
        </picker>
      </view>
      <view class="action-buttons">
        <view class="btn btn-primary" @click="loadQualityData">查询数据</view>
        <view class="btn btn-outline" @click="loadStrengthData">强度分析</view>
      </view>
    </view>

    <view class="summary-section" v-if="qualityTrend">
      <view class="section-title">质量数据概览</view>
      <view class="summary-grid">
        <view class="summary-item">
          <view class="summary-value">{{ qualityTrend.total_samples?.toLocaleString() || 0 }}</view>
          <view class="summary-label">总样本数</view>
        </view>
        <view class="summary-item">
          <view class="summary-value text-success">{{ qualityTrend.total_passed?.toLocaleString() || 0 }}</view>
          <view class="summary-label">合格样本</view>
        </view>
        <view class="summary-item">
          <view class="summary-value" :class="qualityTrend.avg_pass_rate >= 95 ? 'text-success' : 'text-warning'">
            {{ qualityTrend.avg_pass_rate || 0 }}%
          </view>
          <view class="summary-label">平均合格率</view>
        </view>
      </view>
    </view>

    <view class="chart-section" v-if="qualityTrend && qualityTrend.data">
      <view class="section-title">原材料检验合格率趋势</view>
      <view class="chart-container">
        <view class="line-chart">
          <view class="y-axis">
            <view class="y-tick" v-for="tick in 6" :key="tick">
              {{ ((tick - 1) * 20) }}%
            </view>
          </view>
          <view class="chart-area">
            <view class="grid-lines">
              <view class="grid-line" v-for="line in 5" :key="line"></view>
            </view>
            <view class="data-points">
              <view 
                class="data-point" 
                v-for="(item, idx) in qualityTrend.data" 
                :key="idx"
                :style="{ 
                  left: getPointX(idx, qualityTrend.data.length),
                  bottom: getPointY(item.pass_rate)
                }"
              >
                <view class="point-label">{{ item.pass_rate }}%</view>
              </view>
            </view>
            <view class="x-labels">
              <view class="x-label" v-for="(item, idx) in qualityTrend.data" :key="idx">
                {{ getShortDate(item.date) }}
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="table-section" v-if="qualityTrend && qualityTrend.data">
      <view class="section-title">详细数据</view>
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">日期</view>
          <view class="table-cell">材料名称</view>
          <view class="table-cell">总样本</view>
          <view class="table-cell">合格数</view>
          <view class="table-cell">合格率</view>
        </view>
        <scroll-view scroll-x class="table-body">
          <view class="table-row" v-for="(item, idx) in qualityTrend.data" :key="idx">
            <view class="table-cell">{{ getShortDate(item.date) }}</view>
            <view class="table-cell">{{ item.material_name || '-' }}</view>
            <view class="table-cell">{{ item.total_samples?.toLocaleString() || 0 }}</view>
            <view class="table-cell text-success">{{ item.passed_samples?.toLocaleString() || 0 }}</view>
            <view class="table-cell" :class="item.pass_rate >= 95 ? 'text-success' : 'text-warning'">
              {{ item.pass_rate || 0 }}%
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <view class="empty-state" v-if="!loading && !qualityTrend">
      <view class="empty-icon">📋</view>
      <view class="empty-text">请选择日期范围后点击查询</view>
    </view>

    <view class="loading-state" v-if="loading">
      <view class="loading-text">数据加载中...</view>
    </view>
  </view>
</template>

<script>
import { qualityApi } from '@/api/index.js'

export default {
  data() {
    return {
      startDate: '',
      endDate: '',
      qualityTrend: null,
      loading: false
    }
  },
  onLoad() {
    this.initDates()
  },
  methods: {
    initDates() {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      
      this.endDate = `${year}-${month}-${day}`
      
      const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000)
      const sYear = thirtyDaysAgo.getFullYear()
      const sMonth = String(thirtyDaysAgo.getMonth() + 1).padStart(2, '0')
      const sDay = String(thirtyDaysAgo.getDate()).padStart(2, '0')
      
      this.startDate = `${sYear}-${sMonth}-${sDay}`
    },

    onStartDateChange(e) {
      this.startDate = e.detail.value
    },

    onEndDateChange(e) {
      this.endDate = e.detail.value
    },

    getShortDate(dateStr) {
      if (!dateStr) return ''
      const parts = dateStr.split('-')
      return `${parts[1]}-${parts[2]}`
    },

    getPointX(index, total) {
      if (total <= 1) return '50%'
      const percentage = (index / (total - 1)) * 100
      return `${percentage}%`
    },

    getPointY(rate) {
      const clampedRate = Math.min(Math.max(rate, 0), 100)
      const percentage = (clampedRate / 100) * 100
      return `${percentage}%`
    },

    async loadQualityData() {
      if (!this.startDate || !this.endDate) {
        uni.showToast({ title: '请选择日期范围', icon: 'none' })
        return
      }

      this.loading = true
      this.qualityTrend = null

      try {
        const result = await qualityApi.getQualityTrend(this.startDate, this.endDate)
        this.qualityTrend = result
        
        if (result && result.data && result.data.length > 0) {
          uni.showToast({ title: '加载成功', icon: 'success' })
        } else {
          uni.showToast({ title: '暂无数据', icon: 'none' })
        }
      } catch (e) {
        console.error('加载质量数据失败:', e)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    loadStrengthData() {
      uni.navigateTo({ url: '/pages/quality/strength' })
    }
  }
}
</script>

<style lang="scss" scoped>
.container {
  min-height: 100vh;
  background-color: #F5F7FA;
  padding-bottom: 40rpx;
}

.filter-section {
  background-color: #FFFFFF;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.filter-row {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;

  &:last-child {
    margin-bottom: 0;
  }

  .filter-label {
    width: 160rpx;
    font-size: 28rpx;
    color: #666666;
  }

  .picker-text {
    display: flex;
    align-items: center;
    padding: 16rpx 24rpx;
    background-color: #F5F7FA;
    border-radius: 8rpx;
    font-size: 28rpx;
    color: #333333;
  }
}

.action-buttons {
  display: flex;
  margin-top: 24rpx;
}

.btn {
  flex: 1;
  padding: 20rpx;
  border-radius: 12rpx;
  text-align: center;
  font-size: 28rpx;
  font-weight: 500;
  margin: 0 10rpx;

  &.btn-primary {
    background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
    color: #FFFFFF;
  }

  &.btn-outline {
    background-color: #FFFFFF;
    color: #1890FF;
    border: 2rpx solid #1890FF;
  }
}

.summary-section,
.chart-section,
.table-section {
  background-color: #FFFFFF;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F2329;
  margin-bottom: 20rpx;
}

.summary-grid {
  display: flex;
}

.summary-item {
  flex: 1;
  text-align: center;
  padding: 16rpx;

  .summary-value {
    font-size: 36rpx;
    font-weight: 600;
    color: #1F2329;
    margin-bottom: 8rpx;

    &.text-success {
      color: #52C41A;
    }

    &.text-warning {
      color: #FAAD14;
    }
  }

  .summary-label {
    font-size: 24rpx;
    color: #999999;
  }
}

.chart-container {
  .line-chart {
    display: flex;
    height: 360rpx;
  }

  .y-axis {
    width: 80rpx;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding-right: 12rpx;

    .y-tick {
      font-size: 20rpx;
      color: #999999;
      text-align: right;
    }
  }

  .chart-area {
    flex: 1;
    position: relative;
    border-left: 2rpx solid #E8E8E8;
    border-bottom: 2rpx solid #E8E8E8;
    padding-left: 12rpx;
    padding-bottom: 40rpx;
  }

  .grid-lines {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 40rpx;
    display: flex;
    flex-direction: column;
    justify-content: space-between;

    .grid-line {
      height: 1rpx;
      background-color: #F0F0F0;
    }
  }

  .data-points {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 40rpx;

    .data-point {
      position: absolute;
      width: 24rpx;
      height: 24rpx;
      background-color: #52C41A;
      border-radius: 50%;
      border: 4rpx solid #D9F7BE;
      transform: translate(-50%, 50%);

      .point-label {
        position: absolute;
        top: -40rpx;
        left: 50%;
        transform: translateX(-50%);
        font-size: 20rpx;
        color: #52C41A;
        font-weight: 500;
        white-space: nowrap;
      }
    }
  }

  .x-labels {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    display: flex;
    justify-content: space-between;
    padding-top: 8rpx;

    .x-label {
      font-size: 20rpx;
      color: #999999;
      transform: translateX(-50%);

      &:first-child {
        transform: translateX(-25%);
      }

      &:last-child {
        transform: translateX(-75%);
      }
    }
  }
}

.table-container {
  .table-header {
    display: flex;
    background-color: #FAFAFA;
    border-radius: 8rpx 8rpx 0 0;
  }

  .table-body {
    white-space: nowrap;
  }

  .table-row {
    display: flex;
    border-bottom: 1rpx solid #F0F0F0;

    &:last-child {
      border-bottom: none;
    }
  }

  .table-cell {
    width: 180rpx;
    padding: 20rpx 12rpx;
    font-size: 24rpx;
    text-align: center;
    flex-shrink: 0;

    .table-header & {
      font-weight: 600;
      color: #666666;
    }

    &.text-success {
      color: #52C41A;
      font-weight: 500;
    }

    &.text-warning {
      color: #FAAD14;
      font-weight: 500;
    }
  }
}

.empty-state,
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80rpx 40rpx;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-text,
.loading-text {
  font-size: 28rpx;
  color: #999999;
}
</style>
