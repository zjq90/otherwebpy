<template>
    <view class="page-container">
        <view class="search-section">
            <view class="search-input">
                <text class="uni-icon uni-icon-search"></text>
                <input 
                    type="text" 
                    placeholder="搜索供应商名称、联系人" 
                    v-model="searchKeyword"
                    placeholder-class="placeholder"
                    @confirm="handleSearch"
                />
            </view>
        </view>
        
        <view class="stats-cards" v-if="stats.total_suppliers">
            <view class="stat-card">
                <text class="stat-value">{{ stats.total_suppliers }}</text>
                <text class="stat-label">供应商总数</text>
            </view>
            <view class="stat-card">
                <text class="stat-value">{{ stats.avg_rating || '-' }}</text>
                <text class="stat-label">平均评分</text>
            </view>
            <view class="stat-card">
                <text class="stat-value">{{ stats.active_suppliers || 0 }}</text>
                <text class="stat-label">活跃供应商</text>
            </view>
        </view>
        
        <view class="supplier-list" v-if="supplierList.length > 0">
            <view 
                class="supplier-item" 
                v-for="item in supplierList" 
                :key="item.id"
                @click="goToDetail(item.id)"
            >
                <view class="item-header">
                    <view class="supplier-name-section">
                        <view class="supplier-avatar">
                            <text>{{ item.supplier_name.charAt(0) }}</text>
                        </view>
                        <view class="supplier-info">
                            <text class="supplier-name">{{ item.supplier_name }}</text>
                            <view class="status-badge" :class="{ active: item.is_active === 1 }">
                                {{ item.is_active === 1 ? '合作中' : '已停用' }}
                            </view>
                        </view>
                    </view>
                    <view class="rating-section">
                        <view class="stars">
                            <text 
                                v-for="i in 5" 
                                :key="i" 
                                class="star" 
                                :class="{ filled: i <= Math.round(item.quality_rating) }"
                            >★</text>
                        </view>
                        <text class="rating-score">{{ item.quality_rating.toFixed(1) }}</text>
                    </view>
                </view>
                
                <view class="item-content">
                    <view class="info-row" v-if="item.contact_person">
                        <text class="info-label">联系人</text>
                        <text class="info-value">{{ item.contact_person }}</text>
                    </view>
                    <view class="info-row" v-if="item.phone">
                        <text class="info-label">联系电话</text>
                        <text class="info-value">{{ item.phone }}</text>
                    </view>
                </view>
                
                <view class="item-footer">
                    <view class="footer-item">
                        <text class="footer-label">供货次数</text>
                        <text class="footer-value">{{ item.total_orders || 0 }}次</text>
                    </view>
                    <view class="footer-item">
                        <text class="footer-label">累计金额</text>
                        <text class="footer-value">¥{{ (item.total_amount || 0).toFixed(2) }}</text>
                    </view>
                    <view class="footer-action">
                        <view class="evaluate-btn" @click.stop="goToEvaluate(item)">
                            <text>评价</text>
                        </view>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="empty-state" v-else-if="!loading">
            <view class="empty-icon">
                <text class="uni-icon uni-icon-home"></text>
            </view>
            <text class="empty-text">暂无供应商数据</text>
            <text class="empty-hint" v-if="isAdmin">点击右上角添加新供应商</text>
        </view>
        
        <view class="loading-state" v-if="loading">
            <text>加载中...</text>
        </view>
        
        <view class="load-more" v-if="!loading && hasMore" @click="loadMore">
            <text>加载更多</text>
        </view>
        
        <view class="fab-btn" v-if="isAdmin" @click="goToAdd">
            <text class="uni-icon uni-icon-plus"></text>
        </view>
    </view>
</template>

<script>
/**
 * 供应商列表页面
 * 功能：展示供应商列表，支持搜索、查看详情、评价供应商
 * 管理员可添加新供应商
 */
import config from '@/utils/config.js'

