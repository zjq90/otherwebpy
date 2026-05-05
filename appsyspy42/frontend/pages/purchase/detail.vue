<template>
    <view class="page-container">
        <view class="detail-card" v-if="purchase">
            <view class="card-header">
                <view class="header-left">
                    <text class="request-no">{{ purchase.request_no }}</text>
                    <view class="status-tag" :class="getStatusClass(purchase.status)">
                        {{ purchase.status }}
                    </view>
                </view>
            </view>
            
            <view class="info-section">
                <text class="section-title">采购信息</text>
                <view class="info-list">
                    <view class="info-item">
                        <text class="info-label">原材料</text>
                        <view class="info-value">
                            <text class="name">{{ purchase.material_name }}</text>
                            <view class="type-tag" :class="getTypeClass(purchase.material_type)">
                                {{ purchase.material_type }}
                            </view>
                        </view>
                    </view>
                    <view class="info-item">
                        <text class="info-label">申请数量</text>
                        <text class="info-value text">{{ purchase.quantity }} {{ purchase.unit }}</text>
                    </view>
                    <view class="info-item" v-if="purchase.expected_delivery_date">
                        <text class="info-label">预计到货</text>
                        <text class="info-value text">{{ formatDate(purchase.expected_delivery_date) }}</text>
                    </view>
                    <view class="info-item" v-if="purchase.reason">
                        <text class="info-label">申请原因</text>
                        <text class="info-value text reason">{{ purchase.reason }}</text>
                    </view>
                </view>
            </view>
            
            <view class="info-section">
                <text class="section-title">申请人信息</text>
                <view class="info-list">
                    <view class="info-item">
                        <text class="info-label">申请人</text>
                        <text class="info-value text">{{ purchase.requester_name }}</text>
                    </view>
                    <view class="info-item">
                        <text class="info-label">申请时间</text>
                        <text class="info-value text">{{ formatDateTime(purchase.created_at) }}</text>
                    </view>
                </view>
            </view>
            
            <view class="info-section" v-if="purchase.status !== '待审批'">
                <text class="section-title">审批信息</text>
                <view class="info-list">
                    <view class="info-item" v-if="purchase.approver_name">
                        <text class="info-label">审批人</text>
                        <text class="info-value text">{{ purchase.approver_name }}</text>
                    </view>
                    <view class="info-item" v-if="purchase.approval_time">
                        <text class="info-label">审批时间</text>
                        <text class="info-value text">{{ formatDateTime(purchase.approval_time) }}</text>
                    </view>
                    <view class="info-item" v-if="purchase.approval_comment">
                        <text class="info-label">审批意见</text>
                        <text class="info-value text">{{ purchase.approval_comment }}</text>
                    </view>
                </view>
            </view>
        </view>
        
        <view class="empty-state" v-else-if="!loading">
            <text class="empty-text">采购申请不存在</text>
        </view>
        
        <view class="loading-state" v-if="loading">
            <text>加载中...</text>
        </view>
        
        <view class="action-section" v-if="purchase">
            <view class="action-buttons" v-if="purchase.status === '待审批' && isAdmin">
                <button class="action-btn reject" @click="handleReject">拒绝</button>
                <button class="action-btn approve" @click="handleApprove">批准</button>
            </view>
            <view class="action-buttons" v-else-if="purchase.status === '待审批' && !isAdmin">
                <button class="action-btn cancel" @click="handleCancel">取消申请</button>
            </view>
            <view class="action-buttons" v-else-if="purchase.status === '已批准' && isAdmin">
                <button class="action-btn complete" @click="handleComplete">标记完成</button>
            </view>
        </view>
    </view>
</template>

<script>
import config from '@/utils/config.js'

