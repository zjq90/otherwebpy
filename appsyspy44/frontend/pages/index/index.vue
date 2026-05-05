<template>
  <view class="container">
    <view class="header">
      <view class="title">生产数据管理系统</view>
      <view class="subtitle">实时监控 · 数据分析 · 智能决策</view>
    </view>

    <view class="stat-section">
      <view class="stat-row">
        <view class="stat-card">
          <view class="stat-value">{{ stats.totalProduction }}</view>
          <view class="stat-label">今日产量</view>
        </view>
        <view class="stat-card success">
          <view class="stat-value">{{ stats.completionRate }}%</view>
          <view class="stat-label">任务完成率</view>
        </view>
      </view>
      <view class="stat-row">
        <view class="stat-card warning">
          <view class="stat-value">{{ stats.qualityRate }}%</view>
          <view class="stat-label">生产合格率</view>
        </view>
        <view class="stat-card">
          <view class="stat-value">{{ stats.equipmentRate }}%</view>
          <view class="stat-label">设备开机率</view>
        </view>
      </view>
    </view>

    <view class="quick-section">
      <view class="section-title">快捷功能</view>
      <view class="quick-grid">
        <view class="quick-item" @click="goToPage('/pages/production/report')">
          <view class="quick-icon production">
            <text class="icon-text">📊</text>
          </view>
          <text class="quick-text">生产报表</text>
        </view>
        <view class="quick-item" @click="goToPage('/pages/quality/trend')">
          <view class="quick-icon quality">
            <text class="icon-text">✅</text>
          </view>
          <text class="quick-text">质量分析</text>
        </view>
        <view class="quick-item" @click="goToPage('/pages/equipment/analysis')">
          <view class="quick-icon equipment">
            <text class="icon-text">⚙️</text>
          </view>
          <text class="quick-text">设备分析</text>
        </view>
        <view class="quick-item" @click="goToPage('/pages/export/export')">
          <view class="quick-icon export">
            <text class="icon-text">📥</text>
          </view>
          <text class="quick-text">报表导出</text>
        </view>
      </view>
    </view>

    <view class="trend-section">
      <view class="section-header">
        <view class="section-title">产量趋势</view>
        <view class="section-more" @click="goToPage('/pages/production/report')">
          查看更多 →
        </view>
      </view>
      <view class="chart-placeholder">
        <view class="chart-title">近7天产量趋势</view>
        <view class="chart-bars">
          <view class="bar-item" v-for="(item, index) in trendData" :key="index">
            <view class="bar" :style="{ height: item.height }">
              <view class="bar-label">{{ item.value }}</view>
            </view>
            <view class="bar-day">{{ item.day }}</view>
          </view>
        </view>
      </view>
    </view>

    <view class="alert-section" v-if="alerts.length > 0">
      <view class="section-title">待处理提醒</view>
      <view class="alert-list">
        <view class="alert-item" v-for="(alert, index) in alerts" :key="index">
          <view class="alert-icon" :class="alert.type">
            <text>{{ alert.icon }}</text>
          </view>
          <view class="alert-content">
            <view class="alert-title">{{ alert.title }}</view>
            <view class="alert-desc">{{ alert.description }}</view>
          </view>
          <view class="alert-time">{{ alert.time }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import { productionApi, qualityApi, equipmentApi } from '@/api/index.js'

export default {
  data() {
    return {
      stats: {
        totalProduction: '12,580',
        completionRate: '92.5',
        qualityRate: '98.3',
        equipmentRate: '96.7'
      },
      trendData: [
        { day: '周一', value: '12.5k', height: '80%' },
        { day: '周二', value: '14.2k', height: '90%' },
        { day: '周三', value: '11.8k', height: '75%' },
        { day: '周四', value: '15.1k', height: '95%' },
        { day: '周五', value: '13.6k', height: '85%' },
        { day: '周六', value: '9.8k', height: '60%' },
        { day: '周日', value: '8.5k', height: '50%' }
      ],
      alerts: [
        {
          type: 'warning',
          icon: '⚠️',
          title: '设备保养提醒',
          description: '球磨机-1 计划保养时间已到',
          time: '今天'
        },
        {
          type: 'danger',
          icon: '🔴',
          title: '质量异常',
          description: '昨日成品强度达标率低于目标值',
          time: '昨天'
        }
      ]
    }
  },
  onLoad() {
    this.loadDashboardData()
  },
  methods: {
    goToPage(url) {
      uni.navigateTo({ url: url })
    },
    async loadDashboardData() {
      try {
        const today = this.getTodayDate()
        
        const [productionRes, qualityRes, equipmentRes] = await Promise.all([
          productionApi.getDailyReport(today).catch(() => null),
          qualityApi.getQualityTrend(today, today).catch(() => null),
          equipmentApi.getOperatingRateChart('line', today, today).catch(() => null)
        ])
        
        if (productionRes) {
          this.stats.totalProduction = productionRes.total_actual?.toLocaleString() || '0'
          this.stats.completionRate = productionRes.avg_completion_rate?.toFixed(1) || '0'
          this.stats.qualityRate = productionRes.avg_pass_rate?.toFixed(1) || '0'
        }
        
        if (equipmentRes && equipmentRes.series && equipmentRes.series.length > 0) {
          const rates = equipmentRes.series[0].data
          if (rates.length > 0) {
            this.stats.equipmentRate = rates[rates.length - 1]?.toFixed(1) || '0'
          }
        }
      } catch (e) {
        console.log('加载数据失败，使用模拟数据:', e)
      }
    },
    getTodayDate() {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
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

.header {
  background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
  padding: 40rpx 30rpx 60rpx;
  color: #FFFFFF;

  .title {
    font-size: 40rpx;
    font-weight: 600;
    margin-bottom: 8rpx;
  }

  .subtitle {
    font-size: 26rpx;
    opacity: 0.9;
  }
}

.stat-section {
  padding: 0 20rpx;
  margin-top: -40rpx;

  .stat-row {
    display: flex;
    margin-bottom: 20rpx;
  }

  .stat-card {
    flex: 1;
    background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
    border-radius: 16rpx;
    padding: 24rpx;
    margin: 0 10rpx;
    color: #FFFFFF;
    text-align: center;

    &.success {
      background: linear-gradient(135deg, #52C41A 0%, #73D13D 100%);
    }

    &.warning {
      background: linear-gradient(135deg, #FAAD14 0%, #FFC53D 100%);
    }

    .stat-value {
      font-size: 44rpx;
      font-weight: 600;
      margin-bottom: 8rpx;
    }

    .stat-label {
      font-size: 24rpx;
      opacity: 0.9;
    }
  }
}

.quick-section,
.trend-section,
.alert-section {
  padding: 0 20rpx;
  margin-top: 30rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1F2329;
}

.section-more {
  font-size: 26rpx;
  color: #1890FF;
}

.quick-grid {
  display: flex;
  flex-wrap: wrap;
  background-color: #FFFFFF;
  border-radius: 16rpx;
  padding: 20rpx 10rpx;
}

.quick-item {
  width: 25%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx 10rpx;

  .quick-icon {
    width: 80rpx;
    height: 80rpx;
    border-radius: 20rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 12rpx;

    &.production {
      background: linear-gradient(135deg, #E6F7FF 0%, #BAE7FF 100%);
    }

    &.quality {
      background: linear-gradient(135deg, #F6FFED 0%, #D9F7BE 100%);
    }

    &.equipment {
      background: linear-gradient(135deg, #FFF7E6 0%, #FFE58F 100%);
    }

    &.export {
      background: linear-gradient(135deg, #FFF1F0 0%, #FFCCC7 100%);
    }

    .icon-text {
      font-size: 40rpx;
    }
  }

  .quick-text {
    font-size: 24rpx;
    color: #666666;
  }
}

.chart-placeholder {
  background-color: #FFFFFF;
  border-radius: 16rpx;
  padding: 24rpx;

  .chart-title {
    font-size: 28rpx;
    color: #666666;
    margin-bottom: 30rpx;
    text-align: center;
  }

  .chart-bars {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    height: 300rpx;
    padding: 0 10rpx;

    .bar-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      flex: 1;

      .bar {
        width: 40rpx;
        background: linear-gradient(180deg, #1890FF 0%, #40A9FF 100%);
        border-radius: 8rpx 8rpx 0 0;
        display: flex;
        align-items: flex-end;
        justify-content: center;
        padding-bottom: 8rpx;
        min-height: 40rpx;
        transition: height 0.3s ease;

        .bar-label {
          font-size: 20rpx;
          color: #FFFFFF;
          font-weight: 500;
        }
      }

      .bar-day {
        font-size: 22rpx;
        color: #999999;
        margin-top: 12rpx;
      }
    }
  }
}

.alert-list {
  background-color: #FFFFFF;
  border-radius: 16rpx;
  overflow: hidden;
}

.alert-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-bottom: 1rpx solid #F0F0F0;

  &:last-child {
    border-bottom: none;
  }

  .alert-icon {
    width: 60rpx;
    height: 60rpx;
    border-radius: 12rpx;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
    font-size: 32rpx;

    &.warning {
      background-color: #FFFBE6;
    }

    &.danger {
      background-color: #FFF2F0;
    }
  }

  .alert-content {
    flex: 1;

    .alert-title {
      font-size: 28rpx;
      color: #1F2329;
      font-weight: 500;
      margin-bottom: 6rpx;
    }

    .alert-desc {
      font-size: 24rpx;
      color: #999999;
    }
  }

  .alert-time {
    font-size: 22rpx;
    color: #CCCCCC;
  }
}
</style>
