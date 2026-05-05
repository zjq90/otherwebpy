<template>
  <view class="container">
    <view class="section">
      <view class="section-title">选择报表类型</view>
      <view class="type-grid">
        <view 
          class="type-item" 
          :class="{ active: reportType === 'production' }"
          @click="reportType = 'production'"
        >
          <view class="type-icon">📊</view>
          <view class="type-text">生产数据报表</view>
        </view>
        <view 
          class="type-item" 
          :class="{ active: reportType === 'quality' }"
          @click="reportType = 'quality'"
        >
          <view class="type-icon">✅</view>
          <view class="type-text">质量趋势分析</view>
        </view>
        <view 
          class="type-item" 
          :class="{ active: reportType === 'equipment' }"
          @click="reportType = 'equipment'"
        >
          <view class="type-icon">⚙️</view>
          <view class="type-text">设备运行分析</view>
        </view>
      </view>
    </view>

    <view class="section">
      <view class="section-title">选择时间范围</view>
      <view class="date-selector">
        <view class="date-row">
          <view class="date-label">开始日期:</view>
          <picker mode="date" :value="startDate" @change="onStartDateChange">
            <view class="date-picker">{{ startDate }}</view>
          </picker>
        </view>
        <view class="date-row">
          <view class="date-label">结束日期:</view>
          <picker mode="date" :value="endDate" @change="onEndDateChange">
            <view class="date-picker">{{ endDate }}</view>
          </picker>
        </view>
      </view>
      
      <view class="quick-dates">
        <view 
          class="quick-date" 
          :class="{ active: quickDate === 'today' }"
          @click="setQuickDate('today')"
        >今天</view>
        <view 
          class="quick-date" 
          :class="{ active: quickDate === 'week' }"
          @click="setQuickDate('week')"
        >本周</view>
        <view 
          class="quick-date" 
          :class="{ active: quickDate === 'month' }"
          @click="setQuickDate('month')"
        >本月</view>
        <view 
          class="quick-date" 
          :class="{ active: quickDate === 'quarter' }"
          @click="setQuickDate('quarter')"
        >本季度</view>
      </view>
    </view>

    <view class="section">
      <view class="section-title">导出格式</view>
      <view class="format-grid">
        <view 
          class="format-item" 
          :class="{ active: format === 'xlsx' }"
          @click="format = 'xlsx'"
        >
          <view class="format-icon xlsx">📗</view>
          <view class="format-text">Excel (.xlsx)</view>
        </view>
        <view 
          class="format-item" 
          :class="{ active: format === 'csv' }"
          @click="format = 'csv'"
        >
          <view class="format-icon csv">📄</view>
          <view class="format-text">CSV (.csv)</view>
        </view>
        <view 
          class="format-item" 
          :class="{ active: format === 'pdf' }"
          @click="format = 'pdf'"
        >
          <view class="format-icon pdf">📕</view>
          <view class="format-text">PDF (.pdf)</view>
        </view>
      </view>
    </view>

    <view class="preview-section" v-if="previewData">
      <view class="section-title">数据预览</view>
      <view class="preview-stats">
        <view class="preview-stat">
          <view class="preview-label">数据条数</view>
          <view class="preview-value">{{ previewData.count }}</view>
        </view>
        <view class="preview-stat">
          <view class="preview-label">预估大小</view>
          <view class="preview-value">{{ previewData.size }}</view>
        </view>
        <view class="preview-stat">
          <view class="preview-label">包含图表</view>
          <view class="preview-value">{{ previewData.hasChart ? '是' : '否' }}</view>
        </view>
      </view>
    </view>

    <view class="action-section">
      <view class="btn btn-secondary" @click="previewReport">
        预览数据
      </view>
      <view class="btn btn-primary" @click="exportReport" :class="{ disabled: exporting }">
        {{ exporting ? '导出中...' : '导出报表' }}
      </view>
    </view>

    <view class="history-section">
      <view class="section-title">导出历史</view>
      <view class="history-list">
        <view class="history-item" v-for="(item, idx) in exportHistory" :key="idx">
          <view class="history-info">
            <view class="history-name">{{ item.name }}</view>
            <view class="history-detail">{{ item.type }} | {{ item.size }} | {{ item.date }}</view>
          </view>
          <view class="history-action" @click="downloadHistory(item)">
            <text>📥</text>
          </view>
        </view>
        <view class="empty-history" v-if="exportHistory.length === 0">
          暂无导出历史
        </view>
      </view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      reportType: 'production',
      startDate: '',
      endDate: '',
      quickDate: '',
      format: 'xlsx',
      previewData: null,
      exporting: false,
      exportHistory: []
    }
  },
  onLoad() {
    this.initDates()
    this.loadHistory()
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
      this.quickDate = ''
    },

    onEndDateChange(e) {
      this.endDate = e.detail.value
      this.quickDate = ''
    },

    setQuickDate(type) {
      this.quickDate = type
      const today = new Date()
      const year = today.getFullYear()
      const month = today.getMonth()
      const day = today.getDate()
      
      let start = new Date()
      let end = new Date()
      
      switch (type) {
        case 'today':
          start = new Date(year, month, day)
          end = new Date(year, month, day)
          break
        case 'week':
          const dayOfWeek = today.getDay()
          const monday = new Date(today)
          monday.setDate(day - (dayOfWeek === 0 ? 6 : dayOfWeek - 1))
          start = monday
          end = new Date(monday.getTime() + 6 * 24 * 60 * 60 * 1000)
          break
        case 'month':
          start = new Date(year, month, 1)
          end = new Date(year, month + 1, 0)
          break
        case 'quarter':
          const quarter = Math.floor(month / 3)
          start = new Date(year, quarter * 3, 1)
          end = new Date(year, quarter * 3 + 3, 0)
          break
      }
      
      this.startDate = this.formatDate(start)
      this.endDate = this.formatDate(end)
    },

    formatDate(date) {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    },

    async previewReport() {
      uni.showLoading({ title: '加载预览...' })
      
      await new Promise(resolve => setTimeout(resolve, 800))
      
      this.previewData = {
        count: Math.floor(Math.random() * 100) + 50,
        size: `${(Math.random() * 2 + 0.5).toFixed(2)} MB`,
        hasChart: true
      }
      
      uni.hideLoading()
      uni.showToast({ title: '预览加载完成', icon: 'success' })
    },

    async exportReport() {
      if (this.exporting) return
      
      this.exporting = true
      uni.showLoading({ title: '正在导出...' })
      
      try {
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        const typeNames = {
          production: '生产数据报表',
          quality: '质量趋势分析',
          equipment: '设备运行分析'
        }
        
        const newItem = {
          name: `${typeNames[this.reportType]}_${this.endDate}.${this.format}`,
          type: typeNames[this.reportType],
          size: `${(Math.random() * 3 + 0.5).toFixed(2)} MB`,
          date: this.formatDate(new Date())
        }
        
        this.exportHistory.unshift(newItem)
        if (this.exportHistory.length > 10) {
          this.exportHistory.pop()
        }
        
        uni.hideLoading()
        uni.showModal({
          title: '导出成功',
          content: `报表已导出到下载目录\n文件名: ${newItem.name}`,
          showCancel: false
        })
      } catch (e) {
        uni.hideLoading()
        uni.showToast({ title: '导出失败', icon: 'none' })
      } finally {
        this.exporting = false
      }
    },

    loadHistory() {
      const typeNames = {
        production: '生产数据报表',
        quality: '质量趋势分析',
        equipment: '设备运行分析'
      }
      
      const today = new Date()
      for (let i = 0; i < 5; i++) {
        const date = new Date(today.getTime() - i * 24 * 60 * 60 * 1000)
        const types = ['production', 'quality', 'equipment']
        const type = types[i % 3]
        
        this.exportHistory.push({
          name: `${typeNames[type]}_${this.formatDate(date)}.xlsx`,
          type: typeNames[type],
          size: `${(Math.random() * 3 + 0.5).toFixed(2)} MB`,
          date: this.formatDate(date)
        })
      }
    },

    downloadHistory(item) {
      uni.showToast({ title: '开始下载...', icon: 'none' })
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

.section {
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

.type-grid,
.format-grid {
  display: flex;
}

.type-item,
.format-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx;
  border-radius: 12rpx;
  margin: 0 8rpx;
  border: 2rpx solid #E8E8E8;

  &.active {
    border-color: #1890FF;
    background-color: #E6F7FF;
  }

  .type-icon,
  .format-icon {
    font-size: 48rpx;
    margin-bottom: 12rpx;
  }

  .type-text,
  .format-text {
    font-size: 24rpx;
    color: #666666;

    .active & {
      color: #1890FF;
    }
  }
}

.date-selector {
  .date-row {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;

    &:last-child {
      margin-bottom: 0;
    }

    .date-label {
      width: 160rpx;
      font-size: 28rpx;
      color: #666666;
    }

    .date-picker {
      flex: 1;
      padding: 16rpx 24rpx;
      background-color: #F5F7FA;
      border-radius: 8rpx;
      font-size: 28rpx;
      color: #333333;
    }
  }
}

.quick-dates {
  display: flex;
  margin-top: 20rpx;

  .quick-date {
    flex: 1;
    text-align: center;
    padding: 16rpx;
    margin: 0 8rpx;
    border-radius: 8rpx;
    font-size: 26rpx;
    color: #666666;
    background-color: #F5F7FA;

    &.active {
      background-color: #E6F7FF;
      color: #1890FF;
    }
  }
}

.preview-section,
.action-section,
.history-section {
  background-color: #FFFFFF;
  padding: 24rpx;
  margin-bottom: 20rpx;
}

.preview-stats {
  display: flex;

  .preview-stat {
    flex: 1;
    text-align: center;
    padding: 16rpx;

    .preview-label {
      font-size: 24rpx;
      color: #999999;
      margin-bottom: 8rpx;
    }

    .preview-value {
      font-size: 32rpx;
      font-weight: 600;
      color: #1890FF;
    }
  }
}

.action-section {
  display: flex;

  .btn {
    flex: 1;
    padding: 24rpx;
    border-radius: 12rpx;
    text-align: center;
    font-size: 30rpx;
    font-weight: 500;
    margin: 0 10rpx;

    &.btn-primary {
      background: linear-gradient(135deg, #1890FF 0%, #40A9FF 100%);
      color: #FFFFFF;

      &.disabled {
        opacity: 0.6;
      }
    }

    &.btn-secondary {
      background-color: #F5F7FA;
      color: #666666;
    }
  }
}

.history-list {
  .history-item {
    display: flex;
    align-items: center;
    padding: 16rpx 0;
    border-bottom: 1rpx solid #F0F0F0;

    &:last-child {
      border-bottom: none;
    }

    .history-info {
      flex: 1;

      .history-name {
        font-size: 28rpx;
        color: #1F2329;
        margin-bottom: 6rpx;
      }

      .history-detail {
        font-size: 22rpx;
        color: #999999;
      }
    }

    .history-action {
      padding: 16rpx;
      font-size: 32rpx;
    }
  }

  .empty-history {
    text-align: center;
    padding: 40rpx;
    color: #999999;
    font-size: 28rpx;
  }
}
</style>
