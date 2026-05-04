<template>
  <view class="measurement-container">
    <view class="header-section">
      <text class="page-title">体测记录</text>
      <view class="sync-btn" @click="handleSync">
        <text class="sync-icon">🔄</text>
        <text class="sync-text">同步健身房</text>
      </view>
    </view>
    
    <view class="chart-section">
      <view class="chart-header">
        <text class="chart-title">数据趋势</text>
        <view class="chart-type-tabs">
          <view 
            class="chart-type-tab" 
            :class="{ active: chartType === 'weight' }"
            @click="chartType = 'weight'"
          >
            体重
          </view>
          <view 
            class="chart-type-tab" 
            :class="{ active: chartType === 'body_fat_rate' }"
            @click="chartType = 'body_fat_rate'"
          >
            体脂率
          </view>
          <view 
            class="chart-type-tab" 
            :class="{ active: chartType === 'muscle_mass' }"
            @click="chartType = 'muscle_mass'"
          >
            肌肉量
          </view>
        </view>
      </view>
      
      <view class="chart-container">
        <canvas 
          class="line-chart" 
          canvas-id="lineCanvas" 
          :style="{ width: chartWidth + 'px', height: chartHeight + 'px' }"
        ></canvas>
        <view class="empty-chart" v-if="chartData.length === 0">
          <text class="empty-text">暂无数据可展示</text>
        </view>
      </view>
      
      <view class="chart-stats" v-if="chartData.length > 0">
        <view class="chart-stat-item">
          <text class="stat-label">最高值</text>
          <text class="stat-value">{{ getChartStat('max') }}{{ getUnit() }}</text>
        </view>
        <view class="chart-stat-item">
          <text class="stat-label">最低值</text>
          <text class="stat-value">{{ getChartStat('min') }}{{ getUnit() }}</text>
        </view>
        <view class="chart-stat-item">
          <text class="stat-label">变化值</text>
          <text class="stat-value" :class="getChangeClass()">
            {{ getChangeValue() }}
          </text>
        </view>
      </view>
    </view>
    
    <view class="list-section">
      <view class="list-header">
        <text class="list-title">历史记录</text>
        <text class="list-count">共 {{ measurementList.length }} 条</text>
      </view>
      
      <view class="measurement-list" v-if="measurementList.length > 0">
        <view 
          class="measurement-item" 
          v-for="(item, index) in measurementList" 
          :key="index"
          @click="showDetail(item)"
        >
          <view class="item-main">
            <view class="item-date-row">
              <text class="item-date">{{ formatDate(item.measurement_date) }}</text>
              <view class="item-source" :class="item.source">
                {{ item.source === 'gym_sync' ? '健身房同步' : '手动录入' }}
              </view>
            </view>
            <view class="item-stats">
              <view class="item-stat">
                <text class="item-stat-label">体重</text>
                <text class="item-stat-value">{{ item.weight }}<text class="item-unit">kg</text></text>
              </view>
              <view class="item-stat">
                <text class="item-stat-label">体脂</text>
                <text class="item-stat-value">{{ item.body_fat_rate }}<text class="item-unit">%</text></text>
              </view>
              <view class="item-stat">
                <text class="item-stat-label">肌肉</text>
                <text class="item-stat-value">{{ item.muscle_mass }}<text class="item-unit">kg</text></text>
              </view>
              <view class="item-stat">
                <text class="item-stat-label">BMI</text>
                <text class="item-stat-value">{{ item.bmi }}</text>
              </view>
            </view>
          </view>
          <text class="item-arrow">›</text>
        </view>
      </view>
      
      <view class="empty-list" v-else>
        <view class="empty-icon">📊</view>
        <text class="empty-title">暂无体测记录</text>
        <text class="empty-subtitle">点击下方按钮添加第一条记录</text>
      </view>
    </view>
    
    <view class="add-btn" @click="goToAdd">
      <text class="add-icon">+</text>
      <text class="add-text">添加记录</text>
    </view>
    
    <view class="detail-popup" v-if="showDetailPopup">
      <view class="popup-mask" @click="hideDetail"></view>
      <view class="popup-content">
        <view class="popup-header">
          <text class="popup-title">体测详情</text>
          <text class="popup-close" @click="hideDetail">×</text>
        </view>
        
        <view class="detail-content" v-if="selectedMeasurement">
          <view class="detail-section">
            <text class="detail-section-title">基本信息</text>
            <view class="detail-row">
              <text class="detail-label">测量日期</text>
              <text class="detail-value">{{ formatDate(selectedMeasurement.measurement_date) }}</text>
            </view>
            <view class="detail-row">
              <text class="detail-label">数据来源</text>
              <text class="detail-value" :class="selectedMeasurement.source">
                {{ selectedMeasurement.source === 'gym_sync' ? '健身房同步' : '手动录入' }}
              </text>
            </view>
          </view>
          
          <view class="detail-section">
            <text class="detail-section-title">身体数据</text>
            <view class="detail-grid">
              <view class="detail-grid-item">
                <text class="detail-grid-label">体重</text>
                <text class="detail-grid-value">{{ selectedMeasurement.weight }} <text class="detail-grid-unit">kg</text></text>
              </view>
              <view class="detail-grid-item">
                <text class="detail-grid-label">体脂率</text>
                <text class="detail-grid-value">{{ selectedMeasurement.body_fat_rate }} <text class="detail-grid-unit">%</text></text>
              </view>
              <view class="detail-grid-item">
                <text class="detail-grid-label">肌肉量</text>
                <text class="detail-grid-value">{{ selectedMeasurement.muscle_mass }} <text class="detail-grid-unit">kg</text></text>
              </view>
              <view class="detail-grid-item">
                <text class="detail-grid-label">BMI</text>
                <text class="detail-grid-value">{{ selectedMeasurement.bmi }}</text>
              </view>
              <view class="detail-grid-item">
                <text class="detail-grid-label">基础代谢</text>
                <text class="detail-grid-value">{{ selectedMeasurement.bmr || '-' }}</text>
              </view>
              <view class="detail-grid-item">
                <text class="detail-grid-label">水分率</text>
                <text class="detail-grid-value">{{ selectedMeasurement.water_rate || '-' }}{{ selectedMeasurement.water_rate ? '%' : '' }}</text>
              </view>
              <view class="detail-grid-item">
                <text class="detail-grid-label">骨量</text>
                <text class="detail-grid-value">{{ selectedMeasurement.bone_mass || '-' }}{{ selectedMeasurement.bone_mass ? 'kg' : '' }}</text>
              </view>
              <view class="detail-grid-item">
                <text class="detail-grid-label">蛋白质</text>
                <text class="detail-grid-value">{{ selectedMeasurement.protein_rate || '-' }}{{ selectedMeasurement.protein_rate ? '%' : '' }}</text>
              </view>
            </view>
          </view>
          
          <view class="detail-section" v-if="selectedMeasurement.notes">
            <text class="detail-section-title">备注</text>
            <text class="detail-notes">{{ selectedMeasurement.notes }}</text>
          </view>
          
          <view class="detail-actions">
            <button class="detail-btn delete-btn" @click="deleteMeasurement">删除记录</button>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      userInfo: {},
      chartType: 'weight',
      chartWidth: 0,
      chartHeight: 300,
      chartData: [],
      measurementList: [],
      showDetailPopup: false,
      selectedMeasurement: null
    }
  },
  onLoad() {
    this.initChartSize()
  },
  onShow() {
    this.loadData()
  },
  methods: {
    initChartSize() {
      const systemInfo = uni.getSystemInfoSync()
      this.chartWidth = systemInfo.windowWidth - 60
    },
    
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      const year = date.getFullYear()
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      return `${year}-${month}-${day}`
    },
    
    getUnit() {
      const unitMap = {
        'weight': 'kg',
        'body_fat_rate': '%',
        'muscle_mass': 'kg'
      }
      return unitMap[this.chartType] || ''
    },
    
    getChartStat(type) {
      if (this.chartData.length === 0) return 0
      const values = this.chartData.map(item => item.value)
      if (type === 'max') {
        return Math.max(...values)
      } else if (type === 'min') {
        return Math.min(...values)
      }
      return 0
    },
    
    getChangeValue() {
      if (this.chartData.length < 2) return '0'
      const first = this.chartData[0].value
      const last = this.chartData[this.chartData.length - 1].value
      const change = (last - first).toFixed(1)
      return change > 0 ? `+${change}` : change
    },
    
    getChangeClass() {
      if (this.chartData.length < 2) return ''
      const first = this.chartData[0].value
      const last = this.chartData[this.chartData.length - 1].value
      const change = last - first
      
      if (this.chartType === 'body_fat_rate') {
        return change < 0 ? 'down' : 'up'
      }
      return change > 0 ? 'up' : 'down'
    },
    
    async loadData() {
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      if (!this.userInfo.id) return
      
      await Promise.all([
        this.loadMeasurementList(),
        this.loadChartData()
      ])
    },
    
    async loadMeasurementList() {
      try {
        this.measurementList = await api.measurementApi.getList(this.userInfo.id)
      } catch (error) {
        console.error('加载体测记录失败:', error)
      }
    },
    
    async loadChartData() {
      try {
        const stats = await api.measurementApi.getStats(this.userInfo.id, {
          start_date: this.getStartDate(),
          end_date: this.getEndDate()
        })
        
        // 转换数据格式用于图表
        this.chartData = stats.trend_data.map(item => ({
          date: item.measurement_date,
          value: item[this.chartType]
        })).filter(item => item.value !== null && item.value !== undefined)
        
        this.drawChart()
      } catch (error) {
        console.error('加载图表数据失败:', error)
        this.chartData = []
      }
    },
    
    getStartDate() {
      const now = new Date()
      now.setMonth(now.getMonth() - 3)
      return now.toISOString().split('T')[0]
    },
    
    getEndDate() {
      return new Date().toISOString().split('T')[0]
    },
    
    drawChart() {
      if (this.chartData.length === 0) return
      
      const ctx = uni.createCanvasContext('lineCanvas', this)
      const padding = { top: 30, right: 30, bottom: 40, left: 50 }
      const width = this.chartWidth
      const height = this.chartHeight
      const chartWidth = width - padding.left - padding.right
      const chartHeight = height - padding.top - padding.bottom
      
      const values = this.chartData.map(item => item.value)
      const maxValue = Math.max(...values)
      const minValue = Math.min(...values)
      const valueRange = maxValue - minValue || 1
      
      ctx.clearRect(0, 0, width, height)
      
      ctx.setStrokeStyle('#e5e5e5')
      ctx.setLineWidth(1)
      
      for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartHeight / 4) * i
        ctx.beginPath()
        ctx.moveTo(padding.left, y)
        ctx.lineTo(width - padding.right, y)
        ctx.stroke()
        
        const value = maxValue - (valueRange / 4) * i
        ctx.setFillStyle('#909399')
        ctx.setFontSize(12)
        ctx.setTextAlign('right')
        ctx.fillText(value.toFixed(1), padding.left - 5, y + 5)
      }
      
      ctx.beginPath()
      ctx.setStrokeStyle('#409EFF')
      ctx.setLineWidth(2)
      
      const points = this.chartData.map((item, index) => {
        const x = padding.left + (chartWidth / Math.max(this.chartData.length - 1, 1)) * index
        const y = padding.top + chartHeight - ((item.value - minValue) / valueRange) * chartHeight
        return { x, y, value: item.value, date: item.date }
      })
      
      points.forEach((point, index) => {
        if (index === 0) {
          ctx.moveTo(point.x, point.y)
        } else {
          ctx.lineTo(point.x, point.y)
        }
      })
      ctx.stroke()
      
      const gradient = ctx.createLinearGradient(0, padding.top, 0, height - padding.bottom)
      gradient.addColorStop(0, 'rgba(64, 158, 255, 0.3)')
      gradient.addColorStop(1, 'rgba(64, 158, 255, 0.05)')
      
      ctx.beginPath()
      ctx.setFillStyle(gradient)
      ctx.moveTo(points[0].x, height - padding.bottom)
      points.forEach(point => {
        ctx.lineTo(point.x, point.y)
      })
      ctx.lineTo(points[points.length - 1].x, height - padding.bottom)
      ctx.closePath()
      ctx.fill()
      
      points.forEach(point => {
        ctx.beginPath()
        ctx.setFillStyle('#fff')
        ctx.setStrokeStyle('#409EFF')
        ctx.setLineWidth(2)
        ctx.arc(point.x, point.y, 4, 0, 2 * Math.PI)
        ctx.fill()
        ctx.stroke()
      })
      
      ctx.setFillStyle('#909399')
      ctx.setFontSize(10)
      ctx.setTextAlign('center')
      
      const step = Math.max(1, Math.floor(points.length / 5))
      points.forEach((point, index) => {
        if (index % step === 0 || index === points.length - 1) {
          const date = new Date(point.date)
          const label = `${date.getMonth() + 1}/${date.getDate()}`
          ctx.fillText(label, point.x, height - 10)
        }
      })
      
      ctx.draw()
    },
    
    handleSync() {
      uni.showLoading({ title: '同步中...' })
      
      setTimeout(async () => {
        try {
          await api.measurementApi.syncFromGym(this.userInfo.id)
          uni.hideLoading()
          uni.showToast({
            title: '同步成功',
            icon: 'success'
          })
          this.loadData()
        } catch (error) {
          uni.hideLoading()
          uni.showToast({
            title: error.message || '同步失败',
            icon: 'none'
          })
        }
      }, 1500)
    },
    
    showDetail(item) {
      this.selectedMeasurement = item
      this.showDetailPopup = true
    },
    
    hideDetail() {
      this.showDetailPopup = false
      this.selectedMeasurement = null
    },
    
    async deleteMeasurement() {
      if (!this.selectedMeasurement) return
      
      uni.showModal({
        title: '确认删除',
        content: '确定要删除这条体测记录吗？',
        success: async (res) => {
          if (res.confirm) {
            try {
              await api.measurementApi.delete(this.selectedMeasurement.id)
              this.hideDetail()
              uni.showToast({
                title: '删除成功',
                icon: 'success'
              })
              this.loadData()
            } catch (error) {
              uni.showToast({
                title: error.message || '删除失败',
                icon: 'none'
              })
            }
          }
        }
      })
    },
    
    goToAdd() {
      uni.navigateTo({
        url: '/pages/measurement-add/measurement-add'
      })
    }
  },
  watch: {
    chartType() {
      this.loadChartData()
    }
  }
}
</script>

