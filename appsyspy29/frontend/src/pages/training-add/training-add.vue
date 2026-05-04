<template>
  <view class="add-container">
    <view class="header-section">
      <text class="page-title">记录训练</text>
    </view>
    
    <scroll-view class="form-scroll" scroll-y>
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">训练日期</text>
          <picker 
            mode="date" 
            :value="formData.training_date" 
            @change="onDateChange"
          >
            <view class="picker-value">
              <text :class="formData.training_date ? '' : 'placeholder-text'">
                {{ formData.training_date || '请选择日期' }}
              </text>
              <text class="picker-arrow">›</text>
            </view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="form-label">训练类型</text>
          <view class="type-options">
            <view 
              class="type-option" 
              :class="{ active: formData.training_type === item.value }"
              v-for="(item, index) in trainingTypes" 
              :key="index"
              @click="selectType(item.value)"
            >
              <text class="type-icon">{{ item.icon }}</text>
              <text class="type-text">{{ item.label }}</text>
            </view>
          </view>
        </view>
        
        <view class="form-item">
          <text class="form-label">训练时长 (分钟)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入训练时长" 
            v-model="formData.duration"
            placeholder-class="placeholder-text"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">心情状态</text>
          <view class="mood-options">
            <view 
              class="mood-option" 
              :class="{ active: formData.mood === item.value }"
              v-for="(item, index) in moodOptions" 
              :key="index"
              @click="selectMood(item.value)"
            >
              <text class="mood-icon">{{ item.icon }}</text>
              <text class="mood-text">{{ item.label }}</text>
            </view>
          </view>
        </view>
        
        <view class="form-item">
          <text class="form-label">训练地点</text>
          <input 
            class="form-input" 
            type="text" 
            placeholder="请输入训练地点（可选）" 
            v-model="formData.location"
            placeholder-class="placeholder-text"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label">消耗卡路里</text>
          <view class="calories-input">
            <input 
              class="form-input" 
              type="number" 
              placeholder="请输入或自动计算" 
              v-model="formData.total_calories"
              placeholder-class="placeholder-text"
            />
            <button class="calc-btn" @click="calculateCalories">自动计算</button>
          </view>
        </view>
      </view>
      
      <view class="items-section">
        <view class="section-header">
          <text class="section-title">训练项目</text>
          <view class="add-item-btn" @click="addExerciseItem">
            <text class="add-icon">+</text>
            <text class="add-text">添加项目</text>
          </view>
        </view>
        
        <view class="exercise-list" v-if="exerciseItems.length > 0">
          <view class="exercise-item" v-for="(item, index) in exerciseItems" :key="index">
            <view class="item-header">
              <text class="item-order">{{ index + 1 }}</text>
              <picker 
                :range="exercises" 
                range-key="name" 
                :value="getExerciseIndex(item.exercise_id)"
                @change="(e) => selectExercise(index, e.detail.value)"
              >
                <view class="exercise-picker">
                  <text :class="item.exercise_id ? '' : 'placeholder-text'">
                    {{ getExerciseName(item.exercise_id) || '选择训练项目' }}
                  </text>
                  <text class="picker-arrow">›</text>
                </view>
              </picker>
              <text class="delete-btn" @click="removeExerciseItem(index)">×</text>
            </view>
            
            <view class="item-form">
              <view class="form-row">
                <view class="form-col">
                  <text class="form-sub-label">组数</text>
                  <input 
                    class="form-small-input" 
                    type="number" 
                    placeholder="组数" 
                    v-model="item.sets"
                  />
                </view>
                <view class="form-col">
                  <text class="form-sub-label">次数</text>
                  <input 
                    class="form-small-input" 
                    type="number" 
                    placeholder="次数" 
                    v-model="item.reps"
                  />
                </view>
                <view class="form-col">
                  <text class="form-sub-label">重量(kg)</text>
                  <input 
                    class="form-small-input" 
                    type="digit" 
                    placeholder="重量" 
                    v-model="item.weight"
                  />
                </view>
              </view>
              
              <view class="form-row">
                <view class="form-col">
                  <text class="form-sub-label">休息时间(秒)</text>
                  <input 
                    class="form-small-input" 
                    type="number" 
                    placeholder="休息" 
                    v-model="item.rest_time"
                  />
                </view>
                <view class="form-col">
                  <text class="form-sub-label">备注</text>
                  <input 
                    class="form-small-input" 
                    type="text" 
                    placeholder="备注" 
                    v-model="item.notes"
                  />
                </view>
              </view>
            </view>
          </view>
        </view>
        
        <view class="empty-exercise" v-else>
          <text class="empty-text">暂无训练项目</text>
          <text class="empty-hint">点击上方"添加项目"按钮</text>
        </view>
      </view>
      
      <view class="form-section">
        <view class="form-item">
          <text class="form-label">训练备注</text>
          <textarea 
            class="form-textarea" 
            placeholder="记录本次训练的感受和总结（可选）" 
            v-model="formData.notes"
            placeholder-class="placeholder-text"
          />
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
        {{ loading ? '保存中...' : '保存记录' }}
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
      exercises: [],
      trainingTypes: [
        { label: '力量训练', value: 'strength', icon: '💪' },
        { label: '有氧运动', value: 'cardio', icon: '🏃' },
        { label: '拉伸', value: 'flexibility', icon: '🧘' },
        { label: 'CrossFit', value: 'crossfit', icon: '🔥' },
        { label: 'HIIT', value: 'hiit', icon: '⚡' }
      ],
      moodOptions: [
        { label: '很棒', value: 'great', icon: '😄' },
        { label: '不错', value: 'good', icon: '😊' },
        { label: '一般', value: 'normal', icon: '😐' },
        { label: '疲劳', value: 'tired', icon: '😫' }
      ],
      formData: {
        training_date: '',
        training_type: '',
        duration: '',
        total_calories: '',
        mood: '',
        location: '',
        notes: ''
      },
      exerciseItems: [],
      loading: false
    }
  },
  onLoad() {
    this.initForm()
    this.loadExercises()
  },
  methods: {
    initForm() {
      this.userInfo = uni.getStorageSync('userInfo') || {}
      
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0')
      const day = today.getDate().toString().padStart(2, '0')
      this.formData.training_date = `${year}-${month}-${day}`
      
      this.exerciseItems = []
    },
    
    async loadExercises() {
      try {
        this.exercises = await api.exerciseApi.getList()
      } catch (error) {
        console.error('加载训练项目失败:', error)
      }
    },
    
    onDateChange(e) {
      this.formData.training_date = e.detail.value
    },
    
    selectType(type) {
      this.formData.training_type = type
    },
    
    selectMood(mood) {
      this.formData.mood = mood
    },
    
    addExerciseItem() {
      this.exerciseItems.push({
        exercise_id: null,
        sets: '',
        reps: '',
        weight: '',
        rest_time: '',
        notes: ''
      })
    },
    
    removeExerciseItem(index) {
      this.exerciseItems.splice(index, 1)
    },
    
    getExerciseIndex(exerciseId) {
      if (!exerciseId) return 0
      const index = this.exercises.findIndex(e => e.id === exerciseId)
      return index >= 0 ? index : 0
    },
    
    getExerciseName(exerciseId) {
      if (!exerciseId) return ''
      const exercise = this.exercises.find(e => e.id === exerciseId)
      return exercise ? exercise.name : ''
    },
    
    selectExercise(itemIndex, exerciseIndex) {
      this.exerciseItems[itemIndex].exercise_id = this.exercises[exerciseIndex].id
    },
    
    calculateCalories() {
      if (!this.formData.duration || !this.formData.training_type) {
        uni.showToast({
          title: '请先选择训练类型和时长',
          icon: 'none'
        })
        return
      }
      
      const duration = parseInt(this.formData.duration) || 0
      const type = this.formData.training_type
      
      let met = 3.5
      switch (type) {
        case 'strength': met = 6.0; break
        case 'cardio': met = 8.0; break
        case 'flexibility': met = 2.5; break
        case 'crossfit': met = 10.0; break
        case 'hiit': met = 12.0; break
      }
      
      const weight = 70
      const calories = Math.round((met * 3.5 * weight / 200) * duration)
      
      this.formData.total_calories = calories.toString()
      
      uni.showToast({
        title: `估算约 ${calories} 卡路里`,
        icon: 'success'
      })
    },
    
    async handleSubmit() {
      if (!this.userInfo.id) {
        uni.showToast({
          title: '请先登录',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.training_date) {
        uni.showToast({
          title: '请选择训练日期',
          icon: 'none'
        })
        return
      }
      
      if (!this.formData.training_type) {
        uni.showToast({
          title: '请选择训练类型',
          icon: 'none'
        })
        return
      }
      
      this.loading = true
      
      try {
        const data = {
          user_id: this.userInfo.id,
          training_date: this.formData.training_date,
          training_type: this.formData.training_type,
          duration: parseInt(this.formData.duration) || 0,
          total_calories: parseInt(this.formData.total_calories) || 0,
          mood: this.formData.mood || null,
          location: this.formData.location || null,
          notes: this.formData.notes || null,
          items: this.exerciseItems
            .filter(item => item.exercise_id)
            .map(item => ({
              exercise_id: item.exercise_id,
              sets: parseInt(item.sets) || null,
              reps: parseInt(item.reps) || null,
              weight: parseFloat(item.weight) || null,
              rest_time: parseInt(item.rest_time) || null,
              notes: item.notes || null
            }))
        }
        
        await api.trainingLogApi.create(data)
        
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

.type-options {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.type-option {
  padding: 20rpx 24rpx;
  background-color: #f5f7fa;
  border-radius: 16rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 120rpx;
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
}

.mood-options {
  display: flex;
  justify-content: space-around;
}

.mood-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 24rpx;
  border-radius: 16rpx;
  border: 2rpx solid transparent;
}

.mood-option.active {
  background-color: rgba(64, 158, 255, 0.1);
  border-color: #409EFF;
}

.mood-icon {
  font-size: 48rpx;
  margin-bottom: 8rpx;
}

.mood-text {
  font-size: 24rpx;
  color: #606266;
}

.mood-option.active .mood-text {
  color: #409EFF;
}

.calories-input {
  display: flex;
  gap: 20rpx;
}

.calories-input .form-input {
  flex: 1;
}

.calc-btn {
  height: 88rpx;
  padding: 0 30rpx;
  line-height: 88rpx;
  background-color: #409EFF;
  color: #fff;
  border-radius: 12rpx;
  font-size: 26rpx;
  margin: 0;
}

.items-section {
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

.add-item-btn {
  display: flex;
  align-items: center;
  padding: 12rpx 20rpx;
  background-color: rgba(64, 158, 255, 0.1);
  border-radius: 30rpx;
}

.add-icon {
  font-size: 32rpx;
  color: #409EFF;
  margin-right: 6rpx;
  font-weight: 300;
}

.add-text {
  font-size: 26rpx;
  color: #409EFF;
}

.exercise-list {
  padding: 0 30rpx;
}

.exercise-item {
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.exercise-item:last-child {
  border-bottom: none;
}

.item-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.item-order {
  width: 48rpx;
  height: 48rpx;
  background-color: #409EFF;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24rpx;
  margin-right: 16rpx;
}

.exercise-picker {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 72rpx;
  padding: 0 20rpx;
  background-color: #f5f7fa;
  border-radius: 10rpx;
  margin-right: 16rpx;
}

.delete-btn {
  width: 48rpx;
  height: 48rpx;
  background-color: #fef0f0;
  color: #f56c6c;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  line-height: 1;
}

.item-form {
  padding-left: 64rpx;
}

.form-row {
  display: flex;
  gap: 20rpx;
  margin-bottom: 16rpx;
}

.form-row:last-child {
  margin-bottom: 0;
}

.form-col {
  flex: 1;
}

.form-sub-label {
  font-size: 22rpx;
  color: #909399;
  display: block;
  margin-bottom: 8rpx;
}

.form-small-input {
  width: 100%;
  height: 64rpx;
  padding: 0 16rpx;
  background-color: #f5f7fa;
  border-radius: 8rpx;
  font-size: 26rpx;
  text-align: center;
  box-sizing: border-box;
}

.empty-exercise {
  padding: 60rpx 30rpx;
  text-align: center;
}

.empty-text {
  font-size: 28rpx;
  color: #909399;
  display: block;
  margin-bottom: 12rpx;
}

.empty-hint {
  font-size: 24rpx;
  color: #c0c4cc;
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
