<template>
  <view class="add-container">
    <view class="header-section">
      <text class="page-title">新建目标</text>
    </view>
    
    <scroll-view class="form-scroll" scroll-y>
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">目标类型</text>
          <view class="type-options">
            <view 
              class="type-option" 
              :class="{ active: formData.goal_type === item.value }"
              v-for="(item, index) in goalTypes" 
              :key="index"
              @click="selectType(item.value)"
            >
              <text class="type-icon">{{ item.icon }}</text>
              <text class="type-text">{{ item.label }}</text>
            </view>
          </view>
        </view>
        
        <view class="form-item">
          <text class="form-label">目标名称</text>
          <input 
            class="form-input" 
            type="text" 
            placeholder="请输入目标名称" 
            v-model="formData.goal_name"
            placeholder-class="placeholder-text"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">目标描述</text>
          <textarea 
            class="form-textarea" 
            placeholder="描述一下您的目标（可选）" 
            v-model="formData.description"
            placeholder-class="placeholder-text"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">目标数值</text>
          <view class="value-input-row">
            <input 
              class="form-small-input" 
              type="digit" 
              placeholder="当前值" 
              v-model="formData.current_value"
              placeholder-class="placeholder-text"
            />
            <text class="value-arrow">→</text>
            <input 
              class="form-small-input" 
              type="digit" 
              placeholder="目标值" 
              v-model="formData.target_value"
              placeholder-class="placeholder-text"
            />
          </view>
        </view>
        
        <view class="form-item">
          <text class="form-label">单位</text>
          <input 
            class="form-input" 
            type="text" 
            placeholder="例如：kg、%、次等" 
            v-model="formData.unit"
            placeholder-class="placeholder-text"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">开始日期</text>
          <picker 
            mode="date" 
            :value="formData.start_date" 
            @change="(e) => formData.start_date = e.detail.value"
          >
            <view class="picker-value">
              <text :class="formData.start_date ? '' : 'placeholder-text'">
                {{ formData.start_date || '请选择开始日期' }}
              </text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="form-label">结束日期</text>
          <picker 
            mode="date" 
            :value="formData.end_date" 
            @change="(e) => formData.end_date = e.detail.value"
          >
            <view class="picker-value">
              <text :class="formData.end_date ? '' : 'placeholder-text'">
                {{ formData.end_date || '请选择结束日期' }}
              </text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>
      </view>
      
      <view class="recommend-section" v-if="formData.goal_type">
        <view class="section-header">
          <text class="section-title">推荐方案</text>
          <view class="generate-btn" @click="generateRecommendation">
            <text class="generate-icon">✨</text>
            <text class="generate-text">生成推荐</text>
          </view>
        </view>
        
        <view class="recommend-card" v-if="recommendation">
          <view class="recommend-plan" v-if="recommendation.training_plan">
            <text class="recommend-label">训练计划</text>
            <text class="recommend-text">{{ recommendation.training_plan }}</text>
          </view>
          <view class="recommend-plan" v-if="recommendation.diet_advice">
            <text class="recommend-label">饮食建议</text>
            <text class="recommend-text">{{ recommendation.diet_advice }}</text>
          </view>
        </view>
        
        <view class="empty-recommend" v-else>
          <text class="empty-text">选择目标类型后点击"生成推荐"获取个性化方案</text>
        </view>
      </view>
      
      <view class="bottom-space"></view>
    </scroll-view>
    
    <view class="btn-section">
      <button 
        class="submit-btn btn-primary" 
        :disabled="loading"
        @click="handleSubmit"
      >
        {{ loading ? '创建中...' : '创建目标' }}
      </button>
    </view>
  </view>
</template>

<script>
import api from '@/utils/api.js'

