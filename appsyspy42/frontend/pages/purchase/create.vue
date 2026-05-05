<template>
    <view class="page-container">
        <view class="form-section">
            <view class="form-item">
                <view class="form-label">
                    <text class="required">*</text>
                    <text>选择原材料</text>
                </view>
                <picker 
                    :value="materialIndex" 
                    :range="materialList" 
                    range-key="material_name" 
                    @change="onMaterialChange"
                >
                    <view class="picker-value">
                        <text v-if="selectedMaterial">{{ selectedMaterial.material_name }}</text>
                        <text v-else class="placeholder">请选择原材料</text>
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </picker>
            </view>
            
            <view class="material-info" v-if="selectedMaterial">
                <view class="info-item">
                    <text class="info-label">类型</text>
                    <view class="type-tag" :class="getTypeClass(selectedMaterial.material_type)">
                        {{ selectedMaterial.material_type }}
                    </view>
                </view>
                <view class="info-item" v-if="selectedMaterial.specification">
                    <text class="info-label">规格</text>
                    <text class="info-value">{{ selectedMaterial.specification }}</text>
                </view>
            </view>
            
            <view class="form-item">
                <view class="form-label">
                    <text class="required">*</text>
                    <text>需求数量</text>
                </view>
                <view class="input-group">
                    <input 
                        type="digit" 
                        placeholder="请输入需求数量" 
                        v-model="formData.quantity"
                        class="quantity-input"
                    />
                    <text class="unit-text">{{ formData.unit }}</text>
                </view>
            </view>
            
            <view class="form-item">
                <view class="form-label">
                    <text>单位</text>
                </view>
                <picker 
                    :value="unitIndex" 
                    :range="unitOptions" 
                    @change="onUnitChange"
                >
                    <view class="picker-value">
                        <text>{{ formData.unit }}</text>
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </picker>
            </view>
            
            <view class="form-item">
                <view class="form-label">
                    <text>预计到货时间</text>
                </view>
                <picker 
                    mode="date" 
                    :value="formData.expected_delivery_date" 
                    :start="startDate"
                    @change="onDateChange"
                >
                    <view class="picker-value">
                        <text v-if="formData.expected_delivery_date">{{ formData.expected_delivery_date }}</text>
                        <text v-else class="placeholder">请选择预计到货时间</text>
                        <text class="uni-icon uni-icon-arrow-right"></text>
                    </view>
                </picker>
            </view>
            
            <view class="form-item textarea-item">
                <view class="form-label">
                    <text>申请原因</text>
                </view>
                <textarea 
                    placeholder="请输入申请原因（如：库存预警、生产计划需求等）"
                    v-model="formData.reason"
                    :maxlength="500"
                    class="textarea-input"
                />
                <view class="word-count">
                    <text>{{ formData.reason ? formData.reason.length : 0 }}/500</text>
                </view>
            </view>
        </view>
        
        <view class="tips-section">
            <view class="tips-title">温馨提示</view>
            <view class="tips-list">
                <view class="tips-item">请准确填写需求数量，系统将按此数量安排采购</view>
                <view class="tips-item">预计到货时间请根据实际生产需求合理安排</view>
                <view class="tips-item">提交后需经管理员审批，审批通过后自动同步至系统</view>
            </view>
        </view>
        
        <view class="footer-btn">
            <button 
                class="submit-btn" 
                :class="{ disabled: !canSubmit }"
                @click="handleSubmit"
                :disabled="!canSubmit"
            >
                提交申请
            </button>
        </view>
    </view>
</template>

<script>
/**
 * 采购申请创建页面
 * 功能：采购员提交新的采购申请
 * 表单字段：原材料选择、需求数量、单位、预计到货时间、申请原因
 */
import config from '@/utils/config.js'