export default {
    data() {
        return {
            purchaseId: null,
            purchase: null,
            isAdmin: false,
            loading: false
        }
    },
    
    onLoad(options) {
        const userInfo = uni.getStorageSync(config.userInfoKey)
        this.isAdmin = userInfo?.role === '管理员'
        
        if (options.id) {
            this.purchaseId = parseInt(options.id)
            this.loadDetail()
        }
    },
    
    methods: {
        async loadDetail() {
            if (!this.purchaseId) return
            
            this.loading = true
            
            try {
                const res = await this.$api.getPurchaseDetail(this.purchaseId)
                this.purchase = res
            } catch (err) {
                console.error('加载采购详情失败:', err)
                uni.showToast({
                    title: '加载失败',
                    icon: 'none'
                })
            } finally {
                this.loading = false
            }
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
        
        async handleApprove() {
            uni.showModal({
                title: '确认审批',
                content: '确定要批准此采购申请吗？',
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            await this.$api.approvePurchase(this.purchaseId, {
                                status: '已批准',
                                approval_comment: '同意申请'
                            })
                            
                            uni.showToast({
                                title: '审批成功',
                                icon: 'success'
                            })
                            
                            setTimeout(() => {
                                uni.navigateBack()
                            }, 1000)
                            
                        } catch (err) {
                            console.error('审批失败:', err)
                        }
                    }
                }
            })
        },
        
        async handleReject() {
            uni.showModal({
                title: '确认拒绝',
                content: '确定要拒绝此采购申请吗？',
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            await this.$api.approvePurchase(this.purchaseId, {
                                status: '已拒绝',
                                approval_comment: '申请被拒绝'
                            })
                            
                            uni.showToast({
                                title: '操作成功',
                                icon: 'success'
                            })
                            
                            setTimeout(() => {
                                uni.navigateBack()
                            }, 1000)
                            
                        } catch (err) {
                            console.error('操作失败:', err)
                        }
                    }
                }
            })
        },
        
        async handleCancel() {
            uni.showModal({
                title: '确认取消',
                content: '确定要取消此采购申请吗？',
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            await this.$api.cancelPurchase(this.purchaseId)
                            
                            uni.showToast({
                                title: '取消成功',
                                icon: 'success'
                            })
                            
                            setTimeout(() => {
                                uni.navigateBack()
                            }, 1000)
                            
                        } catch (err) {
                            console.error('取消失败:', err)
                        }
                    }
                }
            })
        },
        
        async handleComplete() {
            uni.showModal({
                title: '确认完成',
                content: '确定要标记此采购申请为已完成吗？',
                success: async (res) => {
                    if (res.confirm) {
                        try {
                            await this.$api.approvePurchase(this.purchaseId, {
                                status: '已完成',
                                approval_comment: '采购已完成'
                            })
                            
                            uni.showToast({
                                title: '操作成功',
                                icon: 'success'
                            })
                            
                            setTimeout(() => {
                                uni.navigateBack()
                            }, 1000)
                            
                        } catch (err) {
                            console.error('操作失败:', err)
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

.detail-card {
    background: #fff;
    margin: 20rpx;
    border-radius: 16rpx;
    padding: 24rpx;
    box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
    padding-bottom: 20rpx;
    margin-bottom: 20rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.header-left {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.request-no {
    font-size: 36rpx;
    font-weight: 600;
    color: #333;
}

.status-tag {
    font-size: 26rpx;
    padding: 8rpx 20rpx;
    border-radius: 12rpx;
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

.info-section {
    margin-bottom: 24rpx;
    padding-bottom: 24rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.info-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
}

.section-title {
    font-size: 30rpx;
    font-weight: 600;
    color: #333;
    margin-bottom: 20rpx;
}

.info-list {
    display: flex;
    flex-direction: column;
    gap: 16rpx;
}

.info-item {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.info-label {
    font-size: 28rpx;
    color: #999;
    min-width: 160rpx;
}

.info-value {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: flex-end;
}

.info-value.text {
    font-size: 28rpx;
    color: #333;
}

.info-value.text.reason {
    text-align: right;
    line-height: 1.6;
}

.info-value .name {
    font-size: 28rpx;
    color: #333;
    margin-right: 12rpx;
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

.action-buttons {
    display: flex;
    gap: 20rpx;
}

.action-btn {
    flex: 1;
    height: 88rpx;
    border-radius: 44rpx;
    border: none;
    font-size: 30rpx;
    font-weight: 500;
}

.action-btn::after {
    border: none;
}

.action-btn.approve {
    background: linear-gradient(90deg, #52c41a 0%, #73d13d 100%);
    color: #fff;
}

.action-btn.reject {
    background: linear-gradient(90deg, #ff4d4f 0%, #ff7875 100%);
    color: #fff;
}

.action-btn.cancel {
    background: #f5f5f5;
    color: #666;
}

.action-btn.complete {
    background: linear-gradient(90deg, #1677ff 0%, #4096ff 100%);
    color: #fff;
}
</style>
