<template>
    <view class="page-container">
        <view class="supplier-card">
            <view class="supplier-header">
                <view class="supplier-avatar">
                    <text>{{ supplierName ? supplierName.charAt(0) : '供' }}</text>
                </view>
                <view class="supplier-info">
                    <text class="supplier-name">{{ supplierName || '未知供应商' }}</text>
                </view>
            </view>
        </view>
        
        <view class="form-section">
            <view class="section-title">评分评价</view>
            
            <view class="rating-list">
                <view class="rating-item">
                    <view class="rating-label">
                        <text class="required">*</text>
                        <text>质量评分</text>
                    </view>
                    <view class="rating-stars">
                        <text 
                            v-for="i in 5" 
                            :key="i" 
                            class="star" 
                            :class="{ filled: i <= formData.quality_score }"
                            @click="setRating('quality_score', i)"
                        >★</text>
                        <text class="score-display">{{ formData.quality_score }}分</text>
                    </view>
                </view>
                
                <view class="rating-item">
                    <view class="rating-label">
                        <text class="required">*</text>
                        <text>交货及时性</text>
                    </view>
                    <view class="rating-stars">
                        <text 
                            v-for="i in 5" 
                            :key="i" 
                            class="star" 
                            :class="{ filled: i <= formData.delivery_score }"
                            @click="setRating('delivery_score', i)"
                        >★</text>
                        <text class="score-display">{{ formData.delivery_score }}分</text>
                    </view>
                </view>
                
                <view class="rating-item">
                    <view class="rating-label">
                        <text class="required">*</text>
                        <text>价格合理性</text>
                    </view>
                    <view class="rating-stars">
                        <text 
                            v-for="i in 5" 
                            :key="i" 
                            class="star" 
                            :class="{ filled: i <= formData.price_score }"
                            @click="setRating('price_score', i)"
                        >★</text>
                        <text class="score-display">{{ formData.price_score }}分</text>
                    </view>
                </view>
                
                <view class="rating-item">
                    <view class="rating-label">
                        <text class="required">*</text>
                        <text>服务态度</text>
                    </view>
                    <view class="rating-stars">
                        <text 
                            v-for="i in 5" 
                            :key="i" 
                            class="star" 
                            :class="{ filled: i <= formData.service_score }"
                            @click="setRating('service_score', i)"
                        >★</text>
                        <text class="score-display">{{ formData.service_score }}分</text>
                    </view>
                </view>
            </view>
            
            <view class="total-score-section">
                <view class="total-label">综合评分</view>
                <view class="total-score-display">
                    <text class="total-value">{{ totalScore.toFixed(1) }}</text>
                    <text class="total-unit">分</text>
                </view>
            </view>
        </view>
        
        <view class="form-section">
            <view class="section-title">评价内容</view>
            
            <view class="textarea-section">
                <textarea 
                    placeholder="请输入对该供应商的评价内容，帮助其他用户了解供应商情况..."
                    v-model="formData.comment"
                    :maxlength="500"
                    class="textarea-input"
                />
                <view class="word-count">
                    <text>{{ formData.comment ? formData.comment.length : 0 }}/500</text>
                </view>
            </view>
        </view>
        
        <view class="tips-section">
            <view class="tips-title">评价说明</view>
            <view class="tips-list">
                <view class="tips-item">
                    <text class="tips-num">1</text>
                    <text class="tips-text">请根据实际合作体验进行真实、客观的评价</text>
                </view>
                <view class="tips-item">
                    <text class="tips-num">2</text>
                    <text class="tips-text">评分范围为1-5分，分数越高表示满意度越高</text>
                </view>
                <view class="tips-item">
                    <text class="tips-num">3</text>
                    <text class="tips-text">评价内容将作为其他用户采购决策的参考</text>
                </view>
            </view>
        </view>
        
        <view class="footer-btn">
            <button 
                class="submit-btn" 
                :class="{ disabled: !canSubmit || submitting }"
                @click="handleSubmit"
                :disabled="!canSubmit || submitting"
            >
                {{ submitting ? '提交中...' : '提交评价' }}
            </button>
        </view>
    </view>
</template>

<script>
/**
 * 供应商评价页面
 * 功能：用户对供应商进行评分和评价
 * 评分维度：质量、交货及时性、价格合理性、服务态度
 */
