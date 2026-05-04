<template>
  <view class="add-container">
    <view class="header-section">
      <text class="page-title">添加体测记录</text>
    </view>
    
    <view class="form-section">
      <view class="form-item">
        <text class="form-label">测量日期</text>
        <picker 
          mode="date" 
          :value="formData.measurement_date" 
          @change="onDateChange"
        >
          <view class="picker-value">
            <text :class="formData.measurement_date ? '' : 'placeholder-text'">
              {{ formData.measurement_date || '请选择日期' }}
            </text>
            <text class="picker-arrow">›</text>
          </view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="form-label">体重 (kg)</text>
        <input 
          class="form-input" 
          type="digit" 
          placeholder="请输入体重" 
          v-model="formData.weight"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">体脂率 (%)</text>
        <input 
          class="form-input" 
          type="digit" 
          placeholder="请输入体脂率" 
          v-model="formData.body_fat_rate"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">肌肉量 (kg)</text>
        <input 
          class="form-input" 
          type="digit" 
          placeholder="请输入肌肉量" 
          v-model="formData.muscle_mass"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">身高 (cm) - 用于计算BMI</text>
        <input 
          class="form-input" 
          type="digit" 
          placeholder="请输入身高" 
          v-model="height"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">基础代谢 (可选)</text>
        <input 
          class="form-input" 
          type="number" 
          placeholder="请输入基础代谢" 
          v-model="formData.bmr"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">水分率 % (可选)</text>
        <input 
          class="form-input" 
          type="digit" 
          placeholder="请输入水分率" 
          v-model="formData.water_rate"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">骨量 kg (可选)</text>
        <input 
          class="form-input" 
          type="digit" 
          placeholder="请输入骨量" 
          v-model="formData.bone_mass"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">蛋白质率 % (可选)</text>
        <input 
          class="form-input" 
          type="digit" 
          placeholder="请输入蛋白质率" 
          v-model="formData.protein_rate"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-item">
        <text class="form-label">备注 (可选)</text>
        <textarea 
          class="form-textarea" 
          placeholder="请输入备注信息" 
          v-model="formData.notes"
          placeholder-class="placeholder-text"
        />
      </view>
      
      <view class="form-tips">
        <view class="tips-card" v-if="formData.weight && height">
          <text class="tips-title">预估BMI</text>
          <text class="tips-value" :class="getBmiClass()">{{ calculateBmi() }}</text>
          <text class="tips-desc">{{ getBmiDesc() }}</text>
        </view>
      </view>
    </view>
    
    <view class="btn-section">
      <button 
        class="submit-btn btn-primary" 
        :disabled="loading"
        @click="handleSubmit"
      >
        {{ loading ? '提交中...' : '保存记录' }}
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
      height: '',
      formData: {
        measurement_date: '',
        weight: '',
        body_fat_rate: '',
        muscle_mass: '',
        bmr: '',
        water_rate: '',
        bone_mass: '',
        protein_rate: '',
        notes: '',
        source: 'manual'
      },
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
      this.formData.measurement_date = `${year}-${month}-${day}`
    },
    
    onDateChange(e) {
      this.formData.measurement_date = e.detail.value
    },
    
    calculateBmi() {
      if (!this.formData.weight || !this.height) return '--'
      const weight = parseFloat(this.formData.weight)
      const height = parseFloat(this.height) / 100
      if (height <= 0) return '--'
      const bmi = weight / (height * height)
      return bmi.toFixed(1)
    },
    
    getBmiClass() {
      const bmi = parseFloat(this.calculateBmi())
      if (isNaN(bmi)) return ''
      if (bmi < 18.5) return 'light'
      if (bmi < 24) return 'normal'
      if (bmi < 28) return 'overweight'
      return 'obese'
    },
    
    getBmiDesc() {
      const bmi = parseFloat(this.calculateBmi())
      if (isNaN(bmi)) return ''
      if (bmi < 18.5) return '体重偏轻'
      if (bmi < 24) return '体重正常'
      if (bmi < 28) return '体重偏重'
      return '肥胖'
    },
    
    async handleSubmit() {
      if (!this.userInfo.id) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.measurement_date) {
        uni.showToast({
          title: '请选择测量日期',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.weight) {
        uni.showToast({
          title: '请输入体重',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        const data = {
          user_id: this.userInfo.id,
          measurement_date: this.formData.measurement_date,
          weight: parseFloat(this.formData.weight) || null,
          body_fat_rate: parseFloat(this.formData.body_fat_rate) || null,
          muscle_mass: parseFloat(this.formData.muscle_mass) || null,
          bmr: parseInt(this.formData.bmr) || null,
          water_rate: parseFloat(this.formData.water_rate) || null,
          bone_mass: parseFloat(this.formData.bone_mass) || null,
          protein_rate: parseFloat(this.formData.protein_rate) || null,
          notes: this.formData.notes || null,
          source: 'manual'
        }
        
        if (data.weight && this.height) {
          const height = parseFloat(this.height) / 100
          if (height > 0) {
            data.bmi = parseFloat((data.weight / (height * height)).toFixed(1))
          }
        }
        
        await api.measurementApi.create(data)
        
        uni.showToast({
          title: '保存成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1000)
        
      } catch (error) {
        uni.showToast({
          title: error.message || '保存失败',
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
  padding-bottom: 180rpx;
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

.form-tips {
  margin-top: 30rpx;
}

.tips-card {
  padding: 30rpx;
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1), rgba(102, 177, 255, 0.1));
  border-radius: 16rpx;
  text-align: center;
}

.tips-title {
  font-size: 26rpx;
  color: #606266;
  display: block;
  margin-bottom: 12rpx;
}

.tips-value {
  font-size: 52rpx;
  font-weight: 600;
  display: block;
  margin-bottom: 12rpx;
}

.tips-value.light {
  color: #409EFF;
}

.tips-value.normal {
  color: #67c23a;
}

.tips-value.overweight {
  color: #e6a23c;
}

.tips-value.obese {
  color: #f56c6c;
}

.tips-desc {
  font-size: 26rpx;
  color: #909399;
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
