<template>
    <view class="page-container">
        <view class="header">
            <view class="user-info">
                <view class="avatar">
                    <text>{{ userInfo.real_name ? userInfo.real_name.charAt(0) : 'U' }}</text>
                </view>
                <view class="info">
                    <text class="name">{{ userInfo.real_name }}</text>
                    <text class="role">{{ userInfo.role }}</text>
                </view>
            </view>
            
            <view class="notification" @click="goToAlerts">
                <text class="uni-icon uni-icon-bell"></text>
                <view v-if="alertsCount > 0" class="badge">{{ alertsCount }}</view>
            </view>
        </view>
        
        <view class="stats-section">
            <view class="stats-card">
                <view class="stat-item" @click="goToInventory">
                    <view class="stat-icon inventory-icon"></view>
                    <view class="stat-content">
                        <text class="stat-value">{{ stats.total_materials || 0 }}</text>
                        <text class="stat-label">原材料种类</text>
                    </view>
                </view>
                
                <view class="stat-item" @click="goToLowStock">
                    <view class="stat-icon warning-icon"></view>
                    <view class="stat-content">
                        <text class="stat-value danger">{{ stats.low_stock_count || 0 }}</text>
                        <text class="stat-label">低库存预警</text>
                    </view>
                </view>
            </view>
            
            <view class="stats-card">
                <view class="stat-item" @click="goToPurchase">
                    <view class="stat-icon purchase-icon"></view>
                    <view class="stat-content">
                        <text class="stat-value">{{ pendingCount || 0 }}</text>
                        <text class="stat-label">待审批申请</text>
                    </view>
                </view>
                
                <view class="stat-item" @click="goToSupplier">
                    <view class="stat-icon supplier-icon"></view>
                    <view class="stat-content">
                        <text class="stat-value">{{ supplierStats.total_suppliers || 0 }}</text>
                        <text class="stat-label">供应商数量</text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="quick-actions">
            <text class="section-title">快捷操作</text>
            
            <view class="action-grid">
                <view class="action-item" @click="goToInventory">
                    <view class="action-icon inventory">
                        <text class="uni-icon uni-icon-list"></text>
                    </view>
                    <text class="action-label">库存查询</text>
                </view>
                
                <view class="action-item" @click="goToCreatePurchase">
                    <view class="action-icon purchase">
                        <text class="uni-icon uni-icon-plus"></text>
                    </view>
                    <text class="action-label">采购申请</text>
                </view>
                
                <view class="action-item" @click="goToSupplier">
                    <view class="action-icon supplier">
                        <text class="uni-icon uni-icon-contact"></text>
                    </view>
                    <text class="action-label">供应商管理</text>
                </view>
                
                <view class="action-item" @click="goToLowStock">
                    <view class="action-icon alert">
                        <text class="uni-icon uni-icon-info"></text>
                    </view>
                    <text class="action-label">库存预警</text>
                </view>
            </view>
        </view>
        
        <view class="low-stock-section" v-if="lowStockAlerts.length > 0">
            <view class="section-header">
                <text class="section-title">低库存预警</text>
                <text class="more" @click="goToLowStock">查看全部 ></text>
            </view>
            
            <view class="alert-list">
                <view class="alert-item" v-for="item in lowStockAlerts" :key="item.id">
                    <view class="alert-icon-mini"></view>
                    <view class="alert-content">
                        <text class="alert-name">{{ item.material_name }}</text>
                        <text class="alert-info">当前: {{ item.current_value }} / 阈值: {{ item.threshold_value }}</text>
                    </view>
                    <view class="alert-tag">低库存</view>
                </view>
            </view>
        </view>
    </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
    data() {
        return {
            userInfo: {},
            stats: {},
            supplierStats: {},
            pendingCount: 0,
            alertsCount: 0,
            lowStockAlerts: []
        }
    },
    
    onShow() {
        this.loadData()
    },
    
    onLoad() {
        this.userInfo = uni.getStorageSync(config.userInfoKey) || {}
    },
    
    methods: {
        async loadData() {
            try {
                const [statsRes, supplierRes, pendingRes, alertsRes] = await Promise.all([
                    this.$api.getInventoryStats(),
                    this.$api.getSupplierStats(),
                    this.$api.getPendingCount(),
                    this.$api.getLowStockAlerts({ is_handled: 0 })
                ])
                
                this.stats = statsRes
                this.supplierStats = supplierRes
                this.pendingCount = pendingRes.count || 0
                this.alertsCount = alertsRes.total || 0
                this.lowStockAlerts = alertsRes.list?.slice(0, 3) || []
                
            } catch (err) {
                console.error('加载数据失败:', err)
            }
        },
        
        goToInventory() {
            uni.switchTab({ url: '/pages/inventory/list' })
        },
        
        goToPurchase() {
            uni.switchTab({ url: '/pages/purchase/list' })
        },
        
        goToSupplier() {
            uni.switchTab({ url: '/pages/supplier/list' })
        },
        
        goToLowStock() {
            uni.navigateTo({ url: '/pages/inventory/alerts' })
        },
        
        goToAlerts() {
            uni.navigateTo({ url: '/pages/inventory/alerts' })
        },
        
        goToCreatePurchase() {
            uni.navigateTo({ url: '/pages/purchase/create' })
        }
    }
}
</script>

