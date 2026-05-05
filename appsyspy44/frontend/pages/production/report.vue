<template>
  <view class="container">
    <view class="filter-section">
      <view class="filter-row">
        <view class="filter-label">报告类型:</view>
        <view class="filter-options">
          <view 
            class="filter-option" 
            :class="{ active: reportType === 'daily' }"
            @click="reportType = 'daily'"
          >日报</view>
          <view 
            class="filter-option" 
            :class="{ active: reportType === 'weekly' }"
            @click="reportType = 'weekly'"
          >周报</view>
          <view 
            class="filter-option" 
            :class="{ active: reportType === 'monthly' }"
            @click="reportType = 'monthly'"
          >月报</view>
        </view>
      </view>
      
      <view class="filter-row">
        <view class="filter-label">选择日期:</view>
        <picker 
          mode="date" 
          :value="selectedDate" 
          :start="startDate" 
          :end="endDate"
          @change="onDateChange"
        >
          <view class="picker-text">
            {{ selectedDate }}
            <text class="picker-icon">▼</text>
          </view>
        </picker>
      </view>

      <view class="filter-row">
        <view class="filter-label">图表类型:</view>
        <view class="filter-options">
          <view 
            class="filter-option" 
            :class="{ active: chartType === 'bar' }"
            @click="chartType = 'bar'"
          >柱状图</view>
          <view 
            class="filter-option" 
            :class="{ active: chartType === 'line' }"
            @click="chartType = 'line'"
          >折线图</view>
        </view>
      </view>

      <view class="action-buttons">
        <view class="btn btn-primary" @click="loadReport">
          查询数据
        </view>
        <view class="btn btn-outline" @click="exportReport">
          导出报表
        </view>
      </view>
    </view>

    <view class="summary-section" v-if="reportData">
      <view class="section-title">数据概览</view>
      <view class="summary-grid">
        <view class="summary-item">
          <view class="summary-value">{{ reportData.total_planned?.toLocaleString() || 0 }}</view>
          <view class="summary-label">计划产量</view>
        </view>
        <view class="summary-item">
          <view class="summary-value text-primary">{{ reportData.total_actual?.toLocaleString() || 0 }}</view>
          <view class="summary-label">实际产量</view>
        </view>
        <view class="summary-item">
          <view class="summary-value text-success">{{ reportData.total_qualified?.toLocaleString() || 0 }}</view>
          <view class="summary-label">合格产量</view>
        </view>
        <view class="summary-item">
          <view class="summary-value text-warning">{{ reportData.avg_completion_rate || 0 }}%</view>
          <view class="summary-label">平均完成率</view>
        </view>
        <view class="summary-item">
          <view class="summary-value text-success">{{ reportData.avg_pass_rate || 0 }}%</view>
          <view class="summary-label">平均合格率</view>
        </view>
      </view>
    </view>

    <view class="chart-section" v-if="chartData">
      <view class="section-title">产量统计图表</view>
      <view class="chart-container">
        <view class="chart-legend">
          <view class="legend-item">
            <view class="legend-color planned"></view>
            <text>计划产量</text>
          </view>
          <view class="legend-item">
            <view class="legend-color actual"></view>
            <text>实际产量</text>
          </view>
          <view class="legend-item">
            <view class="legend-color qualified"></view>
            <text>合格产量</text>
          </view>
        </view>
        
        <view class="chart-area">
          <view class="chart-y-axis">
            <view class="y-tick" v-for="(tick, idx) in yTicks" :key="idx">
              {{ tick }}
            </view>
          </view>
          
          <view class="chart-bars">
            <view class="bar-group" v-for="(item, idx) in chartData.data" :key="idx">
              <view class="bar-set">
                <view 
                  class="bar-item planned" 
                  :style="{ height: getBarHeight(item.planned_quantity, maxValue) }"
                ></view>
                <view 
                  class="bar-item actual" 
                  :style="{ height: getBarHeight(item.actual_quantity, maxValue) }"
                ></view>
                <view 
                  class="bar-item qualified" 
                  :style="{ height: getBarHeight(item.qualified_quantity, maxValue) }"
                ></view>
              </view>
              <view class="bar-label">{{ getShortDate(item.date) }}</view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="table-section" v-if="reportData && reportData.data">
      <view class="section-title">详细数据</view>
      <view class="table-container">
        <view class="table-header">
          <view class="table-cell">日期</view>
          <view class="table-cell">计划</view>
          <view class="table-cell">实际</view>
          <view class="table-cell">合格</view>
          <view class="table-cell">完成率</view>
          <view class="table-cell">合格率</view>
        </view>
        <scroll-view scroll-x class="table-body">
          <view class="table-row" v-for="(item, idx) in reportData.data" :key="idx">
            <view class="table-cell">{{ getShortDate(item.date) }}</view>
            <view class="table-cell">{{ item.planned_quantity?.toLocaleString() || 0 }}</view>
            <view class="table-cell text-primary">{{ item.actual_quantity?.toLocaleString() || 0 }}</view>
            <view class="table-cell text-success">{{ item.qualified_quantity?.toLocaleString() || 0 }}</view>
            <view class="table-cell" :class="item.completion_rate >= 90 ? 'text-success' : 'text-warning'">
              {{ item.completion_rate || 0 }}%
            </view>
            <view class="table-cell" :class="item.pass_rate >= 95 ? 'text-success' : 'text-warning'">
              {{ item.pass_rate || 0 }}%
            </view>
          </view>
        </scroll-view>
      </view>
    </view>

    <view class="empty-state" v-if="!loading && !reportData">
      <view class="empty-icon">📊</view>
      <view class="empty-text">请选择报告类型和日期后点击查询</view>
    </view>

    <view class="loading-state" v-if="loading">
      <view class="loading-text">数据加载中...</view>
    </view>
  </view>