export default {
    data() {
        return {
            searchKeyword: '',
            supplierList: [],
            stats: {
                total_suppliers: 0,
                avg_rating: 0,
                active_suppliers: 0
            },
            isAdmin: false,
            page: 1,
            pageSize: 20,
            loading: false,
            hasMore: true
        }
    },
    
    onShow() {
        const userInfo = uni.getStorageSync(config.userInfoKey)
        this.isAdmin = userInfo?.role === '管理员'
        
        this.page = 1
        this.supplierList = []
        this.loadData()
        this.loadStats()
    },
    
    methods: {
        async loadData() {
            if (this.loading) return
            
            this.loading = true
            
            try {
                const params = {
                    page: this.page,
                    page_size: this.pageSize
                }
                
                if (this.searchKeyword) {
                    params.keyword = this.searchKeyword
                }
                
                const res = await this.$api.getSupplierList(params)
                
                if (res.list && res.list.length > 0) {
                    if (this.page === 1) {
                        this.supplierList = res.list
                    } else {
                        this.supplierList = [...this.supplierList, ...res.list]
                    }
                    this.hasMore = this.page < res.total_pages
                } else {
                    this.hasMore = false
                }
                
            } catch (err) {
                console.error('加载供应商列表失败:', err)
            } finally {
                this.loading = false
            }
        },
        
        async loadStats() {
            try {
                const res = await this.$api.getSupplierStats()
                this.stats.total_suppliers = res.total_suppliers || 0
                this.stats.avg_rating = res.avg_supplier_rating || 0
                this.stats.active_suppliers = this.supplierList.filter(s => s.is_active === 1).length
            } catch (err) {
                console.error('加载统计数据失败:', err)
            }
        },
        
        handleSearch() {
            this.page = 1
            this.supplierList = []
            this.loadData()
        },
        
        loadMore() {
            if (!this.hasMore) return
            this.page++
            this.loadData()
        },
        
        goToDetail(id) {
            uni.navigateTo({
                url: `/pages/supplier/detail?id=${id}`
            })
        },
        
        goToEvaluate(item) {
            uni.navigateTo({
                url: `/pages/supplier/evaluation?supplier_id=${item.id}&supplier_name=${encodeURIComponent(item.supplier_name)}`
            })
        },
        
        goToAdd() {
            uni.showModal({
                title: '添加供应商',
                content: '请在后台管理系统中添加供应商',
                showCancel: false
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

.search-section {
    padding: 20rpx;
    background: #fff;
}

.search-input {
    display: flex;
    align-items: center;
    background: #f5f5f5;
    border-radius: 40rpx;
    padding: 0 24rpx;
    height: 72rpx;
}

.search-input text {
    font-size: 32rpx;
    color: #999;
    margin-right: 16rpx;
}

.search-input input {
    flex: 1;
    font-size: 28rpx;
}

.placeholder {
    color: #999;
}

.stats-cards {
    display: flex;
    padding: 20rpx;
    gap: 16rpx;
    background: #fff;
    margin-bottom: 20rpx;
}

.stat-card {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24rpx 16rpx;
    background: linear-gradient(135deg, #e6f4ff 0%, #bae7ff 100%);
    border-radius: 12rpx;
}

.stat-value {
    font-size: 40rpx;
    font-weight: 600;
    color: #1677ff;
    margin-bottom: 8rpx;
}

.stat-label {
    font-size: 24rpx;
    color: #666;
}

.supplier-list {
    padding: 0 20rpx;
}

.supplier-item {
    background: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.item-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20rpx;
    padding-bottom: 16rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.supplier-name-section {
    display: flex;
    align-items: center;
}

.supplier-avatar {
    width: 80rpx;
    height: 80rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 20rpx;
}

.supplier-avatar text {
    font-size: 36rpx;
    color: #fff;
    font-weight: 500;
}

.supplier-info {
    display: flex;
    flex-direction: column;
}

.supplier-name {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 8rpx;
}

.status-badge {
    font-size: 22rpx;
    padding: 4rpx 16rpx;
    border-radius: 8rpx;
    background: #f5f5f5;
    color: #999;
}

.status-badge.active {
    background: #f6ffed;
    color: #52c41a;
}

.rating-section {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.stars {
    display: flex;
    gap: 4rpx;
}

.star {
    font-size: 28rpx;
    color: #e0e0e0;
}

.star.filled {
    color: #faad14;
}

.rating-score {
    font-size: 24rpx;
    color: #666;
    margin-top: 4rpx;
}

.item-content {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
    margin-bottom: 16rpx;
}

.info-row {
    display: flex;
    justify-content: space-between;
}

.info-label {
    font-size: 26rpx;
    color: #999;
}

.info-value {
    font-size: 26rpx;
    color: #333;
}

.item-footer {
    display: flex;
    align-items: center;
    padding-top: 16rpx;
    border-top: 1rpx solid #f0f0f0;
}

.footer-item {
    flex: 1;
    display: flex;
    flex-direction: column;
}

.footer-label {
    font-size: 22rpx;
    color: #999;
    margin-bottom: 4rpx;
}

.footer-value {
    font-size: 24rpx;
    color: #333;
    font-weight: 500;
}

.footer-action {
    margin-left: 20rpx;
}

.evaluate-btn {
    padding: 12rpx 28rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    border-radius: 28rpx;
}

.evaluate-btn text {
    font-size: 24rpx;
    color: #fff;
}

.empty-state {
    padding: 100rpx 0;
    text-align: center;
}

.empty-icon {
    width: 160rpx;
    height: 160rpx;
    background: #f5f5f5;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24rpx;
}

.empty-icon text {
    font-size: 80rpx;
    color: #d9d9d9;
}

.empty-text {
    font-size: 28rpx;
    color: #999;
    display: block;
    margin-bottom: 12rpx;
}

.empty-hint {
    font-size: 24rpx;
    color: #bfbfbf;
    display: block;
}

.loading-state {
    padding: 60rpx 0;
    text-align: center;
    color: #999;
}

.load-more {
    padding: 30rpx;
    text-align: center;
    color: #1677ff;
    font-size: 28rpx;
}

.fab-btn {
    position: fixed;
    right: 40rpx;
    bottom: 140rpx;
    width: 100rpx;
    height: 100rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4rpx 20rpx rgba(22, 119, 255, 0.4);
    z-index: 100;
}

.fab-btn text {
    font-size: 48rpx;
    color: #fff;
}
</style>
