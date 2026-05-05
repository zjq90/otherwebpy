<template>
  <view class="page">
    <view class="avatar-section" @click="changeAvatar">
      <image :src="form.avatar || '/static/images/default-avatar.png'" class="user-avatar"></image>
      <view class="avatar-tip">
        <text class="camera-icon">📷</text>
        <text class="tip-text">更换头像</text>
      </view>
    </view>
    
    <view class="form-section">
      <view class="form-item">
        <text class="form-label">昵称</text>
        <input 
          v-model="form.nickname" 
          type="text" 
          placeholder="请输入昵称"
          maxlength="20"
        />
      </view>
      
      <view class="form-item" @click="selectGender">
        <text class="form-label">性别</text>
        <picker :value="genderIndex" :range="genderOptions" @change="onGenderChange">
          <view class="picker-value">
            <text>{{ genderOptions[genderIndex] || '请选择' }}</text>
            <text class="picker-arrow">›</text>
          </view>
        </picker>
      </view>
      
      <view class="form-item" @click="selectBirthday">
        <text class="form-label">生日</text>
        <picker mode="date" :value="form.birthday" @change="onBirthdayChange">
          <view class="picker-value">
            <text>{{ form.birthday || '请选择' }}</text>
            <text class="picker-arrow">›</text>
          </view>
        </picker>
      </view>
      
      <view class="form-item">
        <text class="form-label">手机号</text>
        <view class="phone-section">
          <text class="phone-text">{{ maskPhone(form.phone) }}</text>
          <view class="change-phone" @click="changePhone">更换</view>
        </view>
      </view>
    </view>
    
    <view class="save-section">
      <view class="save-btn" @click="handleSave">保存修改</view>
    </view>
    
    <view class="logout-section">
      <view class="logout-btn" @click="handleLogout">退出登录</view>
    </view>
  </view>
</template>

<script>
import api from '@/common/api.js'
import utils from '@/common/utils.js'

const GENDER_MAP = {
  0: '未知',
  1: '男',
  2: '女'
}

export default {
  data() {
    return {
      form: {
        avatar: '',
        nickname: '',
        gender: 0,
        birthday: '',
        phone: ''
      },
      genderOptions: ['未知', '男', '女'],
      genderIndex: 0
    }
  },
  
  onShow() {
    this.loadUserInfo()
  },
  
  methods: {
    maskPhone(phone) {
      return utils.maskPhone(phone)
    },
    
    async loadUserInfo() {
      const token = uni.getStorageSync('token')
      if (!token) {
        utils.showToast('请先登录')
        uni.navigateTo({
          url: '/pages/login/login'
        })
        return
      }
      
      try {
        const res = await api.get('/user/profile')
        if (res.code === 200) {
          this.form = {
            avatar: res.data.avatar || '',
            nickname: res.data.nickname || '',
            gender: res.data.gender || 0,
            birthday: res.data.birthday || '',
            phone: res.data.phone || ''
          }
          
          this.genderIndex = this.form.gender
        }
      } catch (e) {
        console.error('加载用户信息失败:', e)
      }
    },
    
    changeAvatar() {
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed'],
        sourceType: ['album', 'camera'],
        success: async (res) => {
          const tempFilePath = res.tempFilePaths[0]
          
          utils.showLoading('上传中...')
          
          try {
            const uploadRes = await api.uploadFile('/user/avatar', tempFilePath)
            
            utils.hideLoading()
            
            if (uploadRes.code === 200) {
              this.form.avatar = uploadRes.data.avatar_url
              utils.showToast('上传成功')
            }
          } catch (e) {
            utils.hideLoading()
            console.error('上传头像失败:', e)
          }
        }
      })
    },
    
    selectGender() {
    },
    
    onGenderChange(e) {
      this.genderIndex = e.detail.value
      this.form.gender = this.genderIndex
    },
    
    selectBirthday() {
    },
    
    onBirthdayChange(e) {
      this.form.birthday = e.detail.value
    },
    
    changePhone() {
      utils.showModal('更换手机号功能开发中', '提示', false)
    },
    
    async handleSave() {
      if (!this.form.nickname) {
        utils.showToast('请输入昵称')
        return
      }
      
      utils.showLoading('保存中...')
      
      try {
        const updateData = {
          nickname: this.form.nickname,
          gender: this.form.gender
        }
        
        if (this.form.birthday) {
          updateData.birthday = this.form.birthday
        }
        
        const res = await api.put('/user/profile', updateData)
        
        utils.hideLoading()
        
        if (res.code === 200) {
          uni.setStorageSync('userInfo', res.data)
          const app = getApp()
          app.globalData.userInfo = res.data
          
          utils.showToast('保存成功')
          
          setTimeout(() => {
            uni.navigateBack()
          }, 1500)
        }
      } catch (e) {
        utils.hideLoading()
        console.error('保存失败:', e)
      }
    },
    
    async handleLogout() {
      const confirmed = await utils.showModal('确定要退出登录吗？')
      if (!confirmed) return
      
      const app = getApp()
      app.globalData.hasLogin = false
      app.globalData.userInfo = null
      
      uni.removeStorageSync('token')
      uni.removeStorageSync('userInfo')
      
      utils.showToast('已退出登录')
      
      setTimeout(() => {
        uni.reLaunch({
          url: '/pages/index/index'
        })
      }, 1500)
    }
  }
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: $bg-color;
  padding-bottom: 40rpx;
}

.avatar-section {
  background-color: $white;
  padding: 60rpx 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20rpx;
}

.user-avatar {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  border: 4rpx solid $border-color;
}

.avatar-tip {
  display: flex;
  align-items: center;
  margin-top: 20rpx;
}

.camera-icon {
  font-size: 28rpx;
  margin-right: 8rpx;
}

.tip-text {
  font-size: $font-size-sm;
  color: $primary-color;
}

.form-section {
  background-color: $white;
  padding: 0 30rpx;
  margin-bottom: 40rpx;
}

.form-item {
  display: flex;
  align-items: center;
  padding: 30rpx 0;
  border-bottom: 1rpx solid $border-color;
  
  &:last-child {
    border-bottom: none;
  }
}

.form-label {
  width: 160rpx;
  font-size: $font-size-base;
  color: $text-color;
  flex-shrink: 0;
}

.form-item input {
  flex: 1;
  font-size: $font-size-base;
  color: $text-color;
  text-align: right;
}

.picker-value {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.picker-value text:first-child {
  font-size: $font-size-base;
  color: $text-color;
}

.picker-arrow {
  font-size: $font-size-lg;
  color: $text-muted;
}

.phone-section {
  flex: 1;
  display: flex;
  justify-content: flex-end;
  align-items: center;
}

.phone-text {
  font-size: $font-size-base;
  color: $text-color;
  margin-right: 20rpx;
}

.change-phone {
  padding: 8rpx 20rpx;
  background-color: rgba($primary-color, 0.1);
  color: $primary-color;
  font-size: $font-size-sm;
  border-radius: 30rpx;
}

.save-section {
  padding: 0 30rpx;
  margin-bottom: 40rpx;
}

.save-btn {
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  background-color: $primary-color;
  color: $white;
  font-size: $font-size-lg;
  font-weight: bold;
  border-radius: $border-radius-lg;
}

.logout-section {
  padding: 0 30rpx;
}

.logout-btn {
  height: 88rpx;
  line-height: 88rpx;
  text-align: center;
  background-color: $white;
  color: $danger-color;
  font-size: $font-size-base;
  border-radius: $border-radius-lg;
}
</style>
