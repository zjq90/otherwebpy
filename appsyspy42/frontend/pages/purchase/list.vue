<template>
    <view class="page-container">
        <view class="filter-section">
            <scroll-view scroll-x class="filter-scroll">
                <view class="filter-list">
                    <view 
                        class="filter-item" 
                        :class="{ active: currentStatus === '' }"
                        @click="filterByStatus('')"
                    >
                        全部
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentStatus === '待审批' }"
                        @click="filterByStatus('待审批')"
                    >
                        待审批
                        <view class="badge" v-if="pendingCount > 0">{{ pendingCount }}</view>
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentStatus === '已批准' }"
                        @click="filterByStatus('已批准')"
                    >
                        已批准
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentStatus === '已拒绝' }"
                        @click="filterByStatus('已拒绝')"
                    >
                        已拒绝
                    </view>
                    <view 
                        class="filter-item" 
                        :class="{ active: currentStatus === '已完成' }"
                        @click="filterByStatus('已完成')"
                    >
                        已完成
                    </view>
                </view>
            </scroll-view>
        </view>
        
        <view class="purchase-list" v-if="purchaseList.length > 0">
            <view 
                class="purchase-item" 
                v-for="item in purchaseList" 
                :key="item.id"
                @click="goToDetail(item.id)"
            >
                <view class="item-header">
                    <view class="request-no">
                        <text class="no-label">申请单号</text>
                        <text class="no-value">{{ item.request_no }}</text>
                    </view>
                    <view class="status-tag" :class="getStatusClass(item.status)">
                        {{ item.status }}
                    </view>
                </view>
                
                <view class="item-content">
                    <view class="material-info">
                        <text class="material-name">{{ item.material_name }}</text>
                        <view class="type-tag" :class="getTypeClass(item.material_type)">
                            {{ item.material_type }}
                        </view>
                    </view>
                    
                    <view class="quantity-info">
                        <text class="label">申请数量</text>
                        <text class="value">{{ item.quantity }} {{ item.unit }}</text>
                    </view>
                    
                    <view class="delivery-info" v-if="item.expected_delivery_date">
                        <text class="label">预计到货</text>
                        <text class="value">{{ formatDate(item.expected_delivery_date) }}</text>
                    </view>
                    
                    <view class="applicant-info">
                        <text class="label">申请人</text>
                        <text class="value">{{ item.requester_name }}</text>
                    </view>
                </view>
                
                <view class="item-footer">
                    <text class="create-time">{{ formatDateTime(item.created_at) }}</text>
                    <view class="footer-actions" v-if="item.status === '待审批' && isAdmin">
                        <button class="action-btn reject" @click.stop="handleReject(item)">拒绝</button>
                        <button class="action-btn approve" @click.stop="handleApprove(item)">批准</button>
                    </view>
                    <view class="footer-actions" v-else-if="item.status === '待审批' && !isAdmin">
                        <button class="action-btn cancel" @click.stop="handleCancel(item)">取消申请</button>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="empty-state" v-else-if="!loading">
            <text class="empty-text">暂无采购申请</text>
        </view>
        
        <view class="loading-state" v-if="loading">
            <text>加载中...</text>
        </view>
        
        <view class="load-more" v-if="!loading && hasMore" @click="loadMore">
            <text>加载更多</text>
        </view>
        
        <view class="fab-btn" @click="goToCreate">
            <text class="uni-icon uni-icon-plus"></text>
        </view>
    </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
    data() {
        return {
            currentStatus: '',
            purchaseList: [],
            pendingCount: 0,
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
        this.purchaseList = []
        this.loadData()
        this.loadPendingCount()
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
                
                if (this.currentStatus) {
                    params.status = this.currentStatus
                }
                
                const res = await this.$api.getPurchaseList(params)
                
                if (res.list && res.list.length > 0) {
                    if (this.page === 1) {
                        this.purchaseList = res.list
                    } else {
                        this.purchaseList = [...this.purchaseList, ...res.list]
                    }
                    this.hasMore = this.page < res.total_pages
                } else {
                    this.hasMore = false
                }
                
            } catch (err) {
                console.error('加载采购申请列表失败:', err)
            } finally {
                this.loading = false
            }
        },
        
        async loadPendingCount() {
            try {
                const res = await this.$api.getPendingCount()
                this.pendingCount = res.count || 0
            } catch (err) {
                console.error('获取待审批数量失败:', err)
            }
        },
        
        filterByStatus(status) {
            this.currentStatus = status
            this.page = 1
            this.purchaseList = []
            this.loadData()
        },
        
        loadMore() {
            if (!this.hasMore) return
            this.page++
            this.loadData()
        },
        
        getStatusClass(status) {
            const classMap = {
                '待审批': 'pending',
                '已批准': 'approved',
                '已拒绝': 'rejected',
                '已完成': 'completed'
            }
            return classMap[status] || ''
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
        
        goToDetail(id) {
            uni.navigateTo({
                url: `/pages/purchase/detail?id=${id}`
            })
        },
        
        goToCreate() {
            uni.navigateTo({
                url: '/pages/purchase/create'
            })
        },
        
        async handleApprove(item) {
            uni.showModal({
                title: '确认审批',
                content: `确定要批准申请单号为 ${item.request_no} 的采购申请吗？`,
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            await this.$api.approvePurchase(item.id, {
                                status: '已批准',
                                approval_comment: '同意申请'
                            })
                            
                            uni.showToast({
                                title: '审批成功',
                                icon: 'success'
                            })
                            
                            this.page = 1
                            this.purchaseList = []
                            this.loadData()
                            this.loadPendingCount()
                            
                        } catch (err) {
                            console.error('审批失败:', err)
                        }
                    }
                }
            })
        },
        
        async handleReject(item) {
            uni.showModal({
                title: '确认拒绝',
                content: `确定要拒绝申请单号为 ${item.request_no} 的采购申请吗？`,
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            await this.$api.approvePurchase(item.id, {
                                status: '已拒绝',
                                approval_comment: '申请被拒绝'
                            })
                            
                            uni.showToast({
                                title: '操作成功',
                                icon: 'success'
                            })
                            
                            this.page = 1
                            this.purchaseList = []
                            this.loadData()
                            this.loadPendingCount()
                            
                        } catch (err) {
                            console.error('操作失败:', err)
                        }
                    }
                }
            })
        },
        
        async handleCancel(item) {
            uni.showModal({
                title: '确认取消',
                content: `确定要取消申请单号为 ${item.request_no} 的采购申请吗？`,
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            await this.$api.cancelPurchase(item.id)
                            
                            uni.showToast({
                                title: '取消成功',
                                icon: 'success'
                            })
                            
                            this.page = 1
                            this.purchaseList = []
                            this.loadData()
                            
                        } catch (err) {
                            console.error('取消失败:', err)
                        }
                    }
                }
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

