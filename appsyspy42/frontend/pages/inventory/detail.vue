<template>
    <view class="page-container">
        <view class="detail-card" v-if="inventory">
            <view class="card-header">
                <view class="header-left">
                    <text class="material-name">{{ inventory.material_name }}</text>
                    <view class="type-tag" :class="getTypeClass(inventory.material_type)">
                        {{ inventory.material_type }}
                    </view>
                </view>
                <view class="status-badge" v-if="inventory.is_low_stock === 1">
                    <text class="status-text">低库存预警</text>
                </view>
            </view>
            
            <view class="info-section">
                <text class="section-title">基本信息</text>
                <view class="info-list">
                    <view class="info-item">
                        <text class="info-label">料仓位置</text>
                        <text class="info-value">{{ inventory.warehouse_name }}</text>
                    </view>
                    <view class="info-item">
                        <text class="info-label">料仓地址</text>
                        <text class="info-value">{{ inventory.warehouse_location || '-' }}</text>
                    </view>
                    <view class="info-item">
                        <text class="info-label">规格型号</text>
                        <text class="info-value">{{ inventory.specification || '-' }}</text>
                    </view>
                    <view class="info-item">
                        <text class="info-label">计量单位</text>
                        <text class="info-value">{{ inventory.unit }}</text>
                    </view>
                </view>
            </view>
            
            <view class="stock-section">
                <text class="section-title">库存信息</text>
                <view class="stock-cards">
                    <view class="stock-card current">
                        <text class="stock-label">当前库存</text>
                        <text class="stock-value" :class="{ danger: inventory.is_low_stock === 1 }">
                            {{ inventory.quantity }}
                        </text>
                        <text class="stock-unit">{{ inventory.unit }}</text>
                    </view>
                    <view class="stock-card threshold">
                        <text class="stock-label">安全阈值</text>
                        <text class="stock-value">{{ inventory.safety_threshold }}</text>
                        <text class="stock-unit">{{ inventory.unit }}</text>
                    </view>
                </view>
                
                <view class="stock-progress" v-if="inventory.safety_threshold > 0">
                    <view class="progress-bar">
                        <view 
                            class="progress-fill" 
                            :style="{ width: getProgressWidth() + '%' }"
                            :class="{ danger: inventory.is_low_stock === 1 }"
                        ></view>
                    </view>
                    <view class="progress-labels">
                        <text class="progress-label">0</text>
                        <text class="progress-label">{{ inventory.safety_threshold }} (阈值)</text>
                    </view>
                </view>
            </view>
            
            <view class="other-section" v-if="inventory.unit_price || inventory.expiry_date || inventory.batch_number">
                <text class="section-title">其他信息</text>
                <view class="info-list">
                    <view class="info-item" v-if="inventory.unit_price">
                        <text class="info-label">单价</text>
                        <text class="info-value">¥ {{ inventory.unit_price }}</text>
                    </view>
                    <view class="info-item" v-if="inventory.expiry_date">
                        <text class="info-label">保质期</text>
                        <text class="info-value">{{ formatDate(inventory.expiry_date) }}</text>
                    </view>
                    <view class="info-item" v-if="inventory.production_date">
                        <text class="info-label">生产日期</text>
                        <text class="info-value">{{ formatDate(inventory.production_date) }}</text>
                    </view>
                    <view class="info-item" v-if="inventory.batch_number">
                        <text class="info-label">批次号</text>
                        <text class="info-value">{{ inventory.batch_number }}</text>
                    </view>
                    <view class="info-item">
                        <text class="info-label">最后更新</text>
                        <text class="info-value">{{ formatDateTime(inventory.updated_at) }}</text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="empty-state" v-else-if="!loading">
            <text class="empty-text">库存数据不存在</text>
        </view>
        
        <view class="loading-state" v-if="loading">
            <text>加载中...</text>
        </view>
        
        <view class="action-section" v-if="inventory">
            <button 
                class="action-btn primary" 
                @click="createPurchaseRequest"
            >
                发起采购申请
            </button>
        </view>
    </view>
</template>

