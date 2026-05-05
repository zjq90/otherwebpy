<template>
    <view class="page-container">
        <view class="supplier-header" v-if="supplier">
            <view class="supplier-avatar">
                <text>{{ supplier.supplier_name.charAt(0) }}</text>
            </view>
            <view class="supplier-info">
                <view class="name-row">
                    <text class="supplier-name">{{ supplier.supplier_name }}</text>
                    <view class="status-badge" :class="{ active: supplier.is_active === 1 }">
                        {{ supplier.is_active === 1 ? '合作中' : '已停用' }}
                    </view>
                </view>
                <view class="rating-row">
                    <view class="stars">
                        <text 
                            v-for="i in 5" 
                            :key="i" 
                            class="star" 
                            :class="{ filled: i <= Math.round(supplier.quality_rating) }"
                        >★</text>
                    </view>
                    <text class="rating-score">{{ supplier.quality_rating.toFixed(1) }} 分</text>
                </view>
            </view>
        </view>
        
        <view class="stats-section" v-if="supplier">
            <view class="stat-item">
                <text class="stat-value">{{ supplier.total_orders || 0 }}</text>
                <text class="stat-label">供货次数</text>
            </view>
            <view class="stat-divider"></view>
            <view class="stat-item">
                <text class="stat-value">¥{{ (supplier.total_amount || 0).toFixed(2) }}</text>
                <text class="stat-label">累计金额</text>
            </view>
        </view>
        
        <view class="info-section">
            <view class="section-title">基本信息</view>
            <view class="info-list">
                <view class="info-item" v-if="supplier.contact_person">
                    <text class="info-label">联系人</text>
                    <text class="info-value">{{ supplier.contact_person }}</text>
                </view>
                <view class="info-item" v-if="supplier.phone">
                    <text class="info-label">联系电话</text>
                    <text class="info-value" @click="callPhone(supplier.phone)">{{ supplier.phone }}</text>
                </view>
                <view class="info-item" v-if="supplier.address">
                    <text class="info-label">地址</text>
                    <text class="info-value text-multi">{{ supplier.address }}</text>
                </view>
                <view class="info-item" v-if="supplier.business_license">
                    <text class="info-label">营业执照</text>
                    <text class="info-value">{{ supplier.business_license }}</text>
                </view>
                <view class="info-item" v-if="supplier.description">
                    <text class="info-label">供应商简介</text>
                    <text class="info-value text-multi">{{ supplier.description }}</text>
                </view>
            </view>
        </view>
        
        <view class="tab-section">
            <view class="tab-list">
                <view 
                    class="tab-item" 
                    :class="{ active: activeTab === 'supply' }"
                    @click="switchTab('supply')"
                >
                    供货记录
                    <view class="tab-badge" v-if="supplyRecords.length > 0">{{ supplyRecords.length }}</view>
                </view>
                <view 
                    class="tab-item" 
                    :class="{ active: activeTab === 'evaluation' }"
                    @click="switchTab('evaluation')"
                >
                    历史评价
                    <view class="tab-badge" v-if="evaluations.length > 0">{{ evaluations.length }}</view>
                </view>
            </view>
        </view>
        
        <view class="tab-content" v-if="activeTab === 'supply'">
            <view class="supply-list" v-if="supplyRecords.length > 0">
                <view class="supply-item" v-for="item in supplyRecords" :key="item.id">
                    <view class="supply-header">
                        <text class="material-name">{{ item.material_name }}</text>
                        <view class="quality-tag" :class="item.quality_status === '合格' ? 'pass' : 'fail'">
                            {{ item.quality_status }}
                        </view>
                    </view>
                    <view class="supply-content">
                        <view class="supply-row">
                            <text class="label">供货数量</text>
                            <text class="value">{{ item.quantity }} {{ item.unit }}</text>
                        </view>
                        <view class="supply-row">
                            <text class="label">单价</text>
                            <text class="value">¥{{ item.unit_price.toFixed(2) }}</text>
                        </view>
                        <view class="supply-row">
                            <text class="label">总金额</text>
                            <text class="value highlight">¥{{ item.total_amount.toFixed(2) }}</text>
                        </view>
                        <view class="supply-row" v-if="item.delivery_date">
                            <text class="label">送货日期</text>
                            <text class="value">{{ formatDate(item.delivery_date) }}</text>
                        </view>
                        <view class="supply-row" v-if="item.batch_number">
                            <text class="label">批次号</text>
                            <text class="value">{{ item.batch_number }}</text>
                        </view>
                    </view>
                    <view class="supply-footer" v-if="item.remark">
                        <text class="remark-label">备注：</text>
                        <text class="remark-text">{{ item.remark }}</text>
                    </view>
                </view>
            </view>
            <view class="empty-state" v-else>
                <text class="empty-text">暂无供货记录</text>
            </view>
        </view>
        
        <view class="tab-content" v-if="activeTab === 'evaluation'">
            <view class="evaluation-list" v-if="evaluations.length > 0">
                <view class="evaluation-item" v-for="item in evaluations" :key="item.id">
                    <view class="evaluation-header">
                        <view class="evaluator-info">
                            <view class="evaluator-avatar">
                                <text>{{ item.evaluator_name.charAt(0) }}</text>
                            </view>
                            <view class="evaluator-detail">
                                <text class="evaluator-name">{{ item.evaluator_name }}</text>
                                <text class="evaluation-date">{{ formatDateTime(item.evaluation_date) }}</text>
                            </view>
                        </view>
                        <view class="total-score">
                            <text class="score-value">{{ item.total_score.toFixed(1) }}</text>
                            <text class="score-unit">分</text>
                        </view>
                    </view>
                    
                    <view class="score-detail">
                        <view class="score-item">
                            <text class="score-label">质量</text>
                            <view class="stars-small">
                                <text 
                                    v-for="i in 5" 
                                    :key="i" 
                                    class="star-small" 
                                    :class="{ filled: i <= Math.round(item.quality_score) }"
                                >★</text>
                            </view>
                        </view>
                        <view class="score-item">
                            <text class="score-label">交货</text>
                            <view class="stars-small">
                                <text 
                                    v-for="i in 5" 
                                    :key="i" 
                                    class="star-small" 
                                    :class="{ filled: i <= Math.round(item.delivery_score) }"
                                >★</text>
                            </view>
                        </view>
                        <view class="score-item">
                            <text class="score-label">价格</text>
                            <view class="stars-small">
                                <text 
                                    v-for="i in 5" 
                                    :key="i" 
                                    class="star-small" 
                                    :class="{ filled: i <= Math.round(item.price_score) }"
                                >★</text>
                            </view>
                        </view>
                        <view class="score-item">
                            <text class="score-label">服务</text>
                            <view class="stars-small">
                                <text 
                                    v-for="i in 5" 
                                    :key="i" 
                                    class="star-small" 
                                    :class="{ filled: i <= Math.round(item.service_score) }"
                                >★</text>
                            </view>
                        </view>
                    </view>
                    
                    <view class="evaluation-comment" v-if="item.comment">
                        <text class="comment-text">{{ item.comment }}</text>
                    </view>
                </view>
            </view>
            <view class="empty-state" v-else>
                <text class="empty-text">暂无评价记录</text>
            </view>
        </view>
        
        <view class="footer-btn" v-if="supplier && supplier.is_active === 1">
            <button class="evaluate-btn" @click="goToEvaluate">
                <text>评价供应商</text>
            </button>
        </view>
    </view>
