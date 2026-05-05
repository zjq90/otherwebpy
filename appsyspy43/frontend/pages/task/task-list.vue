<template>
  <view class="task-list-container">
    <!-- 顶部筛选标签 -->
    <scroll-view scroll-x class="filter-scroll">
      <view class="filter-tabs">
        <view 
          class="filter-tab" 
          :class="{ active: currentTab === 'all' }"
          @click="switchTab('all')"
        >
          <text class="tab-text">全部任务</text>
          <text class="tab-count" v-if="tabCounts.all > 0">{{ tabCounts.all }}</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: currentTab === 'pending' }"
          @click="switchTab('pending')"
        >
          <text class="tab-text">待分配</text>
          <text class="tab-count" v-if="tabCounts.pending > 0">{{ tabCounts.pending }}</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: currentTab === 'assigned' }"
          @click="switchTab('assigned')"
        >
          <text class="tab-text">已分配</text>
          <text class="tab-count" v-if="tabCounts.assigned > 0">{{ tabCounts.assigned }}</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: currentTab === 'in_progress' }"
          @click="switchTab('in_progress')"
        >
          <text class="tab-text">进行中</text>
          <text class="tab-count" v-if="tabCounts.in_progress > 0">{{ tabCounts.in_progress }}</text>
        </view>
        <view 
          class="filter-tab" 
          :class="{ active: currentTab === 'completed' }"
          @click="switchTab('completed')"
        >
          <text class="tab-text">已完成</text>
          <text class="tab-count" v-if="tabCounts.completed > 0">{{ tabCounts.completed }}</text>
        </view>
      </view>
    </scroll-view>
    
    <!-- 搜索栏 -->
    <view class="search-bar">
      <view class="search-input-wrapper">
        <text class="search-icon">🔍</text>
        <input 
          class="search-input" 
          v-model="searchKeyword" 
          placeholder="搜索任务编号、货物名称等"
          @confirm="searchTasks"
        />
        <view class="search-clear" v-if="searchKeyword" @click="clearSearch">
          <text>×</text>
        </view>
      </view>
      <view class="search-btn" @click="searchTasks">
        <text>搜索</text>
      </view>
    </view>
    
    <!-- 任务列表 -->
    <scroll-view 
      scroll-y 
      class="task-scroll"
      @scrolltolower="loadMore"
      :refresher-enabled="true"
      :refresher-triggered="isRefreshing"
      @refresherrefresh="onRefresh"
    >
      <!-- 任务卡片列表 -->
      <view class="task-list" v-if="taskList.length > 0">
        <view 
          class="task-card card" 
          v-for="(task, index) in taskList" 
          :key="task.id"
          @click="goToTaskDetail(task.id)"
        >
          <!-- 任务头部 -->
          <view class="task-header">
            <view class="task-no-wrapper">
              <text class="task-no">{{ task.task_no }}</text>
              <text class="task-name" v-if="task.task_name">{{ task.task_name }}</text>
            </view>
            <text class="status-tag" :class="getStatusClass(task.status)">
              {{ getStatusText(task.status) }}
            </text>
          </view>
          
          <!-- 任务信息 -->
          <view class="task-info">
            <view class="info-row">
              <view class="info-label">
                <text class="label-icon">📦</text>
                <text class="label-text">货物</text>
              </view>
              <text class="info-value">{{ task.cargo_name || '-' }}</text>
            </view>
            
            <view class="info-row">
              <view class="info-label">
                <text class="label-icon">🚩</text>
                <text class="label-text">装货地</text>
              </view>
              <text class="info-value">{{ task.loading_address || '-' }}</text>
            </view>
            
            <view class="info-row">
              <view class="info-label">
                <text class="label-icon">🏁</text>
                <text class="label-text">卸货地</text>
              </view>
              <text class="info-value">{{ task.unloading_address || '-' }}</text>
            </view>
            
            <view class="info-row" v-if="task.driver">
              <view class="info-label">
                <text class="label-icon">👤</text>
                <text class="label-text">司机</text>
              </view>
              <text class="info-value">{{ task.driver.real_name || '-' }}</text>
            </view>
            
            <view class="info-row" v-if="task.estimated_arrival_time">
              <view class="info-label">
                <text class="label-icon">⏰</text>
                <text class="label-text">预计到达</text>
              </view>
              <text class="info-value">{{ formatTime(task.estimated_arrival_time) }}</text>
            </view>
          </view>
          
          <!-- 任务操作按钮 -->
          <view class="task-actions" v-if="showActionButtons(task)">
            <view class="action-btn action-primary" v-if="canAssign(task)" @click.stop="assignTask(task)">
              <text>分配任务</text>
            </view>
            <view class="action-btn action-success" v-if="canConfirm(task)" @click.stop="confirmTask(task)">
              <text>确认任务</text>
            </view>
            <view class="action-btn action-primary" v-if="canDepart(task)" @click.stop="updateTaskStatus(task, 'departed')">
              <text>已出发</text>
            </view>
            <view class="action-btn action-primary" v-if="canArrive(task)" @click.stop="updateTaskStatus(task, 'arrived')">
              <text>已到达</text>
            </view>
            <view class="action-btn action-success" v-if="canComplete(task)" @click.stop="goToUpdateStatus(task)">
              <text>卸料上传</text>
            </view>
          </view>
          
          <!-- 任务底部信息 -->
          <view class="task-footer">
            <text class="footer-text">创建时间: {{ formatTime(task.created_at) }}</text>
            <text class="footer-text" v-if="task.vehicle">车辆: {{ task.vehicle.plate_number }}</text>
          </view>
        </view>
      </view>
      
      <!-- 空状态 -->
      <view class="empty-state" v-else-if="!loading">
        <text class="empty-icon">📋</text>
        <text class="empty-text">暂无任务数据</text>
        <view class="refresh-btn" @click="onRefresh">
          <text>点击刷新</text>
        </view>
      </view>
      
      <!-- 加载中 -->
      <view class="loading-state" v-if="loading">
        <text class="loading-text">加载中...</text>
      </view>
      
      <!-- 加载更多状态 -->
      <view class="load-more-state" v-if="!loading && hasMore && taskList.length > 0">
        <text class="load-more-text">上拉加载更多</text>
      </view>
      
      <view class="load-more-state" v-if="!loading && !hasMore && taskList.length > 0">
        <text class="load-more-text">没有更多数据了</text>
      </view>
    </scroll-view>
    
    <!-- 浮动创建按钮（调度员/管理员可见） -->
    <view class="fab-button" v-if="canCreateTask" @click="goToCreateTask">
      <text class="fab-icon">+</text>
    </view>
  </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
  data() {
    return {
      currentTab: 'all',
      searchKeyword: '',
      taskList: [],
      tabCounts: {
        all: 0,
        pending: 0,
        assigned: 0,
        in_progress: 0,
        completed: 0
      },
      loading: false,
      isRefreshing: false,
      hasMore: true,
      currentPage: 1,
      pageSize: 10,
      userInfo: null
    }
  },
  
  onLoad() {
    this.userInfo = uni.getStorageSync(config.userInfoKey) || {}
    this.loadData()
  },
  
  onShow() {
    this.onRefresh()
  },
  
  computed: {
    // 是否可以创建任务
    canCreateTask() {
      const role = this.userInfo?.role
      return role === config.roles.ADMIN || role === config.roles.DISPATCHER
    }
  },
  
  methods: {
    // 切换标签
    switchTab(tab) {
      if (this.currentTab !== tab) {
        this.currentTab = tab
        this.taskList = []
        this.currentPage = 1
        this.hasMore = true
        this.loadData()
      }
    },
    
    // 搜索任务
    searchTasks() {
      this.currentPage = 1
      this.taskList = []
      this.hasMore = true
      this.loadData()
    },
    
    // 清除搜索
    clearSearch() {
      this.searchKeyword = ''
      this.searchTasks()
    },
    
    // 加载数据
    async loadData() {
      if (this.loading) return
      
      this.loading = true
      
      try {
        const token = uni.getStorageSync(config.tokenKey)
        
        // 构建查询参数
        let url = `${config.baseUrl}/api/tasks?page=${this.currentPage}&size=${this.pageSize}`
        
        // 根据标签添加状态筛选
        if (this.currentTab !== 'all') {
          if (this.currentTab === 'pending') {
            url += '&status=pending'
          } else if (this.currentTab === 'assigned') {
            url += '&status=assigned,confirmed'
          } else if (this.currentTab === 'in_progress') {
            url += '&status=departed,arrived,unloading'
          } else if (this.currentTab === 'completed') {
            url += '&status=completed'
          }
        }
        
        // 添加搜索关键词
        if (this.searchKeyword) {
          url += `&keyword=${encodeURIComponent(this.searchKeyword)}`
        }
        
        const res = await uni.request({
          url: url,
          method: 'GET',
          header: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          const data = res[1].data.data
          
          if (this.currentPage === 1) {
            this.taskList = data.items || []
          } else {
            this.taskList = [...this.taskList, ...(data.items || [])]
          }
          
          this.hasMore = this.taskList.length < data.total
          
          // 更新统计数据（仅第一页）
          if (this.currentPage === 1 && data.stats) {
            this.tabCounts = {
              all: data.total || 0,
              pending: data.stats.pending || 0,
              assigned: data.stats.assigned || 0,
              in_progress: data.stats.in_progress || 0,
              completed: data.stats.completed || 0
            }
          }
        }
      } catch (error) {
        console.error('加载任务列表失败:', error)
        uni.showToast({ title: '加载失败', icon: 'none' })
      } finally {
        this.loading = false
        this.isRefreshing = false
      }
    },
    
    // 下拉刷新
    onRefresh() {
      this.isRefreshing = true
      this.currentPage = 1
      this.hasMore = true
      this.loadData()
    },
    
    // 加载更多
    loadMore() {
      if (!this.loading && this.hasMore) {
        this.currentPage++
        this.loadData()
      }
    },
    
    // 获取任务状态样式类
    getStatusClass(status) {
      return `status-${status}`
    },
    
    // 获取任务状态文本
    getStatusText(status) {
      return config.taskStatusText[status] || '未知状态'
    },
    
    // 格式化时间
    formatTime(timeStr) {
      if (!timeStr) return '-'
      const date = new Date(timeStr)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hour = String(date.getHours()).padStart(2, '0')
      const minute = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day} ${hour}:${minute}`
    },
    
    // 是否显示操作按钮
    showActionButtons(task) {
      const role = this.userInfo?.role
      
      // 管理员和调度员可以分配任务
      if ((role === config.roles.ADMIN || role === config.roles.DISPATCHER) && 
          task.status === 'pending') {
        return true
      }
      
      // 司机可以确认、出发、到达、完成任务
      if (role === config.roles.DRIVER) {
        const driverTasks = ['assigned', 'confirmed', 'departed', 'arrived']
        return driverTasks.includes(task.status)
      }
      
      return false
    },
    
    // 是否可以分配任务
    canAssign(task) {
      const role = this.userInfo?.role
      return (role === config.roles.ADMIN || role === config.roles.DISPATCHER) && 
             task.status === 'pending'
    },
    
    // 是否可以确认任务
    canConfirm(task) {
      return this.userInfo?.role === config.roles.DRIVER && 
             task.status === 'assigned'
    },
    
    // 是否可以出发
    canDepart(task) {
      return this.userInfo?.role === config.roles.DRIVER && 
             task.status === 'confirmed'
    },
    
    // 是否可以到达
    canArrive(task) {
      return this.userInfo?.role === config.roles.DRIVER && 
             task.status === 'departed'
    },
    
    // 是否可以完成
    canComplete(task) {
      return this.userInfo?.role === config.roles.DRIVER && 
             (task.status === 'arrived' || task.status === 'unloading')
    },
    
    // 跳转到任务详情
    goToTaskDetail(id) {
      uni.navigateTo({
        url: `/pages/task/task-detail?id=${id}`
      })
    },
    
    // 跳转到创建任务
    goToCreateTask() {
      uni.navigateTo({
        url: '/pages/task/task-create'
      })
    },
    
    // 分配任务
    assignTask(task) {
      uni.navigateTo({
        url: `/pages/task/task-create?task_id=${task.id}&action=assign`
      })
    },
    
    // 确认任务
    async confirmTask(task) {
      try {
        const token = uni.getStorageSync(config.tokenKey)
        const res = await uni.request({
          url: `${config.baseUrl}/api/tasks/${task.id}/confirm`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          uni.showToast({ title: '任务已确认', icon: 'success' })
          this.onRefresh()
        } else {
          uni.showToast({ title: res[1].data?.message || '操作失败', icon: 'none' })
        }
      } catch (error) {
        console.error('确认任务失败:', error)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    
    // 更新任务状态
    async updateTaskStatus(task, newStatus) {
      try {
        const token = uni.getStorageSync(config.tokenKey)
        const res = await uni.request({
          url: `${config.baseUrl}/api/tasks/${task.id}/status`,
          method: 'POST',
          header: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          data: {
            new_status: newStatus,
            description: `状态更新为: ${this.getStatusText(newStatus)}`
          }
        })
        
        if (res[1].statusCode === 200 && res[1].data.code === 200) {
          uni.showToast({ title: '状态更新成功', icon: 'success' })
          this.onRefresh()
        } else {
          uni.showToast({ title: res[1].data?.message || '操作失败', icon: 'none' })
        }
      } catch (error) {
        console.error('更新任务状态失败:', error)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    
    // 跳转到状态更新页面（卸料上传）
    goToUpdateStatus(task) {
      uni.navigateTo({
        url: `/pages/driver/task-status?id=${task.id}`
      })
    }
  }
}
</script>

<style scoped>
.task-list-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #F5F5F5;
}

/* 筛选标签 */
.filter-scroll {
  background: #FFFFFF;
  white-space: nowrap;
  padding: 20rpx 0;
  border-bottom: 1rpx solid #EBEEF5;
}

.filter-tabs {
  display: inline-flex;
  padding: 0 20rpx;
  gap: 20rpx;
}

.filter-tab {
  display: inline-flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 24rpx;
  background: #F5F7FA;
  border-radius: 30rpx;
}

.filter-tab.active {
  background: #409EFF;
}

.tab-text {
  font-size: 26rpx;
  color: #606266;
}

.filter-tab.active .tab-text {
  color: #FFFFFF;
}

.tab-count {
  font-size: 22rpx;
  padding: 2rpx 12rpx;
  background: rgba(0, 0, 0, 0.1);
  border-radius: 20rpx;
  color: #909399;
}

.filter-tab.active .tab-count {
  background: rgba(255, 255, 255, 0.2);
  color: #FFFFFF;
}

/* 搜索栏 */
.search-bar {
  display: flex;
  padding: 20rpx;
  background: #FFFFFF;
  gap: 20rpx;
  align-items: center;
}

.search-input-wrapper {
  flex: 1;
  display: flex;
  align-items: center;
  background: #F5F7FA;
  border-radius: 40rpx;
  padding: 0 24rpx;
  height: 72rpx;
}

.search-icon {
  font-size: 28rpx;
  margin-right: 12rpx;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #303133;
}

.search-clear {
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #C0C4CC;
  border-radius: 50%;
}

.search-clear text {
  font-size: 24rpx;
  color: #FFFFFF;
}

.search-btn {
  padding: 16rpx 32rpx;
  background: #409EFF;
  border-radius: 8rpx;
}

.search-btn text {
  font-size: 28rpx;
  color: #FFFFFF;
}

/* 任务列表滚动区域 */
.task-scroll {
  flex: 1;
  padding: 20rpx;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 20rpx;
}

.task-card {
  margin-bottom: 0;
}

/* 任务头部 */
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
  padding-bottom: 20rpx;
  border-bottom: 1rpx solid #EBEEF5;
}

.task-no-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.task-no {
  font-size: 30rpx;
  font-weight: bold;
  color: #303133;
}

.task-name {
  font-size: 24rpx;
  color: #909399;
}

/* 任务信息 */
.task-info {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.info-row {
  display: flex;
  align-items: flex-start;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8rpx;
  width: 120rpx;
  flex-shrink: 0;
}

.label-icon {
  font-size: 24rpx;
}

.label-text {
  font-size: 24rpx;
  color: #909399;
}

.info-value {
  font-size: 26rpx;
  color: #606266;
  flex: 1;
}

/* 任务操作按钮 */
.task-actions {
  display: flex;
  gap: 20rpx;
  margin-bottom: 20rpx;
  padding-top: 16rpx;
  border-top: 1rpx solid #EBEEF5;
}

.action-btn {
  flex: 1;
  padding: 16rpx;
  border-radius: 8rpx;
  text-align: center;
}

.action-primary {
  background: #ECF5FF;
}

.action-primary text {
  font-size: 26rpx;
  color: #409EFF;
}

.action-success {
  background: #F0F9EB;
}

.action-success text {
  font-size: 26rpx;
  color: #67C23A;
}

/* 任务底部 */
.task-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 16rpx;
  border-top: 1rpx dashed #EBEEF5;
}

.footer-text {
  font-size: 22rpx;
  color: #C0C4CC;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 100rpx 0;
}

.empty-icon {
  font-size: 100rpx;
  margin-bottom: 20rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
  margin-bottom: 30rpx;
}

.refresh-btn {
  padding: 16rpx 48rpx;
  background: #409EFF;
  border-radius: 8rpx;
}

.refresh-btn text {
  font-size: 28rpx;
  color: #FFFFFF;
}

/* 加载状态 */
.loading-state,
.load-more-state {
  display: flex;
  justify-content: center;
  padding: 30rpx 0;
}

.loading-text,
.load-more-text {
  font-size: 26rpx;
  color: #909399;
}

/* 浮动按钮 */
.fab-button {
  position: fixed;
  right: 40rpx;
  bottom: 120rpx;
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #409EFF 0%, #66b1ff 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(64, 158, 255, 0.4);
  z-index: 100;
}

.fab-icon {
  font-size: 48rpx;
  color: #FFFFFF;
  font-weight: bold;
}
</style>
