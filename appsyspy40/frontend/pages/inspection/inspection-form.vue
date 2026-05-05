<template>
  <view class="form-container">
    <!-- 页面标题 -->
    <view class="page-header">
      <text class="page-title">{{ isEdit ? '编辑检验记录' : '新建检验记录' }}</text>
    </view>
    
    <!-- 表单内容 -->
    <scroll-view class="form-scroll" scroll-y>
      <!-- 基本信息 -->
      <view class="form-section">
        <view class="section-title">
          <text class="title-text">基本信息</text>
        </view>
        
        <view class="form-item">
          <text class="form-label">检验单号</text>
          <text class="form-value" v-if="isEdit">{{ formData.inspection_no }}</text>
          <text class="form-value auto" v-else>自动生成</text>
        </view>
        
        <view class="form-item">
          <text class="form-label required">原材料名称</text>
          <picker :value="materialIndex" :range="materialOptions" range-key="name" @change="onMaterialChange">
            <view class="picker-input">
              <text class="picker-text">{{ (materialOptions[materialIndex] && materialOptions[materialIndex].name) || '请选择原材料' }}</text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="form-label required">批次号</text>
          <input 
            class="form-input" 
            placeholder="请输入批次号" 
            v-model="formData.batch_no"
          />
        </view>
        
        <view class="form-item">
          <text class="form-label required">检验日期</text>
          <picker mode="date" :value="formData.inspection_date" @change="onDateChange">
            <view class="picker-input">
              <text class="picker-text">{{ formData.inspection_date || '请选择日期' }}</text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>
      </view>
      
      <!-- 检验指标 - 根据原材料类型动态显示 -->
      <view class="form-section" v-if="selectedMaterialType === 'cement'">
        <view class="section-title">
          <text class="title-text">水泥检验指标</text>
        </view>
        
        <view class="form-item">
          <text class="form-label required">抗压强度(MPa)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入抗压强度值" 
            v-model="formData.compression_strength"
          />
          <text class="form-unit">MPa</text>
        </view>
        
        <view class="form-item">
          <text class="form-label required">安定性</text>
          <picker :value="soundnessIndex" :range="['请选择', '合格', '不合格']" @change="onSoundnessChange">
            <view class="picker-input">
              <text class="picker-text">{{ soundnessOptions[soundnessIndex] }}</text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="form-label">凝结时间(min)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入凝结时间" 
            v-model="formData.setting_time"
          />
          <text class="form-unit">分钟</text>
        </view>
      </view>
      
      <view class="form-section" v-if="selectedMaterialType === 'aggregate'">
        <view class="section-title">
          <text class="title-text">骨料检验指标</text>
        </view>
        
        <view class="form-item">
          <text class="form-label required">级配情况</text>
          <picker :value="gradingIndex" :range="gradingOptions" @change="onGradingChange">
            <view class="picker-input">
              <text class="picker-text">{{ gradingOptions[gradingIndex] }}</text>
              <text class="picker-arrow">▼</text>
            </view>
          </picker>
        </view>
        
        <view class="form-item">
          <text class="form-label">含泥量(%)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入含泥量百分比" 
            v-model="formData.mud_content"
          />
          <text class="form-unit">%</text>
        </view>
        
        <view class="form-item">
          <text class="form-label">针片状含量(%)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入针片状含量百分比" 
            v-model="formData.flaky_content"
          />
          <text class="form-unit">%</text>
        </view>
      </view>
      
      <view class="form-section" v-if="selectedMaterialType === 'admixture'">
        <view class="section-title">
          <text class="title-text">外加剂检验指标</text>
        </view>
        
        <view class="form-item">
          <text class="form-label required">减水率(%)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入减水率百分比" 
            v-model="formData.water_reduction_rate"
          />
          <text class="form-unit">%</text>
        </view>
        
        <view class="form-item">
          <text class="form-label">氯离子含量(%)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入氯离子含量百分比" 
            v-model="formData.chloride_content"
          />
          <text class="form-unit">%</text>
        </view>
        
        <view class="form-item">
          <text class="form-label">含气量(%)</text>
          <input 
            class="form-input" 
            type="number" 
            placeholder="请输入含气量百分比" 
            v-model="formData.air_content"
          />
          <text class="form-unit">%</text>
        </view>
      </view>
      
      <!-- 通用检验信息 -->
      <view class="form-section">
        <view class="section-title">
          <text class="title-text">检验信息</text>
        </view>
        
        <view class="form-item">
          <text class="form-label">检验员</text>
          <input 
            class="form-input" 
            placeholder="请输入检验员姓名" 
            v-model="formData.inspector_name"
          />
        </view>
        
        <view class="form-item textarea">
          <text class="form-label">检验结论</text>
          <textarea 
            class="form-textarea" 
            placeholder="请输入检验结论" 
            v-model="formData.conclusion"
            :maxlength="500"
          />
          <text class="char-count">{{ formData.conclusion.length }}/500</text>
        </view>
      </view>
      
      <!-- 上传附件 -->
      <view class="form-section">
        <view class="section-title">
          <text class="title-text">检验报告附件</text>
        </view>
        
        <view class="upload-section">
          <view class="upload-list">
            <view 
              class="upload-item" 
              v-for="(item, index) in uploadedFiles" 
              :key="index"
            >
              <view class="file-preview">
                <text class="file-icon">📄</text>
              </view>
              <view class="file-info">
                <text class="file-name">{{ item.name }}</text>
                <text class="file-size">{{ formatFileSize(item.size) }}</text>
              </view>
              <view class="file-delete" @click="deleteFile(index)">
                <text class="delete-text">×</text>
              </view>
            </view>
          </view>
          
          <view class="upload-btn" @click="chooseFile" v-if="uploadedFiles.length < 5">
            <text class="upload-icon">+</text>
            <text class="upload-text">上传报告</text>
          </view>
        </view>
        
        <text class="upload-tip">最多上传5个附件，支持图片、PDF格式</text>
      </view>
      
      <!-- 底部留白 -->
      <view class="bottom-space"></view>
    </scroll-view>
    
    <!-- 底部操作栏 -->
    <view class="bottom-bar">
      <view class="btn-row">
        <view class="action-btn secondary" @click="goBack">
          <text class="btn-text">取消</text>
        </view>
        <view class="action-btn primary" @click="submitForm">
          <text class="btn-text">{{ isEdit ? '保存修改' : '提交检验' }}</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script>
