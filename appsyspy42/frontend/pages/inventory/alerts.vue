<template>
    <view class="page-container">
        <view class="stats-section">
            <view class="stat-item">
                <text class="stat-value">{{ stats.unhandledCount || 0 }}</text>
                <text class="stat-label">未处理</text>
            </view>
            <view class="stat-item">
                <text class="stat-value">{{ stats.handledCount || 0 }}</text>
                <text class="stat-label">已处理</text>
            </view>
        </view>
        
        <view class="filter-tabs">
            <view 
                class="tab-item" 
                :class="{ active: currentTab === 'unhandled' }"
                @click="switchTab('unhandled')"
            >
                未处理
                <view class="badge" v-if="stats.unhandledCount > 0">{{ stats.unhandledCount }}</view>
            </view>
            <view 
                class="tab-item" 
                :class="{ active: currentTab === 'handled' }"
                @click="switchTab('handled')"
            >
                已处理
            </view>
        </view>
        
        <view class="alert-list" v-if="alertList.length > 0">
            <view 
                class="alert-item" 
                v-for="item in alertList" 
                :key="item.id"
                :class="{ handled: item.is_handled === 1 }"
            >
                <view class="alert-header">
                    <view class="alert-type">
                        <view class="type-icon" :class="item.alert_type === '低库存' ? 'low-stock' : 'expiry'"></view>
                        <text class="type-text">{{ item.alert_type }}</text>
                    </view>
                    <text class="alert-time">{{ formatTime(item.created_at) }}</text>
                </view>
                
                <view class="alert-content">
                    <view class="content-row">
                        <text class="content-label">原材料</text>
                        <text class="content-value">{{ item.material_name }}</text>
                    </view>
                    <view class="content-row">
                        <text class="content-label">类型</text>
                        <view class="type-tag" :class="getTypeClass(item.material_type)">
                            {{ item.material_type }}
                        </view>
                    </view>
                    <view class="content-row">
                        <text class="content-label">料仓</text>
                        <text class="content-value">{{ item.warehouse_name }}</text>
                    </view>
                    <view class="content-row highlight">
                        <text class="content-label">当前值</text>
                        <text class="content-value danger">{{ item.current_value }}</text>
                        <text class="content-label"> / 阈值</text>
                        <text class="content-value">{{ item.threshold_value }}</text>
                    </view>
                </view>
                
                <view class="alert-message">
                    <text class="message-text">{{ item.message }}</text>
                </view>
                
                <view class="alert-actions" v-if="item.is_handled !== 1">
                    <button class="action-btn view-detail" @click="viewDetail(item)">
                        查看详情
                    </button>
                    <button class="action-btn create-purchase" @click="goToPurchase(item)">
                        发起采购
                    </button>
                </view>
                
                <view class="handled-tag" v-if="item.is_handled === 1">
                    <text class="handled-text">已处理</text>
                </view>
            </view>
        </view>
        
        <view class="empty-state" v-else-if="!loading">
            <text class="empty-text">暂无预警信息</text>
        </view>
        
        <view class="loading-state" v-if="loading">
            <text>加载中...</text>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            currentTab: 'unhandled',
            alertList: [],
            stats: {
                unhandledCount: 0,
                handledCount: 0
            },
            loading: false
        }
    },
    
    onShow() {
        this.loadData()
    },
    
    methods: {
        async loadData() {
            this.loading = true
            
            try {
                const [unhandledRes, handledRes] = await Promise.all([
                    this.$api.getLowStockAlerts({ is_handled: 0 }),
                    this.$api.getLowStockAlerts({ is_handled: 1 })
                ])
                
                this.stats.unhandledCount = unhandledRes.total || 0
                this.stats.handledCount = handledRes.total || 0
                
                if (this.currentTab === 'unhandled') {
                    this.alertList = unhandledRes.list || []
                } else {
                    this.alertList = handledRes.list || []
                }
                
            } catch (err) {
                console.error('加载预警列表失败:', err)
            } finally {
                this.loading = false
            }
        },
        
        switchTab(tab) {
            this.currentTab = tab
            this.loadData()
        },
        
        getTypeClass(type) {
            const classMap = {
                '水泥': 'cement',
                '砂石': 'sand',
                '粉煤灰': 'flyash',
                '外加剂': 'additive'
            }
            return classMap[type] || ''
        },
        
        formatTime(dateStr) {
            if (!dateStr) return ''
            const date = new Date(dateStr)
            const now = new Date()
            const diff = now - date
            
            if (diff < 60000) return '刚刚'
            if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
            if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
            if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
            
            return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, '0')}`
        },
        
        viewDetail(item) {
            uni.navigateTo({
                url: `/pages/inventory/detail?id=${item.inventory_id}`
            })
        },
        
        goToPurchase(item) {
            uni.navigateTo({
                url: `/pages/purchase/create?alert_id=${item.id}`
            })
        }
    }
}
</script>

<style scoped>
.page-container {
    min-height: 100vh;
    background-color: #f5f5f5;
}

.stats-section {
    display: flex;
    background: #fff;
    padding: 24rpx;
    margin-bottom: 20rpx;
}

.stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-value {
    font-size: 48rpx;
    font-weight: 600;
    color: #333;
}

.stat-label {
    font-size: 24rpx;
    color: #999;
    margin-top: 8rpx;
}

.filter-tabs {
    display: flex;
    background: #fff;
    padding: 0 20rpx;
    margin-bottom: 20rpx;
}

.tab-item {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24rpx 0;
    font-size: 28rpx;
    color: #666;
    position: relative;
}

.tab-item.active {
    color: #1677ff;
    font-weight: 500;
}

.tab-item.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60rpx;
    height: 6rpx;
    background: #1677ff;
    border-radius: 3rpx;
}

.badge {
    background: #ff4d4f;
    color: #fff;
    font-size: 20rpx;
    padding: 2rpx 10rpx;
    border-radius: 16rpx;
    margin-left: 8rpx;
}

.alert-list {
    padding: 0 20rpx;
}

.alert-item {
    background: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.alert-item.handled {
    opacity: 0.7;
}

.alert-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
}

.alert-type {
    display: flex;
    align-items: center;
}

.type-icon {
    width: 12rpx;
    height: 32rpx;
    border-radius: 6rpx;
    margin-right: 12rpx;
}

.type-icon.low-stock {
    background: #ff4d4f;
}

.type-icon.expiry {
    background: #faad14;
}

.type-text {
    font-size: 26rpx;
    color: #333;
    font-weight: 500;
}

.alert-time {
    font-size: 24rpx;
    color: #999;
}

.alert-content {
    background: #fafafa;
    border-radius: 12rpx;
    padding: 20rpx;
    margin-bottom: 16rpx;
}

.content-row {
    display: flex;
    align-items: center;
    margin-bottom: 12rpx;
}

.content-row:last-child {
    margin-bottom: 0;
}

.content-row.highlight {
    background: #fff2f0;
    margin: 16rpx -20rpx -20rpx;
    padding: 16rpx 20rpx;
    border-radius: 0 0 12rpx 12rpx;
}

.content-label {
    font-size: 26rpx;
    color: #999;
    width: 100rpx;
}

.content-value {
    font-size: 26rpx;
    color: #333;
}

.content-value.danger {
    color: #ff4d4f;
    font-weight: 500;
}

.type-tag {
    font-size: 22rpx;
    padding: 4rpx 12rpx;
    border-radius: 6rpx;
}

.type-tag.cement {
    background: #e6f4ff;
    color: #1677ff;
}

.type-tag.sand {
    background: #f6ffed;
    color: #52c41a;
}

.type-tag.flyash {
    background: #fff7e6;
    color: #fa8c16;
}

.type-tag.additive {
    background: #f9f0ff;
    color: #722ed1;
}

.alert-message {
    padding: 16rpx 0;
    border-top: 1rpx solid #f0f0f0;
}

.message-text {
    font-size: 26rpx;
    color: #666;
    line-height: 1.6;
}

.alert-actions {
    display: flex;
    gap: 20rpx;
    margin-top: 20rpx;
    padding-top: 20rpx;
    border-top: 1rpx solid #f0f0f0;
}

.action-btn {
    flex: 1;
    height: 72rpx;
    border-radius: 36rpx;
    border: none;
    font-size: 26rpx;
}

.action-btn::after {
    border: none;
}

.action-btn.view-detail {
    background: #f5f5f5;
    color: #666;
}

.action-btn.create-purchase {
    background: linear-gradient(90deg, #1677ff 0%, #4096ff 100%);
    color: #fff;
}

.handled-tag {
    text-align: center;
    margin-top: 20rpx;
    padding-top: 20rpx;
    border-top: 1rpx solid #f0f0f0;
}

.handled-text {
    font-size: 24rpx;
    color: #52c41a;
}

.empty-state {
    padding: 100rpx 0;
    text-align: center;
}

.empty-text {
    font-size: 28rpx;
    color: #999;
}

.loading-state {
    padding: 60rpx 0;
    text-align: center;
    color: #999;
}
</style>