.filter-section {
    background: #fff;
    padding: 20rpx;
}

.filter-scroll {
    white-space: nowrap;
}

.filter-list {
    display: flex;
    gap: 16rpx;
}

.filter-item {
    display: inline-flex;
    align-items: center;
    padding: 12rpx 28rpx;
    background: #f5f5f5;
    border-radius: 32rpx;
    font-size: 26rpx;
    color: #666;
    position: relative;
}

.filter-item.active {
    background: #e6f4ff;
    color: #1677ff;
}

.badge {
    position: absolute;
    top: -8rpx;
    right: -8rpx;
    background: #ff4d4f;
    color: #fff;
    font-size: 18rpx;
    padding: 2rpx 8rpx;
    border-radius: 12rpx;
    min-width: 24rpx;
    text-align: center;
}

.purchase-list {
    padding: 20rpx;
}

.purchase-item {
    background: #fff;
    border-radius: 16rpx;
    padding: 24rpx;
    margin-bottom: 20rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.item-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20rpx;
    padding-bottom: 16rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.request-no {
    display: flex;
    align-items: baseline;
}

.no-label {
    font-size: 24rpx;
    color: #999;
    margin-right: 12rpx;
}

.no-value {
    font-size: 28rpx;
    color: #333;
    font-weight: 500;
}

.status-tag {
    font-size: 24rpx;
    padding: 6rpx 16rpx;
    border-radius: 8rpx;
}

.status-tag.pending {
    background: #fffbe6;
    color: #faad14;
}

.status-tag.approved {
    background: #f6ffed;
    color: #52c41a;
}

.status-tag.rejected {
    background: #fff2f0;
    color: #ff4d4f;
}

.status-tag.completed {
    background: #e6f4ff;
    color: #1677ff;
}

.item-content {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
}

.material-info {
    display: flex;
    align-items: center;
}

.material-name {
    font-size: 32rpx;
    font-weight: 600;
    color: #333;
    margin-right: 16rpx;
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

.quantity-info, .delivery-info, .applicant-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.label {
    font-size: 26rpx;
    color: #999;
}

.value {
    font-size: 26rpx;
    color: #333;
}

.item-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 20rpx;
    padding-top: 16rpx;
    border-top: 1rpx solid #f0f0f0;
}

.create-time {
    font-size: 24rpx;
    color: #999;
}

.footer-actions {
    display: flex;
    gap: 16rpx;
}

.action-btn {
    height: 56rpx;
    padding: 0 24rpx;
    border-radius: 28rpx;
    border: none;
    font-size: 24rpx;
}

.action-btn::after {
    border: none;
}

.action-btn.approve {
    background: #52c41a;
    color: #fff;
}

.action-btn.reject {
    background: #ff4d4f;
    color: #fff;
}

.action-btn.cancel {
    background: #f5f5f5;
    color: #666;
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