export default {
    data() {
        return {
            supplierId: null,
            supplierName: '',
            formData: {
                quality_score: 5,
                delivery_score: 5,
                price_score: 5,
                service_score: 5,
                comment: ''
            },
            submitting: false
        }
    },
    
    onLoad(options) {
        if (options.supplier_id) {
            this.supplierId = parseInt(options.supplier_id)
        }
        if (options.supplier_name) {
            this.supplierName = decodeURIComponent(options.supplier_name)
        }
    },
    
    computed: {
        totalScore() {
            const { quality_score, delivery_score, price_score, service_score } = this.formData
            return (quality_score + delivery_score + price_score + service_score) / 4
        },
        
        canSubmit() {
            return this.supplierId !== null && 
                   this.formData.quality_score >= 1 &&
                   this.formData.delivery_score >= 1 &&
                   this.formData.price_score >= 1 &&
                   this.formData.service_score >= 1
        }
    },
    
    methods: {
        setRating(field, value) {
            this.formData[field] = value
        },
        
        async handleSubmit() {
            if (!this.canSubmit || this.submitting) return
            
            uni.showModal({
                title: '确认提交',
                content: `确认提交对「${this.supplierName}」的评价？\n综合评分：${this.totalScore.toFixed(1)}分`,
                success: async (res) => {
                    if (res.confirm) {
                        await this.doSubmit()
                    }
                }
            })
        },
        
        async doSubmit() {
            this.submitting = true
            
            try {
                const submitData = {
                    supplier_id: this.supplierId,
                    quality_score: this.formData.quality_score,
                    delivery_score: this.formData.delivery_score,
                    price_score: this.formData.price_score,
                    service_score: this.formData.service_score
                }
                
                if (this.formData.comment) {
                    submitData.comment = this.formData.comment
                }
                
                await this.$api.createEvaluation(submitData)
                
                uni.showToast({
                    title: '评价成功',
                    icon: 'success'
                })
                
                setTimeout(() => {
                    uni.navigateBack()
                }, 1500)
                
            } catch (err) {
                console.error('提交评价失败:', err)
                uni.showToast({
                    title: err.message || '提交失败',
                    icon: 'none'
                })
            } finally {
                this.submitting = false
            }
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

.supplier-card {
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    padding: 30rpx;
}

.supplier-header {
    display: flex;
    align-items: center;
}

.supplier-avatar {
    width: 100rpx;
    height: 100rpx;
    background: rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 24rpx;
}

.supplier-avatar text {
    font-size: 44rpx;
    color: #fff;
    font-weight: 500;
}

.supplier-name {
    font-size: 34rpx;
    font-weight: 600;
    color: #fff;
}

.form-section {
    background: #fff;
    margin: 20rpx;
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

.rating-list {
    padding: 0 30rpx;
}

.rating-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24rpx 0;
    border-bottom: 1rpx solid #f0f0f0;
}

.rating-item:last-child {
    border-bottom: none;
}

.rating-label {
    display: flex;
    align-items: center;
}

.required {
    color: #ff4d4f;
    margin-right: 8rpx;
    font-size: 28rpx;
}

.rating-label text:last-child {
    font-size: 28rpx;
    color: #333;
}

.rating-stars {
    display: flex;
    align-items: center;
}

.star {
    font-size: 44rpx;
    color: #e0e0e0;
    margin: 0 4rpx;
}

.star.filled {
    color: #faad14;
}

.score-display {
    font-size: 24rpx;
    color: #999;
    margin-left: 12rpx;
    min-width: 60rpx;
}

.total-score-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 24rpx 30rpx;
    background: #fafafa;
}

.total-label {
    font-size: 28rpx;
    color: #666;
}

.total-score-display {
    display: flex;
    align-items: baseline;
}

.total-value {
    font-size: 48rpx;
    font-weight: 600;
    color: #1677ff;
}

.total-unit {
    font-size: 24rpx;
    color: #999;
    margin-left: 4rpx;
}

.textarea-section {
    padding: 24rpx 30rpx;
}

.textarea-input {
    width: 100%;
    height: 200rpx;
    padding: 20rpx;
    background: #fafafa;
    border-radius: 8rpx;
    font-size: 28rpx;
    line-height: 1.6;
    box-sizing: border-box;
}

.word-count {
    text-align: right;
    margin-top: 12rpx;
}

.word-count text {
    font-size: 24rpx;
    color: #999;
}

.tips-section {
    margin: 20rpx;
    padding: 24rpx;
    background: #fffbe6;
    border-radius: 12rpx;
}

.tips-title {
    font-size: 28rpx;
    color: #faad14;
    font-weight: 500;
    margin-bottom: 16rpx;
}

.tips-list {
    display: flex;
    flex-direction: column;
    gap: 12rpx;
}

.tips-item {
    display: flex;
    align-items: flex-start;
}

.tips-num {
    width: 36rpx;
    height: 36rpx;
    background: #faad14;
    color: #fff;
    font-size: 22rpx;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 12rpx;
    flex-shrink: 0;
}

.tips-text {
    font-size: 24rpx;
    color: #666;
    line-height: 1.6;
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

.submit-btn {
    width: 100%;
    height: 88rpx;
    background: linear-gradient(135deg, #1677ff 0%, #4096ff 100%);
    color: #fff;
    font-size: 32rpx;
    border-radius: 44rpx;
    border: none;
}

.submit-btn::after {
    border: none;
}

.submit-btn.disabled {
    background: #d9d9d9;
    color: #bfbfbf;
}
</style>
