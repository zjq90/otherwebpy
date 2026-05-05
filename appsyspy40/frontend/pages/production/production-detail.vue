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
          <view class="header-info">
            <text class="production-no">{{ productionData.production_no || '-' }}</text>
            <text class="truck-no">罐车: {{ productionData.truck_no || '-' }}</text>
          </view>
          <view class="status-tag" :class="productionData.status === '正常' ? 'normal' : 'warning'">
            <text class="status-text">{{ productionData.status || '正常' }}</text>
          </view>
        </view>
        
        <view class="info-list">
          <view class="info-item">
            <text class="info-label">生产时间</text>
            <text class="info-value">{{ formatTime(productionData.production_date) }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">工程名称</text>
            <text class="info-value">{{ productionData.project_name || '-' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">施工部位</text>
            <text class="info-value">{{ productionData.construction_site || '-' }}</text>
          </view>
          <view class="info-item">
            <text class="info-label">搅拌方量</text>
            <text class="info-value">{{ productionData.mix_volume || '-' }} m³</text>
          </view>
        </view>
      </view>
      
      <view class="section-card">
        <view class="section-title">
          <text class="title-text">搅拌参数</text>
        </view>
        <view class="params-grid">
          <view class="param-item">
            <text class="param-label">搅拌时间</text>
            <view class="param-value-row">
              <text class="param-value" :class="isMixingTimeOk() ? '' : 'warning'">
                {{ productionData.mixing_time || '-' }}
              </text>
              <text class="param-unit">秒</text>
            </view>
            <view class="param-target">
              <text class="target-text">目标: {{ productionData.target_mix_duration || 90 }} 秒</text>
            </view>
          </view>
          <view class="param-item">
            <text class="param-label">搅拌转速</text>
            <view class="param-value-row">
              <text class="param-value">{{ productionData.mixing_speed || '-' }}</text>
              <text class="param-unit">rpm</text>
            </view>
          </view>
          <view class="param-item">
            <text class="param-label">出料温度</text>
            <view class="param-value-row">
              <text class="param-value">{{ productionData.discharge_temp || '-' }}</text>
              <text class="param-unit">°C</text>
            </view>
          </view>
          <view class="param-item">
            <text class="param-label">坍落度</text>
            <view class="param-value-row">
              <text class="param-value">{{ productionData.slump || '-' }}</text>
              <text class="param-unit">mm</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="formulaData">
        <view class="section-title">
          <text class="title-text">生产配方</text>
          <text class="formula-code">{{ formulaData.formula_code || '-' }}</text>
        </view>
        <view class="formula-table">
          <view class="table-header">
            <text class="cell material">原材料</text>
            <text class="cell target">目标</text>
            <text class="cell actual">实际</text>
            <text class="cell deviation">偏差</text>
          </view>
          <view class="table-row" v-for="(item, index) in formulaItems" :key="index">
            <text class="cell material">{{ item.material }}</text>
            <text class="cell target">{{ item.target }}</text>
            <text class="cell actual">{{ item.actual }}</text>
            <text class="cell deviation" :class="getDeviationClass(item.deviation)">
              {{ item.deviation }}%
            </text>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="feedings.length > 0">
        <view class="section-title">
          <text class="title-text">投料记录</text>
          <text class="count-text">共 {{ feedings.length }} 次</text>
        </view>
        <view class="feeding-list">
          <view class="feeding-item" v-for="(item, index) in feedings" :key="index">
            <view class="feeding-order">
              <text class="order-text">第{{ index + 1}}次</text>
            </view>
            <view class="feeding-content">
              <text class="feeding-material">{{ item.material_type_name || item.material_type || '-' }}</text>
              <text class="feeding-time">{{ formatTime(item.feeding_time, 'time') }}</text>
            </view>
            <view class="feeding-amount">
              <text class="amount-text">{{ item.actual_amount || '-' }} kg</text>
            </view>
          </view>
        </view>
      </view>
      
      <view class="section-card" v-if="alerts.length > 0">
        <view class="section-title warning">
          <text class="title-text">相关预警</text>
          <text class="count-warning">{{ alerts.length }} 条</text>
        </view>
        <view class="alert-list-mini">
          <view 
            class="alert-item" 
            v-for="(item, index) in alerts" 
            :key="index"
            @click="goToAlert(item)"
          >
            <view class="alert-level" :class="item.alert_level.toLowerCase()">
              <text class="level-text">{{ item.alert_level }}</text>
            </view>
            <view class="alert-info">
              <text class="alert-type">{{ alertTypeText(item.alert_type) }}</text>
              <text class="alert-desc">{{ item.description }}</text>
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
      productionId: null,
      productionData: {},
      formulaData: null,
      formulaItems: [],
      feedings: [],
      alerts: []
    }
  },
  onLoad(options) {
    if (options.id) {
      this.productionId = options.id
      this.loadDetail()
    }
  },
  methods: {
    async loadDetail() {
      this.loading = true
      
      try {
        const res = await request.get('/api/productions/' + this.productionId)
        
        if (res.code === 200) {
          this.productionData = res.data
          if (res.data.formula) {
            this.formulaData = res.data.formula
            this.processFormulaData()
          }
          if (res.data.feedings) {
            this.feedings = res.data.feedings
          }
          if (res.data.alerts) {
            this.alerts = res.data.alerts
          }
        }
      } catch (err) {
        console.error('加载生产详情失败:', err)
        this.loadMockData()
      } finally {
        this.loading = false
      }
    },
    
    loadMockData() {
      this.productionData = {
        id: 1,
        production_no: 'PRO20260505123456',
        truck_no: '豫A-12345',
        status: '正常',
        production_date: '2026-05-05T10:30:00',
        project_name: '郑州市轨道交通8号线工程',
        construction_site: '主体结构承台',
        mix_volume: 8.5,
        mixing_time: 95,
        target_mix_duration: 90,
        mixing_speed: 35,
        discharge_temp: 25,
        slump: 180
      }
      
      this.formulaData = {
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
        admixture_deviation: -2.86
      }
      
      this.processFormulaData()
      
      this.feedings = [
        { feeding_time: '2026-05-05T10:30:00', material_type: '水泥', material_type_name: '水泥', actual_amount: 348 },
        { feeding_time: '2026-05-05T10:30:15', material_type: 'sand', material_type_name: '砂', actual_amount: 745 },
        { feeding_time: '2026-05-05T10:30:30', material_type: 'stone', material_type_name: '碎石', actual_amount: 1048 },
        { feeding_time: '2026-05-05T10:30:45', material_type: 'water', material_type_name: '水', actual_amount: 180 },
        { feeding_time: '2026-05-05T10:31:00', material_type: 'admixture', material_type_name: '外加剂', actual_amount: 6.8 }
      ]
    },
    
    processFormulaData() {
      if (!this.formulaData) return
      
      const formula = this.formulaData
      
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
    
    isMixingTimeOk() {
      if (!this.productionData.mixing_time || !this.productionData.target_mix_duration) return true
      return this.productionData.mixing_time >= this.productionData.target_mix_duration
    },
    
    getDeviationClass(deviation) {
      const dev = Math.abs(parseFloat(deviation) || 0)
      if (dev > 2) return 'warning'
      return 'normal'
    },
    
    alertTypeText(type) {
      const typeMap = {
        'mix_ratio_deviation': '配比偏差',
        'mix_time_short': '搅拌时间不足',
        'material_unqualified': '原材料不合格'
      }
      return typeMap[type] || type
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
    
    goToAlert(item) {
      uni.navigateTo({
        url: '/pages/alert/alert-detail?id=' + item.id
      })
    }
  }
}
</script>

<style scoped>
.detail-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
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

.header-info {
  display: flex;
  flex-direction: column;
}

.production-no {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 4rpx;
}

.truck-no {
  font-size: 22rpx;
  color: #999;
}

.status-tag {
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
}

.status-tag.normal {
  background: #e8f5e9;
}

.status-tag.warning {
  background: #ffebee;
}

.status-text {
  font-size: 22rpx;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
  margin-bottom: 16rpx;
}

.section-title.warning {
  border-bottom-color: #ffebee;
}

.title-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.formula-code {
  font-size: 24rpx;
  color: #999;
}

.count-text {
  font-size: 24rpx;
  color: #999;
}

.count-warning {
  font-size: 22rpx;
  color: #c62828;
  background: #ffebee;
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
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
  margin-bottom: 4rpx;
}

.param-value {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.param-value.warning {
  color: #c62828;
}

.param-unit {
  font-size: 22rpx;
  color: #999;
  margin-left: 4rpx;
}

.param-target {
  margin-top: 4rpx;
}

.target-text {
  font-size: 20rpx;
  color: #999;
}

.formula-table {
  margin-top: 8rpx;
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

.feeding-order {
  width: 80rpx;
}

.order-text {
  font-size: 24rpx;
  color: #999;
}

.feeding-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.feeding-material {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 4rpx;
}

.feeding-time {
  font-size: 22rpx;
  color: #999;
}

.feeding-amount {
  width: 120rpx;
  text-align: right;
}

.amount-text {
  font-size: 26rpx;
  color: #1E88E5;
  font-weight: 500;
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

.alert-level {
  padding: 4rpx 12rpx;
  border-radius: 4rpx;
  margin-right: 12rpx;
  flex-shrink: 0;
}

.alert-level.紧急,
.alert-level.严重 {
  background: #ffebee;
}

.alert-level.一般 {
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

.alert-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.alert-type {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 4rpx;
}

.alert-desc {
  font-size: 22rpx;
  color: #666;
}

.bottom-space {
  height: 40rpx;
}
</style>