</template>

<script>
/**
 * 供应商详情页面
 * 功能：展示供应商详细信息，包括基本信息、供货记录、历史评价
 */
export default {
    data() {
        return {
            supplierId: null,
            supplier: null,
            activeTab: 'supply',
            supplyRecords: [],
            evaluations: [],
            loading: false
        }
    },
    
    onLoad(options) {
        if (options.id) {
            this.supplierId = parseInt(options.id)
            this.loadData()
        }
    },
    
    methods: {
        async loadData() {
            if (!this.supplierId) return
            
            this.loading = true
            
            try {
                const [supplierRes, supplyRes, evalRes] = await Promise.all([
                    this.$api.getSupplierDetail(this.supplierId),
                    this.$api.getSupplyRecords({ supplier_id: this.supplierId, page_size: 100 }),
                    this.$api.getEvaluations({ supplier_id: this.supplierId, page_size: 100 })
                ])
                
                this.supplier = supplierRes
                this.supplyRecords = supplyRes.list || []
                this.evaluations = evalRes.list || []
                
            } catch (err) {
                console.error('加载供应商详情失败:', err)
                uni.showToast({
                    title: '加载失败',
                    icon: 'none'
                })
            } finally {
                this.loading = false
            }
        },
        
        switchTab(tab) {
            this.activeTab = tab
        },
        
        callPhone(phone) {
            uni.makePhoneCall({
                phoneNumber: phone
            })
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
        
        goToEvaluate() {
            if (!this.supplier) return
            uni.navigateTo({
                url: `/pages/supplier/evaluation?supplier_id=${this.supplierId}&supplier_name=${encodeURIComponent(this.supplier.supplier_name)}`
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

.supplier-header {
    display: flex;
    align-items: center;
    padding: 30rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
}

.supplier-avatar {
    width: 120rpx;
    height: 120rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
}

.supplier-avatar text {
    font-size: 48rpx;
    color: #fff;
    font-weight: 500;
}

.supplier-info {
    flex: 1;
}

.name-row {
    display: flex;
    align-items: center;
    margin-bottom: 12rpx;
}

.supplier-name {
    font-size: 36rpx;
    font-weight: 600;
    color: #fff;
    margin-right: 16rpx;
}

.status-badge {
    font-size: 22rpx;
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
    background: rgba(255, 255, 255, 0.2);
    color: rgba(255, 255, 255, 0.8);
}

.status-badge.active {
    background: rgba(82, 196, 26, 0.2);
    color: #95de64;
}

.rating-row {
    display: flex;
    align-items: center;
}

.stars {
    display: flex;
    gap: 4rpx;
    margin-right: 12rpx;
}

.star {
    font-size: 28rpx;
    color: rgba(255, 255, 255, 0.4);
}

.star.filled {
    color: #faad14;
}

.rating-score {
    font-size: 24rpx;
    color: rgba(255, 255, 255, 0.9);
}

.stats-section {
    display: flex;
    background: #fff;
    margin: 20rpx;
    border-radius: 16rpx;
    padding: 24rpx 0;
}

.stat-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-divider {
    width: 1rpx;
    background: #f0f0f0;
}

.stat-value {
    font-size: 36rpx;
    font-weight: 600;
    color: #1677ff;
    margin-bottom: 8rpx;
}

.stat-label {
    font-size: 24rpx;
    color: #999;
}

.info-section {
    background: #fff;
    margin: 0 20rpx 20rpx;
    border-radius: 16rpx;
    overflow: hidden;
}

.section-title {
    font-size: 28rpx;
    font-weight: 600;
    color: #333;
    padding: 24rpx 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.info-list {
    padding: 0 30rpx;
}

.info-item {
    display: flex;
    padding: 20rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
}

.info-item:last-child {
    border-bottom: none;
}

.info-label {
    width: 160rpx;
    font-size: 26rpx;
    color: #999;
    flex-shrink: 0;
}

.info-value {
    flex: 1;
    font-size: 26rpx;
    color: #333;
    text-align: right;
}

.info-value.text-multi {
    text-align: left;
    line-height: 1.6;
}

.tab-section {
    background: #fff;
    margin: 0 20rpx 20rpx;
    border-radius: 16rpx;
    overflow: hidden;
}

.tab-list {
    display: flex;
    padding: 0 20rpx;
}

.tab-item {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
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
    width: 48rpx;
    height: 6rpx;
    background: #1677ff;
    border-radius: 3rpx;
}

.tab-badge {
    font-size: 20rpx;
    background: #ff4d4f;
    color: #fff;
    padding: 0 10rpx;
    border-radius: 16rpx;
    margin-left: 8rpx;
}

.tab-content {
    margin: 0 20rpx;
}

.supply-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
}

.supply-item {
    background: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
}

.supply-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16rpx;
    padding-bottom: 16rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.material-name {
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
}

.quality-tag {
    font-size: 22rpx;
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
}

.quality-tag.pass {
    background: #f6ffed;
    color: #52c41a;
}

.quality-tag.fail {
    background: #fff2f0;
    color: #ff4d4f;
}

.supply-content {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
}

.supply-row {
    display: flex;
    justify-content: space-between;
}

.supply-row .label {
    font-size: 26rpx;
    color: #999;
}

.supply-row .value {
    font-size: 26rpx;
    color: #333;
}

.supply-row .value.highlight {
    color: #ff4d4f;
    font-weight: 500;
}

.supply-footer {
    margin-top: 16rpx;
    padding-top: 16rpx;
    border-top: 1rpx solid #f0f0f0;
}

.remark-label {
    font-size: 24rpx;
    color: #999;
}

.remark-text {
    font-size: 24rpx;
    color: #666;
}

.evaluation-list {
    display: flex;
    flex-direction: column;
    gap: 20rpx;
}

.evaluation-item {
    background: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
}

.evaluation-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16rpx;
}

.evaluator-info {
    display: flex;
    align-items: center;
}

.evaluator-avatar {
    width: 64rpx;
    height: 64rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16rpx;
}

.evaluator-avatar text {
    font-size: 28rpx;
    color: #fff;
}

.evaluator-detail {
    display: flex;
    flex-direction: column;
}

.evaluator-name {
    font-size: 28rpx;
    font-weight: 500;
    color: #333;
    margin-bottom: 4rpx;
}

.evaluation-date {
    font-size: 22rpx;
    color: #999;
}

.total-score {
    display: flex;
    align-items: baseline;
}

.score-value {
    font-size: 40rpx;
    font-weight: 600;
    color: #1677ff;
}

.score-unit {
    font-size: 22rpx;
    color: #999;
}

.score-detail {
    display: flex;
    justify-content: space-between;
    padding: 16rpx 0;
    background: #fafafa;
    border-radius: 8rpx;
    margin-bottom: 16rpx;
}

.score-item {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.score-label {
    font-size: 22rpx;
    color: #999;
    margin-bottom: 4rpx;
}

.stars-small {
    display: flex;
    gap: 2rpx;
}

.star-small {
    font-size: 22rpx;
    color: #e0e0e0;
}

.star-small.filled {
    color: #faad14;
}

.evaluation-comment {
    padding-top: 16rpx;
    border-top: 1rpx solid #f0f0f0;
}

.comment-text {
    font-size: 26rpx;
    color: #666;
    line-height: 1.6;
}

.empty-state {
    padding: 80rpx 0;
    text-align: center;
}

.empty-text {
    font-size: 28rpx;
    color: #999;
}

.footer-btn {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 20rpx 30rpx;
    background: #fff;
    box-shadow: 0 -2rpx 10rpx rgba(0, 0, 0, 0.05);
    padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
}

.evaluate-btn {
    width: 100%;
    height: 88rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    color: #fff;
    font-size: 32rpx;
    border-radius: 44rpx;
    border: none;
}

.evaluate-btn::after {
    border: none;
}
</style>