export default {
  data() {
    return {
      userInfo: {},
      goalTypes: [
        { label: '减脂', value: 'lose_weight', icon: '🔥' },
        { label: '增肌', value: 'gain_muscle', icon: '💪' },
        { label: '塑形', value: 'shape', icon: '🏃' },
        { label: '耐力', value: 'endurance', icon: '🧘' }
      ],
      formData: {
        goal_type: '',
        goal_name: '',
        description: '',
        current_value: '',
        target_value: '',
        unit: '',
        start_date: '',
        end_date: ''
      },
      recommendation: null,
      loading: false
    }
  },
  onLoad() {
    this.initForm()
  },
  methods: {
    initForm() {
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0')
      const day = today.getDate().toString().padStart(2, '0')
      this.formData.start_date = `${year}-${month}-${day}`
      
      const endDate = new Date(today)
      endDate.setMonth(endDate.getMonth() + 3)
      const endYear = endDate.getFullYear()
      const endMonth = (endDate.getMonth() + 1).toString().padStart(2, '0')
      const endDay = endDate.getDate().toString().padStart(2, '0')
      this.formData.end_date = `${endYear}-${endMonth}-${endDay}`
      
      this.recommendation = null
    },
    
    selectType(type) {
      this.formData.goal_type = type
      this.updateDefaultName(type)
      this.updateDefaultUnit(type)
    },
    
    updateDefaultName(type) {
      const nameMap = {
        'lose_weight': '减脂计划',
        'gain_muscle': '增肌计划',
        'shape': '塑形计划',
        'endurance': '耐力提升'
      }
      if (!this.formData.goal_name) {
        this.formData.goal_name = nameMap[type] || ''
      }
    },
    
    updateDefaultUnit(type) {
      const unitMap = {
        'lose_weight': 'kg',
        'gain_muscle': 'kg',
        'shape': 'cm',
        'endurance': '分钟'
      }
      if (!this.formData.unit) {
        this.formData.unit = unitMap[type] || ''
      }
    },
    
    async generateRecommendation() {
      if (!this.formData.goal_type) {
        uni.showToast({
          title: '请先选择目标类型',
          icon: 'none'
        })
        return
      }
      
      uni.showLoading({ title: '生成中...' })
      
      try {
        const result = await api.goalApi.generateRecommend({
          goal_type: this.formData.goal_type,
          target_value: parseFloat(this.formData.target_value) || 0
        })
        
        this.recommendation = {
          training_plan: result.training_plan,
          diet_advice: result.diet_advice
        }
        
        uni.hideLoading()
        uni.showToast({
          title: '生成成功',
          icon: 'success'
        })
      } catch (error) {
        uni.hideLoading()
        uni.showToast({
          title: error.message || '生成失败',
          icon: 'none'
        })
      }
    },
    
    async handleSubmit() {
      if (!this.userInfo.id) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.goal_type) {
        uni.showToast({
          title: '请选择目标类型',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.goal_name.trim()) {
        uni.showToast({
          title: '请输入目标名称',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.target_value) {
        uni.showToast({
          title: '请输入目标值',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        const data = {
          user_id: this.userInfo.id,
          goal_type: this.formData.goal_type,
          goal_name: this.formData.goal_name.trim(),
          description: this.formData.description || null,
          target_value: parseFloat(this.formData.target_value) || 0,
          current_value: parseFloat(this.formData.current_value) || 0,
          unit: this.formData.unit || null,
          start_date: this.formData.start_date,
          end_date: this.formData.end_date
        }
        
        const result = await api.goalApi.create(data)
        
        uni.showToast({
          title: '创建成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1000)
        
      } catch (error) {
        uni.showToast({
          title: error.message || '创建失败',
          icon: 'none'
        })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.add-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  flex-direction: column;
}

.header-section {
  padding: 30rpx;
  background-color: #fff;
}

.page-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.form-scroll {
  flex: 1;
  height: 0;
}

.form-section {
  margin: 20rpx;
  background-color: #fff;
  border-radius: 20rpx;
  padding: 30rpx;
}

.form-item {
  margin-bottom: 30rpx;
}

.form-item:last-child {
  margin-bottom: 0;
}

.form-label {
  font-size: 28rpx;
  color: #606266;
  display: block;
  margin-bottom: 16rpx;
}

.form-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.form-textarea {
  width: 100%;
  height: 180rpx;
  padding: 20rpx 24rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #333;
  box-sizing: border-box;
}

.placeholder-text {
  color: #c0c4cc;
}

.type-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.type-option {
  flex: 1;
  min-width: 140rpx;
  padding: 20rpx 16rpx;
  background-color: #f5f7fa;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2rpx solid transparent;
}

.type-option.active {
  background-color: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.type-icon {
  font-size: 40rpx;
  margin-bottom: 8rpx;
}

.type-text {
  font-size: 24rpx;
  color: #606266;
}

.type-option.active .type-text {
  color: #409EFF;
  font-weight: 500;
}

.value-input-row {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.form-small-input {
  flex: 1;
  height: 88rpx;
  padding: 0 24rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  font-size: 28rpx;
  color: #333;
  text-align: center;
  box-sizing: border-box;
}

.value-arrow {
  font-size: 36rpx;
  color: #409EFF;
  font-weight: 600;
}

.picker-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 88rpx;
  padding: 0 24rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
}

.picker-arrow {
  font-size: 36rpx;
  color: #c0c4cc;
}

.recommend-section {
  margin: 20rpx;
  background-color: #fff;
  border-radius: 20rpx;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24rpx 30rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.section-title {
  font-size: 30rpx;
  font-weight: 600;
  color: #333;
}

.generate-btn {
  display: flex;
  align-items: center;
  padding: 12rpx 20rpx;
  background-color: rgba(230, 162, 60, 0.1);
  border-radius: 30rpx;
}

.generate-icon {
  font-size: 28rpx;
  margin-right: 8rpx;
}

.generate-text {
  font-size: 26rpx;
  color: #e6a23c;
}

.recommend-card {
  padding: 24rpx 30rpx;
}

.recommend-plan {
  padding: 20rpx;
  background-color: #f5f7fa;
  border-radius: 12rpx;
  margin-bottom: 16rpx;
}

.recommend-plan:last-child {
  margin-bottom: 0;
}

.recommend-label {
  font-size: 26rpx;
  font-weight: 500;
  color: #606266;
  display: block;
  margin-bottom: 12rpx;
}

.recommend-text {
  font-size: 26rpx;
  color: #333;
  line-height: 1.8;
}

.empty-recommend {
  padding: 40rpx 30rpx;
  text-align: center;
}

.empty-text {
  font-size: 26rpx;
  color: #909399;
}

.bottom-space {
  height: 200rpx;
}

.btn-section {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24rpx 30rpx;
  background-color: #fff;
  border-top: 1rpx solid #f0f0f0;
  padding-bottom: calc(24rpx + env(safe-area-inset-bottom));
}

.submit-btn {
  width: 100%;
  height: 88rpx;
  line-height: 88rpx;
  border-radius: 16rpx;
  font-size: 30rpx;
  font-weight: 500;
}
</style>