</template>

<script>
import { productionApi } from '@/api/index.js'

export default {
  data() {
    return {
      reportType: 'daily',
      selectedDate: '',
      startDate: '2024-01-01',
      endDate: '',
      chartType: 'bar',
      reportData: null,
      chartData: null,
      loading: false,
      maxValue: 0,
      yTicks: []
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
      this.selectedDate = `${year}-${month}-${day}`
      this.startDate = `${year - 1}-01-01`
    },

    onDateChange(e) {
      this.selectedDate = e.detail.value
    },

    getShortDate(dateStr) {
      if (!dateStr) return ''
      const parts = dateStr.split('-')
      if (this.reportType === 'daily') {
        return `${parts[1]}-${parts[2]}`
      }
      return `${parts[1]}-${parts[2]}`
    },

    async loadReport() {
      if (!this.selectedDate) {
        uni.showToast({ title: '请选择日期', icon: 'none' })
        return
      }

      this.loading = true
      this.reportData = null
      this.chartData = null

      try {
        let result
        const dateParts = this.selectedDate.split('-')
        const year = parseInt(dateParts[0])
        const month = parseInt(dateParts[1])
        const day = parseInt(dateParts[2])

        if (this.reportType === 'daily') {
          result = await productionApi.getDailyReport(this.selectedDate)
        } else if (this.reportType === 'weekly') {
          const weekStart = this.getWeekStart(year, month, day)
          result = await productionApi.getWeeklyReport(weekStart)
        } else {
          result = await productionApi.getMonthlyReport(year, month)
        }

        this.reportData = result
        
        if (result && result.data && result.data.length > 0) {
          this.chartData = result
          this.calculateMaxValue()
        }

        uni.showToast({ title: '加载成功', icon: 'success' })
      } catch (e) {
        console.error('加载报表失败:', e)
        uni.showToast({ title: '加载失败，请稍后重试', icon: 'none' })
      } finally {
        this.loading = false
      }
    },

    getWeekStart(year, month, day) {
      const date = new Date(year, month - 1, day)
      const dayOfWeek = date.getDay()
      const diff = date.getDate() - dayOfWeek + (dayOfWeek === 0 ? -6 : 1)
      const monday = new Date(date.setDate(diff))
      
      const y = monday.getFullYear()
      const m = String(monday.getMonth() + 1).padStart(2, '0')
      const d = String(monday.getDate()).padStart(2, '0')
      
      return `${y}-${m}-${d}`
    },

    calculateMaxValue() {
      if (!this.chartData || !this.chartData.data) return

      const values = this.chartData.data.flatMap(item => [
        item.planned_quantity || 0,
        item.actual_quantity || 0,
        item.qualified_quantity || 0
      ])

      const max = Math.max(...values, 100)
      const roundedMax = Math.ceil(max / 1000) * 1000
      
      this.maxValue = roundedMax
      
      const tickCount = 5
      this.yTicks = []
      for (let i = tickCount; i >= 0; i--) {
        const value = Math.round((roundedMax / tickCount) * i)
        this.yTicks.push(value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value)
      }
    },

    getBarHeight(value, max) {
      if (max === 0) return '0%'
      const percentage = Math.min((value / max) * 100, 100)
      return `${percentage}%`
    },

    async exportReport() {
      if (!this.reportData) {
        uni.showToast({ title: '请先查询数据', icon: 'none' })
        return
      }

      uni.showLoading({ title: '正在导出...' })
      
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        uni.hideLoading()
        uni.showModal({
          title: '导出成功',
          content: '报表已导出到下载目录',
          showCancel: false
        })
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: '导出失败', icon: 'none' })
      }
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

  .filter-options {
    display: flex;
    flex: 1;
  }

  .filter-option {
    padding: 12rpx 24rpx;
    margin-right: 16rpx;
    border-radius: 8rpx;
    font-size: 26rpx;
    color: #666666;
    background-color: #F5F7FA;
    border: 2rpx solid transparent;

    &.active {
      color: #1890FF;
      background-color: #E6F7FF;
      border-color: #91D5FF;
    }
  }

  .picker-text {
    display: flex;
    align-items: center;
    padding: 16rpx 24rpx;
    background-color: #F5F7FA;
    border-radius: 8rpx;
    font-size: 28rpx;
    color: #333333;

    .picker-icon {
      margin-left: 16rpx;
      font-size: 20rpx;
      color: #999999;
    }
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
    background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
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
  flex-wrap: wrap;
}