<script>
export default {
    data() {
        return {
            inventoryId: null,
            inventory: null,
            loading: false
        }
    },
    
    onLoad(options) {
        if (options.id) {
            this.inventoryId = parseInt(options.id)
            this.loadDetail()
        }
    },
    
    methods: {
        async loadDetail() {
            if (!this.inventoryId) return
            
            this.loading = true
            
            try {
                const res = await this.$api.getInventoryDetail(this.inventoryId)
                this.inventory = res
            } catch (err) {
                console.error('加载库存详情失败:', err)
                uni.showToast({
                    title: '加载失败',
                    icon: 'none'
                })
            } finally {
                this.loading = false
            }
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
        
        getProgressWidth() {
            if (!this.inventory) return 0
            const { quantity, safety_threshold } = this.inventory
            if (safety_threshold <= 0) return 0
            const width = (quantity / safety_threshold) * 100
            return Math.min(width, 150)
        },
        
        formatDate(dateStr) {
            if (!dateStr) return '-'
            const date = new Date(dateStr)
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
        },
        
        formatDateTime(dateStr) {
            if (!dateStr) return '-'
            const date = new Date(dateStr)
            return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
        },
        
        createPurchaseRequest() {
            if (!this.inventory) return
            
            uni.navigateTo({
                url: `/pages/purchase/create?material_id=${this.inventory.material_id}&material_name=${encodeURIComponent(this.inventory.material_name)}`
            })
        }
    }
}
</script>

<style scoped>
.page-container {
    min-height: 100vh;
    background-color: #f5f5f5;
    padding-bottom: 140rpx;
}

.detail-card {
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
    margin-bottom: 24rpx;
    padding-bottom: 24rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.header-left {
    display: flex;
    align-items: center;
}

.material-name {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
    margin-right: 16rpx;
}

.type-tag {
    font-size: 24rpx;
    padding: 6rpx 16rpx;
    border-radius: 8rpx;
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

.status-badge {
    background: #fff2f0;
    border: 1rpx solid #ff7875;
    padding: 6rpx 16rpx;
    border-radius: 8rpx;
}

.status-text {
    font-size: 24rpx;
    color: #ff4d4f;
}

.section-title {
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
}

.info-section, .stock-section, .other-section {
    margin-bottom: 24rpx;
    padding-bottom: 24rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.other-section {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.info-list {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.info-label {
    font-size: 28rpx;
    color: #999;
}

.info-value {
    font-size: 28rpx;
    color: #333;
}

.stock-cards {
    display: flex;
    gap: 20rpx;
    margin-bottom: 24rpx;
}

.stock-card {
    flex: 1;
    padding: 24rpx;
    border-radius: 12rpx;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stock-card.current {
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
}

.stock-card.current.danger {
    background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
}

.stock-card.threshold {
    background: #f5f5f5;
}

.stock-label {
    font-size: 24rpx;
    margin-bottom: 12rpx;
}

.stock-card.current .stock-label {
    color: rgba(255, 255, 255, 0.8);
}

.stock-card.threshold .stock-label {
    color: #999;
}

.stock-value {
    font-size: 48rpx;
    font-weight: 600;
}

.stock-card.current .stock-value {
    color: #fff;
}

.stock-card.threshold .stock-value {
    color: #333;
}

.stock-unit {
    font-size: 24rpx;
    margin-top: 8rpx;
}

.stock-card.current .stock-unit {
    color: rgba(255, 255, 255, 0.8);
}

.stock-card.threshold .stock-unit {
    color: #999;
}

.stock-progress {
    padding: 20rpx;
    background: #fafafa;
    border-radius: 12rpx;
}

.progress-bar {
    height: 16rpx;
    background: #e8e8e8;
    border-radius: 8rpx;
    overflow: hidden;
    margin-bottom: 12rpx;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #1677ff 0%, #4096ff 100%);
    border-radius: 8rpx;
    transition: width 0.3s ease;
}

.progress-fill.danger {
    background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
}

.progress-labels {
    display: flex;
    justify-content: space-between;
}

.progress-label {
    font-size: 22rpx;
    color: #999;
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

.action-section {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20rpx;
    background: #fff;
    box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.action-btn {
    width: 100%;
    height: 88rpx;
    border-radius: 44rpx;
    border: none;
    font-size: 32rpx;
    font-weight: 500;
}

.action-btn::after {
    border: none;
}

.action-btn.primary {
    background: linear-gradient(90deg, #1677ff 0%, #4096ff 100%);
    color: #fff;
}
</style>
