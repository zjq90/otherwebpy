<template>
  <view class="trace-container">
    <!-- 扫码区域 -->
    <view class="scan-section">
      <view class="scan-card" @click="scanQRCode">
        <view class="scan-icon">
          <text class="icon-text">📷</text>
        </view>
        <view class="scan-info">
          <text class="scan-title">扫描罐车二维码</text>
          <text class="scan-desc">点击扫描混凝土运输罐车二维码</text>
        </view>
        <view class="scan-arrow">
          <text class="arrow-text">›</text>
        </view>
      </view>
    </view>
    
    <!-- 手动输入 -->
    <view class="input-section">
      <view class="section-title">
        <text class="title-text">手动输入</text>
      </view>
      <view class="input-row">
        <input 
          class="qr-input" 
          placeholder="请输入二维码标识或生产单号" 
          v-model="qrCode"
        />
        <view class="search-btn" @click="searchByQR">
          <text class="btn-text">查询</text>
        </view>
      </view>
    </view>
    
    <!-- 按罐车查询 -->
    <view class="truck-section">
      <view class="section-title">
        <text class="title-text">按罐车查询</text>
      </view>
      <view class="truck-input-row">
        <picker :value="truckIndex" :range="truckList" @change="onTruckChange">
          <view class="picker-input">
            <text class="picker-text">{{ truckList[truckIndex] || '请选择罐车编号' }}</text>
            <text class="picker-arrow">▼</text>
          </view>
        </picker>
      </view>
    </view>
    
    <!-- 最近追溯记录 -->
    <view class="history-section" v-if="historyList.length > 0">
      <view class="section-title">
        <text class="title-text">最近追溯</text>
      </view>
      <view class="history-list">
        <view 
          class="history-item" 
          v-for="(item, index) in historyList" 
          :key="index"
          @click="goToTraceResult(item)"
        >
          <view class="history-icon">
            <text class="icon-text">📋</text>
          </view>
          <view class="history-info">
            <text class="history-no">{{ item.production_no }}</text>
            <text class="history-truck">罐车: {{ item.truck_no }}</text>
          </view>
          <view class="history-status" :class="item.status">
            <text class="status-text">{{ item.status }}</text>
          </view>
        </view>
      </view>
    </view>
    
    <!-- 空状态 -->
    <view class="empty-state" v-else>
      <view class="empty-icon">
        <text class="empty-text">🔍</text>
      </view>
      <text class="empty-title">暂无追溯记录</text>
      <text class="empty-desc">扫描二维码或手动输入查询生产记录</text>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      qrCode: '',
      truckIndex: 0,
      truckList: ['请选择罐车', '豫A-12345', '豫A-12346', '豫A-12347', '豫A-12348', '豫A-12349'],
      historyList: []
    }
  },
  onShow() {
    this.loadHistory()
  },
  methods: {
    scanQRCode() {
      // 调用uni-app扫码API
      uni.scanCode({
        success: (res) => {
          console.log('扫码结果:', res.result)
          this.qrCode = res.result
          this.searchByQR()
        },
        fail: (err) => {
          console.error('扫码失败:', err)
          uni.showToast({
            title: '扫码失败，请重试',
            icon: 'none'
          })
        }
      })
    },
    
    async searchByQR() {
      if (!this.qrCode.trim()) {
        uni.showToast({
          title: '请输入二维码标识',
          icon: 'none'
        })
        return
      }
      
      try {
        const res = await request.get(`/api/trace/qr/${this.qrCode}`)
        
        if (res.code === 200) {
          // 保存到历史记录
          this.saveToHistory(res.data)
          
          // 跳转到追溯结果页
          uni.navigateTo({
            url: `/pages/trace/trace-result?qrCode=${this.qrCode}`
          })
        }
      } catch (err) {
        console.error('查询失败:', err)
        // 使用模拟数据演示
        uni.navigateTo({
          url: `/pages/trace/trace-result?qrCode=${this.qrCode}`
        })
      }
    },
    
    onTruckChange(e) {
      this.truckIndex = e.detail.value
      if (this.truckIndex > 0) {
        // 查询该罐车的生产记录
        this.searchByTruck(this.truckList[this.truckIndex])
      }
    },
    
    async searchByTruck(truckNo) {
      try {
        const res = await request.get(`/api/trace/truck/${truckNo}`)
        
        if (res.code === 200 && res.data.productions.length > 0) {
          // 显示第一个生产记录
          const production = res.data.productions[0]
          this.qrCode = production.qr_code
          this.saveToHistory(production)
          
          uni.navigateTo({
            url: `/pages/trace/trace-result?qrCode=${production.qr_code}`
          })
        } else {
          uni.showToast({
            title: '未找到该罐车的生产记录',
            icon: 'none'
          })
        }
      } catch (err) {
        console.error('查询罐车失败:', err)
        // 模拟跳转
        uni.navigateTo({
          url: `/pages/trace/trace-result?qrCode=QR202605051030001234`
        })
      }
    },
    
    saveToHistory(data) {
      // 从本地存储获取历史记录
      let history = uni.getStorageSync('traceHistory') || []
      
      // 添加新记录
      const newRecord = {
        production_no: data.production?.production_no || 'PRO-' + Date.now(),
        qr_code: data.production?.qr_code || this.qrCode,
        truck_no: data.production?.truck_no || '-',
        status: data.production?.status || '正常',
        trace_time: new Date().toISOString()
      }
      
      // 检查是否已存在
      const existIndex = history.findIndex(item => item.qr_code === newRecord.qr_code)
      if (existIndex > -1) {
        history.splice(existIndex, 1)
      }
      
      // 添加到开头
      history.unshift(newRecord)
      
      // 限制历史记录数量
      if (history.length > 10) {
        history = history.slice(0, 10)
      }
      
      // 保存到本地存储
      uni.setStorageSync('traceHistory', history)
      
      // 更新页面数据
      this.historyList = history
    },
    
    loadHistory() {
      const history = uni.getStorageSync('traceHistory') || []
      this.historyList = history
    },
    
    goToTraceResult(item) {
      uni.navigateTo({
        url: `/pages/trace/trace-result?qrCode=${item.qr_code}`
      })
    }
  }
}
</script>