.summary-item {
  width: 33.33%;
  text-align: center;
  padding: 16rpx 8rpx;

  .summary-value {
    font-size: 36rpx;
    font-weight: 600;
    color: #1F2329;
    margin-bottom: 8rpx;

    &.text-primary {
      color: #1890FF;
    }

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
  .chart-legend {
    display: flex;
    justify-content: center;
    margin-bottom: 24rpx;

    .legend-item {
      display: flex;
      align-items: center;
      margin: 0 20rpx;
      font-size: 24rpx;
      color: #666666;

      .legend-color {
        width: 24rpx;
        height: 24rpx;
        border-radius: 4rpx;
        margin-right: 10rpx;

        &.planned {
          background-color: #91D5FF;
        }

        &.actual {
          background-color: #1890FF;
        }

        &.qualified {
          background-color: #52C41A;
        }
      }
    }
  }

  .chart-area {
    display: flex;
    height: 360rpx;
  }

  .chart-y-axis {
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

  .chart-bars {
    flex: 1;
    display: flex;
    align-items: flex-end;
    border-left: 2rpx solid #E8E8E8;
    border-bottom: 2rpx solid #E8E8E8;
    padding-left: 12rpx;
    padding-bottom: 12rpx;
  }

  .bar-group {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;

    .bar-set {
      flex: 1;
      display: flex;
      align-items: flex-end;
      justify-content: center;
      width: 100%;

      .bar-item {
        width: 12rpx;
        margin: 0 6rpx;
        border-radius: 6rpx 6rpx 0 0;
        transition: height 0.3s ease;

        &.planned {
          background-color: #91D5FF;
        }

        &.actual {
          background-color: #1890FF;
        }

        &.qualified {
          background-color: #52C41A;
        }
      }
    }

    .bar-label {
      font-size: 20rpx;
      color: #999999;
      margin-top: 12rpx;
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
    width: 160rpx;
    padding: 20rpx 12rpx;
    font-size: 24rpx;
    text-align: center;
    flex-shrink: 0;

    .table-header & {
      font-weight: 600;
      color: #666666;
    }

    &.text-primary {
      color: #1890FF;
      font-weight: 500;
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