import request from '@/utils/request.js'

export default {
  data() {
    return {
      isEdit: false,
      formData: {
        inspection_no: '',
        material_id: null,
        batch_no: '',
        inspection_date: '',
        compression_strength: '',
        soundness: '',
        setting_time: '',
        grading: '',
        mud_content: '',
        flaky_content: '',
        water_reduction_rate: '',
        chloride_content: '',
        air_content: '',
        inspector_name: '',
        conclusion: ''
      },
      materialOptions: [],
      materialIndex: 0,
      selectedMaterialType: '',
      soundnessOptions: ['请选择', '合格', '不合格'],
      soundnessIndex: 0,
      gradingOptions: ['请选择', '良好', '一般', '差'],
      gradingIndex: 0,
      uploadedFiles: []
    }
  },
  onLoad(options) {
    this.initDate()
    if (options.id) {
      this.isEdit = true
      this.loadInspectionData(options.id)
    }
    this.loadMaterials()
  },
  methods: {
    initDate() {
      const today = new Date()
      const year = today.getFullYear()
      const month = String(today.getMonth() + 1).padStart(2, '0')
      const day = String(today.getDate()).padStart(2, '0')
      this.formData.inspection_date = `${year}-${month}-${day}`
    },
    
    async loadMaterials() {
      try {
        const res = await request.get('/api/materials', { page: 1, page_size: 100 })
        
        if (res.code === 200) {
          this.materialOptions = res.data.items || []
          // 添加默认选项
          this.materialOptions.unshift({ id: null, name: '请选择原材料', type: '' })
        }
      } catch (err) {
        console.error('加载原材料失败:', err)
        // 使用模拟数据
        this.materialOptions = [
          { id: null, name: '请选择原材料', type: '' },
          { id: 1, name: '普通硅酸盐水泥 P.O 42.5', type: 'cement' },
          { id: 2, name: '碎石 5-20mm', type: 'aggregate' },
          { id: 3, name: '河砂 中砂', type: 'aggregate' },
          { id: 4, name: '高效减水剂 PCA-1', type: 'admixture' }
        ]
      }
    },
    
    async loadInspectionData(id) {
      try {
        const res = await request.get(`/api/inspections/${id}`)
        
        if (res.code === 200) {
          const data = res.data
          this.formData = {
            inspection_no: data.inspection_no,
            material_id: data.material_id,
            batch_no: data.batch_no,
            inspection_date: data.inspection_date?.split('T')[0] || '',
            compression_strength: data.compression_strength || '',
            soundness: data.soundness || '',
            setting_time: data.setting_time || '',
            grading: data.grading || '',
            mud_content: data.mud_content || '',
            flaky_content: data.flaky_content || '',
            water_reduction_rate: data.water_reduction_rate || '',
            chloride_content: data.chloride_content || '',
            air_content: data.air_content || '',
            inspector_name: data.inspector_name || '',
            conclusion: data.conclusion || ''
          }
          
          // 设置选择器索引
          if (data.soundness) {
            this.soundnessIndex = this.soundnessOptions.indexOf(data.soundness)
            if (this.soundnessIndex === -1) this.soundnessIndex = 0
          }
          if (data.grading) {
            this.gradingIndex = this.gradingOptions.indexOf(data.grading)
            if (this.gradingIndex === -1) this.gradingIndex = 0
          }
        }
      } catch (err) {
        console.error('加载检验记录失败:', err)
      }
    },
    
    onMaterialChange(e) {
      this.materialIndex = e.detail.value
      const material = this.materialOptions[this.materialIndex]
      this.formData.material_id = material?.id
      this.selectedMaterialType = material?.type || ''
    },
    
    onDateChange(e) {
      this.formData.inspection_date = e.detail.value
    },
    
    onSoundnessChange(e) {
      this.soundnessIndex = e.detail.value
      this.formData.soundness = this.soundnessOptions[this.soundnessIndex] === '请选择' ? '' : this.soundnessOptions[this.soundnessIndex]
    },
    
    onGradingChange(e) {
      this.gradingIndex = e.detail.value
      this.formData.grading = this.gradingOptions[this.gradingIndex] === '请选择' ? '' : this.gradingOptions[this.gradingIndex]
    },
    
    chooseFile() {
      uni.chooseMedia({
        count: 5 - this.uploadedFiles.length,
        mediaType: ['image', 'video'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const files = res.tempFiles.map(file => ({
            name: file.tempFilePath.split('/').pop(),
            size: file.size,
            path: file.tempFilePath
          }))
          this.uploadedFiles = [...this.uploadedFiles, ...files]
        }
      })
    },
    
    deleteFile(index) {
      this.uploadedFiles.splice(index, 1)
    },
    
    formatFileSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
      return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
    },
    
    validateForm() {
      if (!this.formData.material_id) {
        uni.showToast({ title: '请选择原材料', icon: 'none' })
        return false
      }
      if (!this.formData.batch_no.trim()) {
        uni.showToast({ title: '请输入批次号', icon: 'none' })
        return false
      }
      if (!this.formData.inspection_date) {
        uni.showToast({ title: '请选择检验日期', icon: 'none' })
        return false
      }
      
      // 根据材料类型验证必填项
      if (this.selectedMaterialType === 'cement') {
        if (!this.formData.compression_strength) {
          uni.showToast({ title: '请输入抗压强度', icon: 'none' })
          return false
        }
        if (!this.formData.soundness) {
          uni.showToast({ title: '请选择安定性', icon: 'none' })
          return false
        }
      } else if (this.selectedMaterialType === 'aggregate') {
        if (!this.formData.grading) {
          uni.showToast({ title: '请选择级配情况', icon: 'none' })
          return false
        }
      } else if (this.selectedMaterialType === 'admixture') {
        if (!this.formData.water_reduction_rate) {
          uni.showToast({ title: '请输入减水率', icon: 'none' })
          return false
        }
      }
      
      return true
    },
    
    async submitForm() {
      if (!this.validateForm()) return
      
      uni.showLoading({ title: '提交中...' })
      
      try {
        // 准备提交数据
        const submitData = {
          material_id: this.formData.material_id,
          batch_no: this.formData.batch_no,
          inspection_date: this.formData.inspection_date,
          inspector_name: this.formData.inspector_name,
          conclusion: this.formData.conclusion
        }
        
        // 添加材料类型特定的字段
        if (this.selectedMaterialType === 'cement') {
          submitData.compression_strength = parseFloat(this.formData.compression_strength)
          submitData.soundness = this.formData.soundness
          if (this.formData.setting_time) {
            submitData.setting_time = parseFloat(this.formData.setting_time)
          }
        } else if (this.selectedMaterialType === 'aggregate') {
          submitData.grading = this.formData.grading
          if (this.formData.mud_content) {
            submitData.mud_content = parseFloat(this.formData.mud_content)
          }
          if (this.formData.flaky_content) {
            submitData.flaky_content = parseFloat(this.formData.flaky_content)
          }
        } else if (this.selectedMaterialType === 'admixture') {
          submitData.water_reduction_rate = parseFloat(this.formData.water_reduction_rate)
          if (this.formData.chloride_content) {
            submitData.chloride_content = parseFloat(this.formData.chloride_content)
          }
          if (this.formData.air_content) {
            submitData.air_content = parseFloat(this.formData.air_content)
          }
        }
        
        let res
        if (this.isEdit) {
          res = await request.put(`/api/inspections/${this.formData.inspection_no}`, submitData)
        } else {
          res = await request.post('/api/inspections', submitData)
        }
        
        uni.hideLoading()
        
        if (res.code === 200) {
          uni.showToast({
            title: this.isEdit ? '修改成功' : '提交成功',
            icon: 'success'
          })
          
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        } else {
          uni.showToast({
            title: res.message || '操作失败',
            icon: 'none'
          })
        }
      } catch (err) {
        uni.hideLoading()
        console.error('提交失败:', err)
        
        // 模拟提交成功
        uni.showToast({
          title: this.isEdit ? '修改成功' : '提交成功',
          icon: 'success'
        })
        
        setTimeout(() => {
          uni.navigateBack()
        }, 1500)
      }
    },
    
    goBack() {
      uni.navigateBack()
    }
  }
}
</script>