<style scoped>
.page-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 40rpx;
}

.header {
    background: linear-gradient(180deg, #1677ff 0%, #4096ff 100%);
    padding: 40rpx 30rpx;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-info {
    display: flex;
    align-items: center;
}

.avatar {
    width: 96rpx;
    height: 96rpx;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
}

.avatar text {
    font-size: 40rpx;
    font-weight: bold;
    color: #fff;
}

.info {
    display: flex;
    flex-direction: column;
}

.name {
    font-size: 32rpx;
    font-weight: 500;
    color: #fff;
    margin-bottom: 8rpx;
}

.role {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.8);
}

.notification {
    position: relative;
    width: 72rpx;
    height: 72rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
}

.notification text {
    font-size: 36rpx;
    color: #fff;
}

.badge {
    position: absolute;
    top: 0;
    right: 0;
    min-width: 32rpx;
    height: 32rpx;
    background: #ff4d4f;
    border-radius: 16rpx;
    font-size: 20rpx;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 8rpx;
}

.stats-section {
    padding: 20rpx;
    margin-top: -30rpx;
}

.stats-card {
    background: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    display: flex;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.stat-item {
    flex: 1;
    display: flex;
    align-items: center;
}

.stat-icon {
    width: 88rpx;
    height: 88rpx;
    border-radius: 16rpx;
    margin-right: 20rpx;
}

.inventory-icon {
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
}

.warning-icon {
    background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
}

.purchase-icon {
    background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
}

.supplier-icon {
    background: linear-gradient(135deg, #faad14 0%, #ffc53d 100%);
}

.stat-content {
    display: flex;
    flex-direction: column;
}

.stat-value {
    font-size: 44rpx;
    font-weight: bold;
    color: #333;
}

.stat-value.danger {
    color: #ff4d4f;
}

.stat-label {
    font-size: 24rpx;
    color: #999;
    margin-top: 8rpx;
}

.quick-actions {
    background: #fff;
    margin: 0 20rpx 20rpx;
    border-radius: 16rpx;
    padding: 24rpx;
}

.section-title {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 24rpx;
}

.action-grid {
    display: flex;
    flex-wrap: wrap;
}

.action-item {
    width: 25%;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16rpx 0;
}

.action-icon {
    width: 96rpx;
    height: 96rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16rpx;
}

.action-icon.inventory {
    background: #e6f4ff;
}

.action-icon.purchase {
    background: #f6ffed;
}

.action-icon.supplier {
    background: #fffbe6;
}

.action-icon.alert {
    background: #fff2f0;
}

.action-icon text {
    font-size: 44rpx;
}

.action-icon.inventory text {
    color: #1677ff;
}

.action-icon.purchase text {
    color: #52c41a;
}

.action-icon.supplier text {
    color: #faad14;
}

.action-icon.alert text {
    color: #ff4d4f;
}

.action-label {
    font-size: 24rpx;
    color: #666;
}

.low-stock-section {
    background: #fff;
    margin: 0 20rpx;
    border-radius: 16rpx;
    padding: 24rpx;
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
}

.more {
    font-size: 26rpx;
    color: #1677ff;
}

.alert-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
}

.alert-item {
    display: flex;
    align-items: center;
    padding: 20rpx;
    background: #fff2f0;
    border-radius: 12rpx;
}

.alert-icon-mini {
    width: 12rpx;
    height: 60rpx;
    background: #ff4d4f;
    border-radius: 6rpx;
    margin-right: 20rpx;
}

.alert-content {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.alert-name {
    font-size: 28rpx;
    color: #333;
    font-weight: 500;
}

.alert-info {
    font-size: 24rpx;
    color: #999;
    margin-top: 8rpx;
}

.alert-tag {
    font-size: 22rpx;
    color: #ff4d4f;
    background: #fff;
    padding: 6rpx 16rpx;
    border-radius: 8rpx;
}
</style>