<style scoped>
.measurement-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding-bottom: 120rpx;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  background-color: #fff;
}

.page-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.sync-btn {
  display: flex;
  align-items: center;
  padding: 16rpx 24rpx;
  background-color: rgba(64, 158, 255, 0.1);
  border-radius: 30rpx;
}

.sync-icon {
  font-size: 28rpx;
  margin-right: 8rpx;
}

.sync-text {
  font-size: 26rpx;
  color: #409EFF;
}

.chart-section {
  margin: 20rpx;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.chart-header {
  margin-bottom: 20rpx;
}

.chart-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.chart-type-tabs {
  display: flex;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  padding: 6rpx;
}

.chart-type-tab {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  font-size: 26rpx;
  color: #606266;
  border-radius: 8rpx;
}

.chart-type-tab.active {
  background-color: #409EFF;
  color: #fff;
}

.chart-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}

.line-chart {
  display: block;
}

.empty-chart {
  position: absolute;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-text {
  font-size: 26rpx;
  color: #c0c4cc;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 20rpx;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.chart-stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 24rpx;
  color: #909399;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.stat-value.up {
  color: #f56c6c;
}

.stat-value.down {
  color: #67c23a;
}

.list-section {
  margin: 20rpx;
  background-color: #fff;
  border-radius: 20rpx;
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.list-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.list-count {
  font-size: 24rpx;
  color: #909399;
}

.measurement-list {
  padding: 0 30rpx;
}

.measurement-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.measurement-item:last-child {
  border-bottom: none;
}

.item-main {
  flex: 1;
}

.item-date-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16rpx;
}

.item-date {
  font-size: 28rpx;
  font-weight: 500;
  color: #333;
}

.item-source {
  font-size: 22rpx;
  padding: 4rpx 12rpx;
  border-radius: 6rpx;
}

.item-source.gym_sync {
  background-color: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.item-source.manual {
  background-color: rgba(64, 158, 255, 0.1);
  color: #409EFF;
}

.item-stats {
  display: flex;
  gap: 20rpx;
}

.item-stat {
  display: flex;
  flex-direction: column;
}

.item-stat-label {
  font-size: 22rpx;
  color: #909399;
  margin-bottom: 4rpx;
}

.item-stat-value {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.item-unit {
  font-size: 22rpx;
  color: #909399;
  font-weight: 400;
}

.item-arrow {
  font-size: 36rpx;
  color: #c0c4cc;
  margin-left: 20rpx;
}

.empty-list {
  padding: 80rpx 30rpx;
  text-align: center;
}

.empty-icon {
  font-size: 80rpx;
  margin-bottom: 20rpx;
}

.empty-title {
  font-size: 30rpx;
  color: #606266;
  display: block;
  margin-bottom: 12rpx;
}

.empty-subtitle {
  font-size: 26rpx;
  color: #909399;
}

.add-btn {
  position: fixed;
  bottom: 40rpx;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  padding: 24rpx 48rpx;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  border-radius: 50rpx;
  box-shadow: 0 8rpx 24rpx rgba(64, 158, 255, 0.3);
}

.add-icon {
  font-size: 40rpx;
  color: #fff;
  margin-right: 12rpx;
  font-weight: 300;
}

.add-text {
  font-size: 30rpx;
  color: #fff;
  font-weight: 500;
}

.detail-popup {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 100;
}

.popup-mask {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
}

.popup-content {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  max-height: 80vh;
  background-color: #fff;
  border-top-left-radius: 32rpx;
  border-top-right-radius: 32rpx;
  overflow: hidden;
}

.popup-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.popup-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.popup-close {
  font-size: 48rpx;
  color: #909399;
  line-height: 1;
}

.detail-content {
  padding: 30rpx;
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 30rpx;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 20rpx;
  display: block;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 28rpx;
  color: #606266;
}

.detail-value {
  font-size: 28rpx;
  color: #333;
  font-weight: 500;
}

.detail-grid {
  display: flex;
  flex-wrap: wrap;
  margin: 0 -10rpx;
}

.detail-grid-item {
  width: 50%;
  padding: 0 10rpx;
  margin-bottom: 20rpx;
  box-sizing: border-box;
}

.detail-grid-label {
  font-size: 24rpx;
  color: #909399;
  display: block;
  margin-bottom: 8rpx;
}

.detail-grid-value {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.detail-grid-unit {
  font-size: 22rpx;
  color: #909399;
  font-weight: 400;
}

.detail-notes {
  font-size: 28rpx;
  color: #606266;
  line-height: 1.6;
}

.detail-actions {
  margin-top: 40rpx;
  padding-top: 30rpx;
  border-top: 1rpx solid #f0f0f0;
}

.detail-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 16rpx;
  font-size: 30rpx;
}

.delete-btn {
  background-color: #fef0f0;
  color: #f56c6c;
}
</style>