export default {
    data() {
        return {
            materialList: [],
            materialIndex: -1,
            selectedMaterial: null,
            unitOptions: ['吨', '千克', '立方米', '袋', '桶'],
            unitIndex: 0,
            startDate: '',
            formData: {
                material_id: null,
                quantity: '',
                unit: '吨',
                expected_delivery_date: '',
                reason: ''
            },
            submitting: false
        }
    },
    
    onLoad(options) {
        this.initStartDate()
        if (options.alert_id) {
            this.loadFromAlert(options.alert_id)
        }
        this.loadMaterials()
    },
    
    computed: {
        canSubmit() {
            return this.selectedMaterial && 
                   this.formData.quantity && 
                   parseFloat(this.formData.quantity) > 0 &&
                   !this.submitting
        }
    },
    
    methods: {
        initStartDate() {
            const today = new Date()
            const year = today.getFullYear()
            const month = String(today.getMonth() + 1).padStart(2, '0')
            const day = String(today.getDate()).padStart(2, '0')
            this.startDate = `${year}-${month}-${day}`
        },
        
        async loadFromAlert(alertId) {
            try {
                const res = await this.$api.getLowStockAlerts({})
                const alert = res.list?.find(a => a.id === parseInt(alertId))
                if (alert) {
                    this.formData.reason = `库存预警：${alert.material_name} 当前库存为 ${alert.current_value}，低于安全阈值 ${alert.threshold_value}`
                }
            } catch (err) {
                console.error('加载预警信息失败:', err)
            }
        },
        
        async loadMaterials() {
            try {
                const res = await this.$api.getMaterials({ page_size: 100 })
                this.materialList = res.list || []
            } catch (err) {
                console.error('加载原材料列表失败:', err)
                uni.showToast({
                    title: '加载原材料失败',
                    icon: 'none'
                })
            }
        },
        
        onMaterialChange(e) {
            this.materialIndex = e.detail.value
            this.selectedMaterial = this.materialList[this.materialIndex]
            this.formData.material_id = this.selectedMaterial.id
            if (this.selectedMaterial.unit) {
                this.unitIndex = this.unitOptions.indexOf(this.selectedMaterial.unit)
                if (this.unitIndex === -1) {
                    this.unitIndex = 0
                }
                this.formData.unit = this.unitOptions[this.unitIndex]
            }
        },
        
        onUnitChange(e) {
            this.unitIndex = e.detail.value
            this.formData.unit = this.unitOptions[this.unitIndex]
        },
        
        onDateChange(e) {
            this.formData.expected_delivery_date = e.detail.value
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
        
        async handleSubmit() {
            if (!this.canSubmit) return
            
            uni.showModal({
                title: '确认提交',
                content: `确认提交采购申请？\n原材料：${this.selectedMaterial.material_name}\n数量：${this.formData.quantity} ${this.formData.unit}`,
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
                    material_id: this.formData.material_id,
                    quantity: parseFloat(this.formData.quantity),
                    unit: this.formData.unit
                }
                
                if (this.formData.expected_delivery_date) {
                    submitData.expected_delivery_date = this.formData.expected_delivery_date
                }
                
                if (this.formData.reason) {
                    submitData.reason = this.formData.reason
                }
                
                const res = await this.$api.createPurchase(submitData)
                
                uni.showToast({
                    title: '提交成功',
                    icon: 'success'
                })
                
                setTimeout(() => {
                    uni.navigateBack()
                }, 1500)
                
            } catch (err) {
                console.error('提交采购申请失败:', err)
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

.form-section {
    background: #fff;
    margin-top: 20rpx;
}

.form-item {
    display: flex;
    flex-direction: column;
    padding: 24rpx 30rpx;
    border-bottom: 1rpx solid #f0f0f0;
}

.form-label {
    display: flex;
    align-items: center;
    margin-bottom: 16rpx;
}

.required {
    color: #ff4d4f;
    margin-right: 8rpx;
    font-size: 28rpx;
}

.form-label text:last-child {
    font-size: 28rpx;
    color: #333;
}

.picker-value {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 72rpx;
    padding: 0 20rpx;
    background: #fafafa;
    border-radius: 8rpx;
}

.picker-value text {
    font-size: 28rpx;
    color: #333;
}

.picker-value .placeholder {
    color: #999;
}

.picker-value .uni-icon {
    font-size: 28rpx;
    color: #999;
}

.material-info {
    padding: 20rpx 30rpx;
    background: #f6ffed;
    border-bottom: 1rpx solid #f0f0f0;
}

.info-item {
    display: flex;
    align-items: center;
    margin-bottom: 12rpx;
}

.info-item:last-child {
    margin-bottom: 0;
}

.info-label {
    font-size: 26rpx;
    color: #666;
    margin-right: 20rpx;
    min-width: 80rpx;
}

.info-value {
    font-size: 26rpx;
    color: #333;
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

.input-group {
    display: flex;
    align-items: center;
    background: #fafafa;
    border-radius: 8rpx;
    padding: 0 20rpx;
}

.quantity-input {
    flex: 1;
    height: 72rpx;
    font-size: 28rpx;
    color: #333;
}

.unit-text {
    font-size: 28rpx;
    color: #666;
    padding-left: 20rpx;
    border-left: 1rpx solid #e0e0e0;
}

.textarea-item {
    padding-bottom: 30rpx;
}

.textarea-input {
    height: 200rpx;
    padding: 20rpx;
    background: #fafafa;
    border-radius: 8rpx;
    font-size: 28rpx;
    line-height: 1.6;
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
    margin: 30rpx;
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