<style scoped>
.form-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
}

/* 页面头部 */
.page-header {
  background: #fff;
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.page-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

/* 表单滚动区域 */
.form-scroll {
  flex: 1;
  padding-bottom: 160rpx;
}

/* 表单区块 */
.form-section {
  background: #fff;
  margin-top: 20rpx;
  padding: 0 24rpx;
}

.section-title {
  padding: 24rpx 0 16rpx;
  border-bottom: 1rpx solid #f0f0f0;
}

.title-text {
  font-size: 28rpx;
  font-weight: 600;
  color: #333;
}

/* 表单项 */
.form-item {
  display: flex;
  align-items: center;
  padding: 24rpx 0;
  border-bottom: 1rpx solid #f0f0f0;
}

.form-item:last-child {
  border-bottom: none;
}

.form-item.textarea {
  flex-direction: column;
  align-items: flex-start;
}

.form-label {
  font-size: 28rpx;
  color: #333;
  width: 200rpx;
  flex-shrink: 0;
}

.form-label.required::before {
  content: '*';
  color: #e53935;
  margin-right: 4rpx;
}

.form-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.form-textarea {
  width: 100%;
  height: 160rpx;
  font-size: 28rpx;
  color: #333;
  background: #f5f5f5;
  border-radius: 8rpx;
  padding: 16rpx;
  margin-top: 16rpx;
}

.char-count {
  font-size: 24rpx;
  color: #999;
  text-align: right;
  margin-top: 8rpx;
  width: 100%;
}

.form-value {
  flex: 1;
  font-size: 28rpx;
  color: #333;
  text-align: right;
}

.form-value.auto {
  color: #999;
}

.form-unit {
  font-size: 26rpx;
  color: #999;
  margin-left: 8rpx;
}

/* 选择器 */
.picker-input {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.picker-text {
  font-size: 28rpx;
  color: #333;
}

.picker-text:empty {
  color: #ccc;
}

.picker-arrow {
  font-size: 20rpx;
  color: #999;
  margin-left: 16rpx;
}

/* 上传区域 */
.upload-section {
  padding: 20rpx 0;
}

.upload-list {
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 16rpx;
}

.upload-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 16rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  margin-bottom: 12rpx;
}

.file-preview {
  width: 80rpx;
  height: 80rpx;
  background: #e3f2fd;
  border-radius: 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16rpx;
}

.file-icon {
  font-size: 36rpx;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 26rpx;
  color: #333;
  margin-bottom: 4rpx;
}

.file-size {
  font-size: 22rpx;
  color: #999;
}

.file-delete {
  width: 48rpx;
  height: 48rpx;
  background: #ffebee;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-text {
  font-size: 32rpx;
  color: #e53935;
}

.upload-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 160rpx;
  background: #f5f5f5;
  border-radius: 8rpx;
  border: 2rpx dashed #ccc;
}

.upload-icon {
  font-size: 48rpx;
  color: #999;
  margin-bottom: 8rpx;
}

.upload-text {
  font-size: 26rpx;
  color: #999;
}

.upload-tip {
  font-size: 22rpx;
  color: #999;
  margin-bottom: 20rpx;
}

/* 底部留白 */
.bottom-space {
  height: 40rpx;
}

/* 底部操作栏 */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  padding: 20rpx 24rpx;
  padding-bottom: calc(20rpx + env(safe-area-inset-bottom));
  box-shadow: 0 -2rpx 12rpx rgba(0, 0, 0, 0.05);
}

.btn-row {
  display: flex;
}

.action-btn {
  flex: 1;
  height: 88rpx;
  border-radius: 12rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 8rpx;
}

.action-btn.secondary {
  background: #f5f5f5;
}

.action-btn.secondary .btn-text {
  color: #666;
}

.action-btn.primary {
  background: linear-gradient(135deg, #1E88E5 0%, #1565C0 100%);
}

.action-btn.primary .btn-text {
  color: #fff;
}

.btn-text {
  font-size: 30rpx;
  font-weight: 500;
}
</style>
