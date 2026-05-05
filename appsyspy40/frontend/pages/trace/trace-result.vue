<template>
  <view class="trace-result-container">
    <view class="loading-state" v-if="loading">
      <view class="loading-icon">
        <text class="loading-text">⏳</text>
      </view>
      <text class="loading-title">正在追溯质量数据...</text>
    </view>
    
    <view v-else>
      <view class="info-card">
        <view class="card-header">
          <view class="header-icon">
            <text class="icon-text">🏭</text>
          </view>
          <view class="header-info">
            <text class="production-no">{{ (traceData.production && traceData.production.production_no) || '-' }}</text>
            <text class="truck-no">罐车: {{ (traceData.production && traceData.production.truck_no) || '-' }}</text>
          </view>
          <view class="status-tag" :class="getStatusClass(traceData.production ? traceData.production.status : '')">
            <text class="status-text">{{ (traceData.production && traceData.production.status) || '正常' }}</text>
          </view>
        </view>
        
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">生产时间</text>
            <text class="info-value">{{ formatTime(traceData.production ? traceData.production.production_date : '') }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">工程名称</text>
            <text class="info-value">{{ (traceData.production && traceData.production.project_name) || '-' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">施工部位</text>
            <text class="info-value">{{ (traceData.production && traceData.production.construction_site) || '-' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">混凝土强度</text>
            <text class="info-value highlight">{{ (traceData.formula && traceData.formula.strength_grade) || '-' }}</text>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="traceData.formula">
        <view class="section-header">
          <text class="section-title">生产配方</text>
          <text class="formula-no">{{ traceData.formula.formula_code || '-' }}</text>
        </view>
        
        <view class="formula-table">
          <view class="table-header">
            <text class="cell material">原材料</text>
            <text class="cell target">目标用量</text>
            <text class="cell actual">实际用量</text>
            <text class="cell deviation">偏差</text>
          </view>
          
          <view class="table-row" v-for="(item, index) in formulaItems" :key="index">
            <text class="cell material">{{ item.material }}</text>
            <text class="cell target">{{ item.target }} kg</text>
            <text class="cell actual">{{ item.actual }} kg</text>
            <text class="cell deviation" :class="getDeviationClass(item.deviation)">
              {{ item.deviation }}%
            </text>
          </view>
        </view>
        
        <view class="formula-summary">
          <view class="summary-item">
            <text class="summary-label">总用量</text>
            <text class="summary-value">{{ traceData.formula.total_weight || '-' }} kg/m³</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">水灰比</text>
            <text class="summary-value">{{ traceData.formula.water_cement_ratio || '-' }}</text>
          </view>
          <view class="summary-item">
            <text class="summary-label">砂率</text>
            <text class="summary-value">{{ traceData.formula.sand_ratio || '-' }}%</text>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="traceData.production">
        <view class="section-header">
          <text class="section-title">搅拌参数</text>
        </view>
        
        <view class="params-grid">
          <view class="param-item">
            <text class="param-label">搅拌时间</text>
            <view class="param-value-row">
              <text class="param-value">{{ traceData.production.mixing_time || '-' }}</text>
              <text class="param-unit">秒</text>
            </view>
            <view class="param-status" v-if="traceData.production.mixing_time">
              <text :class="parseInt(traceData.production.mixing_time) < 90 ? 'warning' : 'normal'">
                {{ parseInt(traceData.production.mixing_time) < 90 ? '时间不足' : '正常' }}
              </text>
            </view>
          </view>
          
          <view class="param-item">
            <text class="param-label">搅拌转速</text>
            <view class="param-value-row">
              <text class="param-value">{{ traceData.production.mixing_speed || '-' }}</text>
              <text class="param-unit">rpm</text>
            </view>
          </view>
          
          <view class="param-item">
            <text class="param-label">出料温度</text>
            <view class="param-value-row">
              <text class="param-value">{{ traceData.production.discharge_temp || '-' }}</text>
              <text class="param-unit">°C</text>
            </view>
          </view>
          
          <view class="param-item">
            <text class="param-label">坍落度</text>
            <view class="param-value-row">
              <text class="param-value">{{ traceData.production.slump || '-' }}</text>
              <text class="param-unit">mm</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="traceData.feedings && traceData.feedings.length > 0">
        <view class="section-header">
          <text class="section-title">投料记录</text>
          <text class="count-badge">共 {{ traceData.feedings.length }} 条</text>
        </view>
        
        <view class="feeding-list">
          <view class="feeding-item" v-for="(item, index) in traceData.feedings" :key="index">
            <view class="feeding-time">
              <text class="time-text">{{ formatTime(item.feeding_time, 'time') }}</text>
            </view>
            <view class="feeding-content">
              <text class="feeding-material">{{ item.material_name || '-' }}</text>
              <text class="feeding-amount">{{ item.feeding_amount || '-' }} kg</text>
            </view>
            <view class="feeding-order">
              <text class="order-text">第{{ index + 1}}次</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="traceData.reports && traceData.reports.length > 0">
        <view class="section-header">
          <text class="section-title">检验报告</text>
        </view>
        
        <view class="report-list">
          <view 
            class="report-item" 
            v-for="(item, index) in traceData.reports" 
            :key="index"
            @click="viewReport(item)"
          >
            <view class="report-icon">
              <text class="icon-text">📄</text>
            </view>
            <view class="report-info">
              <text class="report-title">{{ item.report_title || '检验报告' }}</text>
              <text class="report-date">{{ formatTime(item.report_date) }}</text>
            </view>
            <view class="report-arrow">
              <text class="arrow-text">›</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="traceData.alerts && traceData.alerts.length > 0">
        <view class="section-header alert">
          <text class="section-title">相关预警</text>
          <text class="count-badge warning">{{ traceData.alerts.length }} 条预警</text>
        </view>
        
        <view class="alert-list-mini">
          <view 
            class="alert-item" 
            v-for="(item, index) in traceData.alerts" 
            :key="index"
            @click="goToAlert(item)"
          >
            <view class="alert-level-badge" :class="item.alert_level.toLowerCase()">
              <text class="level-badge-text">{{ item.alert_level }}</text>
            </view>
            <view class="alert-content-mini">
              <text class="alert-type-mini">{{ alertTypeText(item.alert_type) }}</text>
              <text class="alert-desc-mini">{{ item.description }}</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="bottom-space"></view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      loading: true,
      qrCode: '',
      traceData: {},
      formulaItems: []
    }
  },
  onLoad(options) {
    if (options.qrCode) {
      this.qrCode = options.qrCode
      this.loadTraceData()
    }
  },
  methods: {
    async loadTraceData() {
      this.loading = true
      
      try {
        const res = await request.get('/api/trace/qr/' + this.qrCode)
        
        if (res.code === 200) {
          this.traceData = res.data
          this.processFormulaData()
        }
      } catch (err) {
        console.error('加载追溯数据失败:', err)
        this.loadMockData()
      } finally {
        this.loading = false
      }
    },
    
    processFormulaData() {
      if (!this.traceData.formula) return
      
      const formula = this.traceData.formula
      
      this.formulaItems = [
        {
          material: '水泥',
          target: formula.cement_target || '-',
          actual: formula.cement_actual || '-',
          deviation: formula.cement_deviation || 0
        },
        {
          material: '砂',
          target: formula.sand_target || '-',
          actual: formula.sand_actual || '-',
          deviation: formula.sand_deviation || 0
        },
        {
          material: '碎石',
          target: formula.stone_target || '-',
          actual: formula.stone_actual || '-',
          deviation: formula.stone_deviation || 0
        },
        {
          material: '水',
          target: formula.water_target || '-',
          actual: formula.water_actual || '-',
          deviation: formula.water_deviation || 0
        },
        {
          material: '外加剂',
          target: formula.admixture_target || '-',
          actual: formula.admixture_actual || '-',
          deviation: formula.admixture_deviation || 0
        }
      ]
    },
    
    loadMockData() {
      this.traceData = {
        production: {
          production_no: 'PRO-20260505-0012',
          truck_no: '豫A-12345',
          status: '正常',
          production_date: '2026-05-05T10:30:00',
          project_name: '郑州市轨道交通8号线工程',
          construction_site: '主体结构承台',
          mixing_time: '95',
          mixing_speed: '35',
          discharge_temp: '25',
          slump: '180',
          qr_code: 'QR202605051030001234'
        },
        formula: {
          formula_code: 'F-C30-2026-001',
          strength_grade: 'C30',
          cement_target: 350,
          cement_actual: 348,
          cement_deviation: -0.57,
          sand_target: 750,
          sand_actual: 745,
          sand_deviation: -0.67,
          stone_target: 1050,
          stone_actual: 1048,
          stone_deviation: -0.19,
          water_target: 180,
          water_actual: 180,
          water_deviation: 0,
          admixture_target: 7,
          admixture_actual: 6.8,
          admixture_deviation: -2.86,
          total_weight: 2337,
          water_cement_ratio: '0.51',
          sand_ratio: '41.7'
        },
        feedings: [
          { feeding_time: '2026-05-05T10:30:00', material_name: '水泥', feeding_amount: 348, order: 1 },
          { feeding_time: '2026-05-05T10:30:15', material_name: '砂', feeding_amount: 745, order: 2 },
          { feeding_time: '2026-05-05T10:30:30', material_name: '碎石', feeding_amount: 1048, order: 3 },
          { feeding_time: '2026-05-05T10:30:45', material_name: '水', feeding_amount: 180, order: 4 },
          { feeding_time: '2026-05-05T10:31:00', material_name: '外加剂', feeding_amount: 6.8, order: 5 }
        ],
        reports: [
          { id: 1, report_title: '混凝土出厂检验报告', report_date: '2026-05-05T11:00:00' },
          { id: 2, report_title: '配合比设计报告', report_date: '2026-05-03T10:00:00' }
        ],
        alerts: [
          {
            id: 1,
            alert_level: '一般',
            alert_type: 'mix_ratio_deviation',
            description: '外加剂用量偏差-2.86%，接近阈值',
            status: '待处理'
          }
        ]
      }
      
      this.processFormulaData()
    },
    
    getStatusClass(status) {
      if (status === '正常') return 'normal'
      if (status === '异常') return 'warning'
      return 'normal'
    },
    
    getDeviationClass(deviation) {
      const dev = Math.abs(parseFloat(deviation) || 0)
      if (dev > 2) return 'warning'
      return 'normal'
    },
    
    formatTime(timeStr, format) {
      if (!timeStr) return '-'
      const date = new Date(timeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hour = String(date.getHours()).padStart(2, '0')
      const minute = String(date.getMinutes()).padStart(2, '0')
      
      if (format === 'time') {
        return hour + ':' + minute
      }
      return year + '-' + month + '-' + day + ' ' + hour + ':' + minute
    },
    
    alertTypeText(type) {
      const typeMap = {
        'mix_ratio_deviation': '配比偏差',
        'mix_time_short': '搅拌时间不足',
        'material_unqualified': '原材料不合格'
      }
      return typeMap[type] || type
    },
    
    viewReport(item) {
      uni.showToast({
        title: '查看报告功能开发中',
        icon: 'none'
      })
    },
    
    goToAlert(item) {
      uni.navigateTo({
        url: '/pages/alert/alert-detail?id=' + item.id
      })
    }
  }
}
</script>

<style scoped>
.trace-result-container {
  min-height: 100vh;
  background: #f5f5f5;
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

.info-card {
  background: #fff;
  margin: 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.header-icon {
  width: 72rpx;
  height: 72rpx;
  background: #e3f2fd;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.header-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.production-no {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 4rpx;
}

.truck-no {
  font-size: 24rpx;
  color: #999;
}

.status-tag {
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.status-tag.normal {
  background: #e8f5e9;
}

.status-tag.warning {
  background: #ffebee;
}

.status-text {
  font-size: 24rpx;
}

.normal .status-text {
  color: #2e7d32;
}

.warning .status-text {
  color: #c62828;
}

.info-list {
  padding-top: 20rpx;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12rpx 0;
}

.info-label {
  font-size: 26rpx;
  color: #999;
}

.info-value {
  font-size: 26rpx;
  color: #333;
}

.info-value.highlight {
  font-weight: 600;
  color: #1E88E5;
}

.section-card {
  background: #fff;
  margin: 0 20rpx 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #f0f0f0;
  margin-bottom: 20rpx;
}

.section-header.alert {
  border-bottom-color: #ffebee;
}

.section-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.formula-no {
  font-size: 24rpx;
  color: #999;
}

.count-badge {
  padding: 4rpx 12rpx;
  background: #e3f2fd;
  border-radius: 20rpx;
  font-size: 22rpx;
  color: #1565c0;
}

.count-badge.warning {
  background: #ffebee;
  color: #c62828;
}

.formula-table {
  margin-bottom: 20rpx;
}

.table-header {
  display: flex;
  padding: 16rpx 0;
  background: #f5f5f5;
  border-radius: 8rpx;
  margin-bottom: 8rpx;
}

.table-row {
  display: flex;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.table-row:last-child {
  border-bottom: none;
}

.cell {
  font-size: 24rpx;
  text-align: center;
}

.cell.material {
  width: 30%;
  text-align: left;
}

.cell.target,
.cell.actual {
  width: 22%;
}

.cell.deviation {
  width: 26%;
}

.table-header .cell {
  font-weight: 600;
  color: #666;
}

.table-row .cell {
  color: #333;
}

.cell.deviation.normal {
  color: #2e7d32;
}

.cell.deviation.warning {
  color: #c62828;
}

.formula-summary {
  display: flex;
  justify-content: space-around;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.summary-label {
  font-size: 22rpx;
  color: #999;
  margin-bottom: 4rpx;
}

.summary-value {
  font-size: 26rpx;
  font-weight: 600;
  color: #333;
}

.params-grid {
  display: flex;
  flex-wrap: wrap;
  margin: -8rpx;
}

.param-item {
  width: 48%;
  margin: 8rpx 1%;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 20rpx;
}

.param-label {
  font-size: 24rpx;
  color: #999;
  margin-bottom: 12rpx;
  display: block;
}

.param-value-row {
  display: flex;
  align-items: baseline;
  margin-bottom: 8rpx;
}

.param-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.param-unit {
  font-size: 22rpx;
  color: #999;
  margin-left: 4rpx;
}

.param-status text {
  font-size: 22rpx;
}

.param-status text.normal {
  color: #2e7d32;
}

.param-status text.warning {
  color: #c62828;
}

.feeding-list {
  margin-top: 8rpx;
}

.feeding-item {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.feeding-item:last-child {
  border-bottom: none;
}

.feeding-time {
  width: 100rpx;
}

.time-text {
  font-size: 24rpx;
  color: #999;
}

.feeding-content {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.feeding-material {
  font-size: 26rpx;
  color: #333;
}

.feeding-amount {
  font-size: 26rpx;
  color: #1E88E5;
  font-weight: 500;
}

.feeding-order {
  width: 80rpx;
  text-align: right;
}

.order-text {
  font-size: 22rpx;
  color: #999;
}

.report-list {
  margin-top: 8rpx;
}

.report-item {
  display: flex;
  align-items: center;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.report-item:last-child {
  border-bottom: none;
}

.report-icon {
  width: 64rpx;
  height: 64rpx;
  background: #e3f2fd;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.report-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.report-title {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 4rpx;
}

.report-date {
  font-size: 22rpx;
  color: #999;
}

.report-arrow {
  padding: 0 8rpx;
}

.arrow-text {
  font-size: 36rpx;
  color: #ccc;
}

.alert-list-mini {
  margin-top: 8rpx;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  padding: 16rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-level-badge {
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
  margin-right: 12rpx;
  flex-shrink: 0;
}

.alert-level-badge.紧急,
.alert-level-badge.严重 {
  background: #ffebee;
}

.alert-level-badge.一般 {
  background: #fff3e0;
}

.level-badge-text {
  font-size: 22rpx;
}

.紧急 .level-badge-text,
.严重 .level-badge-text {
  color: #c62828;
}

.一般 .level-badge-text {
  color: #ef6c00;
}

.alert-content-mini {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.alert-type-mini {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 4rpx;
}

.alert-desc-mini {
  font-size: 22rpx;
  color: #666;
}

.bottom-space {
  height: 40rpx;
}
</style>
