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
        <view class="btn btn-primary" @click="loadEquipmentData">查询数据</view>
        <view class="btn btn-outline" @click="loadFaultData">故障统计</view>
      </view>
    </view>

    <view class="summary-section">
      <view class="section-title">设备状态概览</view>
      <view class="summary-grid">
        <view class="summary-item">
          <view class="stat-card">
            <view class="stat-value">{{ equipmentStats.total || 10 }}</view>
            <view class="stat-label">设备总数</view>
          </view>
        </view>
        <view class="summary-item">
          <view class="stat-card success">
            <view class="stat-value">{{ equipmentStats.running || 8 }}</view>
            <view class="stat-label">运行中</view>
          </view>
        </view>
        <view class="summary-item">
          <view class="stat-card warning">
            <view class="stat-value">{{ equipmentStats.maintenance || 1 }}</view>
            <view class="stat-label">维护中</view>
          </view>
        </view>
        <view class="summary-item">
          <view class="stat-card danger">
            <view class="stat-value">{{ equipmentStats.fault || 1 }}</view>
            <view class="stat-label">故障</view>
          </view>
        </view>
      </view>
    </view>

    <view class="chart-section" v-if="operatingRateData">
      <view class="section-title">设备开机率趋势</view>
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
                v-for="(item, idx) in chartDataPoints" 
                :key="idx"
                :style="{ 
                  left: getPointX(idx, chartDataPoints.length),
                  bottom: getPointY(item.rate)
                }"
              >
                <view class="point-label">{{ item.rate }}%</view>
              </view>
            </view>
            <view class="x-labels">
              <view class="x-label" v-for="(item, idx) in chartDataPoints" :key="idx">
                {{ item.date }}
              </view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="table-section">
      <view class="section-title">设备运行详情</view>
      <view class="equipment-list">
        <view class="equipment-item" v-for="(equipment, idx) in equipmentList" :key="idx">
          <view class="equipment-header">
            <view class="equipment-name">{{ equipment.name }}</view>
            <view class="equipment-status" :class="equipment.status">
              {{ equipment.statusText }}
            </view>
          </view>
          <view class="equipment-stats">
            <view class="stat-item">
              <view class="stat-label">今日运行</view>
              <view class="stat-value">{{ equipment.runtime }}小时</view>
            </view>
            <view class="stat-item">
              <view class="stat-label">今日停机</view>
              <view class="stat-value">{{ equipment.downtime }}小时</view>
            </view>
            <view class="stat-item">
              <view class="stat-label">开机率</view>
              <view class="stat-value" :class="equipment.rate >= 90 ? 'text-success' : 'text-warning'">
                {{ equipment.rate }}%
              </view>
            </view>
          </view>
          <view class="equipment-info">
            <text class="info-text">设备编号: {{ equipment.no }}</text>
            <text class="info-text">位置: {{ equipment.location }}</text>
          </view>
        </view>
      </view>
    </view>

    <view class="maintenance-section" v-if="maintenanceList.length > 0">
      <view class="section-title">待保养设备</view>
      <view class="maintenance-list">
        <view class="maintenance-item" v-for="(item, idx) in maintenanceList" :key="idx">
          <view class="maintenance-icon">
            <text>🔧</text>
          </view>
          <view class="maintenance-content">
            <view class="maintenance-title">{{ item.equipmentName }}</view>
            <view class="maintenance-desc">{{ item.content }}</view>
            <view class="maintenance-date">计划时间: {{ item.planDate }}</view>
          </view>
          <view class="maintenance-status" :class="item.urgent ? 'urgent' : ''">
            {{ item.urgent ? '紧急' : '待执行' }}
          </view>
        </view>
      </view>
    </view>

    <view class="loading-state" v-if="loading">
      <view class="loading-text">数据加载中...</view>
    </view>
  </view>
</template>

<script>
import { equipmentApi } from '@/api/index.js'