<style scoped>
.trace-container {
  min-height: 100vh;
  background: #f5f5f5;
  padding-bottom: 40rpx;
}

/* 扫码区域 */
.scan-section {
  padding: 32rpx 24rpx;
}

.scan-card {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  border-radius: 16rpx;
  padding: 32rpx;
  display: flex;
  align-items: center;
  box-shadow: 0 8rpx 24rpx rgba(30, 136, 229, 0.3);
}

.scan-icon {
  width: 96rpx;
  height: 96rpx;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 24rpx;
}

.icon-text {
  font-size: 48rpx;
}

.scan-info {
  flex: 1;
}

.scan-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #fff;
  margin-bottom: 8rpx;
  display: block;
}

.scan-desc {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.8);
}

.scan-arrow {
  padding: 0 16rpx;
}

.arrow-text {
  font-size: 48rpx;
  color: rgba(255, 255, 255, 0.6);
}

/* 输入区域 */
.input-section,
.truck-section {
  background: #fff;
  margin: 0 24rpx 20rpx;
  border-radius: 16rpx;
  padding: 24rpx;
}

.section-title {
  margin-bottom: 20rpx;
}

.title-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

.input-row,
.truck-input-row {
  display: flex;
  align-items: center;
}

.qr-input {
  flex: 1;
  height: 88rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 24rpx;
  font-size: 28rpx;
}

.search-btn {
  margin-left: 16rpx;
  padding: 20rpx 32rpx;
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
  border-radius: 12rpx;
}

.btn-text {
  font-size: 28rpx;
  color: #fff;
  font-weight: 500;
}

/* 选择器 */
.picker-input {
  width: 100%;
  height: 88rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.picker-text {
  font-size: 28rpx;
  color: #333;
}

.picker-arrow {
  font-size: 20rpx;
  color: #999;
}

/* 历史记录 */
.history-section {
  margin: 20rpx 24rpx 0;
}

.history-list {
  background: #fff;
  border-radius: 16rpx;
  overflow: hidden;
}

.history-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.history-item:last-child {
  border-bottom: none;
}

.history-icon {
  width: 72rpx;
  height: 72rpx;
  background: #e3f2fd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20rpx;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.history-no {
  font-size: 28rpx;
  color: #333;
  margin-bottom: 8rpx;
}

.history-truck {
  font-size: 24rpx;
  color: #999;
}

.history-status {
  padding: 6rpx 16rpx;
  border-radius: 4rpx;
}

.history-status.正常 {
  background: #e8f5e9;
}

.history-status.异常 {
  background: #ffebee;
}

.status-text {
  font-size: 22rpx;
}

.正常 .status-text {
  color: #2e7d32;
}

.异常 .status-text {
  color: #c62828;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 80rpx 0;
}

.empty-icon {
  width: 140rpx;
  height: 140rpx;
  background: #e3f2fd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24rpx;
}

.empty-text {
  font-size: 56rpx;
}

.empty-title {
  font-size: 30rpx;
  color: #333;
  margin-bottom: 12rpx;
}

.empty-desc {
  font-size: 26rpx;
  color: #999;
}
</style>