export default {
  data() {
    return {
      startDate: '',
      endDate: '',
      loading: false,
      operatingRateData: null,
      equipmentStats: {
        total: 10,
        running: 8,
        maintenance: 1,
        fault: 1
      },
      chartDataPoints: [
        { date: '05-01', rate: 96.5 },
        { date: '05-02', rate: 94.2 },
        { date: '05-03', rate: 97.8 },
        { date: '05-04', rate: 95.6 },
        { date: '05-05', rate: 98.3 },
        { date: '05-06', rate: 92.1 },
        { date: '05-07', rate: 95.0 }
      ],
      equipmentList: [
        {
          no: 'EQ2026001',
          name: '球磨机-1',
          status: 'running',
          statusText: '运行中',
          runtime: 22.5,
          downtime: 1.5,
          rate: 93.8,
          location: '车间1区'
        },
        {
          no: 'EQ2026002',
          name: '回转窑-1',
          status: 'running',
          statusText: '运行中',
          runtime: 24.0,
          downtime: 0.0,
          rate: 100.0,
          location: '车间1区'
        },
        {
          no: 'EQ2026003',
          name: '破碎机-1',
          status: 'maintenance',
          statusText: '维护中',
          runtime: 12.0,
          downtime: 12.0,
          rate: 50.0,
          location: '车间2区'
        },
        {
          no: 'EQ2026004',
          name: '输送机-1',
          status: 'running',
          statusText: '运行中',
          runtime: 23.5,
          downtime: 0.5,
          rate: 97.9,
          location: '车间2区'
        },
        {
          no: 'EQ2026005',
          name: '包装机-1',
          status: 'fault',
          statusText: '故障',
          runtime: 0.0,
          downtime: 24.0,
          rate: 0.0,
          location: '车间3区'
        }
      ],
      maintenanceList: [
        {
          equipmentName: '球磨机-1',
          content: '日常保养 - 润滑油检查',
          planDate: '2026-05-06',
          urgent: false
        },
        {
          equipmentName: '回转窑-1',
          content: '一级保养 - 轴承更换',
          planDate: '2026-05-05',
          urgent: true
        }
      ]
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
      
      const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000)
      const sYear = sevenDaysAgo.getFullYear()
      const sMonth = String(sevenDaysAgo.getMonth() + 1).padStart(2, '0')
      const sDay = String(sevenDaysAgo.getDate()).padStart(2, '0')
      
      this.startDate = `${sYear}-${sMonth}-${sDay}`
    },

    onStartDateChange(e) {
      this.startDate = e.detail.value
    },

    onEndDateChange(e) {
      this.endDate = e.detail.value
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

    async loadEquipmentData() {
      if (!this.startDate || !this.endDate) {
        uni.showToast({ title: '请选择日期范围', icon: 'none' })
        return
      }

      this.loading = true

      try {
        const result = await equipmentApi.getOperatingRateChart('line', this.startDate, this.endDate)
        this.operatingRateData = result
        
        if (result && result.series && result.series.length > 0) {
          const rates = result.series[0].data
          const dates = result.x_axis_data || []
          
          if (rates && rates.length > 0) {
            this.chartDataPoints = rates.map((rate, idx) => ({
              date: dates[idx] || `第${idx + 1}天`,
              rate: rate
            }))
          }
        }
        
        uni.showToast({ title: '加载成功', icon: 'success' })
      } catch (e) {
        console.error('加载设备数据失败:', e)
      } finally {
        this.loading = false
      }
    },

    loadFaultData() {
      uni.navigateTo({ url: '/pages/equipment/fault' })
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
    background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
    color: #FFFFFF;
  }

  &.btn-outline {
    background-color: #FFFFFF;
    color: #FAAD14;
    border: 2rpx solid #FAAD14;
  }
}

.summary-section,
.chart-section,
.table-section,
.maintenance-section {
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
  width: 50%;
  padding: 8rpx;
  box-sizing: border-box;

  .stat-card {
    background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
    border-radius: 16rpx;
    padding: 24rpx;
    text-align: center;
    color: #FFFFFF;

    &.success {
      background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
    }

    &.warning {
      background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
    }

    &.danger {
      background: linear-gradient(135deg, #FF4D4F 0%, #FF7875 100%);
    }

    .stat-value {
      font-size: 40rpx;
      font-weight: 600;
      margin-bottom: 8rpx;
    }

    .stat-label {
      font-size: 24rpx;
      opacity: 0.9;
    }
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
      background-color: #FAAD14;
      border-radius: 50%;
      border: 4rpx solid #FFE58F;
      transform: translate(-50%, 50%);

      .point-label {
        position: absolute;
        top: -40rpx;
        left: 50%;
        transform: translateX(-50%);
        font-size: 20rpx;
        color: #FAAD14;
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

.equipment-list {
  .equipment-item {
    background-color: #FAFAFA;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 16rpx;

    &:last-child {
      margin-bottom: 0;
    }

    .equipment-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16rpx;

      .equipment-name {
        font-size: 30rpx;
        font-weight: 600;
        color: #1F2329;
      }

      .equipment-status {
        padding: 6rpx 16rpx;
        border-radius: 6rpx;
        font-size: 22rpx;

        &.running {
          background-color: #F6FFED;
          color: #52C41A;
        }

        &.maintenance {
          background-color: #FFFBE6;
          color: #FAAD14;
        }

        &.fault {
          background-color: #FFF2F0;
          color: #FF4D4F;
        }
      }
    }

    .equipment-stats {
      display: flex;
      margin-bottom: 16rpx;

      .stat-item {
        flex: 1;
        text-align: center;

        .stat-label {
          font-size: 22rpx;
          color: #999999;
          margin-bottom: 6rpx;
        }

        .stat-value {
          font-size: 28rpx;
          font-weight: 500;
          color: #1F2329;

          &.text-success {
            color: #52C41A;
          }

          &.text-warning {
            color: #FAAD14;
          }
        }
      }
    }

    .equipment-info {
      display: flex;
      justify-content: space-between;

      .info-text {
        font-size: 22rpx;
        color: #999999;
      }
    }
  }
}

.maintenance-list {
  .maintenance-item {
    display: flex;
    align-items: center;
    padding: 16rpx 0;
    border-bottom: 1rpx solid #F0F0F0;

    &:last-child {
      border-bottom: none;
    }

    .maintenance-icon {
      width: 60rpx;
      height: 60rpx;
      background-color: #FFFBE6;
      border-radius: 12rpx;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 32rpx;
      margin-right: 16rpx;
    }

    .maintenance-content {
      flex: 1;

      .maintenance-title {
        font-size: 28rpx;
        font-weight: 500;
        color: #1F2329;
        margin-bottom: 6rpx;
      }

      .maintenance-desc {
        font-size: 24rpx;
        color: #666666;
        margin-bottom: 4rpx;
      }

      .maintenance-date {
        font-size: 22rpx;
        color: #999999;
      }
    }

    .maintenance-status {
      padding: 8rpx 16rpx;
      background-color: #FFFBE6;
      color: #FAAD14;
      border-radius: 6rpx;
      font-size: 22rpx;

      &.urgent {
        background-color: #FFF2F0;
        color: #FF4D4F;
      }
    }
  }
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80rpx 40rpx;
}

.loading-text {
  font-size: 28rpx;
  color: #999999;
}
</style>
